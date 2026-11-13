# api-mi-proyecto – Sesión 11: Despliegue Continuo en la nube

API REST de Tareas (FastAPI + Pydantic) lista para desplegar en Render con Despliegue Continuo desde GitHub.

## Contenido

| Archivo | Función |
|---|---|
| `main.py` | API completa: CRUD `/tareas`, `/health`, `/version`, `/config-check`, `/simular-error`, CORS, arranque con `$PORT` |
| `requirements.txt` | Dependencias (contrato de build) |
| `.gitignore` | Excluye `venv/`, `.env`, caches |
| `.env` | Variables LOCALES (no se sube a GitHub) |
| `.env.example` | Plantilla pública de variables |
| `render.yaml` | Blueprint opcional de Render |
| `cliente_web.html` | Cliente JS con `fetch()` para probar CORS |
| `test_main.py` | Pruebas con pytest |
| `comandos_powershell.ps1` | Todos los comandos de la sesión para PowerShell |
| `GUIA_RESUELTA_SESION_11.md` | Reflexiones, autoevaluación, lista de cotejo, errores frecuentes |

## Inicio rápido (PowerShell)

```powershell
cd api-mi-proyecto
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Abrir http://localhost:8000/docs

## Render

- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Variables (Environment): `API_SECRET_KEY`, `MODO_DEBUG=False`, `ENVIRONMENT=produccion`
