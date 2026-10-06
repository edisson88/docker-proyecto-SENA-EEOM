# Proyecto Docker SENA

Proyecto integrador del curso **Despliegue de aplicaciones y servicios en contenedores Docker**.

La solución implementa una arquitectura multiservicio compuesta por:

- **Nginx** como proxy inverso.
- **FastAPI** como API backend.
- **PostgreSQL** como base de datos.
- **Docker Compose** para orquestar los servicios.
- **Volumen Docker** para persistencia de datos.
- **Red interna Docker** para la comunicación entre servicios.

---

## Arquitectura

La solución sigue este flujo:

```text
Usuario / Host
      |
      | http://localhost:8080
      v
Nginx
      |
      | api:8000
      v
API FastAPI
      |
      | db:5432
      v
PostgreSQL
      |
      v
Volumen pgdata
```

Solo Nginx publica un puerto hacia el host.

La API y PostgreSQL permanecen dentro de la red interna de Docker.

El diagrama completo se encuentra en:

```text
docs/arquitectura.png
```

---

## Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Docker Engine | Motor de contenedores |
| Docker Compose | Orquestación de servicios |
| Python 3.14 | Entorno de ejecución de la API |
| FastAPI | API backend |
| Uvicorn | Servidor ASGI |
| PostgreSQL 18 | Base de datos |
| Nginx 1.30 | Proxy inverso |
| Git | Control de versiones |

Imágenes utilizadas:

```text
python:3.14-slim
postgres:18-alpine
nginx:1.30-alpine
```

---

## Estructura del proyecto

```text
docker-proyecto-SENA-EEOM/
├── .dockerignore
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
├── app/
│   └── main.py
├── nginx/
│   └── default.conf
├── docs/
│   ├── arquitectura.png
│   ├── entorno.md
│   ├── pruebas.md
│   └── requisitos.md
└── .github/
    └── workflows/
```

---

## Servicios

### Proxy Nginx

Imagen:

```text
nginx:1.30-alpine
```

Puerto interno:

```text
80
```

Puerto publicado en el host:

```text
8080
```

Nginx recibe las solicitudes externas y las reenvía hacia la API.

---

### API FastAPI

Imagen base:

```text
python:3.14-slim
```

Puerto interno:

```text
8000
```

La API no publica directamente su puerto hacia el host.

Endpoints implementados:

```text
/
```

```text
/health
```

```text
/db
```

---

### PostgreSQL

Imagen:

```text
postgres:18-alpine
```

Puerto interno:

```text
5432
```

PostgreSQL no publica el puerto 5432 hacia el host.

Los datos se almacenan persistentemente en el volumen:

```text
pgdata
```

---

## Requisitos previos

Para ejecutar el proyecto se requiere:

- Docker Engine instalado.
- Docker Compose disponible mediante `docker compose`.
- Git instalado.
- Puerto `8080` disponible en el equipo.

El proyecto fue validado en:

```text
Ubuntu 26.04.1 LTS
Docker Engine 29.8.1
Docker Compose v5.5.1
Arquitectura amd64 / x86_64
```

---

## Variables de entorno

El repositorio contiene el archivo:

```text
.env.example
```

Este archivo sirve como plantilla para crear las variables necesarias.

Antes de levantar la solución, crear el archivo `.env`:

```bash
cp .env.example .env
```

Luego editar:

```bash
nano .env
```

Ejemplo:

```env
DB_NAME=appdb
DB_USER=postgres
DB_PASSWORD=ClaveSegura
DB_HOST=db
```

El archivo `.env` está excluido del repositorio mediante `.gitignore`.

---

