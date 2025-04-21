import numpy as np # type: ignore
import re
import json

Nx, Ny, Nz = 10, 10, 10
x0, y0, z0 = 0, 0, 0
dx, dy, dz = 1, 1, 1
# Cambiar según la simulacion y la precisión

deltaX = dx/Nx
deltaY = dy/Ny
deltaZ = dz/Nz

with open("caseData.json", "r") as file:
    params = json.load(file)

xi = params["xi"]

def shift(x, y, z):

    if x != x0 and x != (x0 + dx):
        x = dx/2 * (1 + (np.tanh(xi*(2*(x/deltaX)/(Nx)-1)))/np.tanh(xi))
    if y != y0 and y != (y0 + dy):
        y = dy/2 * (1 + (np.tanh(xi*(2*(y/deltaY)/(Ny)-1)))/np.tanh(xi))
    if z != z0 and z != (z0 + dz):
        z = dz/2 * (1 + (np.tanh(xi*(2*(z/deltaZ)/(Nz)-1)))/np.tanh(xi))

    return x, y, z

inputFile = "constant/polyMesh/points"
outputFile = inputFile

with open(inputFile, "r") as f:
    lines = f.readlines()

newLines = []

pattern = re.compile(r"\(\s*([\d.eE+-]+)\s+([\d.eE+-]+)\s+([\d.eE+-]+)\s*\)")

for line in lines:
    match = pattern.match(line.strip())
    if match:
        x, y, z = map(float, match.groups())
        x, y, z = shift(x, y, z)
        newLines.append(f"({x:.6f} {y:.6f} {z:.6f})\n")
    else:
        newLines.append(line)

with open(outputFile, "w") as f:
    f.writelines(newLines)
