import pandas as pd
import os
import glob
import numpy as np
import re

BASE = r"C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Datos\original\2023"
dfs = []

def extraer_variable(nombre_archivo):
    nombre = nombre_archivo.lower()
    nombre = re.sub(r"\.(csv|xlsx)$", "", nombre)
    nombre = nombre.replace("_2023", "")
    nombre = nombre.replace("_por_actividad_economica", "")
    nombre = nombre.replace("_actividad_economica", "")
    nombre = nombre.replace("_actividad_económica", "")

    # Normalizar acentos
    nombre = nombre.replace("energético", "energetico")
    nombre = nombre.replace("energética", "energetica")

    return nombre


def procesar(df, variable):
    # Renombrar columnas
    df = df.rename(columns={
        "Código actividad": "codigo",
        "codigo actividad": "codigo",
        "Descripción": "glosa",
        "descripcion": "glosa"
    })

    # Rellenar NaN donde haya "-"
    df = df.replace("-", np.nan)

    # Columnas de países (todas excepto codigo y glosa)
    id_vars = ["codigo", "glosa"]
    paises = [c for c in df.columns if c not in id_vars]

    # Convertir wide → long
    df_long = df.melt(id_vars=id_vars, var_name="pais", value_name="valor")

    # Limpiar valores
    df_long["valor"] = pd.to_numeric(df_long["valor"], errors="coerce")

    # Eliminar filas sin valor
    df_long = df_long.dropna(subset=["valor"])

    # Insertar año y variable
    df_long["anio"] = 2023
    df_long["variable"] = variable

    return df_long[["codigo", "glosa", "anio", "pais", "valor", "variable"]]


# ------------------------
# 1. Procesar CSV
# ------------------------
for file in glob.glob(BASE + "/*.csv"):
    variable = extraer_variable(os.path.basename(file))
    df = pd.read_csv(file, encoding="latin1")
    dfp = procesar(df, variable)
    dfs.append(dfp)

# ------------------------
# 2. Procesar Excel
# ------------------------
for file in glob.glob(BASE + "/*.xlsx"):
    variable = extraer_variable(os.path.basename(file))
    df = pd.read_excel(file)
    dfp = procesar(df, variable)
    dfs.append(dfp)

# ------------------------
# 3. Concatenar todo
# ------------------------
df_final = pd.concat(dfs, ignore_index=True)

# Exportar
output = BASE + r"\concatenado_2023.csv"
df_final.to_csv(output, index=False, encoding="utf-8-sig")

print("Archivo final generado en:")
print(output)
print(df_final.head())
