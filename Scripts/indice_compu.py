import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np
import os


os.chdir(r'C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Anál\gráficos_índice_compuesto')

# === 1. Leer datos ===
path = r"C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Datos\chl_mex_deflactada.xlsx"
df = pd.read_excel(path, sheet_name="Sheet1")

# === 2. Pivotear ===
rename_map = {
    "Valor agregado por actividad económica": "VA",
    "Consumo intermedio por actividad económica": "CI",
    "Valor bruto de la producción por actividad económica": "VBP",
    "Remuneración por actividad económica": "REM",
    "Número de ocupados total de la industria manufacturera por país y actividad económica": "Ocupados",
    "Horas trabajadas por actividad económica": "Horas",
    "Consumo de energía eléctrica por actividad económica": "Energia"
}

df_piv = df.pivot_table(
    index=["anio", "pais", "glosa"],
    columns="variable",
    values="valuedefla",
    aggfunc="first"
).reset_index().rename(columns=rename_map)

# === 3. Calcular indicadores ===
df_piv["PL"] = df_piv["VA"] / df_piv["Ocupados"]
#df_piv["PL_horas"] = df_piv["VA"] / df_piv["Horas"]
df_piv["CI_VA"] = df_piv["CI"] / df_piv["VA"]
df_piv["VA_VBP"] = df_piv["VA"] / df_piv["VBP"]

ind_vars = ["PL", "CI_VA", "VA_VBP"]

# === 4. PCA con datos base 2016-2017 ===
df_base = df_piv[df_piv["anio"].isin([2016, 2017, 2018, 2019])].dropna(subset=ind_vars).copy()
scaler = StandardScaler()
X_base = scaler.fit_transform(df_base[ind_vars])

pca = PCA(n_components=1)
pca.fit(X_base)

loadings = pca.components_[0]
weights = np.abs(loadings) / np.abs(loadings).sum()
weights_dict = dict(zip(ind_vars, weights))

print("Pesos PCA:", weights_dict)

# === 5. Aplicar a todo el dataset ===
df_clean = df_piv.dropna(subset=ind_vars).copy()
X_all = scaler.transform(df_clean[ind_vars])

for i, var in enumerate(ind_vars):
    df_clean[var + "_z"] = X_all[:, i]

df_clean["IndiceCompuesto_PCA"] = sum(
    df_clean[var + "_z"] * weights_dict[var] for var in ind_vars
)

# === 6. Filtrar industrias de interés ===
INDUSTRIAS = [
    "Elaboración de productos alimenticios",
    "Fabricación de prendas de vestir",
    "Fabricación de productos de cuero y productos conexos",
    "Fabricación de vehículos automotores, remolques y semirremolques"
]

df_plot = df_clean[df_clean["glosa"].isin(INDUSTRIAS)]

# === 7. Graficar y guardar ===
for industria in INDUSTRIAS:
    data = df_plot[df_plot["glosa"] == industria]

    plt.figure(figsize=(8,5))
    for pais in ["Chile", "México"]:
        subset = data[data["pais"] == pais]
        plt.plot(subset["anio"], subset["IndiceCompuesto_PCA"], marker="o", label=pais)

    plt.title(f"ICPI - {industria}", pad=20)
    plt.xlabel("")
    plt.ylabel("Desviación estándar respecto a la media", labelpad=20)
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Guardar gráfico
    filename = industria.replace(" ", "_").replace(",", "") + ".png"
    plt.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close()

print("Gráficos guardados en la carpeta de trabajo.")
