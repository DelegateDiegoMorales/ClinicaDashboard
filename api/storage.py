"""Almacenamiento con dos modos:
   - Vercel KV (Upstash Redis) si hay KV_REST_API_URL + KV_REST_API_TOKEN (producción).
   - Archivos locales en ../data si no (desarrollo en tu PC).
Guarda todas las sesiones en una sola clave/lista (suficiente para la demo)."""
import os
import json

try:
    import requests
except ImportError:
    requests = None

KV_URL = os.environ.get("KV_REST_API_URL")
KV_TOKEN = os.environ.get("KV_REST_API_TOKEN")
KEY = "delegate:sesiones"

HERE = os.path.dirname(os.path.abspath(__file__))
LOCAL_DIR = os.path.join(HERE, "..", "data")


def usando_kv():
    return bool(KV_URL and KV_TOKEN and requests)


# ---- Vercel KV (Upstash REST) ----
def _kv(cmd):
    r = requests.post(KV_URL, headers={"Authorization": f"Bearer {KV_TOKEN}"},
                      json=cmd, timeout=10)
    r.raise_for_status()
    return r.json().get("result")


def _kv_cargar():
    val = _kv(["GET", KEY])
    return json.loads(val) if val else []


def _kv_guardar(lista):
    _kv(["SET", KEY, json.dumps(lista, ensure_ascii=False)])


# ---- Local (archivos) ----
def _local_path():
    os.makedirs(LOCAL_DIR, exist_ok=True)
    return os.path.join(LOCAL_DIR, "sesiones.json")


def _local_cargar():
    p = _local_path()
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def _local_guardar(lista):
    with open(_local_path(), "w", encoding="utf-8") as f:
        json.dump(lista, f, ensure_ascii=False, indent=2)


# ---- API pública ----
def cargar_todas():
    return _kv_cargar() if usando_kv() else _local_cargar()


def guardar(sesion):
    lista = cargar_todas()
    lista = [s for s in lista if s.get("id") != sesion.get("id")]
    lista.insert(0, sesion)  # más reciente primero
    if usando_kv():
        _kv_guardar(lista)
    else:
        _local_guardar(lista)
    return sesion


def obtener(sid):
    for s in cargar_todas():
        if s.get("id") == sid:
            return s
    return None
