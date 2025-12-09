import pandas as pd

path = r"C:\daymler\CEPAL\prod\Datos\original\remuneracion_total_pais.xls"

df = pd.read_excel(path, header=None, dtype=str)

print("Fila 0:", df.iloc[0].tolist())
print("Fila 1:", df.iloc[1].tolist())
print("Fila 2:", df.iloc[2].tolist())
