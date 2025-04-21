#!/bin/bash

source venv/bin/activate

command -v jq >/dev/null 2>&1 || { echo >&2 "jq no está instalado. Abortando."; exit 1; }

echo "Creando directorio para la simulación"
DIR_NUEVO="_run_$(date +%Y%m%d_%H%M%S)"

rsync -av \
  --include="0/***" \
  --include="constant/***" \
  --include="system/***" \
  --include="*.py" \
  --include="*.json" \
  --exclude="*" \
  ./ "$DIR_NUEVO/"
cd "$DIR_NUEVO" || exit

mkdir -p "output"

echo "Creando malla, actualizando controlDict"
python3 meshGenerator.py

blockMesh

echo "Moviendo puntos"
python3 pointsShifter.py

echo "Estableciendo condiciones de contorno"
python3 boundary.py

echo "Comienza el análisis"
echo "Calculando la iteración inicial"
python3 runCases_Broyden.py

echo "Generando gráficas"
python3 plotter.py

echo "Limpiando carpeta"
shopt -s extglob
borrarSim=$(jq -r '.borrar_SIMS' caseData.json)

if [ "$borrarSim" = 1 ]; then
  rm -rf !('output'|'caseData.json')
else
  rm -rf !('simulaciones'|'output'|'caseData.json')
fi

echo "Fin, gracias por la paciencia"
echo "Si la simulación ha tardado mucho y tenías guardar sims activado, mira de borrar tu papelera de reciclaje. Puede ser que te haya dejado sin memoria"