## Ejecutar el proyecto

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
```

Entrar a la carpeta:

```bash
cd docker-proyecto-SENA-EEOM
```

---

### 2. Crear el archivo `.env`

```bash
cp .env.example .env
```

Editar las variables si es necesario:

```bash
nano .env
```

---

### 3. Construir y levantar la solución

Ejecutar:

```bash
docker compose up -d --build
```

Este comando:

- construye la imagen de la API;
- crea la red interna;
- crea el volumen persistente;
- inicia PostgreSQL;
- espera que PostgreSQL alcance estado saludable;
- inicia la API;
- inicia Nginx.

---

### 4. Verificar el estado de los servicios

```bash
docker compose ps
```

Se espera observar:

```text
api     Up
db      Up (healthy)
proxy   Up
```

Solo el proxy debe publicar el puerto:

```text
0.0.0.0:8080->80/tcp
```

---

## Pruebas de funcionamiento

### Healthcheck de la API

```bash
curl http://localhost:8080/health
```

Resultado esperado:

```json
{"status":"ok"}
```

---

### Conexión con PostgreSQL

```bash
curl http://localhost:8080/db
```

Resultado esperado:

```json
{
  "status": "ok",
  "database": "conectada"
}
```

---

## Validar la red interna

Para comprobar que la API puede resolver el servicio PostgreSQL mediante el nombre `db`:

```bash
docker compose exec api python -c "import socket; print(socket.gethostbyname('db'))"
```

Debe devolver una dirección IP privada de la red Docker.

---

## Validar el aislamiento de PostgreSQL

Ejecutar:

```bash
docker inspect docker-proyecto-sena-eeom-db-1   --format='{{json .NetworkSettings.Ports}}'
```

Resultado esperado:

```text
{"5432/tcp":null}
```

Esto confirma que PostgreSQL no publica ningún puerto hacia el host.

También puede comprobarse mediante:

```bash
curl --max-time 3 http://localhost:5432
```

La conexión debe fallar.

---

## Persistencia de datos

PostgreSQL utiliza el volumen:

```text
pgdata
```

Para comprobar la persistencia se puede crear información en la base de datos y posteriormente ejecutar:

```bash
docker compose down
docker compose up -d
```

El comando `docker compose down` elimina los contenedores, pero conserva el volumen.

Después de recrear los contenedores, los datos deben permanecer disponibles.

> No utilizar `docker compose down -v` si se desea conservar la información, ya que `-v` elimina también los volúmenes.

---

## Comandos útiles

### Levantar la solución

```bash
docker compose up -d
```

### Levantar y reconstruir la API

```bash
docker compose up -d --build
```

### Ver estado

```bash
docker compose ps
```

### Ver logs

```bash
docker compose logs
```

### Logs de la API

```bash
docker compose logs api --tail=50
```

### Logs de PostgreSQL

```bash
docker compose logs db --tail=50
```

### Detener y eliminar contenedores

```bash
docker compose down
```

### Eliminar también los volúmenes

```bash
docker compose down -v
```

### Entrar al contenedor de la API

```bash
docker compose exec api sh
```

### Entrar a PostgreSQL

```bash
docker compose exec db psql -U postgres -d appdb
```

### Ver consumo de recursos

```bash
docker stats
```

---

## Dockerfile

La API utiliza un Dockerfile multi-etapa.

La primera etapa instala las dependencias:

```text
builder
```

La segunda etapa contiene únicamente los componentes necesarios para ejecutar la aplicación.

Además, la aplicación se ejecuta con un usuario sin privilegios:

```text
appuser
```

Esto evita ejecutar el proceso principal del contenedor como `root`.

---

## Seguridad

La solución implementa las siguientes medidas básicas:

- PostgreSQL no publica el puerto 5432 hacia el host.
- La API no publica directamente el puerto 8000.
- Solo Nginx funciona como punto de entrada.
- Las credenciales se cargan mediante variables de entorno.
- `.env` no se almacena en Git.
- `.env.example` contiene únicamente valores de referencia.
- La API se ejecuta con un usuario sin privilegios.
- Se utilizan versiones explícitas de las imágenes en lugar de `latest`.

---

## Documentación

La documentación complementaria se encuentra en la carpeta:

```text
docs/
```

### Requisitos de infraestructura

```text
docs/requisitos.md
```

Contiene los requisitos de infraestructura y sus criterios de aceptación.

### Entorno

```text
docs/entorno.md
```

Describe el entorno utilizado, versiones, configuración y problemas encontrados.

### Pruebas

```text
docs/pruebas.md
```

Registra las validaciones realizadas sobre los servicios, red, aislamiento y persistencia.

### Arquitectura

```text
docs/arquitectura.png
```

Representa gráficamente la arquitectura de despliegue.

---

## Resultado obtenido

Durante las pruebas se verificó correctamente que:

- Docker Engine funciona.
- Los tres servicios se levantan mediante Docker Compose.
- PostgreSQL alcanza estado `healthy`.
- Nginx funciona como proxy inverso.
- La API responde mediante `/health`.
- La API se conecta correctamente con PostgreSQL.
- Docker resuelve los nombres de los servicios dentro de la red interna.
- PostgreSQL no está expuesto directamente al host.
- La API no está expuesta directamente al host.
- Solo Nginx publica el puerto 8080.
- Los datos persisten mediante el volumen `pgdata`.

---

## Autor

**Edisson Eduardo Otálora Murcia**

Proyecto desarrollado como evidencia del curso de despliegue de aplicaciones y servicios en contenedores Docker.
