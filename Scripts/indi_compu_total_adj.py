import pandas as pd
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np
import os

# === CONFIGURACIÓN DE RUTA ===
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

df_piv = (
    df.pivot_table(
        index=["anio", "pais", "glosa"],   
        columns="variable",
        values="valuedefla",
        aggfunc="first"
    )
    .reset_index()
    .rename(columns=rename_map)
)

# === 3. Calcular indicadores ===
df_piv["PL"] = df_piv["VA"] / df_piv["Ocupados"]
df_piv["CI_VA"] = df_piv["CI"] / df_piv["VA"]
df_piv["VA_VBP"] = df_piv["VA"] / df_piv["VBP"]

ind_vars = ["PL", "CI_VA", "VA_VBP"]

# === 4. Industrias comunes entre Chile y México ===
industrias_chile = set(df_piv[df_piv["pais"] == "Chile"]["glosa"].unique())
industrias_mex = set(df_piv[df_piv["pais"] == "México"]["glosa"].unique())
industrias_comunes = industrias_chile.intersection(industrias_mex)
df_common = df_piv[df_piv["glosa"].isin(industrias_comunes)].dropna(subset=ind_vars)

# === 5. Winsorizar (truncar extremos) ===
for var in ind_vars:
    low, high = df_common[var].quantile([0.01, 0.99])
    df_common[var] = df_common[var].clip(low, high)

# === FUNCIÓN GENERAL PARA CALCULAR ÍNDICE CON PCA ===
def calcular_indice_pca(df_in, años_base=(2016, 2017, 2018)):
    df = df_in.copy()
    df_base = df[df["anio"].isin(años_base)].copy()

    scaler = StandardScaler()
    X_base = scaler.fit_transform(df_base[ind_vars])
    pca = PCA(n_components=1).fit(X_base)

    loadings = pca.components_[0]
    weights = np.abs(loadings) / np.abs(loadings).sum()
    weights_dict = dict(zip(ind_vars, weights))

    # Transformar todo el conjunto
    X_all = scaler.transform(df[ind_vars])
    for i, var in enumerate(ind_vars):
        df[var + "_z"] = X_all[:, i]

    df["Indice_PCA"] = sum(df[var + "_z"] * weights_dict[var] for var in ind_vars)
    return df, weights_dict

# === 6A. Índice comparativo 2015–2022 (ambos países) ===
df_cmp = df_common[df_common["anio"] <= 2022]
df_cmp, weights_cmp = calcular_indice_pca(df_cmp)
df_country_cmp = df_cmp.groupby(["anio", "pais"])["Indice_PCA"].median().reset_index()

# === 6B. Índice extendido 2015–2023 (solo México) ===
df_mex = df_common[df_common["pais"] == "México"]
df_mex, weights_mex = calcular_indice_pca(df_mex)
df_country_mex = df_mex.groupby(["anio", "pais"])["Indice_PCA"].median().reset_index()

# === 7. Gráfico comparativo (Chile–México hasta 2022) ===
plt.figure(figsize=(8,5))
for pais in ["Chile", "México"]:
    subset = df_country_cmp[df_country_cmp["pais"] == pais]
    plt.plot(subset["anio"], subset["Indice_PCA"], marker="o", label=pais)

plt.title("Índice Compuesto de Productividad Manufacturera (PCA)\nChile y México (2015–2022)")
plt.xlabel("Año")
plt.ylabel("Índice relativo (0 = promedio)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("Indice_Manufactura_Chile_Mexico_2015_2022.png", dpi=300, bbox_inches="tight")
plt.show()

# === 8. Gráfico México extendido 2015–2023 ===
plt.figure(figsize=(8,5))
plt.plot(df_country_mex["anio"], df_country_mex["Indice_PCA"], marker="o", color="orange", label="México")
plt.title("Índice Compuesto de Productividad Manufacturera (PCA)\nMéxico (2015–2023)")
plt.xlabel("Año")
plt.ylabel("Índice relativo (0 = promedio)")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("Indice_Manufactura_Mexico_2015_2023.png", dpi=300, bbox_inches="tight")
plt.show()
