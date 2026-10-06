ruebas realizadas – Proyecto Docker SENA
Este documento reúne únicamente las pruebas que ya fueron ejecutadas durante la construcción y validación del proyecto Docker.
1. Verificación de Docker Engine
Se verificó la instalación de Docker con:
docker --version
Resultado obtenido:
Docker version 29.8.1
También se verificó Docker Compose:
docker compose version
Resultado obtenido:
Docker Compose version v5.5.1
2. Prueba inicial con hello-world
Se ejecutó:
docker run --rm hello-world
Resultado principal:
Hello from Docker!
Esta prueba confirmó que Docker podía:
- comunicarse con el daemon;
- descargar una imagen desde Docker Hub;
- crear un contenedor;
- ejecutar correctamente el contenedor.
3. Construcción de la imagen propia de la API
Se construyó la imagen con:
docker build -t api-app:1.0.0 .
Posteriormente se verificó:
docker images | grep api-app
Resultado obtenido:
api-app:1.0.0        2eea0a7b08d0        243MB           58MB
Con esto se confirmó que la imagen propia de la API fue creada correctamente.
4. Prueba directa de la API
Se ejecutó el contenedor de la API con:
docker run --rm -p 8000:8000 api-app:1.0.0
Desde otra terminal se probó:
curl http://localhost:8000/health
Resultado obtenido:
{"status":"ok"}
Esto confirmó que la imagen de la API funcionaba correctamente antes de integrarla con Docker Compose.
5. Verificación de los servicios con Docker Compose
Después de configurar PostgreSQL, la API y Nginx, se ejecutó:
docker compose up -d --build
Posteriormente se verificó:
docker compose ps
Resultado observado:
NAME                                IMAGE                           SERVICE   STATUS                    PORTS
docker-proyecto-sena-eeom-api-1     docker-proyecto-sena-eeom-api   api       Up                        8000/tcp
docker-proyecto-sena-eeom-db-1      postgres:18-alpine              db        Up (healthy)              5432/tcp
docker-proyecto-sena-eeom-proxy-1   nginx:1.30-alpine               proxy     Up                        0.0.0.0:8080->80/tcp
Con esta prueba se confirmó que:
- la API estaba activa;
- PostgreSQL estaba activo y en estado healthy;
- Nginx estaba activo;
- solamente Nginx publicaba un puerto hacia el host.
6. Prueba del endpoint de salud a través de Nginx
Se ejecutó:
curl http://localhost:8080/health
Resultado obtenido:
{"status":"ok"}
Esto confirmó que la petición entraba por Nginx y era reenviada correctamente hacia la API.
La ruta validada fue:
Host
  ↓
localhost:8080
  ↓
Nginx
  ↓
api:8000
7. Prueba de conexión entre la API y PostgreSQL
Se ejecutó:
curl http://localhost:8080/db
Resultado obtenido:
{"status":"ok","database":"conectada","version":"PostgreSQL 18.6 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit"}
Esta prueba confirmó que la API podía conectarse correctamente a PostgreSQL.
La ruta completa validada fue:
Host
  ↓
Nginx
  ↓
API
  ↓
PostgreSQL
8. Verificación de resolución de nombres en la red interna
Se ejecutó:
docker compose exec api python -c "import socket; print(socket.gethostbyname('db'))"
Resultado obtenido:
172.18.0.2
Esto confirmó que el servicio api podía resolver el nombre db dentro de la red interna de Docker.
9. Verificación del aislamiento de PostgreSQL
Se verificó la publicación de puertos del contenedor PostgreSQL con:
docker inspect docker-proyecto-sena-eeom-db-1   --format='{{json .NetworkSettings.Ports}}'
Resultado obtenido:
{"5432/tcp":null}
El valor null confirma que el puerto 5432 no está publicado hacia el host.
También se ejecutó:
curl --max-time 3 http://localhost:5432
Resultado obtenido:
curl: (7) Failed to connect to localhost port 5432
Esto confirma que PostgreSQL no está accesible directamente desde el host.
10. Creación de un dato para la prueba de persistencia
Se ingresó a PostgreSQL mediante:
docker compose exec db psql -U postgres -d appdb
Se creó una tabla:
CREATE TABLE prueba (
    id SERIAL PRIMARY KEY,
    mensaje TEXT
);
Resultado:
CREATE TABLE
Luego se insertó un registro:
INSERT INTO prueba (mensaje)
VALUES ('dato persistente Docker');
Resultado:
INSERT 0 1
Se verificó el contenido:
SELECT * FROM prueba;
Resultado obtenido:
 id |         mensaje
----+-------------------------
  1 | dato persistente Docker
(1 row)
11. Prueba de persistencia después de eliminar los contenedores
Se ejecutó:
docker compose down
Con este comando se eliminaron los contenedores y la red del proyecto, pero se conservó el volumen.
Después se volvió a levantar la solución:
docker compose up -d
Se verificó nuevamente:
docker compose ps
Los tres servicios quedaron activos y PostgreSQL volvió a quedar en estado:
healthy
12. Verificación final de persistencia
Después de recrear los contenedores se ejecutó:
docker compose exec db psql -U postgres -d appdb   -c "SELECT * FROM prueba;"
Resultado obtenido:
 id |         mensaje
----+-------------------------
  1 | dato persistente Docker
(1 row)
Esto confirmó que el registro permaneció disponible después de eliminar y recrear los contenedores.
Por lo tanto, la persistencia de PostgreSQL mediante el volumen pgdata quedó validada.
13. Conclusión de las pruebas realizadas
Hasta este punto se ha comprobado correctamente que:
- Docker Engine funciona.
- Docker Compose funciona.
- La imagen propia de la API se construye.
- La API responde correctamente.
- Nginx funciona como proxy inverso.
- PostgreSQL inicia y alcanza estado healthy.
- La API se conecta correctamente a PostgreSQL.
- Los servicios se comunican dentro de la red interna.
- PostgreSQL no está expuesto directamente al host.
- El volumen pgdata conserva los datos después de eliminar y recrear los contenedores.
