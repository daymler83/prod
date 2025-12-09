import pandas as pd
import glob
import os

RUTA_EXCELS = r"C:\daymler\CEPAL\prod\Datos\original"
RUTA_OUT = r"C:\daymler\CEPAL\prod\Datos"

# países que queremos conservar
PAYS_KEEP = {"Brasil", "Colombia", "Ecuador", "Perú", "Uruguay", "México", "Chile"}

def procesar_archivo(path):
    print("\nProcesando:", os.path.basename(path))
    variable = os.path.splitext(os.path.basename(path))[0]

    df = pd.read_excel(path, header=None)

    # ---- fila 0 contiene los años repetidos ----
    years_row = df.iloc[0].fillna("")
    
    # ---- fila 1 contiene los países ----
    countries_row = df.iloc[1].fillna("")
    
    # ---- datos desde fila 2 (incluyendo código y glosa) ----
    data = df.iloc[2:].reset_index(drop=True)

    # detectar posiciones donde empieza un año
    year_positions = []
    for i, val in enumerate(years_row):
        try:
            y = int(val)
            year_positions.append(i)
        except:
            pass

    registros = []

    for idx, start_col in enumerate(year_positions):
        year = int(years_row[start_col])
        
        # definir fin del bloque
        if idx < len(year_positions) - 1:
            end_col = year_positions[idx + 1]
        else:
            end_col = df.shape[1]

        # países válidos dentro del bloque
        keep_cols = []
        keep_countries = []
        
        # Recorrer todas las columnas del bloque
        for col in range(start_col, end_col):
            country = countries_row[col]
            if country in PAYS_KEEP:
                keep_cols.append(col)
                keep_countries.append(country)
        
        if len(keep_cols) == 0:
            print(f"⚠️ Año {year}: sin países válidos en {os.path.basename(path)}")
            continue
        
        print(f"  Año {year}: países encontrados {len(keep_countries)} -> {keep_countries}")

        # Las columnas 0 y 1 siempre son "Código actividad" y "Descripción"
        # IMPORTANTE: estas columnas están DUPLICADAS en cada bloque, 
        # pero solo necesitamos tomarlas una vez desde cualquier bloque

        # En tus archivos reales:
        # Columna 1 = código actividad
        # Columna 2 = glosa / descripción
        sub = data.iloc[:, [1, 2] + keep_cols].copy()
        sub.columns = ["codigo", "glosa"] + keep_countries


        
        # Verificar si código y glosa tienen valores
        print(f"  Muestra de códigos: {sub['codigo'].head(3).tolist()}")
        print(f"  Muestra de glosas: {sub['glosa'].head(3).tolist()}")
        
        # derretir
        sub = sub.melt(
            id_vars=["codigo", "glosa"],
            var_name="pais",
            value_name="valor"
        )
        
        sub["anio"] = year
        sub["variable"] = variable
        
        registros.append(sub)

    if not registros:
        print("⚠️ Archivo ignorado:", path)
        return pd.DataFrame()

    return pd.concat(registros, ignore_index=True)


def procesar_todos():
    archivos = glob.glob(os.path.join(RUTA_EXCELS, "*.xls")) + \
               glob.glob(os.path.join(RUTA_EXCELS, "*.xlsx"))

    print("\nArchivos detectados:", len(archivos))
    
    # Procesar cada archivo individualmente para diagnóstico
    resultados = []
    for i, archivo in enumerate(archivos):
        print(f"\n{'='*60}")
        print(f"Procesando archivo {i+1}/{len(archivos)}")
        df_temp = procesar_archivo(archivo)
        if not df_temp.empty:
            # Verificar qué años y países contiene este archivo
            años = df_temp['anio'].unique()
            países = df_temp['pais'].unique()
            print(f"  -> Años procesados: {sorted(años)}")
            print(f"  -> Países encontrados: {sorted(países)}")
            
            # Verificar la estructura de datos
            print(f"  -> Estructura: {df_temp.shape[0]} filas × {df_temp.shape[1]} columnas")
            print(f"  -> Columnas: {df_temp.columns.tolist()}")
            print(f"  -> Muestra de datos:")
            print(df_temp.head(3).to_string())
            
            resultados.append(df_temp)
    
    if resultados:
        df_total = pd.concat(resultados, ignore_index=True)
        
        # Mostrar resumen del consolidado final
        print(f"\n{'='*60}")
        print("RESUMEN DEL CONSOLIDADO FINAL:")
        print(f"Total de registros: {len(df_total)}")
        print(f"Columnas: {df_total.columns.tolist()}")
        
        # Mostrar distribución por año
        print("\nDistribución por año:")
        año_counts = df_total['anio'].value_counts().sort_index()
        for año, count in año_counts.items():
            print(f"  {año}: {count} registros")
        
        # Mostrar distribución por país
        print("\nDistribución por país:")
        país_counts = df_total['pais'].value_counts()
        for país, count in país_counts.items():
            print(f"  {país}: {count} registros")
        
        # Mostrar distribución por variable
        print("\nDistribución por variable:")
        var_counts = df_total['variable'].value_counts()
        for var, count in var_counts.items():
            print(f"  {var}: {count} registros")
        
        # Verificar valores únicos en código y glosa
        print(f"\nValores únicos en 'codigo': {df_total['codigo'].nunique()}")
        print(f"Valores únicos en 'glosa': {df_total['glosa'].nunique()}")
        print(f"\nMuestra de códigos y glosas:")
        print(df_total[['codigo', 'glosa']].drop_duplicates().head(10).to_string())
        
        # Verificación específica para Brasil
        print(f"\n{'='*60}")
        print("VERIFICACIÓN ESPECÍFICA PARA BRASIL:")
        brasil_data = df_total[df_total['pais'] == 'Brasil']
        print(f"Total registros de Brasil: {len(brasil_data)}")
        
        if len(brasil_data) > 0:
            print("Años disponibles para Brasil:")
            años_brasil = sorted(brasil_data['anio'].unique())
            for año in años_brasil:
                count = len(brasil_data[brasil_data['anio'] == año])
                print(f"  {año}: {count} registros")
        else:
            print("⚠️ No hay registros de Brasil en el consolidado final")
        
        # Guardar el consolidado
        out_path = os.path.join(RUTA_OUT, "consolidado_final.csv")
        df_total.to_csv(out_path, index=False, encoding="utf-8-sig")
        print(f"\n✔ Archivo generado: {out_path}")
        
        return df_total
    else:
        print("❌ No se procesó ningún archivo")
        return pd.DataFrame()


if __name__ == "__main__":
    df_final = procesar_todos()
    
    # Guardar también una versión con información sobre Brasil
    if not df_final.empty:
        brasil_df = df_final[df_final['pais'] == 'Brasil']
        if len(brasil_df) > 0:
            brasil_path = os.path.join(RUTA_OUT, "consolidado_brasil.csv")
            brasil_df.to_csv(brasil_path, index=False, encoding="utf-8-sig")
            print(f"\n✔ Archivo específico de Brasil generado: {brasil_path}")