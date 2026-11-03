#!/usr/bin/env python3
"""Reducer con Redis (versión extra).

Lee de Redis los acumulados (count, sum, sumsq) que dejaron los mappers,
calcula promedio y desviación estándar poblacional, imprime los resultados y
los guarda en Redis para consultarlos después:

  result:cat:A       -> {mean, std, count}
  result:sub:A|X     -> {mean, std, count}

Fórmulas:
  media    = sum / count
  varianza = sumsq / count - media^2
  desv.    = raíz(varianza)
"""
import math
import os

import redis

r = redis.Redis(host=os.getenv("REDIS_HOST", "redis"), port=6379, decode_responses=True)


def reduce_group(prefix, title, header):
    print(f"== {title} ==")
    print(header)
    # scan_iter recorre las claves por partes, sin bloquear Redis (a diferencia de KEYS)
    for key in sorted(r.scan_iter(f"stats:{prefix}:*")):
        data = r.hgetall(key)
        count = float(data["count"])
        mean = float(data["sum"]) / count
        variance = max(float(data["sumsq"]) / count - mean ** 2, 0.0)  # evita -0.0000001 por redondeo
        std = math.sqrt(variance)

        group = key.split(":", 2)[2]
        r.hset(f"result:{prefix}:{group}", mapping={
            "mean": round(mean, 2), "std": round(std, 2), "count": int(count)})
        print("\t".join(group.split("|")) + f"\t{mean:.2f}\t{std:.2f}\t{int(count)}")
    print()


reduce_group("cat", "Promedio y desviación estándar por CATEGORÍA (Redis)",
             "Categoría\tPromedio\tDesv.Est\tMuestras")
reduce_group("sub", "Promedio y desviación estándar por CATEGORÍA y SUBCATEGORÍA (Redis)",
             "Categoría\tSubcat.\tPromedio\tDesv.Est\tMuestras")
print("Resultados guardados en Redis con el prefijo result:")
