#!/usr/bin/env python3
"""Mapper: lee líneas CSV y emite  <clave>\t<valor>.

Formato de entrada (sin encabezado):  categoria,subcategoria,valor

--group 1  ->  clave = categoria                 (promedio por categoría)
--group 2  ->  clave = categoria\tsubcategoria   (promedio por dos columnas)

Recibe uno o varios archivos CSV como argumentos. Si no recibe ninguno, lee
de la entrada estándar, igual que el laboratorio original. Lee línea por línea
y nunca carga un archivo completo en memoria, así que sirve para archivos grandes.
"""
import argparse
import fileinput
import sys

parser = argparse.ArgumentParser()
parser.add_argument("--group", type=int, choices=[1, 2], default=2,
                    help="número de columnas para agrupar (1 o 2)")
parser.add_argument("files", nargs="*", help="archivos CSV de entrada")
args = parser.parse_args()

for line in fileinput.input(files=args.files or ("-",)):
    line = line.strip()
    if not line:
        continue

    parts = line.split(",")
    if len(parts) != 3:
        # Línea mal formada: se reporta y se ignora para no detener el trabajo
        print(f"Línea ignorada ({fileinput.filename()}): {line}", file=sys.stderr)
        continue

    category, subcategory, value = (p.strip() for p in parts)
    try:
        float(value)
    except ValueError:
        # Encabezados o valores no numéricos
        continue

    key = category if args.group == 1 else f"{category}\t{subcategory}"
    print(f"{key}\t{value}")
