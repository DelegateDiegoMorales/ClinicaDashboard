"""Plataforma Delégate — API + Dashboard (Flask, lista para Vercel).
Todas las rutas pasan por esta función (ver vercel.json)."""
import os
import sys
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))  # imports locales en /api

from flask import Flask, request, jsonify, Response
try:
    from flask_cors import CORS
except ImportError:
    CORS = None

import actividades
import storage

app = Flask(__name__)
if CORS:
    CORS(app)

HERE = os.path.dirname(os.path.abspath(__file__))


@app.post("/api/sesiones")
def recibir_sesion():
    s = request.get_json(force=True, silent=True)
    if not s:
        return jsonify({"error": "JSON inválido"}), 400

    s["id"] = s.get("id") or uuid.uuid4().hex[:12]
    s["guardadoEn"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    s.setdefault("usuario", "Usuario Demo")
    s["metricas"] = actividades.calcular_metricas(s)

    storage.guardar(s)
    return jsonify(s), 201


@app.get("/api/sesiones")
def listar():
    return jsonify(storage.cargar_todas())


@app.get("/api/sesiones/<sid>")
def una(sid):
    s = storage.obtener(sid)
    return (jsonify(s) if s else (jsonify({"error": "no encontrada"}), 404))


@app.get("/api/actividades")
def acts():
    return jsonify(actividades.ACTIVIDADES)


@app.get("/")
def home():
    with open(os.path.join(HERE, "dashboard.html"), encoding="utf-8") as f:
        return Response(f.read(), mimetype="text/html")


# Ejecución local
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
