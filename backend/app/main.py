from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, get_db
from . import models, schemas, crud

# ==========================================================
# CRITICAL: CREACIÓN DE LA BASE DE DATOS Y TABLAS
# ==========================================================
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SMAT Backend Profesional",
    description="API robusta para la gestión y monitoreo de desastres naturales.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoginRequest(BaseModel):
    username: str
    password: str

# --- RUTA DE AUTENTICACIÓN ---
@app.post("/token", tags=["Seguridad"])
async def login(datos: LoginRequest):
    """
    Ruta para validar usuario y contraseña.
    """
    if datos.username == "admin" and datos.password == "admin123":
        return {
            "access_token": "token-secreto-unmsm", 
            "token_type": "bearer"
        }
    else:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

# --- RUTAS DE ESTACIONES ---

@app.get("/estaciones/", tags=["Gestión de Infraestructura"])
def listar_estaciones(db: Session = Depends(get_db)):
    """
    IMPORTANTE: Retorna directamente la lista para que 
    ApiService().fetchEstaciones() en Flutter no falle.
    """
    return db.query(models.EstacionDB).all()

@app.post("/estaciones/", status_code=201, tags=["Gestión de Infraestructura"])
def crear_estacion(estacion: schemas.EstacionCreate, db: Session = Depends(get_db)):
    """
    Crea una estación. Retorna el objeto dentro de 'data' 
    para mantener compatibilidad con los tests del lab.
    """
    db_estacion = crud.crear_estacion(db=db, estacion=estacion)
    return {"data": db_estacion}

# --- RUTAS DE TELEMETRÍA Y ANÁLISIS ---

@app.post("/lecturas/", status_code=201, tags=["Telemetría de Sensores"])
def registrar_lectura(lectura: schemas.LecturaCreate, db: Session = Depends(get_db)):
    return crud.crear_lectura(db=db, lectura=lectura)

@app.get("/estaciones/{id}/riesgo", tags=["Análisis de Riesgo"])
def obtener_riesgo(id: int, db: Session = Depends(get_db)):
    estacion = db.query(models.EstacionDB).filter(models.EstacionDB.id == id).first()
    if not estacion:
        raise HTTPException(status_code=404, detail="Estación no encontrada")
    return crud.get_riesgo_estacion(db, id)

@app.get("/estaciones/{id}/historial", tags=["Reportes Históricos"])
def obtener_historial(id: int, db: Session = Depends(get_db)):
    return crud.get_historial_lecturas(db, id)

@app.get("/estaciones/stats", tags=["Resumen Ejecutivo"])
def obtener_stats_globales(db: Session = Depends(get_db)):
    return crud.get_stats_globales(db)