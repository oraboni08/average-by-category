#!/usr/bin/env python3
"""Mapper con Redis (versión extra).

Cada mapper procesa UN archivo CSV. Se pueden lanzar varios a la vez (uno por
archivo) y todos escriben en el mismo Redis.

En lugar de emitir cada valor, el mapper acumula en Redis, por cada clave,
solo tres números: count (cuántos), sum (suma) y sumsq (suma de cuadrados).
Con ellos el reducer calcula promedio y desviación estándar sin guardar los
valores, así la memoria no crece con el volumen de datos.

Claves en Redis (tipo hash):
  stats:cat:A        -> {count, sum, sumsq}   agrupado por categoría
  stats:sub:A|X      -> {count, sum, sumsq}   agrupado por categoría y subcategoría

HINCRBYFLOAT es atómico: aunque varios mappers sumen sobre la misma clave al
mismo tiempo, Redis aplica las operaciones una por una y no se pierde ninguna.
"""
import os
import sys

import redis

BATCH = 1000  # cuántos comandos se envían juntos a Redis

path = sys.argv[1]
r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)
pipe = r.pipeline(transaction=False)  # agrupa comandos para no ir a Redis por cada línea

pending = 0
records = 0
with open(path) as f:
    for line in f:
        parts = line.strip().split(",")
        if len(parts) != 3:
            continue
        category, subcategory, value = (p.strip() for p in parts)
        try:
            value = float(value)
        except ValueError:
            continue

        for key in (f"stats:cat:{category}", f"stats:sub:{category}|{subcategory}"):
            pipe.hincrbyfloat(key, "count", 1)
            pipe.hincrbyfloat(key, "sum", value)
            pipe.hincrbyfloat(key, "sumsq", value * value)
        records += 1
        pending += 1

        if pending >= BATCH:
            pipe.execute()
            pending = 0

pipe.execute()
print(f"Mapper [{os.path.basename(path)}]: {records} registros enviados a Redis")
