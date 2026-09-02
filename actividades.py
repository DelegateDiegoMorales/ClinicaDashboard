# Definiciones de actividades. La plataforma es genérica: mide pasos, aciertos y
# porcentaje logrado a partir de estas definiciones + los eventos que llegan por JSON.
# Cada paso: codigo (lo que envía Unity), nombre, obligatorio, disponible.
# 'disponible=False' = paso apagado para la demo (no cuenta en las métricas).

ACTIVIDADES = {
    "resonancia": {
        "id": "resonancia",
        "nombre": "Resonancia Magnética",
        "icono": "🧲",
        "pasos": [
            {"codigo": "SESION_INICIO",         "nombre": "Presiona Iniciar",                 "obligatorio": True,  "disponible": True},
            {"codigo": "IMPLEMENTOS_RETIRADOS",  "nombre": "Retira implementos metálicos",     "obligatorio": True,  "disponible": True},
            {"codigo": "ROPA_CAMBIADA",          "nombre": "Cambio de ropa",                    "obligatorio": True,  "disponible": True},
            {"codigo": "PACIENTE_TRASLADADO",    "nombre": "Traslada al paciente a resonancia", "obligatorio": True,  "disponible": True},
            {"codigo": "INGRESO_SALA",           "nombre": "Ingreso a la sala",                 "obligatorio": True,  "disponible": True},
            {"codigo": "PACIENTE_SENTADO",       "nombre": "El paciente se sienta",             "obligatorio": True,  "disponible": True},
            {"codigo": "PACIENTE_ACOSTADO",      "nombre": "El paciente se acuesta",            "obligatorio": True,  "disponible": True},
            {"codigo": "PACIENTE_EN_EQUIPO",     "nombre": "El paciente entra al tubo",         "obligatorio": True,  "disponible": True},
            {"codigo": "ESCANEO_INICIO",         "nombre": "Inicia el escaneo",                 "obligatorio": True,  "disponible": True},
            {"codigo": "ESCANEO_FIN",            "nombre": "Termina el escaneo",                "obligatorio": True,  "disponible": True},
            {"codigo": "SESION_FIN",             "nombre": "Cierra la sesión",                  "obligatorio": True,  "disponible": True},
        ],
    },

    "lavado_manos": {
        "id": "lavado_manos",
        "nombre": "Lavado de Manos Quirúrgico",
        "icono": "🧼",
        "pasos": [
            {"codigo": "LAV_RETIRA_ACCESORIOS", "nombre": "Retira reloj/anillos, antebrazo descubierto hasta el codo", "obligatorio": True,  "disponible": True},
            {"codigo": "LAV_VERIFICA_UNAS",     "nombre": "Verifica uñas cortas, limpias y sin extensiones",          "obligatorio": True,  "disponible": False},  # 2 - off demo
            {"codigo": "LAV_MOJA",              "nombre": "Moja manos y antebrazo (manos más altas que el codo)",     "obligatorio": True,  "disponible": True},
            {"codigo": "LAV_ESCOBILLA",         "nombre": "Escobilla: rotatorios en dorso, palma e interdigitales",   "obligatorio": True,  "disponible": True},
            {"codigo": "LAV_ROTATORIO_BRAZO",   "nombre": "Rotatorios en muñecas y antebrazo",                        "obligatorio": True,  "disponible": True},
            {"codigo": "LAV_LIMPIA_UNAS",       "nombre": "Limpia las uñas",                                          "obligatorio": True,  "disponible": True},
            {"codigo": "LAV_ENJUAGA",           "nombre": "Enjuaga (manos → muñeca → antebrazo, manos en alto)",      "obligatorio": True,  "disponible": True},
            {"codigo": "LAV_CIERRA_LLAVE",      "nombre": "Cierra la llave con codo o pie, sin usar las manos",       "obligatorio": True,  "disponible": False},  # 8 - off demo
            {"codigo": "LAV_SECA",              "nombre": "Se dirige con manos en alto y seca con compresa estéril",  "obligatorio": True,  "disponible": True},
        ],
    },
}


def obtener_actividad(actividad_id):
    return ACTIVIDADES.get(actividad_id)


def calcular_metricas(sesion):
    """Métricas genéricas de una sesión, adaptándose a la actividad.
    Devuelve pasos (hechos/total disponibles), aciertos, porcentaje, tiempo y puntaje,
    y el estado de cada paso (hecho / omitido / no_disponible)."""
    act = obtener_actividad(sesion.get("actividadId"))
    eventos = sesion.get("eventos", []) or []

    # códigos presentes y su puntaje (para aciertos en orden)
    codigos = {}
    for e in eventos:
        codigos[e.get("codigo")] = e.get("puntaje", e.get("puntajeEvento", 0))

    if not act:
        # Sin definición: métricas sobre los propios eventos
        total = len(eventos)
        hechos = total
        aciertos = sum(1 for e in eventos if (e.get("puntaje", e.get("puntajeEvento", 0)) or 0) > 0)
        tiempo = max([e.get("tiempo", 0) for e in eventos], default=0)
        return {
            "actividadNombre": sesion.get("actividadNombre", sesion.get("actividadId", "—")),
            "pasosHechos": hechos, "pasosTotales": total,
            "aciertos": aciertos, "porcentaje": round(aciertos / total * 100) if total else 0,
            "tiempoSeg": round(tiempo, 1), "puntaje": sesion.get("puntajeFinal"),
            "pasos": [],
        }

    disponibles = [p for p in act["pasos"] if p["disponible"]]
    total = len(disponibles)

    detalle = []
    hechos = 0
    aciertos = 0
    for p in act["pasos"]:
        hecho = p["codigo"] in codigos
        if not p["disponible"]:
            estado = "no_disponible"
        elif hecho:
            estado = "hecho"
            hechos += 1
            if (codigos.get(p["codigo"]) or 0) > 0:
                aciertos += 1
        else:
            estado = "omitido"
        detalle.append({"codigo": p["codigo"], "nombre": p["nombre"],
                        "obligatorio": p["obligatorio"], "estado": estado})

    tiempo = max([e.get("tiempo", 0) for e in eventos], default=0)
    porcentaje = round(hechos / total * 100) if total else 0

    return {
        "actividadNombre": act["nombre"],
        "pasosHechos": hechos, "pasosTotales": total,
        "aciertos": aciertos, "porcentaje": porcentaje,
        "tiempoSeg": round(tiempo, 1), "puntaje": sesion.get("puntajeFinal"),
        "pasos": detalle,
    }
