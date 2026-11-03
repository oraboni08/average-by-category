FROM python:3.10-slim

WORKDIR /app

# Solo la versión con Redis necesita una librería extra
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mapper.py reducer.py mapper_redis.py reducer_redis.py generate_data.py run.sh run_redis.sh ./
COPY input/ ./input/

# Por defecto: flujo clásico del laboratorio (mapper | sort | reducer)
CMD sh run.sh input
