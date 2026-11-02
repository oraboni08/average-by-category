#!/usr/bin/env python3
import sys
import redis

# Conexión al servicio de Redis en Docker
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    
    category, value = line.split(",")
    # Usamos la categoría como clave en Redis y agregamos el valor a su lista
    r.rpush(f"category:{category}", float(value))

print("✅ Mapper: Datos cargados exitosamente en Redis.")