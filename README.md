# 🚀 MapReduce: Promedio y Desviación Estándar por Categoría con Redis + Docker

Este proyecto es una implementación mejorada del laboratorio de **MapReduce en Python y Docker**, que utiliza **Redis** como *Broker* intermedio y almacenamiento key-value para desacoplar el procesamiento entre los Mappers y el Reducer.

---

## 🛠️ Arquitectura y Flujo de Datos

A diferencia del flujo tradicional basado en tuberías de Linux (`cat | mapper | sort | reducer`), esta arquitectura aprovecha **Redis** para gestionar las fases de almacenamiento intermedio y el **Shuffle & Sort**:

1. **Input Splitting**: El archivo `input/data.csv` entrega los registros de entrada al Mapper.
2. **Map Phase (`mapper.py`)**: Parsea las líneas del CSV y empuja (*RPUSH*) cada valor en una lista de Redis identificada por su categoría (`category:<nombre>`).
3. **Shuffle & Sort (Redis)**: Redis agrupa automáticamente de forma atómica todas las muestras correspondientes a la misma clave.
4. **Reduce Phase (`reducer.py`)**: Consulta las claves en Redis, extrae las listas de valores de cada categoría, y calcula:
   - **Promedio** por categoría.
   - **Desviación Estándar Poblacional** por categoría.
5. **Clean Up**: El Reducer limpia las claves procesadas en Redis para garantizar la idempotencia del pipeline.

---

## 📂 Estructura del Proyecto

<pre>
average-by-category/
├── docker-compose.yml     # Orquestación de servicios (Redis + MapReduce)
├── Dockerfile             # Definición del contenedor de la aplicación Python
├── requirements.txt       # Dependencias de Python (redis)
├── mapper.py              # Proceso Mapper (vuelca datos a Redis)
├── reducer.py             # Proceso Reducer (calcula métricas desde Redis)
├── README.md              # Documentación del proyecto
└── input/
    └── data.csv           # Dataset de prueba
</pre>

---

## 📋 Requisitos Previos

- Docker Engine / Docker Desktop
- Docker Compose

---

## 🚀 Cómo Ejecutar

1. **Clonar el repositorio:**
```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd average-by-category
```

2. **Construir y levantar la pila con Docker Compose:**
```bash
docker-compose up --build
```

---

## 📊 Salida Esperada en Consola

<pre>
redis-broker        | Ready to accept connections tcp
average-by-category | ✅ Mapper: Datos cargados exitosamente en Redis.
average-by-category | Categoría: A | Promedio: 4.67 | Desv. Estándar: 1.25 | Muestras: 3
average-by-category | Categoría: B | Promedio: 4.50 | Desv. Estándar: 2.50 | Muestras: 2
average-by-category | Categoría: C | Promedio: 4.00 | Desv. Estándar: 0.00 | Muestras: 1
</pre>

---

## 💡 Ventajas de la Integración con Redis

- **Escalabilidad Horizontal**: Múltiples contenedores mappers pueden ejecutarse en paralelo volcando datos de forma concurrente a la instancia de Redis.
- **Tolerancia a Fallos**: Los datos intermedios persisten en memoria en Redis sin depender del estado o canal de ejecución local de una única máquina.