# Laboratorio Final (2) — Pipeline ETL con FastAPI

**Curso:** Bases de Datos
**Docente:** Miguel Ramos García  
**Universidad de Antioquia**  
**Entrega:** Junio 2026

---

## Descripción

Aplicación backend que orquesta un proceso ETL completo usando la PokéAPI como fuente de datos. El sistema expone 5 endpoints en FastAPI: tres para el pipeline ETL (Extracción, Transformación/Carga, Reset) y dos para Analítica (análisis por columna y perfil dual Mongo/SQL).

## Flujo de Datos

Fuente: PokéAPI (pokeapi.co)
↓
Staging (NoSQL): MongoDB — almacena la data cruda
↓
Data Warehouse (SQL): MySQL — almacena la data limpia y estructurada

## Tecnologías

- **FastAPI** — Framework web para los endpoints
- **MongoDB** — Base de datos NoSQL (staging)
- **MySQL** — Base de datos SQL (data warehouse)
- **Pandas** — Transformación y limpieza de datos
- **SQLAlchemy** — ORM para MySQL
- **PyMongo** — Cliente para MongoDB
- **Python 3.11+**

---

## Estructura del Proyecto

```text
laboratorio_etl/
├── .env                              # Credenciales (NO se sube al repo)
├── .gitignore
├── requirements.txt
└── app/
    ├── main.py                       # Inicialización de FastAPI
    ├── config.py                     # Variables de entorno
    ├── database.py                   # Conexiones Mongo/MySQL
    ├── controllers/
    │   ├── etl_controller.py         # Rutas ETL
    │   └── analitica_controller.py   # Rutas Analítica
    ├── models/
    │   └── personajes_sql.py         # Tabla MySQL (SQLAlchemy)
    ├── services/
    │   ├── etl_service.py            # Lógica ETL
    │   └── analitica_service.py      # Lógica Analítica
    └── views/
        └── schemas.py                # Esquemas Pydantic
```

---

## Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/Santiago-montoya6/laboratorio_etl.git
cd laboratorio_etl
```

### 2. Crear y activar el entorno virtual
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
# .\venv\Scripts\activate       # Windows
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Crear el archivo `.env`
Crear un archivo `.env` en la raíz del proyecto con el siguiente contenido:
MONGO_URI=mongodb://localhost:27017
MONGO_DB=laboratorio_etl
MONGO_COLLECTION=pokemon_raw
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=tu_password
MYSQL_DB=laboratorio_etl

### 5. Crear la base de datos en MySQL
```bash
mysql -u root -p
```
```sql
CREATE DATABASE laboratorio_etl;
exit;
```

### 6. Correr la aplicación
```bash
uvicorn app.main:app --reload
```

La API queda disponible en `http://127.0.0.1:8000`  
Documentación Swagger en `http://127.0.0.1:8000/docs`

---

## Endpoints

| Método | Ruta | Descripción | Responsable |
|--------|------|-------------|-------------|
| POST | `/api/v1/etl/extraer` | Extrae pokémon de la PokéAPI y guarda en MongoDB | Santiago Montoya Vanegas |
| POST | `/api/v1/etl/transformar` | Lee de Mongo, transforma con Pandas e inserta en MySQL | Jonathan Ocampo Timana |
| DELETE | `/api/v1/etl/reset` | Limpia MongoDB y hace TRUNCATE en MySQL | Jonathan Ocampo Timana |
| GET | `/api/v1/analitica/columna/{nombre}` | Análisis estadístico dinámico por columna | Rafael Alexander Riatiga |
| GET | `/api/v1/perfil/{id}` | Perfil dual del registro en Mongo y MySQL | Rafael Alexander Riatiga |

---

## División de Responsabilidades

### Integrante 1 — Santiago Montoya
- Setup inicial del proyecto (estructura, entorno, dependencias)
- `app/config.py` — Variables de entorno
- `app/database.py` — Conexiones a MongoDB y MySQL
- `app/models/personajes_sql.py` — Modelo SQLAlchemy de la tabla
- `app/views/schemas.py` — Esquemas Pydantic
- `app/controllers/etl_controller.py` — Rutas ETL
- `app/services/etl_service.py` — Lógica de extracción (Endpoint A)
- `app/main.py` — Inicialización de FastAPI

### Integrante 2 — [Jonathan Ocampo Timana]
- `app/services/etl_service.py` — Lógica de transformación y carga (Endpoint B)
- Endpoint C: Reset (DELETE /etl/reset)
- Validación de idempotencia en transformación
- PK alineada entre Mongo y MySQL

### Integrante 3 — [Rafael Alexander Riatiga]
- `app/controllers/analitica_controller.py` — Rutas de analítica
- `app/services/analitica_service.py` — Lógica de analítica
- Endpoint D: Análisis por columna con detección dinámica de tipos
- Endpoint E: Perfil dual Mongo + MySQL
- Evidencias de funcionamiento para el PDF de entrega

---

## API Fuente

**PokéAPI** — `https://pokeapi.co/`  

### Columnas en MySQL (`pokemon_master`)

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id_pokemon` | INT (PK) | ID original de la PokéAPI = `_id` en MongoDB |
| `nombre` | VARCHAR | Nombre del pokémon |
| `altura` | INT | Altura en decímetros |
| `peso` | INT | Peso en hectogramos |
| `experiencia_base` | INT | Experiencia base |
| `tipo_primario` | VARCHAR | Tipo principal |
| `tipo_secundario` | VARCHAR | Tipo secundario (puede ser N/A) |
| `habilidad_principal` | VARCHAR | Primera habilidad |
| `es_legendario` | BOOLEAN | Si es legendario |
| `total_movimientos` | INT | Cantidad de movimientos |
| `sprite_url` | VARCHAR | URL de la imagen |
| `fecha_agregado` | DateTime | Fecha de ingesta |

---

