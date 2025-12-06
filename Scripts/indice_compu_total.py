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
    index=["anio", "pais", "glosa"],   # industria 2 dígitos
    columns="variable",
    values="valuedefla",
    aggfunc="first"
).reset_index().rename(columns=rename_map)

# === 3. Calcular indicadores ===
df_piv["PL"] = df_piv["VA"] / df_piv["Ocupados"]
df_piv["CI_VA"] = df_piv["CI"] / df_piv["VA"]
df_piv["VA_VBP"] = df_piv["VA"] / df_piv["VBP"]

ind_vars = ["PL", "CI_VA", "VA_VBP"]

# === 4. Detectar industrias comunes entre Chile y México ===
industrias_chile = set(df_piv[df_piv["pais"] == "Chile"]["glosa"].unique())
industrias_mex = set(df_piv[df_piv["pais"] == "México"]["glosa"].unique())
industrias_comunes = industrias_chile.intersection(industrias_mex)
print(industrias_comunes)

# Filtrar solo esas industrias
df_common = df_piv[df_piv["glosa"].isin(industrias_comunes)].dropna(subset=ind_vars)

# === 5. PCA con base 2016–2017 (todas las industrias comunes) ===
df_base = df_common[df_common["anio"].isin([2016, 2017, 2018, 2019])].copy()
scaler = StandardScaler()
X_base = scaler.fit_transform(df_base[ind_vars])

pca = PCA(n_components=1)
pca.fit(X_base)

loadings = pca.components_[0]
weights = np.abs(loadings) / np.abs(loadings).sum()
weights_dict = dict(zip(ind_vars, weights))
print("Pesos PCA:", weights_dict)

# === 6. Calcular índice para todas las industrias ===
X_all = scaler.transform(df_common[ind_vars])
for i, var in enumerate(ind_vars):
    df_common[var + "_z"] = X_all[:, i]

df_common["Indice_PCA"] = sum(
    df_common[var + "_z"] * weights_dict[var] for var in ind_vars
)

# === 7. Agregar a nivel país–año (promedio simple de industrias comunes) ===
df_country = df_common.groupby(["anio", "pais"])["Indice_PCA"].median().reset_index()

# === 8. Graficar Chile vs México ===
'''
plt.figure(figsize=(8,5))
for pais in ["Chile", "México"]:
    subset = df_country[df_country["pais"] == pais]
    plt.plot(subset["anio"], subset["Indice_PCA"], marker="o", label=pais)

plt.title("Índice Compuesto de Productividad Manufacturera (PCA)", pad=20)
plt.xlabel("")
plt.ylabel("Índice relativo (0 = promedio)", labelpad=20)
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("Indice_Manufactura_Chile_Mexico_16_23.png", dpi=300, bbox_inches="tight")
plt.show()
'''

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

def plot_indice(df_country, smooth=False):
    plt.figure(figsize=(8,5))
    for pais in ["Chile", "México"]:
        subset = df_country[df_country["pais"] == pais]
        x = subset["anio"]
        y = subset["Indice_PCA"]

        if smooth and len(subset) > 3:
            # Interpolación spline para suavizar
            x_new = np.linspace(x.min(), x.max(), 300)
            spline = make_interp_spline(x, y, k=3)
            y_smooth = spline(x_new)
            plt.plot(x_new, y_smooth, label=f"{pais} (suavizado)")
        else:
            plt.plot(x, y, marker="o", label=pais)

    plt.title("Índice Compuesto de Productividad Manufacturera (PCA)", pad=20)
    plt.xlabel("")
    plt.ylabel("Índice relativo (0 = promedio)", labelpad=20)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig("Indice_Manufactura_Chile_Mexico_16_23.png", dpi=300, bbox_inches="tight")
    plt.show()
    plot_indice(df_country, smooth=True)

