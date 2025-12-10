import pandas as pd

# Ruta del archivo
ruta = r"C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Datos\consolidado_final_limpio.xlsx"

# Hojas a incluir
paises = ["Ecuador", "Perú", "Colombia", "Brasil", "Uruguay"]

dfs = []

for pais in paises:

    # Leer hoja
    df = pd.read_excel(ruta, sheet_name=pais)

    # Identificar columnas de años (todas las que sean numéricas tipo 2016, 2017...)
    columnas_anio = [col for col in df.columns if str(col).isdigit()]

    # Melt para transformar columnas de años en filas
    df_melt = df.melt(
        id_vars=["glosa", "codigo"],     # columnas que se mantienen
        value_vars=columnas_anio,        # columnas que se convierten en filas
        var_name="anio",                 # nombre de columna nueva
        value_name="valor"               # nombre de valores
    )

    # Agregar la columna pais
    df_melt["pais"] = pais

    # Ordenar columnas
    df_melt = df_melt[["pais", "anio", "codigo", "glosa", "valor"]]
    df_melt.rename(columns={'valor':'deflactor'}, inplace=True)

    dfs.append(df_melt)

# Concatenar todos los países
consolidado = pd.concat(dfs, ignore_index=True)

# Exportar
salida = r"C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Datos\consolidado_final_limpio_concatenado.xlsx"
consolidado.to_excel(salida, index=False)


