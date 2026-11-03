#!/usr/bin/env python3
"""Genera archivos CSV grandes para probar el flujo con volumen.

Uso:  python3 generate_data.py <carpeta_salida> <num_archivos> <filas_por_archivo>
Ej.:  python3 generate_data.py big 5 200000   ->  1.000.000 de registros
"""
import os
import random
import sys

out_dir, n_files, n_rows = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
os.makedirs(out_dir, exist_ok=True)

categories = ["A", "B", "C", "D"]
subcategories = ["X", "Y", "Z"]
random.seed(42)

for i in range(1, n_files + 1):
    path = os.path.join(out_dir, f"big_{i}.csv")
    with open(path, "w") as f:
        for _ in range(n_rows):
            f.write(f"{random.choice(categories)},{random.choice(subcategories)},"
                    f"{random.randint(1, 100)}\n")
    print(f"Generado {path}")
