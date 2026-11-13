"""
API REST de Tareas - IES "República Federal de Alemania" - Chiclayo
Sesión 10 (FastAPI + Pydantic) y Sesión 11 (Despliegue Continuo en la nube).

Ejecución local : python main.py
Ejecución nube  : uvicorn main:app --host 0.0.0.0 --port $PORT
"""
import os
import logging
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Carga las variables del archivo .env local si existe (en Render no existe;
# allí las variables se inyectan desde el Dashboard > Environment).
load_dotenv()

logger = logging.getLogger("uvicorn.error")

# ---------------------------------------------------------------------------
# Configuración leída desde el entorno (Twelve-Factor App, principio III)
# ---------------------------------------------------------------------------
SECRET_KEY = os.getenv("API_SECRET_KEY", "clave_por_defecto_insegura")
MODO_DEBUG = os.getenv("MODO_DEBUG", "False")
MAX_REGISTROS = int(os.getenv("MAX_REGISTROS", "100"))
# Interruptor del endpoint de diagnóstico (Micropráctica 11.5)
HABILITAR_ERROR_DEMO = os.getenv("HABILITAR_ERROR_DEMO", "False").lower() == "true"

app = FastAPI(
    title="API de Tareas - IESRFA Chiclayo",
    description="API REST desplegada con Despliegue Continuo (CD) en la nube gestionada.",
    version="1.2.0",
)

# ---------------------------------------------------------------------------
# CORS (Micropráctica 11.6)
# ---------------------------------------------------------------------------
# En aprendizaje se permite cualquier origen. En una empresa se especifica el
# dominio exacto, por ejemplo: ["https://mi-portafolio.vercel.app"]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Modelos Pydantic (Sesión 10)
# ---------------------------------------------------------------------------
class TareaCrear(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=100, examples=["Estudiar CD en Render"])
    descripcion: Optional[str] = Field(None, max_length=300)
    completada: bool = False


class Tarea(TareaCrear):
    id: int


# Base de datos en memoria (didáctica)
tareas_db: List[Tarea] = [
    Tarea(id=1, titulo="Configurar GitHub", descripcion="Subir el repositorio", completada=True),
    Tarea(id=2, titulo="Desplegar en Render", descripcion="Crear Web Service", completada=False),
]
siguiente_id = 3


# ---------------------------------------------------------------------------
# Endpoints de Sistema (Micropráctica 11.1, 11.3, 11.4)
# ---------------------------------------------------------------------------
@app.get("/", tags=["Sistema"])
def raiz():
    return {"mensaje": "API de Tareas en la nube. Documentación en /docs"}


@app.get("/health", tags=["Sistema"])
def health_check():
    return {
        "status": "online",
        "ambiente": os.getenv("ENVIRONMENT", "desarrollo_local"),
        "servidor": "FastAPI + Uvicorn Cloud",
    }


@app.get("/version", tags=["Sistema"])
def consultar_version():
    return {
        "version": "1.2.0",
        "descripcion": "API desplegada mediante Continuous Deployment desde GitHub",
        "docente": "Lic. Ronald J. Villar Gonzales",
        "institucion": "IES República Federal de Alemania - Chiclayo",
    }


@app.get("/config-check", tags=["Seguridad"])
def config_check():
    return {
        "modo_debug": MODO_DEBUG,
        # Buena práctica: nunca revelar el valor completo del secreto
        "clave_configurada": SECRET_KEY != "clave_por_defecto_insegura",
        "prefijo_clave": SECRET_KEY[:4] + "****",
    }


# ---------------------------------------------------------------------------
# CRUD de Tareas (Sesión 10)
# ---------------------------------------------------------------------------
@app.get("/tareas", response_model=List[Tarea], tags=["Tareas"])
def listar_tareas():
    return tareas_db


@app.get("/tareas/{tarea_id}", response_model=Tarea, tags=["Tareas"])
def obtener_tarea(tarea_id: int):
    for t in tareas_db:
        if t.id == tarea_id:
            return t
    logger.warning("Tarea %s no encontrada", tarea_id)
    raise HTTPException(status_code=404, detail="Tarea no encontrada")


@app.post("/tareas", response_model=Tarea, status_code=201, tags=["Tareas"])
def crear_tarea(datos: TareaCrear):
    global siguiente_id
    if len(tareas_db) >= MAX_REGISTROS:
        raise HTTPException(status_code=400, detail=f"Límite de {MAX_REGISTROS} registros alcanzado")
    nueva = Tarea(id=siguiente_id, **datos.model_dump())
    siguiente_id += 1
    tareas_db.append(nueva)
    logger.info("Tarea %s creada", nueva.id)
    return nueva


@app.put("/tareas/{tarea_id}", response_model=Tarea, tags=["Tareas"])
def actualizar_tarea(tarea_id: int, datos: TareaCrear):
    for i, t in enumerate(tareas_db):
        if t.id == tarea_id:
            tareas_db[i] = Tarea(id=tarea_id, **datos.model_dump())
            return tareas_db[i]
    raise HTTPException(status_code=404, detail="Tarea no encontrada")


@app.delete("/tareas/{tarea_id}", tags=["Tareas"])
def eliminar_tarea(tarea_id: int):
    for i, t in enumerate(tareas_db):
        if t.id == tarea_id:
            tareas_db.pop(i)
            return {"mensaje": f"Tarea {tarea_id} eliminada"}
    raise HTTPException(status_code=404, detail="Tarea no encontrada")


# ---------------------------------------------------------------------------
# Diagnóstico (Micropráctica 11.5)
# ---------------------------------------------------------------------------
@app.get("/simular-error", tags=["Diagnóstico"])
def simular_error():
    """Con HABILITAR_ERROR_DEMO=True provoca ZeroDivisionError (HTTP 500)
    para practicar la lectura del Traceback en los Runtime Logs.
    Con False (versión corregida) responde de forma controlada."""
    if not HABILITAR_ERROR_DEMO:
        return {"resultado": "Endpoint de diagnóstico deshabilitado (versión corregida)"}
    resultado = 10 / 0  # División por cero: excepción no controlada
    return {"resultado": resultado}


# ---------------------------------------------------------------------------
# Bloque de arranque productivo (Micropráctica 11.1)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn

    # Lee el puerto inyectado por el PaaS; si no existe, usa 8000
    puerto = int(os.environ.get("PORT", 8000))
    # Escucha obligatoria en 0.0.0.0 para entornos en la nube; reload=False en producción
    uvicorn.run("main:app", host="0.0.0.0", port=puerto, reload=False)
