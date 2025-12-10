import pandas as pd
import os
os.chdir(r"C:\daymler\CEPAL\prod\Datos")


df_var=pd.read_csv('consolidado_final.csv')

df_defl=pd.read_excel('consolidado_final_limpio_concatenado.xlsx')

#print(df_var.head())
#print(df_defl.head())

df_final=pd.merge(df_var, df_defl, on=['pais', 'anio', 'codigo', 'glosa'], how='left')

# Eliminar Chile y México
df_final = df_final[~df_final["pais"].isin(["Chile", "México"])]

df_final = df_final.dropna(subset=["codigo", "glosa", "valor"])
df_final = df_final[(df_final["codigo"] != "") & (df_final["glosa"] != "") & (df_final["valor"] != "")]


df_final.to_excel('var_defl.xlsx', index=False)