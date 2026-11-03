#!/bin/sh
# Flujo MapReduce con Redis:
#   1. Limpia los datos anteriores en Redis (para que cada ejecución empiece de cero)
#   2. Lanza un mapper POR CADA CSV, todos en paralelo
#   3. Espera a que todos terminen
#   4. Ejecuta el reducer

INPUT_DIR="${1:-input}"
REDIS_HOST="${REDIS_HOST:-redis}"

python3 -c "import redis; r=redis.Redis(host='$REDIS_HOST'); [r.delete(k) for p in ('stats:*','result:*') for k in r.scan_iter(p)]"

echo "Lanzando mappers en paralelo:"
for f in "$INPUT_DIR"/*.csv; do
  python3 mapper_redis.py "$f" &
done
wait
echo

python3 reducer_redis.py
