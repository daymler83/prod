import pandas as pd
import os
os.chdir(r"C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Datos")


df_var=pd.read_csv(r'C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Datos\original\2023\concatenado_2023.csv', sep=",")

df_defl=pd.read_excel('consolidado_final_limpio_concatenado.xlsx')
df_defl.drop(columns='glosa', inplace=True)

#print(df_var.head())
#print(df_defl.head())

df_final=pd.merge(df_var, df_defl, on=['pais', 'anio', 'codigo'], how='left')

# Eliminar Chile y México
df_final = df_final[~df_final["pais"].isin(["codigo","México"])]



#df_final = df_final.dropna(subset=["codigo", "glosa", "valor"])
df_final = df_final.dropna(subset=["codigo", "valor"])

df_final = df_final[(df_final["codigo"] != "")  & (df_final["valor"] != "")]

df_final = df_final[~((df_final["pais"] != "Chile") & (df_final["codigo"] == "CXX"))]

df_final["valor"] = pd.to_numeric(df_final["valor"], errors="coerce")

df_final["deflactor"] = df_final["deflactor"].fillna(
    df_final.groupby(["pais", "anio"])["deflactor"].transform(
        lambda s: s[df_final.loc[s.index, "codigo"] == "C"].iloc[0]
    )
)

df_final.to_excel('var_defl_2023.xlsx', index=False)