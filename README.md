# MapReduce: Promedio y Desviación Estándar por Categoría con Docker + Python (+ Redis)

Laboratorio 2 – MapReduce · Profesor: Heberth Martinez

Calcula el **promedio** y la **desviación estándar** de valores numéricos agrupados por
**categoría** y por **categoría + subcategoría**, procesando **varios archivos CSV**,
con el paradigma MapReduce.

El proyecto tiene dos versiones:

| Versión | Flujo | Servicio de Docker Compose |
|---|---|---|
| **Laboratorio (base)** | `mapper.py \| sort \| reducer.py` | `mapreduce` |
| **Extra: Redis** | mappers en paralelo → Redis → `reducer_redis.py` | `redis` + `mapreduce-redis` |

---

## Estructura del proyecto

```
average-by-category/
├── docker-compose.yml   # Servicios: mapreduce, redis, mapreduce-redis
├── Dockerfile           # Imagen Python con todos los scripts
├── mapper.py            # Mapper clásico: emite <clave>\t<valor>
├── reducer.py           # Reducer clásico: promedio + desviación estándar (streaming)
├── run.sh               # Ejecuta mapper | sort | reducer sobre todos los CSV
├── mapper_redis.py      # Extra: mapper que acumula count/sum/sumsq en Redis
├── reducer_redis.py     # Extra: reducer que lee de Redis y guarda resultados
├── run_redis.sh         # Extra: lanza un mapper por CSV en paralelo y luego el reducer
├── generate_data.py     # Genera CSV grandes para pruebas de volumen
├── requirements.txt     # redis (solo para la versión extra)
└── input/
    ├── data1.csv
    ├── data2.csv
    └── data3.csv
```

Formato de los CSV (sin encabezado): `categoria,subcategoria,valor`

```
A,X,5
B,Y,7
A,Y,3
```

---

## Cómo se resolvió cada entregable

### 1. Promedio agrupando por dos columnas
`mapper.py` recibe `--group 1` o `--group 2`:

- `--group 1` → emite `A\t5` (clave = categoría)
- `--group 2` → emite `A\tX\t5` (clave = categoría + subcategoría)

`sort` ordena por la clave y el reducer toma **el último campo como valor** y todo lo
anterior como clave, así que el mismo `reducer.py` sirve para una o dos columnas.

### 2. Reducer con desviación estándar
`reducer.py` calcula, por cada clave, el **promedio** y la **desviación estándar
poblacional** `σ = √( Σ(x − μ)² / n )`.

Usa el **algoritmo de Welford**: actualiza media y varianza con cada valor que llega,
sin guardar la lista de valores. Memoria constante sin importar cuántos datos haya.

### 3. Múltiples archivos CSV y grandes volúmenes
- `run.sh` procesa **todos** los `input/*.csv`. El mapper los lee uno por uno, línea
  por línea (`fileinput`), y no se rompe si un archivo no termina en salto de línea.
- `sort` hace un ordenamiento externo: si los datos no caben en memoria, usa archivos
  temporales en disco.
- El reducer usa memoria constante (Welford).
- Las líneas mal formadas o los encabezados se ignoran sin detener el trabajo.
- `docker-compose.yml` monta `./input` como volumen: se pueden agregar CSV sin
  reconstruir la imagen.

---

## Cómo ejecutar

### Versión del laboratorio
```bash
docker compose up --build mapreduce
```

### Versión extra con Redis
```bash
docker compose up --build mapreduce-redis
```
Docker Compose levanta primero `redis`, espera a que responda (`healthcheck`) y luego
ejecuta los mappers en paralelo y el reducer.

Para consultar los resultados guardados en Redis:
```bash
docker exec -it redis-broker redis-cli KEYS "result:*"
docker exec -it redis-broker redis-cli HGETALL "result:cat:A"
```

### Prueba con volumen grande (1.000.000 de registros)
```bash
python generate_data.py big 5 200000
docker compose run --rm -v "$(pwd)/big:/app/big" mapreduce sh run.sh big
docker compose run --rm -v "$(pwd)/big:/app/big" mapreduce-redis sh run_redis.sh big
```

---

## Salida esperada (datos de `input/`)

```
== Promedio y desviación estándar por CATEGORÍA ==
Categoría   Promedio   Desv.Est   Muestras
A           4.67       1.97       6
B           5.50       2.69       4
C           4.25       1.48       4

== Promedio y desviación estándar por CATEGORÍA y SUBCATEGORÍA ==
Categoría   Subcat.   Promedio   Desv.Est   Muestras
A           X         5.00       0.82       3
A           Y         4.33       2.62       3
B           X         5.50       3.50       2
B           Y         5.50       1.50       2
C           X         3.00       1.00       2
C           Y         5.50       0.50       2
```

Ambas versiones producen los mismos números.

---

## ¿Qué aporta Redis?

| Fase MapReduce | Versión base | Versión Redis |
|---|---|---|
| Map | `mapper.py` emite cada registro | `mapper_redis.py`, uno por archivo y **en paralelo** |
| Combine | no hay | cada mapper acumula `count`, `sum` y `sumsq` en vez de enviar cada valor |
| Shuffle & Sort | `sort` | Redis agrupa por clave (un hash por grupo) |
| Reduce | `reducer.py` | `reducer_redis.py` calcula media y desviación |
| Salida | consola | consola + Redis (`result:*`) para consultar después |

`HINCRBYFLOAT` es **atómico**: varios mappers pueden sumar sobre la misma clave al
mismo tiempo sin perder datos.
