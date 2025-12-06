import pandas as pd
import os
import numpy as np

os.chdir(r'C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Datos')

# === 1. Cargar archivos ===
df_madre = pd.read_excel("chl_mex_21_23.xlsx")
df_corr = pd.read_excel("correspondencia.xlsx")
df_chl = pd.read_excel("deflactores_chile.xlsx")
df_mex = pd.read_excel("deflactores_mexico.xlsx")

# === 2. Limpiar nombres de columnas Chile ===
df_chl.columns = df_chl.columns.str.strip()
df_chl.columns = df_chl.columns.str.replace('\xa0', '', regex=True)
df_chl.columns = df_chl.columns.str.replace('\s+', ' ', regex=True)

# === 3. Chile a formato largo ===
df_chl_long = df_chl.melt(
    id_vars=["Descripción series", "Pais"],
    var_name="IndustriaDeflactor",
    value_name="valor_deflactor"
)
df_chl_long.rename(columns={"Descripción series": "anio"}, inplace=True)
df_chl_long["anio"] = pd.to_datetime(df_chl_long["anio"]).dt.year

# === 4. México a formato largo ===
df_mex_long = df_mex.melt(
    id_vars=["Industrias", "Glosa"],
    var_name="anio",
    value_name="valor_deflactor"
)
df_mex_long["anio"] = pd.to_numeric(df_mex_long["anio"], errors="coerce")
df_mex_long = df_mex_long.dropna(subset=["anio"])
df_mex_long["anio"] = df_mex_long["anio"].astype(int)

# === 5. Unir madre con correspondencia ===
df_madre = df_madre.merge(
    df_corr,
    left_on=["pais", "glosa"],
    right_on=["Pais", "IndustriaBadecon"],
    how="left"
)

# === 6. Pegar deflactores 2 dígitos ===
# Chile
df_madre = df_madre.merge(
    df_chl_long[["anio", "IndustriaDeflactor", "valor_deflactor"]],
    on=["anio", "IndustriaDeflactor"],
    how="left"
)

# México
df_madre = df_madre.merge(
    df_mex_long[["anio", "Glosa", "valor_deflactor"]],
    left_on=["anio", "IndustriaDeflactor"],
    right_on=["anio", "Glosa"],
    how="left",
    suffixes=("", "_mex")
)

# Columna final de deflactor específico
df_madre["deflactores2d"] = df_madre.apply(
    lambda x: x["valor_deflactor"] if x["pais"] == "Chile" else x["valor_deflactor_mex"],
    axis=1
)

# === 7. Pegar deflactor general (Industria Manufacturera) ===
# Chile
df_manuf_chl = df_chl_long[df_chl_long["IndustriaDeflactor"] == "Industria Manufacturera"]\
    .rename(columns={"valor_deflactor": "deflactoresletra"})[["anio", "deflactoresletra"]]

df_madre = df_madre.merge(df_manuf_chl, on="anio", how="left")

# México
df_manuf_mex = df_mex_long[df_mex_long["Glosa"] == "Industrias manufactureras"]\
    .rename(columns={"valor_deflactor": "deflactoresletra"})[["anio", "deflactoresletra"]]

df_madre = df_madre.merge(df_manuf_mex, on="anio", how="left", suffixes=("", "_mex"))

# Seleccionar el deflactor general correcto según país
df_madre["deflactoresletra"] = df_madre.apply(
    lambda x: x["deflactoresletra"] if x["pais"] == "Chile" else x["deflactoresletra_mex"],
    axis=1
)

anio_list = list(range(2015, 2025))
df_filtrado = df_madre.loc[df_madre["anio"].astype(int).isin(anio_list)]

# === 8. Crear "deflactores2dfinal" ===
df_filtrado["deflactores2dfinal"] = df_filtrado["deflactores2d"].fillna(df_filtrado["deflactoresletra"])

# === ⚙️ NUEVO BLOQUE: Calcular VA = VBP - CI (antes de deflactar) ===
# Pivot a formato ancho temporal
df_tmp = df_filtrado.pivot_table(
    index=["anio", "pais", "glosa", "unit", "fuente", "IndustriaDeflactor"],
    columns="variable",
    values="value",
    aggfunc="first"
).reset_index()

# Calcular VA (solo donde existan VBP y CI)
df_tmp["VA"] = df_tmp["VBP"] - df_tmp["CI"]

# Volver a formato largo e integrar al df_filtrado
df_va_long = df_tmp.melt(
    id_vars=["anio", "pais", "glosa", "unit", "fuente", "IndustriaDeflactor"],
    value_name="value",
    var_name="variable"
)

# Reunir con deflactores
df_filtrado = df_va_long.merge(
    df_filtrado[["anio", "pais", "glosa", "deflactores2dfinal"]],
    on=["anio", "pais", "glosa"],
    how="left"
)

# === 9. Deflactar los datos ===
df_filtrado['valuedefla'] = df_filtrado['value']
df_filtrado.loc[
    (df_filtrado['unit'].isin(['Millones de dólares', 'Dólares'])) &
    (df_filtrado['variable'].isin(['VBP', 'CI', 'VA', 'REM'])),
    'valuedefla'
] = df_filtrado['value'] / df_filtrado['deflactores2dfinal'] * 100

# === ⚙️ NUEVO BLOQUE: Convertir valores deflactados a millones de USD ===
df_filtrado.loc[
    (df_filtrado['variable'].isin(['VBP', 'CI', 'VA', 'REM'])),
    'valuedefla'
] = df_filtrado['valuedefla'] / 1_000_000

# === ⚙️ NUEVO BLOQUE: Renombrar variables según formato largo ===
rename_vars = {
    "VA": "Valor agregado por actividad económica",
    "CI": "Consumo intermedio por actividad económica",
    "VBP": "Valor bruto de la producción por actividad económica",
    "REM": "Remuneración por actividad económica",
    "EMP": "Número de ocupados total de la industria manufacturera por país y actividad económica"
}
df_filtrado["variable"] = df_filtrado["variable"].replace(rename_vars)

# === 10. Filtro columnas ===
filtro_col = [
    'anio', 'pais', 'value', 'unit', 'fuente', 'variable', 'glosa',
    'deflactores2dfinal', 'valuedefla'
]
df_filtrado_sh = df_filtrado[filtro_col].drop_duplicates()

# === 11. Exportar resultado ===
df_filtrado_sh.to_excel("chl_mex_deflactada_21_23.xlsx", index=False)
print("Archivo final guardado como 'chl_mex_deflactada_21_23.xlsx'")
