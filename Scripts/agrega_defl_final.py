import pandas as pd
import os
os.chdir(r"C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Datos")

df_var = pd.read_csv('consolidado_final.csv')
df_defl = pd.read_excel('consolidado_final_limpio_concatenado.xlsx')

df_final = pd.merge(df_var, df_defl, on=['pais', 'anio', 'glosa', "codigo"], how='left')
'''
# Eliminar filas donde pais es Chile o México
df_final = df_final[~df_final["pais"].isin(["codigo","Chile", "México"])]

# Eliminar filas con NaN en codigo, glosa o valor
df_final = df_final.dropna(subset=["codigo", "glosa", "valor"])


# Eliminar códigos que comienzan con CXX
df_final = df_final[~df_final["codigo"].str.startswith("CXX", na=False)]

# ================================
# 🔥 RELLENAR DEFLECTOR FALTANTE
# ================================

# Asegurar que deflactor es numérico
df_final["deflactor"] = pd.to_numeric(df_final["deflactor"], errors="coerce")

# Extraer deflactor del código C por país y año
c_def_map = (
    df_final[df_final["codigo"] == "C"]
    .drop_duplicates(subset=["pais", "anio"], keep="first")
    .set_index(["pais", "anio"])["deflactor"]
)

# Rellenar deflactor vacío con deflactor de C
df_final["deflactor"] = df_final["deflactor"].fillna(
    df_final.set_index(["pais", "anio"]).index.map(c_def_map)
)
'''


print(df_final.head())
#df_final.to_excel('var_defl.xlsx', index=False)
