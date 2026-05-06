from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, get_db
from . import models, schemas, crud

# ==========================================================
# CRITICAL: CREACIÓN DE LA BASE DE DATOS Y TABLAS
# Esta línea busca el archivo 'smat.db' y crea las tablas
# definidas en models.py si es que aún no existen.
# ==========================================================
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SMAT Backend Profesional",
    description="""
    API robusta para la gestión y monitoreo de desastres naturales.
    Permite la telemetría de sensores en tiempo real y el cálculo de niveles de riesgo.

    **Entidades principales:**
    * **Estaciones:** Puntos de monitoreo físico.
    * **Lecturas:** Datos capturados por sensores.
    * **Riesgos:** Análisis de criticidad basado en umbrales.
    """,
    version="1.0.0",
    terms_of_service="http://unmsm.edu.pe/terms/",
    contact={
        "name": "Soporte Técnico SMAT - FISI",
        "url": "http://fisi.unmsm.edu.pe",
        "email": "desarrollo.smat@unmsm.edu.pe",
},
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
},
)

# Configuración de orígenes permitidos
origins = ["*"] # En producción, especificar dominios reales

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/estaciones/", status_code=201, tags=["Gestión de Infraestructura"])
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(get_db)):
    # Retornamos dentro de "data" para que el test 'assert response.json()["data"]' no falle
    db_estacion = crud.crear_estacion(db=db, estacion=estacion)
    return {"data": db_estacion}

@app.post("/lecturas/", status_code=201, tags=["Telemetría de Sensores"])
def registrar_lectura(lectura: schemas.LecturaCreate, db: Session = Depends(get_db)):
    return crud.crear_lectura(db=db, lectura=lectura)

@app.get("/estaciones/{id}/riesgo", tags=["Análisis de Riesgo"])
def obtener_riesgo(id: int, db: Session = Depends(get_db)):
    # Validación para el test de estación no encontrada
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estaciòn no encontrada")
    return crud.get_riesgo_estacion(db, id)

@app.get("/estaciones/{id}/historial", tags=["Reportes Históricos"])
def obtener_historial(id: int, db: Session = Depends(get_db)):
    return crud.get_historial_lecturas(db, id)

@app.get("/estaciones/stats", tags=["Resumen Ejecutivo"])
def obtener_stats_globales(db: Session = Depends(get_db)):
    return crud.get_stats_globales(db)