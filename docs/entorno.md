# Entorno de trabajo

Este documento describe el entorno utilizado para instalar, configurar, construir y validar la solución de contenedores Docker del proyecto.

---

## 1. Sistema operativo

El proyecto fue desarrollado y probado sobre el siguiente entorno:

- Sistema operativo: Ubuntu 26.04.1 LTS
- Nombre en clave: Resolute Raccoon
- Arquitectura: x86_64 / amd64

Los comandos utilizados para verificar esta información fueron:

```bash
cat /etc/os-release
uname -m
```

La arquitectura `x86_64` corresponde a `amd64` dentro del sistema de paquetes de Ubuntu.

---

## 2. Instalación de Docker Engine

Docker Engine fue instalado de forma nativa sobre Ubuntu utilizando el repositorio oficial de Docker.

Durante la instalación se configuraron los siguientes componentes:

- Docker Engine
- Docker CLI
- containerd
- Docker Buildx
- Docker Compose Plugin

Las versiones verificadas fueron:

```text
Docker version 29.8.1
Docker Compose version v5.5.1
```

Los comandos utilizados para comprobar las versiones fueron:

```bash
docker --version
docker compose version
```

La instalación nativa sobre Ubuntu permite utilizar Docker Engine directamente sobre el núcleo Linux, sin necesidad de Docker Desktop.

---

## 3. Configuración de permisos

Después de instalar Docker, inicialmente el usuario no podía comunicarse con el daemon de Docker.

El error presentado fue:

```text
permission denied while trying to connect to the docker API at unix:///var/run/docker.sock
```

La causa era que el usuario actual no pertenecía al grupo `docker`.

Para solucionar el problema se ejecutó:

```bash
sudo usermod -aG docker $USER
```

Posteriormente se aplicó la nueva pertenencia al grupo mediante:

```bash
newgrp docker
```

Se verificó la configuración con:

```bash
groups
```

Después del cambio, el grupo `docker` apareció asociado al usuario y fue posible ejecutar comandos Docker sin utilizar `sudo`.

---

## 4. Validación inicial de Docker

Una vez instalado Docker y configurados los permisos, se verificó el funcionamiento del motor mediante:

```bash
docker info | head -20
```

Después se ejecutó el contenedor de prueba:

```bash
docker run --rm hello-world
```

El resultado principal fue:

```text
Hello from Docker!
```

Esta prueba permitió confirmar que Docker podía:

- comunicarse correctamente con el daemon;
- acceder a Docker Hub;
- descargar una imagen;
- crear un contenedor;
- ejecutar un contenedor correctamente;
- eliminarlo automáticamente al finalizar mediante `--rm`.

---

## 5. Herramientas utilizadas

Durante el desarrollo y validación del proyecto se utilizaron las siguientes herramientas:

| Herramienta | Uso |
|---|---|
| Ubuntu 26.04.1 LTS | Sistema operativo de trabajo |
| Docker Engine 29.8.1 | Motor de contenedores |
| Docker Compose v5.5.1 | Orquestación de servicios |
| Git | Control de versiones |
| Nano | Edición de archivos desde terminal |
| Python 3.14 | Entorno de ejecución de la API |
| FastAPI | Framework utilizado para la API |
| Uvicorn | Servidor de ejecución de FastAPI |
| PostgreSQL 18 | Base de datos |
| Nginx 1.30 | Proxy inverso |

Las imágenes utilizadas fueron:

```text
python:3.14-slim
postgres:18-alpine
nginx:1.30-alpine
```

Se utilizaron versiones explícitas en lugar de la etiqueta `latest`, con el fin de mantener un despliegue reproducible.

---

## 6. Estructura general del entorno

La solución implementada está compuesta por tres servicios principales:

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

Los servicios se comunican mediante una red Docker interna denominada:

```text
interna
```

La comunicación entre servicios se realiza mediante sus nombres definidos en Docker Compose:

```text
proxy → api:8000
api → db:5432
```

Únicamente Nginx publica un puerto hacia el host:

```text
8080:80
```

La API y PostgreSQL permanecen accesibles únicamente dentro de la red interna.

PostgreSQL utiliza el volumen:

```text
pgdata
```

para garantizar la persistencia de los datos.

---

## 7. Inconvenientes encontrados y soluciones aplicadas

Durante la construcción y despliegue de la solución se presentaron varios inconvenientes que fueron identificados mediante revisión del estado de los contenedores y análisis de logs.

### 7.1 Error de permisos con Docker

Inicialmente, al ejecutar:

```bash
docker info
```

se presentó:

```text
permission denied while trying to connect to the docker API
```

La causa era que el usuario no pertenecía al grupo `docker`.

