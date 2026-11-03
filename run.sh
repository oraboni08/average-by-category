#!/bin/sh
# Ejecuta el flujo MapReduce clásico:  mapper | sort | reducer
# sobre TODOS los CSV de la carpeta (por defecto input/).
#
# LC_ALL=C hace que sort compare byte a byte (más rápido y estable).
# sort ordena por disco con archivos temporales cuando los datos no caben
# en memoria, así que el paso "shuffle & sort" funciona con archivos grandes.

INPUT_DIR="${1:-input}"
FILES=$(ls "$INPUT_DIR"/*.csv)
TAB=$(printf '\t')

echo "Archivos de entrada:"
for f in $FILES; do echo "  - $f"; done
echo

echo "== Promedio y desviación estándar por CATEGORÍA =="
printf "Categoría\tPromedio\tDesv.Est\tMuestras\n"
python3 mapper.py --group 1 $FILES | LC_ALL=C sort -t "$TAB" -k1,1 | python3 reducer.py
echo

echo "== Promedio y desviación estándar por CATEGORÍA y SUBCATEGORÍA =="
printf "Categoría\tSubcat.\tPromedio\tDesv.Est\tMuestras\n"
python3 mapper.py --group 2 $FILES | LC_ALL=C sort -t "$TAB" -k1,2 | python3 reducer.py
