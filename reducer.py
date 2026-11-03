#!/usr/bin/env python3
"""Reducer: calcula promedio y desviación estándar por clave.

Recibe la salida del mapper YA ORDENADA por `sort`, así que todas las líneas
de una misma clave llegan seguidas. La clave puede tener una columna
(categoría) o dos (categoría y subcategoría): siempre se toma el último campo
como valor y lo anterior como clave.

Para soportar grandes volúmenes no se guardan los valores: se usa el algoritmo
de Welford, que actualiza la media y la varianza en una sola pasada con
memoria constante y sin errores numéricos al sumar muchos datos.

Desviación estándar poblacional: sqrt( sum((x - media)^2) / n )
"""
import math
import sys

current_key = None
count = 0
mean = 0.0
m2 = 0.0  # suma de los cuadrados de las diferencias con la media


def emit(key, count, mean, m2):
    std_dev = math.sqrt(m2 / count)
    print(f"{key}\t{mean:.2f}\t{std_dev:.2f}\t{count}")


for line in sys.stdin:
    line = line.rstrip("\n")
    if not line:
        continue

    key, value = line.rsplit("\t", 1)
    value = float(value)

    if key != current_key:
        if current_key is not None:
            emit(current_key, count, mean, m2)
        current_key = key
        count, mean, m2 = 0, 0.0, 0.0

    # Actualización de Welford
    count += 1
    delta = value - mean
    mean += delta / count
    m2 += delta * (value - mean)

# Emitir la última clave
if current_key is not None:
    emit(current_key, count, mean, m2)
