import pandas as pd# type: ignore
import matplotlib.pyplot as plt # type: ignore
import numpy as np # type: ignore
from pathlib import Path

# ------------------ CARGA DE DATOS ------------------ #
df_sim = pd.read_csv("output/registro_simulaciones.csv")
df_grad = pd.read_csv("output/registro_gradientes.csv")

# ------------------ CREACIÓN DE DIRECTORIOS DE SALIDA ------------------ #
output_dir = Path("output")
output_dir_png = output_dir / "png"
output_dir_svg = output_dir / "svg"
output_dir_png.mkdir(exist_ok=True)
output_dir_svg.mkdir(exist_ok=True)

# ------------------ AGRUPAR SIMULACIONES DE GRADIENTE ------------------ #
# Agrupar cada 4 filas como una única evaluación
sim_prom = df_sim.copy()
sim_prom["group"] = sim_prom.index // 4  # cada 4 simulaciones una evaluación

# Promediar Ce, Ck y Error
df_avg = sim_prom.groupby("group").agg({
    "Ce": "mean",
    "Ck": "mean",
    "Error": "mean",
    "E_U": "mean",
    "E_W": "mean",
    "Cs": "mean"
}).reset_index()

# ------------------ NORMA DEL GRADIENTE ------------------ #
df_grad["Norma_gradiente"] = np.sqrt(df_grad["Grad_Ce"]**2 + df_grad["Grad_Ck"]**2)

# CONSTANTE DE SMAGORINSKY
plt.figure(figsize=(10, 5))
plt.plot(df_avg["Cs"], marker = "o", linestyle = "--", color = '#1f77b4')
plt.xlabel("Iteración")
plt.ylabel("Cs")
plt.title("Evolución de Cs por iteración")
plt.grid(True)
plt.show()
plt.savefig(output_dir_png / "evolucion_Cs.png")
plt.savefig(output_dir_svg / "evolucion_Cs.svg", format='svg')

# ------------------ EVOLUCIÓN DEL ERROR MEDIO ------------------ #
plt.figure(figsize=(10, 5))
plt.plot(df_avg["Error"], marker="o", linestyle="--", label="Error medio")
plt.plot(df_avg["E_U"], marker="o", linestyle="--", label="E_U")
plt.plot(df_avg["E_W"], marker="o", linestyle="--", label="E_W")
plt.yscale("log")
plt.xlabel("Iteración")
plt.ylabel("Error")
plt.title("Evolución del error medio y componentes E_U, E_W por iteración")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(output_dir_png / "error_evolucion_con_componentes.png")
plt.savefig(output_dir_svg / "error_evolucion_con_componentes.svg", format='svg')
plt.show()

# ------------------ EVOLUCIÓN DE LA NORMA DEL GRADIENTE ------------------ #
plt.figure(figsize=(10, 5))
plt.plot(df_grad["Norma_gradiente"], marker="o", linestyle="--", color="#ff7f0e")
plt.yscale("log")
plt.xlabel("Iteración")
plt.ylabel("||grad||")
plt.title("Evolución de la norma del gradiente")
plt.grid(True)
plt.tight_layout()
plt.savefig(output_dir_png / "norma_gradiente.png")
plt.savefig(output_dir_svg / "norma_gradiente.svg", format='svg')
plt.show()