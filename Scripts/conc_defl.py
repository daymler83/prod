import os
import pandas as pd
import glob

# Carpeta donde están tus .xlsx
folder = r"C:\daymler\CEPAL\prod\Datos\deflactores\Proc"

# Busca todos los .xlsx dentro de la carpeta
files = glob.glob(os.path.join(folder, "*.xlsx"))

# Lista donde se guardarán los dataframes
dfs = []

for f in files:
    df = pd.read_excel(f)
    df["archivo_origen"] = os.path.basename(f)  # opcional
    dfs.append(df)

# Concatenar
df_final = pd.concat(dfs, ignore_index=True)

df_final.to_excel(folder + "/" + 'concatenado.xlsx', index=False)
