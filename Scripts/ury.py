import pandas as pd
import re

# CONFIGURACIÓN
archivo_excel = r'C:\daymler\CEPAL\prod\Datos\deflactores\URY 2016-2023.xlsx'
nombre_hoja = 'Deflactores'
archivo_salida = r'C:\daymler\CEPAL\prod\Datos\deflactores\deflactores_uruguay.xlsx'

print("Procesando Uruguay...")

# 1. Leer archivo
df = pd.read_excel(archivo_excel, sheet_name=nombre_hoja, dtype=str)

# 2. Limpiar nombres de columnas
df.columns = [str(col).strip() for col in df.columns]

# 3. Renombrar columnas importantes
df = df.rename(columns={
    'Código': 'codigo',
    'Descripción': 'industria'
})

# 4. Limpiar texto de industria
def limpiar_industria(x):
    if pd.isna(x):
        return ''
    x = str(x)
    x = re.sub(r'\s+', ' ', x)
    return x.strip()

df['industria'] = df['industria'].apply(limpiar_industria)

# 5. Identificar columnas de años (incluye 2022*, 2023*)
columnas_años = []
for col in df.columns:
    col_str = str(col).strip()
    
    # Año limpio 2016–2021
    if col_str.isdigit() and len(col_str) == 4:
        columnas_años.append(col)
    
    # Año con asterisco: "2022*", "2023*"
    elif re.match(r'^\d{4}\*', col_str):
        columnas_años.append(col)

# 6. Transformar a formato largo
df_largo = df.melt(
    id_vars=['codigo', 'industria'],
    value_vars=columnas_años,
    var_name='anio',
    value_name='valor'
)

# 7. Limpiar año (eliminar * si existe)
df_largo['anio'] = df_largo['anio'].str.extract(r'(\d{4})')

# 8. Limpiar valor
def limpiar_valor(v):
    if pd.isna(v):
        return None
    v = str(v).replace(',', '.')
    try:
        return float(v)
    except:
        return None

df_largo['valor'] = df_largo['valor'].apply(limpiar_valor)
df_largo = df_largo.dropna(subset=['valor'])

# 9. Ordenar y guardar
df_final = df_largo[['anio', 'codigo', 'industria', 'valor']]\
    .sort_values(['codigo', 'anio'])

df_final.to_excel(archivo_salida, index=False)

print("✓ Uruguay procesado correctamente")
print("✓ Registros:", len(df_final))
print("✓ Industrias:", df_final['industria'].nunique())
print("✓ Años:", sorted(df_final['anio'].unique()))

print("\nEjemplos de industrias:")
print(df_final['industria'].unique()[:10])
