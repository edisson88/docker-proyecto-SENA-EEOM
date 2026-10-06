import os

import psycopg
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def inicio():
    return {
        "mensaje": "Proyecto Docker SENA",
        "estado": "funcionando"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/db")
def database():
    try:
        with psycopg.connect(
            host=os.getenv("DB_HOST", "db"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD")
        ) as conexion:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]

        return {
            "status": "ok",
            "database": "conectada",
            "version": version
        }

    except Exception as error:
        return {
            "status": "error",
            "detalle": str(error)
        }
