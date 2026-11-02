#!/usr/bin/env python3
import redis
import math

r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

# Buscar todas las claves guardadas por el mapper
keys = r.keys("category:*")

if not keys:
    print("⚠️ No se encontraron datos en Redis.")
    sys.exit(0)

for key in sorted(keys):
    category = key.split(":")[1]
    # Obtener todos los valores acumulados en la lista de Redis
    raw_values = r.lrange(key, 0, -1)
    values = [float(v) for v in raw_values]
    
    count = len(values)
    if count == 0:
        continue
        
    # Cálculo del Promedio
    total = sum(values)
    mean = total / count
    
    # Cálculo de la Desviación Estándar Poblacional
    variance = sum((x - mean) ** 2 for x in values) / count
    std_dev = math.sqrt(variance)
    
    print(f"Categoría: {category} | Promedio: {mean:.2f} | Desv. Estándar: {std_dev:.2f} | Muestras: {count}")

# Opcional: Limpiar las claves de Redis procesadas
r.flushdb()