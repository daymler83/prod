import pandas as pd
import re

archivo_excel = r'C:\daymler\CEPAL\prod\Datos\deflactores\PER 2007-2024.xlsx'
archivo_salida = r'C:\daymler\CEPAL\prod\Datos\deflactores\deflactores_peru.xlsx'

print("Procesando Perú...")

# 1. Leer archivo
df = pd.read_excel(archivo_excel, sheet_name="Deflactores")

# 2. Limpiar nombres de columnas
df.columns = [str(c).strip() for c in df.columns]

# 3. RENOMBRAR LA COLUMNA REAL DE INDUSTRIA
# LA COLUMNA CORRECTA ES 'Unnamed: 2'
df = df.rename(columns={'Unnamed: 2': 'industria'})

# 4. Eliminar filas sin industria
df = df[df['industria'].notna()]
df['industria'] = df['industria'].astype(str).str.strip()
df = df[df['industria'] != '']

# 5. Identificar columnas de años
columnas_años = []
for col in df.columns:
    col_str = str(col)
    if col_str.isdigit():  # 2007, 2008, ..., 2021
        columnas_años.append(col)
    elif re.match(r'^\d{4}[A-Za-z\/]+$', col_str):  # 2022P/, 2023E/
        columnas_años.append(col)

# 6. Transformar a formato largo
df_largo = df.melt(
    id_vars=['industria'],
    value_vars=columnas_años,
    var_name='anio',
    value_name='valor'
)

# 7. Limpiar valor
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

# 8. Limpiar año
df_largo['anio'] = df_largo['anio'].astype(str).str.extract(r'(\d{4})')

# 9. Ordenar y guardar
df_final = df_largo[['anio', 'industria', 'valor']].sort_values(['industria', 'anio'])
df_final.to_excel(archivo_salida, index=False)

print("✓ Perú procesado correctamente")
print("✓ Registros:", len(df_final))
print("✓ Años:", sorted(df_final['anio'].unique()))

print("\nEjemplos de industrias:")
print(df_final['industria'].unique()[:15])
