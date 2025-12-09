import pandas as pd
import numpy as np

# CONFIGURACIÓN SIMPLE PARA ECUADOR
archivo_excel =  r'C:\daymler\CEPAL\prod\Datos\deflactores\ECU 2018-2023.xlsx'
nombre_hoja = 'Deflactores'
archivo_salida =  r'C:\daymler\CEPAL\prod\Datos\deflactores\deflactores_ecuador.xlsx'


print(f"Leyendo archivo: {archivo_excel}")
df = pd.read_excel(archivo_excel, sheet_name=nombre_hoja, dtype=str)
print(df.columns.tolist())

# 1. LIMPIAR NOMBRES DE COLUMNAS
df.columns = [str(col).strip() for col in df.columns]
print(f"Columnas originales: {df.columns.tolist()}")

# 2. RELLENAR VALORES NaN EN TODAS LAS COLUMNAS DE TEXTO
for col in df.columns:
    if df[col].dtype == 'object':
        df[col] = df[col].fillna('')

# 3. CREAR UNA COLUMNA UNIFICADA DE INDUSTRIA
def crear_industria_unificada(fila):

    ciiu = str(fila['CIIU']).strip() if pd.notna(fila['CIIU']) else ''
    cod  = str(fila['COD.']).strip() if pd.notna(fila['COD.']) else ''
    industria = str(fila['Industria']).strip() if pd.notna(fila['Industria']) else ''

    # 1. Si es industria normal
    if industria:
        return industria

    # 2. Si COD tiene el total
    if cod.lower().startswith("total"):
        return cod.strip()

    # 3. Detectar encabezados del tipo "A -Agricultura…"
    if isinstance(ciiu, str) and "-" in ciiu:
        partes = ciiu.split("-", 1)
        if len(partes) == 2:
            nombre = partes[1].strip()
            return f"Total {nombre}"

    # 4. Usar CIIU si no hay industria ni total explícito
    if ciiu:
        return ciiu

    return None

# Aplicar la función a cada fila
df['industria_unificada'] = df.apply(crear_industria_unificada, axis=1)

# 4. IDENTIFICAR COLUMNAS DE AÑOS
columnas_años = []
for col in df.columns:
    col_str = str(col).strip()
    # Buscar columnas que sean números de 4 dígitos (años)
    if col_str.isdigit() and len(col_str) == 4:
        columnas_años.append(col)

print(f"\nAños encontrados: {columnas_años}")

# 5. VERIFICAR ALGUNAS FILAS PARA DEBUG
print("\n=== EJEMPLOS DE CONVERSIÓN ===")
for i in range(min(20, len(df))):
    ciiu = str(df.iloc[i, 0]).strip()
    cod = str(df.iloc[i, 1]).strip()
    industria_orig = str(df.iloc[i, 2]).strip()
    industria_unif = df.iloc[i]['industria_unificada']
    
    if 'Total' in industria_unif or not industria_orig:
        print(f"Fila {i}:")
        print(f"  CIIU: '{ciiu}'")
        print(f"  COD: '{cod}'")
        print(f"  Industria original: '{industria_orig}'")
        print(f"  → Industria unificada: '{industria_unif}'")
        print()

# 6. TRANSFORMAR DE ANCHO A LARGO
df_largo = df.melt(
    id_vars=['industria_unificada'],
    value_vars=columnas_años,
    var_name='anio',
    value_name='valor_str'
)

print(f"\nTotal de registros antes de limpiar: {len(df_largo)}")

