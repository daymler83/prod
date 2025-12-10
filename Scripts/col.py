#Colombia

import pandas as pd
import os

# Configuración
archivo_excel = r'C:\daymler\CEPAL\prod\Datos\deflactores\COL 2005-2024.xlsx'  # Cambia esto si el nombre es diferente
nombre_hoja = 'Deflactores'  # Nombre exacto de la hoja
archivo_salida = r'C:\daymler\CEPAL\prod\Datos\COL_deflactores_transformado.xlsx'


# 1. LEER EL EXCEL (manteniendo todo como texto inicialmente)
df = pd.read_excel(
    archivo_excel, 
    sheet_name=nombre_hoja,
    dtype=str  # <-- Esto es clave: leer todo como texto
)

print("✓ Archivo leído")
print(f"Filas: {len(df)}, Columnas: {len(df.columns)}")

# 2. RENOMBRAR LA PRIMERA COLUMNA A 'industria'
df = df.rename(columns={df.columns[0]: 'industria'})

# 3. ELIMINAR FILAS/COLUMNAS VACÍAS
df = df.dropna(how='all')
df = df.dropna(axis=1, how='all')

# 4. TRANSFORMAR DE ANCHO A LARGO
df_largo = df.melt(
    id_vars=['industria'],
    var_name='anio',
    value_name='valor'
)

# 5. LIMPIAR LOS DATOS
# Asegurar que 'anio' sea texto (para mantener '2023pr', '2024pro')
df_largo['anio'] = df_largo['anio'].astype(str).str.strip()

# Convertir 'valor' a número (maneja comas decimales)
def limpiar_valor(valor_str):
    if pd.isna(valor_str):
        return None
    # Reemplazar coma por punto
    return float(str(valor_str).replace(',', '.'))

df_largo['valor'] = df_largo['valor'].apply(limpiar_valor)

# Eliminar filas sin valor
df_largo = df_largo.dropna(subset=['valor'])

# 6. ORDENAR
df_largo = df_largo.sort_values(['industria', 'anio']).reset_index(drop=True)

# 7. MOSTRAR RESULTADO
print("\n✓ Transformación completada")
print(f"Total registros: {len(df_largo)}")
print(f"Años encontrados: {sorted(df_largo['anio'].unique())}")

print("\nPrimeras 10 filas:")
print(df_largo.head(10))

# Mostrar algún año con 'pr' o 'pro' si existe
if df_largo['anio'].str.contains('pr', case=False).any():
    print("\n✓ Se detectaron años con sufijos (preliminar/proyectado):")
    ejemplos = df_largo[df_largo['anio'].str.contains('pr', case=False)].head(3)
    print(ejemplos.to_string(index=False))

# 8. GUARDAR
df_largo.to_excel(archivo_salida, index=False)
print(f"\n✓ Guardado en: {archivo_salida}")