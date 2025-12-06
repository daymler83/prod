import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

path_imp=r'C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Datos'

# === 1. Leer Excel ===
df = pd.read_excel(path_imp + "/"+ "chl_mex_deflactada.xlsx", sheet_name="Sheet1")

# === 2. Industrias a analizar ===
INDUSTRIAS = [
    "Elaboración de productos alimenticios",
    "Fabricación de prendas de vestir",
    "Fabricación de productos de cuero y productos conexos",
    "Fabricación de vehículos automotores, remolques y semirremolques"
]


# === 3. Filtrar solo esas industrias ===
df_sel = df[df["glosa"].isin(INDUSTRIAS)].copy()

# === 4. Pivotear: variables como columnas ===
df_wide = df_sel.pivot_table(
    index=["anio", "pais", "glosa"],
    columns="variable",
    values="valuedefla",
    aggfunc="sum"
).reset_index()

# === 5. Calcular productividad ===
df_wide["VA_EMP"] = (
    df_wide["Valor agregado por actividad económica"]*1000000 /
    df_wide["Número de ocupados total de la industria manufacturera por país y actividad económica"]
)

df_wide["VA_HR"] = (
    df_wide["Valor agregado por actividad económica"]/
    df_wide["Horas trabajadas por actividad económica"]
)

# === 6. Reestructurar para graficar más fácil ===
df_long = df_wide.melt(
    id_vars=["anio", "pais", "glosa"],
    value_vars=["VA_EMP", "VA_HR"],
    var_name="indicador",
    value_name="valor"
)



OUTPUT_PATH = r"C:\Daymler\7. Miscelláneos\20.Cepal\Prod\Anál"
os.makedirs(OUTPUT_PATH, exist_ok=True)



PALETA = {"Chile": "#1f77b4", "México": "#ff7f0e"}

for industria in INDUSTRIAS:
    for indicador in ["VA_EMP"]:
        df_ind = df_long[
            (df_long["glosa"] == industria) &
            (df_long["indicador"] == indicador)
        ].copy()

        plt.figure(figsize=(9,6))
        ax = sns.lineplot(
            data=df_ind,
            x="anio", y="valor",
            hue="pais", marker="o", linewidth=2.5,
            palette=PALETA
        )

        plt.title(f"{industria}", fontsize=13, weight="bold", pad=20)
        plt.ylabel("USD constantes por ocupado, 2018=100", labelpad=20)
        plt.xlabel("")
        plt.legend(title="", loc="best")

        plt.tight_layout()

        # Guardar gráfico
        filename = f"{industria}_{indicador}_niveles".replace(" ", "_").replace(",", "")
        save_path = os.path.join(OUTPUT_PATH, f"{filename}.png")
        plt.savefig(save_path, dpi=600, bbox_inches="tight")
        plt.close()

        print(f"✅ Gráfico guardado: {save_path}")