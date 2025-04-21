import os
import subprocess
from pathlib import Path
import pyvista as pv
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import griddata

def plot_velocity_map(sim_path, tEnd, save_path="U_magnitude_raw", y_target=0.5):
    sim_path = Path(sim_path)
    output_dir = Path("output")
    output_dir_png = output_dir / "png"
    output_dir_svg = output_dir / "svg"
    output_dir_png.mkdir(exist_ok=True)
    output_dir_svg.mkdir(exist_ok=True)

    # Ejecutar foamToVTK
    try:
        subprocess.run(["foamToVTK", "-time", str(tEnd)], cwd=sim_path, check=True)
    except Exception as e:
        print("Error ejecutando foamToVTK:", e)
        return

    # Buscar archivo .vtu
    vtu_file = None
    for root, _, files in os.walk(sim_path / "VTK"):
        if "internal.vtu" in files:
            vtu_file = os.path.join(root, "internal.vtu")
            break
    if not vtu_file:
        print("Archivo internal.vtu no encontrado.")
        return

    mesh = pv.read(vtu_file)
    slice_y = mesh.slice(normal=[0, 1, 0], origin=(0, y_target, 0))

    points = slice_y.points
    x = points[:, 0]
    z = points[:, 2]

    velocities = slice_y.cell_data["U"]
    Umag = np.linalg.norm(velocities, axis = 1)

    cell_centers = slice_y.cell_centers().points  # (N, 3)
    x_cell = cell_centers[:, 0]
    z_cell = cell_centers[:, 2]

    xi = np.sort(np.unique(x_cell))
    zi = np.sort(np.unique(z_cell))
    xi_grid, zi_grid = np.meshgrid(xi, zi)

    
    Ui_grid = griddata((x_cell, z_cell), Umag, (xi_grid, zi_grid), method='linear')

    p = plt.pcolormesh(xi_grid, zi_grid, Ui_grid, shading='auto', cmap='viridis', vmin=0, vmax=1)
    plt.colorbar(p, label='|U| [m/s]')
    plt.xlabel('x')
    plt.ylabel('z')
    plt.xlim([0, 1])
    plt.ylim([0, 1])
    plt.title('Magnitud de velocidad en y = 0.5')
    plt.axis('equal')  
    plt.savefig(output_dir_svg / "Magnitud de velocidades.svg", format='svg')
    plt.savefig(output_dir_png / "Magnitud de velocidades.png")
