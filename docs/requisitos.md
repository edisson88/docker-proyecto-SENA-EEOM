# Requisitos de infraestructura

Este documento define los requisitos de infraestructura de la solución desarrollada para el despliegue de una aplicación web multiservicio mediante Docker.

La solución está compuesta por tres servicios:

- Proxy inverso Nginx.
- API desarrollada con FastAPI.
- Base de datos PostgreSQL.

Cada requisito cuenta con un criterio de aceptación verificable.

| ID | Requisito de infraestructura | Criterio de aceptación |
|---|---|---|
| RI-01 | Los tres servicios deben ejecutarse en contenedores independientes. | `docker compose ps` muestra los servicios `proxy`, `api` y `db` en estado `Up`. |
| RI-02 | Únicamente el proxy inverso Nginx debe estar expuesto hacia el host. | `docker compose ps` muestra únicamente el puerto `8080:80` publicado para el servicio `proxy`. |
| RI-03 | PostgreSQL no debe publicar su puerto 5432 hacia el host. | `docker inspect` muestra `{"5432/tcp":null}` y una conexión a `localhost:5432` falla. |
| RI-04 | La API debe permanecer dentro de la red interna de Docker y no publicar directamente su puerto 8000. | `docker compose ps` muestra `8000/tcp` para la API, sin asociación con un puerto del host. |
| RI-05 | Los servicios deben comunicarse mediante una red interna de Docker. | Desde la API, `socket.gethostbyname('db')` resuelve el servicio `db` a una dirección IP privada. |
| RI-06 | La API debe conectarse correctamente con PostgreSQL utilizando el nombre del servicio `db`. | `curl http://localhost:8080/db` devuelve `"status":"ok"` y `"database":"conectada"`. |
| RI-07 | La aplicación debe disponer de un endpoint que permita verificar su estado. | `curl http://localhost:8080/health` devuelve `{"status":"ok"}`. |
| RI-08 | Los datos de PostgreSQL deben persistir aunque los contenedores sean eliminados y recreados. | Después de ejecutar `docker compose down` y `docker compose up -d`, el registro almacenado previamente sigue disponible. |
| RI-09 | La base de datos debe almacenar sus datos en un volumen Docker. | `docker volume ls` muestra el volumen `pgdata` asociado al proyecto y los datos permanecen después de recrear los contenedores. |
| RI-10 | PostgreSQL debe estar disponible antes de que se inicie la API. | El servicio `db` posee un `healthcheck` y la API usa `depends_on` con la condición `service_healthy`. |
| RI-11 | La solución completa debe poder levantarse mediante un único comando. | `docker compose up -d --build` construye y levanta los tres servicios. |
| RI-12 | La imagen de la API debe construirse mediante un Dockerfile multi-etapa. | El Dockerfile contiene una etapa `builder` y una segunda etapa destinada a la ejecución. |
| RI-13 | La aplicación dentro del contenedor no debe ejecutarse como usuario root. | El Dockerfile crea `appuser` y utiliza la instrucción `USER appuser`. |
| RI-14 | Las credenciales de la base de datos no deben quedar escritas directamente en el código fuente. | La aplicación obtiene las credenciales mediante variables de entorno y `.env` está excluido mediante `.gitignore`. |
| RI-15 | El repositorio debe incluir una plantilla de las variables requeridas sin exponer credenciales reales. | Existe el archivo `.env.example` con las claves requeridas y valores ficticios. |
| RI-16 | Las imágenes base deben utilizar versiones explícitas y reproducibles. | Se utilizan `python:3.14-slim`, `postgres:18-alpine` y `nginx:1.30-alpine`, evitando `latest`. |
| RI-17 | Nginx debe funcionar como único punto de entrada a la aplicación. | Las peticiones a `localhost:8080/health` y `localhost:8080/db` son reenviadas correctamente hacia el servicio `api`. |
| RI-18 | El entorno debe poder ejecutarse de forma nativa sobre Linux. | La solución fue construida y validada en Ubuntu 26.04.1 LTS con Docker Engine 29.8.1 y Docker Compose v5.5.1. |

## Requisitos por sistema operativo

### RI-OS-01 – Windows

En equipos Windows, Docker Engine debe ejecutarse dentro de una distribución Linux sobre WSL2 y los comandos Docker deben ejecutarse desde la terminal Linux.

**Criterio de aceptación:** WSL utiliza versión 2 y Docker Engine responde correctamente dentro de Ubuntu.

### RI-OS-02 – Linux

En equipos Linux, Docker Engine debe ejecutarse de forma nativa como servicio del sistema.

**Criterio de aceptación:** `docker info` responde correctamente y `docker run --rm hello-world` ejecuta un contenedor sin errores.

Este requisito fue validado en:

- Ubuntu 26.04.1 LTS.
- Arquitectura amd64 / x86_64.
- Docker Engine 29.8.1.
- Docker Compose v5.5.1.

### RI-OS-03 – macOS

En equipos macOS, Docker Engine debe ejecutarse sobre un entorno Linux compatible, como Colima.

**Criterio de aceptación:** Docker responde correctamente desde la terminal y los mismos archivos Dockerfile y Docker Compose pueden utilizarse sin modificaciones en la solución.

## Componentes de infraestructura

| Componente | Imagen base | Puerto interno | Función |
|---|---|---:|---|
| Proxy inverso | `nginx:1.30-alpine` | 80 | Recibir las solicitudes externas y reenviarlas hacia la API. |
| API backend | `python:3.14-slim` | 8000 | Procesar las solicitudes y comunicarse con PostgreSQL. |
| Base de datos | `postgres:18-alpine` | 5432 | Almacenar persistentemente la información de la aplicación. |

## Recursos adicionales

### Red

La solución utiliza una red Docker de tipo `bridge` denominada:

```text
interna

### Volumen
PostgreSQL utiliza el volumen: pgdata


Puerto publicado
Únicamente se publica:8080:80
