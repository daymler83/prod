import pandas as pd

# CONFIGURACIÓN PARA BRASIL
archivo_excel = r'C:\daymler\CEPAL\prod\Datos\deflactores\BRA 2000-2024.xlsx'  # Archivo de Brasil
nombre_hoja = 'Deflactores'           # Nombre de la hoja
archivo_salida = r'C:\daymler\CEPAL\prod\Datos\deflactores\deflactores_brasil.xlsx'

# 1. LEER EL ARCHIVO EXCEL
print(f"Leyendo archivo: {archivo_excel}")
df = pd.read_excel(
    archivo_excel, 
    sheet_name=nombre_hoja,
    dtype=str  # Leer todo como texto
)

print(f"✓ Archivo leído: {len(df)} filas, {len(df.columns)} columnas")

# 2. RENOMBRAR LA PRIMERA COLUMNA
# La primera columna contiene los nombres de las industrias
df = df.rename(columns={df.columns[0]: 'industria'})
print(f"✓ Columna renombrada: '{df.columns[0]}'")

# 3. ELIMINAR FILAS Y COLUMNAS VACÍAS
df = df.dropna(how='all')
df = df.dropna(axis=1, how='all')
print(f"✓ Datos limpios: {len(df)} filas, {len(df.columns)} columnas")

# 4. TRANSFORMAR DE ANCHO A LARGO
df_largo = df.melt(
    id_vars=['industria'],
    var_name='anio',
    value_name='valor'
)
print(f"✓ Transformado a formato largo: {len(df_largo)} registros")

# 5. LIMPIAR Y CONVERTIR DATOS
# Mantener año como texto (para posibles sufijos como 'pr', 'pro')
df_largo['anio'] = df_largo['anio'].astype(str).str.strip()

# Convertir valor a número (manejar comas decimales del portugués)
def convertir_valor_brasil(valor_str):
    """Convierte valores brasileños con coma decimal a float"""
    if pd.isna(valor_str):
        return None
    
    valor_str = str(valor_str).strip()
    
    # Reemplazar coma por punto para conversión a float
    if ',' in valor_str:
        # Asegurarse de que solo haya una coma (para decimales)
        valor_str = valor_str.replace(',', '.')
    
    try:
        return float(valor_str)
    except:
        return None

df_largo['valor'] = df_largo['valor'].apply(convertir_valor_brasil)

# Eliminar filas sin valor válido
filas_antes = len(df_largo)
df_largo = df_largo.dropna(subset=['valor'])
print(f"✓ Valores convertidos: {len(df_largo)} registros válidos (eliminados {filas_antes - len(df_largo)})")

# 6. ORDENAR LOS DATOS
df_largo = df_largo.sort_values(['industria', 'anio']).reset_index(drop=True)

# 7. MOSTRAR RESULTADOS
print("\n" + "="*50)
print("RESULTADO FINAL - BRASIL")
print("="*50)

print(f"\n📊 ESTADÍSTICAS:")
print(f"• Total de registros: {len(df_largo):,}")
print(f"• Industrias únicas: {df_largo['industria'].nunique()}")
print(f"• Años disponibles: {sorted(df_largo['anio'].unique())}")

print(f"\n📅 RANGO DE AÑOS:")
anios = df_largo['anio'].unique()
print(f"• Desde: {min(anios)}")
print(f"• Hasta: {max(anios)}")

print(f"\n🏭 PRIMERAS 5 INDUSTRIAS:")
for industria in df_largo['industria'].unique()[:5]:
    print(f"  • {industria}")

print(f"\n📋 MUESTRA DE DATOS (primeras 10 filas):")
print(df_largo.head(10).to_string(index=False))

print(f"\n🔍 EJEMPLO DE UNA INDUSTRIA ('Agricultura...'):")
if 'Agricultura' in df_largo['industria'].iloc[1]:
    muestra = df_largo[df_largo['industria'] == df_largo['industria'].iloc[1]].head(5)
    print(muestra.to_string(index=False))

# 8. GUARDAR EN CSV
df_largo.to_excel(archivo_salida, index=False)
print(f"\n💾 ARCHIVO GUARDADO:")
print(f"• Nombre: {archivo_salida}")
print(f"• Tamaño aproximado: {len(df_largo) * 50:,} bytes")
print(f"• Columnas: {', '.join(df_largo.columns)}")

print("\n✅ PROCESO DE BRASIL COMPLETADO CON ÉXITO")