# 7. FUNCIÓN MEJORADA PARA LIMPIAR VALORES
def limpiar_valor_ecuador_mejorado(valor):
    if pd.isna(valor) or str(valor).strip() == '':
        return None
    
    valor_str = str(valor).strip()
    
    # Casos especiales que podrían aparecer
    if valor_str.lower() in ['nan', 'na', 'n/a', 'null', 'none']:
        return None
    
    # Limpiar espacios múltiples
    valor_str = ' '.join(valor_str.split())
    
    # Reemplazar coma decimal por punto
    valor_str = valor_str.replace(',', '.')
    
    # Extraer solo la parte numérica (permitir punto decimal)
    import re
    # Buscar patrones numéricos como 100.0, 100,0, 100.00, etc.
    match = re.search(r'[-+]?\d*\.?\d+', valor_str)
    
    if match:
        try:
            return float(match.group())
        except:
            return None
    
    return None

# 8. APLICAR LIMPIEZA
df_largo['valor'] = df_largo['valor_str'].apply(limpiar_valor_ecuador_mejorado)

# 9. ELIMINAR FILAS SIN VALORES VÁLIDOS
filas_antes = len(df_largo)
df_largo = df_largo.dropna(subset=['valor'])
print(f"Registros válidos después de limpieza: {len(df_largo)}")
print(f"Registros eliminados: {filas_antes - len(df_largo)}")

# 10. CREAR DATAFRAME FINAL
df_final = df_largo[['anio', 'industria_unificada', 'valor']].copy()
df_final = df_final.rename(columns={'industria_unificada': 'industria'})

# 11. ORDENAR
df_final = df_final.sort_values(['industria', 'anio']).reset_index(drop=True)

# 12. VERIFICAR QUE LOS TOTALES ESTÉN PRESENTES
print("\n=== VERIFICACIÓN DE TOTALES ===")
industrias_con_total = [ind for ind in df_final['industria'].unique() if 'total' in ind.lower()]
print(f"Totales encontrados: {len(industrias_con_total)}")

for total in industrias_con_total:
    # Contar cuántos registros tiene este total
    count = len(df_final[df_final['industria'] == total])
    # Verificar si tiene valores para todos los años
    años_para_total = df_final[df_final['industria'] == total]['anio'].nunique()
    print(f"  '{total}': {count} registros, {años_para_total} años")

# 13. MOSTRAR DISTRIBUCIÓN COMPLETA
print("\n=== DISTRIBUCIÓN DE INDUSTRIAS ===")
print(f"Total de industrias únicas: {df_final['industria'].nunique()}")

# Separar en categorías
df_final['es_total'] = df_final['industria'].str.lower().str.contains('total')
df_final['es_subtotal'] = df_final['industria'].str.lower().str.contains('subtotal')

totales = df_final[df_final['es_total']]
no_totales = df_final[~df_final['es_total']]

print(f"\nIndustrias regulares: {no_totales['industria'].nunique()}")
print(f"Totales: {totales['industria'].nunique()}")

# Mostrar ejemplos de cada tipo
print("\n--- Ejemplos de industrias regulares ---")
for ind in no_totales['industria'].unique()[:10]:
    print(f"  • {ind}")

print("\n--- Ejemplos de totales ---")
for ind in totales['industria'].unique():
    print(f"  • {ind}")

# 14. GUARDAR
df_final[['anio', 'industria', 'valor']].to_excel(archivo_salida, index=False)

print(f"\n💾 ARCHIVO GUARDADO: {archivo_salida}")
print(f"📊 Estadísticas finales:")
print(f"   • Total registros: {len(df_final)}")
print(f"   • Industrias únicas: {df_final['industria'].nunique()}")
print(f"   • Años: {sorted(df_final['anio'].unique())}")

print("\n📋 MUESTRA DE DATOS (incluyendo totales):")
# Mostrar algunas filas con totales
muestra_totales = df_final[df_final['es_total']].head(10)
if len(muestra_totales) > 0:
    print("\nTotales:")
    print(muestra_totales.to_string(index=False))

# Mostrar algunas filas sin totales
muestra_regulares = df_final[~df_final['es_total']].head(10)
if len(muestra_regulares) > 0:
    print("\nIndustrias regulares:")
    print(muestra_regulares.to_string(index=False))

print("\n✅ PROCESO COMPLETADO")