# Abre el archivo de boundary despues de haber creado la malla
# y pone los patches como walls para poder establecer bien la
# condición de nut

import re

boundary_path = "constant/polyMesh/boundary"
with open(boundary_path, "r") as file:
    lines = file.readlines()
    
pattern = re.compile(r"^\s*type\s+patch;")

with open(boundary_path, "w") as file:
    for line in lines:
        if pattern.match(line):
            line = "    type            wall;\n"
        file.write(line)