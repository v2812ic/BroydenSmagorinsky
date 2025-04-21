import classy_blocks as cb
import os
import re 

import json


with open("caseData.json", "r") as f:
    params = json.load(f)


L = params["L"]
N = params["N"]
Re = params["Re"]
U = params["U"]
deltaT = params["deltaT"]
tEnd = params["tEnd"]


# -------------------------------------------------
#--------------------------------------------------------------
# Edición de las condiciones de contorno y la viscosidad dinámica

nu = L*U/Re

# chmod +x runCase.sh

#--------------------------------------------------------------
# Edición del point shifter

pointShifter_path = "pointsShifter.py"
with open(pointShifter_path, "r") as file:
    content = file.read()

content = re.sub(r"Nx,\s*Ny,\s*Nz\s*=\s*\d+,\s*\d+,\s*\d+",
                 f"Nx, Ny, Nz = {N}, {N}, {N}", content)
content = re.sub(r"dx,\s*dy,\s*dz\s*=\s*\d+,\s*\d+,\s*\d+",
                 f"dx, dy, dz = {L}, {L}, {L}", content)

with open(pointShifter_path, "w") as file:
    file.write(content)
#---------------------------------------------------------------
# Edición del ControlDict para poder generar todo desde aquí

controlDict_path = "system/controlDict"
with open(controlDict_path, "r") as file:
    lines = file.readlines()

patterns = {
    "deltaT": re.compile(r"^\s*deltaT\s+(\S+);"),
    "endTime": re.compile(r"^\s*endTime\s+(\S+);"),
    "writeInterval": re.compile(r"^\s*writeInterval\s+(\S+);"),
}

new_values = {
    "deltaT": deltaT,
    "endTime": tEnd,
    "writeInterval": 1/deltaT,
}

with open(controlDict_path, "w") as file:
    for line in lines:
        for key, pattern in patterns.items():
            if pattern.match(line):
                line = f"{key}          {new_values[key]};\n"
        file.write(line)

# EDICION DE VELOCIDAD Y NU

transport_path = "constant/transportProperties"
if os.path.exists(transport_path):
    with open(transport_path, "r") as file:
        lines = file.readlines()

    nu_pattern = re.compile(r"^\s*nu\s+(\S+);")

    with open(transport_path, "w") as file:
        for line in lines:
            if nu_pattern.match(line):
                line = f"nu              {nu};\n"
            file.write(line)

U_path = "0/U"
if os.path.exists(U_path):
    with open(U_path, "r") as file:
        content = file.read()

    # Cambiar internalField
    content = re.sub(r"internalField\s+uniform\s+\(.+?\);",
                     f"internalField   uniform ({U} 0 0);", content)

    # Cambiar valor en el patch 'lid'
    content = re.sub(r"(lid\s*\{[^}]*value\s+uniform\s+)\(.+?\);",
                     rf"\1({U} 0 0);", content, flags=re.DOTALL)

    with open(U_path, "w") as file:
        file.write(content)

# -----------------------------
# Generar malla con Classy Blocks
                
base_points = [
    [0, 0, 0],
    [L, 0, 0],
    [L, L, 0],
    [0, L, 0]
]

base_face = cb.Face(base_points)

extruded_block = cb.Extrude(base_face, L)

extruded_block.set_patch('top', 'lid')
extruded_block.set_patch(['bottom', 'left', 'right', 'front', 'back'], 'walls')

extruded_block.chop(0, count = N)
extruded_block.chop(1, count = N)
extruded_block.chop(2, count = N)

mesh = cb.Mesh()
mesh.add(extruded_block)
if not os.path.exists('system'):
    os.makedirs('system')
mesh.write('system/blockMeshDict')