Se solucionó mediante:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Después se verificó con:

```bash
groups
```

y los comandos Docker pudieron ejecutarse sin `sudo`.

### 7.2 Error con el volumen de PostgreSQL 18

Al levantar PostgreSQL mediante Docker Compose, el contenedor quedó en estado:

```text
unhealthy
```

Se revisaron los logs con:

```bash
docker compose logs db --tail=50
```

Los logs indicaron un problema relacionado con la ubicación del directorio de datos de PostgreSQL 18.

La configuración inicial era:

```yaml
volumes:
  - pgdata:/var/lib/postgresql/data
```

Se ajustó a:

```yaml
volumes:
  - pgdata:/var/lib/postgresql
```

Como el volumen anterior se había creado con una configuración incorrecta, fue necesario eliminarlo mediante:

```bash
docker compose down -v
```

Posteriormente se volvió a levantar la solución:

```bash
docker compose up -d --build
```

Después del cambio, PostgreSQL alcanzó correctamente el estado:

```text
healthy
```

### 7.3 Error en el archivo de configuración de Nginx

El contenedor Nginx no podía iniciar correctamente.

Docker presentó un error relacionado con el montaje del archivo:

```text
not a directory
```

Se verificó el contenido de la carpeta mediante:

```bash
ls -la nginx
file nginx/default.conf
```

Se identificó que `default.conf` había sido creado accidentalmente como directorio y que el archivo correcto tenía el nombre:

```text
default.confx
```

La corrección realizada fue:

```bash
rm -rf nginx/default.conf
mv nginx/default.confx nginx/default.conf
```

Posteriormente se verificó:

```bash
file nginx/default.conf
cat nginx/default.conf
```

Después de esta corrección, Nginx inició correctamente.

### 7.4 Error de sintaxis en la API

Después de levantar la solución, el servicio API aparecía en estado:

```text
Restarting
```

Para identificar la causa se revisaron los logs:

```bash
docker compose logs api --tail=50
```

Se encontró:

```text
SyntaxError: invalid syntax
```

El error estaba en:

```text
app/main.py
```

Se corrigió el código fuente y posteriormente se reconstruyó la imagen mediante:

```bash
docker compose up -d --build
```

Después de la reconstrucción, la API quedó en estado:

```text
Up
```

---

## 8. Comandos utilizados para diagnóstico y validación

Durante la práctica se utilizaron varios comandos para observar el comportamiento de la infraestructura.

### Estado de los servicios

```bash
docker compose ps
```

Permite verificar si los servicios se encuentran en estado `Up`, `healthy`, `Restarting` o detenidos.

### Logs de la API

```bash
docker compose logs api --tail=50
```

Permite identificar errores de ejecución dentro del servicio API.

### Logs de PostgreSQL

```bash
docker compose logs db --tail=50
```

Permite revisar problemas de inicialización, almacenamiento o conexión en PostgreSQL.

### Inspección de contenedores

```bash
docker inspect
```

Permite consultar información detallada sobre redes, puertos, volúmenes y estado de los contenedores.

### Imágenes disponibles

```bash
docker images
```

Permite listar las imágenes disponibles localmente.

### Contenedores en ejecución

```bash
docker ps
```

Permite visualizar los contenedores activos.

### Todos los contenedores

```bash
docker ps -a
```

Permite visualizar tanto contenedores activos como detenidos.

### Validación del archivo Compose

```bash
docker compose config
```

Permite comprobar la sintaxis y configuración resultante del archivo `docker-compose.yml`.

---

## 9. Resultado final del entorno

Al finalizar la configuración y las pruebas, el entorno quedó operativo con las siguientes características:

- Docker Engine instalado y funcionando correctamente.
- Docker Compose disponible como subcomando `docker compose`.
- Usuario autorizado para ejecutar Docker sin `sudo`.
- Imagen propia de la API construida mediante Dockerfile.
- Dockerfile implementado mediante patrón multi-etapa.
- Aplicación ejecutada con un usuario sin privilegios.
- API FastAPI funcionando dentro de un contenedor.
- PostgreSQL 18 funcionando en un contenedor independiente.
- PostgreSQL alcanzando estado `healthy`.
- Nginx funcionando como proxy inverso.
- Red interna Docker permitiendo comunicación entre servicios.
- Base de datos aislada del host.
- API aislada del host.
- Únicamente Nginx expuesto mediante el puerto 8080.
- Volumen `pgdata` proporcionando persistencia.
- Comunicación API–PostgreSQL funcionando correctamente.
- Endpoint `/health` respondiendo correctamente.
- Endpoint `/db` validando conexión con PostgreSQL.
- Persistencia de datos comprobada después de eliminar y recrear contenedores.
