# =====================================================================
# SESIÓN 11 - COMANDOS DE POWERSHELL (Windows)
# Ejecuta los bloques UNO POR UNO (no todo el archivo de golpe).
# Si PowerShell bloquea la activación del venv, ejecuta primero:
#   Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# =====================================================================

# ---------- 0. Ir a la carpeta del proyecto y verificar herramientas ----------
cd $HOME\Desktop\api-mi-proyecto
python --version
git --version

# ---------- MICROPRÁCTICA 11.0: entorno virtual, dependencias, .gitignore ----------
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

# Opción de la guía: congelar TODAS las librerías instaladas
pip freeze > requirements.txt
# (Si prefieres el requirements.txt limpio de este ZIP, omite el comando anterior.)

# Verificar el estado de Git (NO debe aparecer venv/ ni .env)
git init
git branch -M main
git status

# ---------- Primera sincronización con GitHub ----------
# Crea antes un repositorio VACÍO en https://github.com/new llamado api-mi-proyecto
git remote add origin https://github.com/TU_USUARIO/api-mi-proyecto.git
git add .
git commit -m "chore: audita dependencias y exclusiones para despliegue"
git push -u origin main
git status          # Debe decir: working tree clean

# ---------- MICROPRÁCTICA 11.1: probar localmente ----------
python main.py
# Abrir en el navegador:  http://localhost:8000/health   y   http://localhost:8000/docs
# Detener con Ctrl + C

# Simular el puerto dinámico del PaaS:
$env:PORT = "9000"
python main.py
# Abrir: http://localhost:9000/health   (Ctrl + C para detener)
Remove-Item Env:PORT

# ---------- Pruebas automáticas (opcional, recomendado antes de cada push) ----------
pip install pytest httpx
pytest -q

# ---------- MICROPRÁCTICA 11.2: despliegue en Render (se hace en el navegador) ----------
# Build Command : pip install -r requirements.txt
# Start Command : uvicorn main:app --host 0.0.0.0 --port $PORT
# Instance Type : Free
# Luego abre:  https://TU-API.onrender.com/docs

# ---------- MICROPRÁCTICA 11.3: probar el Despliegue Continuo ----------
# (El endpoint /version ya viene en main.py; para la prueba cambia, por ejemplo, "1.2.0" a "1.2.1")
git status
git add main.py
git commit -m "feat: agrega endpoint de version 1.2.0"
git push origin main
# Mira Render > Events/Logs y luego abre: https://TU-API.onrender.com/version

# Probar la API desplegada desde PowerShell:
Invoke-RestMethod https://TU-API.onrender.com/version
Invoke-RestMethod https://TU-API.onrender.com/health

# ---------- MICROPRÁCTICA 11.4: variables de entorno ----------
pip install python-dotenv
pip freeze > requirements.txt
git add main.py .env.example requirements.txt
git commit -m "feat: variables de entorno con python-dotenv"
git push origin main
# Comprobar que .env NO está en Git (no debe devolver nada):
git ls-files | Select-String "^\.env$"
# En Render > Environment agrega:
#   API_SECRET_KEY = clave_produccion_render_xyz_987
#   MODO_DEBUG     = False
Invoke-RestMethod https://TU-API.onrender.com/config-check

# ---------- MICROPRÁCTICA 11.5: logs y error intencional ----------
# 1) Peticiones para ver en Render > Logs:
Invoke-RestMethod https://TU-API.onrender.com/tareas
try { Invoke-RestMethod https://TU-API.onrender.com/tareas/9999 } catch { $_.Exception.Response.StatusCode }
try { Invoke-RestMethod https://TU-API.onrender.com/ruta-inexistente } catch { $_.Exception.Response.StatusCode }

# 2) Activar el error: en Render > Environment agrega HABILITAR_ERROR_DEMO = True
#    (se redespliega solo). Luego:
try { Invoke-RestMethod https://TU-API.onrender.com/simular-error } catch { $_.Exception.Response.StatusCode }
#    Lee el Traceback en Render > Logs (ZeroDivisionError: division by zero)

# 3) Corregir: cambia HABILITAR_ERROR_DEMO = False en Render (o corrige el código) y
#    haz push si modificaste main.py:
git add main.py
git commit -m "fix: corrige endpoint simular-error"
git push origin main

# ---------- MICROPRÁCTICA 11.6: CORS y cliente web ----------
# CORS ya está activo en main.py. Publica los cambios si los modificaste:
git add .
git commit -m "feat: habilita CORS para clientes web"
git push origin main
# Edita cliente_web.html (URL base) y ábrelo:
Start-Process .\cliente_web.html

# ---------- Utilidades ----------
git log --oneline -n 5          # Ver últimos commits
deactivate                      # Salir del entorno virtual
