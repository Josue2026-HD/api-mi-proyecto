# Guía resuelta – Sesión 11: Despliegue Continuo (CD) de APIs en la Nube Gestionada

IES "República Federal de Alemania" · Chiclayo · Arquitectura de Plataformas y Servicios de TI
Estudiante: ____________________  Fecha: ____________

---

## Reflexiones de las microprácticas

**11.0 – ¿Por qué es un grave error subir `venv/` a GitHub?**
Porque (1) contiene binarios compilados para Windows que no funcionan en los contenedores Linux de la nube; (2) pesa cientos de MB e infla el repositorio; (3) es reproducible con `requirements.txt`, por lo que no aporta nada; (4) puede exponer rutas locales y datos del equipo. El contrato correcto es `requirements.txt` + `.gitignore`.

**11.1 – ¿Por qué `reload` debe ser `False` en producción?**
`reload=True` vigila los archivos y reinicia el servidor al detectar cambios: consume CPU/RAM extra, crea procesos adicionales y puede reiniciar el servicio en pleno tráfico. En producción el código solo cambia mediante un nuevo despliegue, así que es innecesario e inseguro. Es una herramienta exclusiva de desarrollo.

**11.2 – ¿Quién gestionó Linux, cortafuegos y SSL? ¿Por qué ahorra costos?**
Lo gestionó Render (modelo PaaS). Ahorra costos porque no se contrata ni se mantiene un administrador de sistemas, no se compran servidores, no se renuevan certificados manualmente, no se aplican parches del SO y se paga solo por uso; el equipo se concentra en el código de negocio.

**11.3 – Si se hace push con un error de sintaxis, ¿qué pasa con el contenedor en producción?**
El nuevo build/arranque falla, Render **aborta ese despliegue y mantiene activa la versión anterior** que sigue atendiendo usuarios (Zero Downtime). El error queda visible en Build/Runtime Logs y se corrige con un nuevo commit. Por eso conviene correr pruebas (CI) antes de integrar a `main`.

**11.4 – ¿Por qué compartir `.env.example` y nunca `.env`?**
`.env.example` documenta *qué* variables necesita el proyecto (nombres y valores ficticios) para que otro desarrollador pueda configurarlo; no contiene secretos. `.env` contiene credenciales reales: si se publica, bots las capturan en segundos y comprometen cuentas, bases de datos y costos.

**11.5 – ¿Por qué el cliente ve un "Internal Server Error" genérico y el detalle va a los logs?**
Por seguridad: un Traceback detallado revela rutas, librerías, versiones, consultas SQL o estructura interna que un atacante puede aprovechar (fuga de información). El usuario no puede actuar sobre el detalle; el equipo técnico sí, desde los logs internos.

**11.6 – ¿Por qué hace falta CORS?**
Los navegadores aplican la Same-Origin Policy y bloquean peticiones `fetch` entre orígenes distintos (por ejemplo, un frontend en Vercel hacia una API en Render). `CORSMiddleware` hace que la API envíe la cabecera `Access-Control-Allow-Origin` que autoriza al navegador. En empresas se lista el dominio exacto en vez de `"*"`.

---

## Resultados esperados de cada micropráctica (cómo verificar)

| Micropráctica | Verificación |
|---|---|
| 11.0 | `git status` → *working tree clean*; en GitHub existen `requirements.txt` y `.gitignore`, sin `venv/` ni `.env` |
| 11.1 | `python main.py` → *Uvicorn running on http://0.0.0.0:8000*; `/health` devuelve `status: online` |
| 11.2 | Estado **Live** en Render; `https://tu-api.onrender.com/docs` abre Swagger |
| 11.3 | Tras `git push`, Render muestra *Deploy started for commit…* y `/version` responde `1.2.0` |
| 11.4 | `/config-check` en la nube → `clave_configurada: true`, `prefijo_clave: "clav****"` |
| 11.5 | En Logs: `200 OK`, `404 Not Found` y el `Traceback … ZeroDivisionError: division by zero` |
| 11.6 | `cliente_web.html` muestra el JSON de `/version` sin error de CORS |

---

## Autoevaluación (solucionario)

1. **c)** Al hacer push a la rama principal (`main`) conectada con el PaaS.
2. **b)** 127.0.0.1 solo acepta tráfico local interno y bloquea las peticiones del balanceador PaaS.
3. **FALSO.** El `.env` permanece local y excluido en `.gitignore`; en Render se usa la sección *Environment*.
4. **c)** `pip install -r requirements.txt`.
5. **b)** A los Runtime Logs del Dashboard del PaaS (revisando el Traceback).

---

## Lista de cotejo (20 puntos) – autoverificación

| N.º | Criterio | Pts | Evidencia en este proyecto |
|---|---|---|---|
| 1 | Repositorio limpio con requirements.txt y .gitignore estricto, sin venv | 3 | `requirements.txt`, `.gitignore` |
| 2 | Uvicorn en 0.0.0.0 y puerto dinámico `$PORT` | 3 | Bloque final de `main.py` y Start Command |
| 3 | Web Service en Render con Build y Start Command | 3 | `render.yaml` / configuración manual |
| 4 | Auto-deploy demostrado tras `git push` | 3 | Endpoint `/version` + evento en Render |
| 5 | Variables de entorno: python-dotenv + Environment de Render | 3 | `.env`, `.env.example`, `/config-check` |
| 6 | CORS habilitado y consulta exitosa desde cliente web | 3 | `CORSMiddleware`, `cliente_web.html` |
| 7 | Inspección de Runtime Logs y explicación de trazas | 2 | `/simular-error`, sección 11.5 |

---

## Anexo B – Errores frecuentes y solución

| Síntoma | Causa | Solución |
|---|---|---|
| `Build Failed: No module named 'fastapi'` | `requirements.txt` desactualizado | `pip freeze > requirements.txt`, add, commit, push |
| `Port scan timeout / Failed to bind to port` | Puerto fijo o host 127.0.0.1 | Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT` |
| `ModuleNotFoundError: main` | Archivo no llamado `main.py` o en subcarpeta | Corregir nombre o *Root Directory* |
| `No 'Access-Control-Allow-Origin' header` | Falta `CORSMiddleware` | Agregar el middleware en `main.py` |
| Primera respuesta tarda ~50 s | *Cold start* del plan gratuito | Normal; en producción real usar plan Always-On |

---

## Importante: aclaración sobre los comandos

- **Windows PowerShell:** activar el venv con `venv\Scripts\Activate.ps1` (en CMD sería `venv\Scripts\activate`).
- En Render el `Start Command` usa `$PORT` (Linux). En PowerShell local se simula con `$env:PORT = "9000"`.
- La carpeta `api-mi-proyecto` del ZIP ya incluye todo; solo debes crear tu repositorio vacío en GitHub y cambiar `TU_USUARIO` y `TU-API` por tus datos reales.
