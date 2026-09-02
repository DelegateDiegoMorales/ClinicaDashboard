"""Seed: simula UN alumno que va dejando sesiones en la plataforma.
Genera varias sesiones (con mejora progresiva) y las envía por POST a la API,
igual que lo haría Unity. Sirve para poblar el dashboard para la demo.

Uso:
    python seed.py                          # contra http://localhost:5000
    python seed.py https://tu.vercel.app    # contra tu deploy

Repetible: usa ids fijos, así re-ejecutar no duplica (si el storage respeta el id).
"""
import sys
import random
from datetime import datetime, timedelta

import requests

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000").rstrip("/")
URL = BASE + "/api/sesiones"
ALUMNO = "Camila Fuentes"
random.seed(7)  # reproducible

# Pasos por actividad (código, dificultad 0..1: mayor = más se falla al inicio)
RESONANCIA = [
    ("SESION_INICIO", 0.02), ("IMPLEMENTOS_RETIRADOS", 0.35), ("ROPA_CAMBIADA", 0.12),
    ("PACIENTE_TRASLADADO", 0.30), ("INGRESO_SALA", 0.45), ("PACIENTE_SENTADO", 0.15),
    ("PACIENTE_ACOSTADO", 0.20), ("PACIENTE_EN_EQUIPO", 0.25), ("ESCANEO_INICIO", 0.18),
    ("ESCANEO_FIN", 0.10), ("SESION_FIN", 0.05),
]
LAVADO = [  # solo los pasos disponibles en la demo
    ("LAV_RETIRA_ACCESORIOS", 0.20), ("LAV_MOJA", 0.10), ("LAV_ESCOBILLA", 0.35),
    ("LAV_ROTATORIO_BRAZO", 0.30), ("LAV_LIMPIA_UNAS", 0.25), ("LAV_ENJUAGA", 0.15),
    ("LAV_SECA", 0.12),
]


def sesion(actividad_id, pasos, intento, total_intentos, fecha, minutos):
    """Un intento: mejora con el número de intento. Devuelve el JSON estilo Unity."""
    destreza = 0.35 + 0.6 * (intento / max(1, total_intentos - 1))  # 0.35 -> 0.95
    eventos = []
    t = 0.0
    paso_dt = (minutos * 60.0) / (len(pasos) + 1)
    for codigo, dif in pasos:
        t += paso_dt * random.uniform(0.7, 1.3)
        prob = max(0.05, min(0.99, destreza - dif + 0.15))
        if random.random() < prob:  # paso realizado (acierto)
            eventos.append({"codigo": codigo, "tiempo": round(t, 1), "puntajeEvento": 10})
        # si no, se omite (no se agrega evento) -> cuenta como error/omitido
    return {
        "id": f"seed-{actividad_id}-{intento:02d}",     # id fijo: re-ejecutar no duplica
        "actividadId": actividad_id,
        "usuario": ALUMNO,
        "guardadoEn": fecha.strftime("%Y-%m-%d %H:%M:%S"),
        "eventos": eventos,
        "puntajeFinal": sum(e["puntajeEvento"] for e in eventos),
    }


def construir():
    envios = []
    hoy = datetime.now()
    # 9 intentos de Resonancia (principal), repartidos en ~6 semanas, con tiempos que bajan
    for i in range(9):
        fecha = hoy - timedelta(days=(9 - i) * 4, hours=random.randint(0, 8))
        minutos = 14.0 - i * 0.9  # 14 min -> ~7 min
        envios.append(sesion("resonancia", RESONANCIA, i, 9, fecha, minutos))
    # 4 intentos de Lavado de Manos
    for i in range(4):
        fecha = hoy - timedelta(days=(4 - i) * 3, hours=random.randint(0, 8))
        minutos = 6.0 - i * 0.6
        envios.append(sesion("lavado_manos", LAVADO, i, 4, fecha, minutos))
    return envios


def main():
    envios = construir()
    print(f"Enviando {len(envios)} sesiones de '{ALUMNO}' a {URL} ...")
    ok = 0
    for s in envios:
        try:
            r = requests.post(URL, json=s, timeout=15)
            if r.status_code in (200, 201):
                m = r.json().get("metricas", {})
                print(f"  ✓ {s['actividadId']:13} intento {s['id'][-2:]}  "
                      f"{m.get('porcentaje','?')}%  {m.get('pasosHechos','?')}/{m.get('pasosTotales','?')} pasos")
                ok += 1
            else:
                print(f"  ✗ {s['id']}  HTTP {r.status_code}: {r.text[:120]}")
        except Exception as e:
            print(f"  ✗ {s['id']}  {e}")
    print(f"\nListo: {ok}/{len(envios)} enviadas. Abre {BASE}/ para ver el dashboard.")


if __name__ == "__main__":
    main()
