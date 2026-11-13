"""Pruebas rápidas de la API (pytest). Ejecutar: pytest -q"""
from fastapi.testclient import TestClient
from main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "online"


def test_version():
    assert client.get("/version").json()["version"] == "1.2.0"


def test_listar_tareas():
    r = client.get("/tareas")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_tarea_inexistente_404():
    assert client.get("/tareas/9999").status_code == 404


def test_ruta_inexistente_404():
    assert client.get("/ruta-inexistente").status_code == 404


def test_crear_tarea():
    r = client.post("/tareas", json={"titulo": "Probar CI"})
    assert r.status_code == 201
    assert r.json()["completada"] is False


def test_config_check_no_revela_secreto():
    data = client.get("/config-check").json()
    assert data["prefijo_clave"].endswith("****")


def test_cors_header():
    r = client.get("/version", headers={"Origin": "http://localhost:5500"})
    assert r.headers.get("access-control-allow-origin") in ("*", "http://localhost:5500")
