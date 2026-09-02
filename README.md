# Plataforma Delégate — Demo (API + Dashboard, lista para Vercel)

Recibe el JSON de sesión desde Unity, calcula métricas (pasos, aciertos, % logrado)
y las muestra en un dashboard de un usuario. Genérico: se adapta a cualquier
actividad definida en `api/actividades.py`.

## Estructura
```
api/index.py        Función Flask (API + sirve el dashboard). Todo pasa por aquí.
api/actividades.py  Definiciones de actividades (resonancia, lavado_manos).
api/storage.py      Almacenamiento: Vercel KV en producción, archivos locales en tu PC.
api/dashboard.html  El dashboard.
vercel.json         Enruta todo a la función.
app.py              Runner local.
```

## Correr en tu PC
```bash
pip install -r requirements.txt
python app.py
```
Abrir http://localhost:5000 (guarda en `./data/sesiones.json`).

## Desplegar en Vercel
1. Sube esta carpeta a un repo (GitHub) e impórtalo en Vercel (framework: Other).
2. Añade **Vercel KV** al proyecto (Storage → KV). Vercel crea las variables
   `KV_REST_API_URL` y `KV_REST_API_TOKEN` automáticamente.
3. Deploy. En producción usa KV; en local usa archivos (mismo código).

> Nota: en Vercel el disco es de solo lectura, por eso el historial se guarda en KV,
> no en archivos. Si no configuras KV, la API responde pero no persiste entre
> invocaciones.

## Poblar el dashboard con un alumno simulado (seed)
El dashboard (`api/dashboard.html`) es el template real de Delégate y se llena
**en vivo** con las sesiones que hay en la API (KPIs, curva de aprendizaje,
errores por paso, tabla de sesiones, detalle del alumno y escenarios). El resto
de vistas (habilidades blandas, monitoreo) quedan como demo visual.

Para simular un alumno que va dejando data:
```bash
python seed.py                       # contra http://localhost:5000
python seed.py https://tu.vercel.app # contra tu deploy
```
Genera 13 sesiones de "Camila Fuentes" (9 de Resonancia + 4 de Lavado) con mejora
progresiva. Usa ids fijos (`seed-...`), así re-ejecutarlo no duplica. Luego, las
sesiones reales que llegan desde Unity (POST) se **suman** a esa data.

> El dashboard pide login (cualquier correo/clave sirve en la demo). Tras entrar,
> hace `fetch` a `/api/sesiones` y `/api/actividades` y sobreescribe la demo con
> la data real. Para refrescar sin recargar: consola del navegador → `DelegateRefrescar()`.

## Enviar una sesión (Unity o prueba)
`POST /api/sesiones`:
```json
{
  "actividadId": "resonancia",
  "usuario": "Diego",
  "eventos": [
    {"codigo": "SESION_INICIO", "tiempo": 0.0, "puntajeEvento": 10},
    {"codigo": "IMPLEMENTOS_RETIRADOS", "tiempo": 12.4, "puntajeEvento": 10}
  ],
  "puntajeFinal": 20
}
```
- `actividadId`: `"resonancia"` o `"lavado_manos"`.
- Los pasos con `disponible=false` (lavado: 2 y 8) no cuentan en las métricas.

Desde Unity usa `EnviarSesion.cs` (pon la URL de tu deploy de Vercel o el PC local).

## Agregar otra actividad
Añade una entrada a `ACTIVIDADES` en `api/actividades.py` con sus pasos
(`codigo`, `nombre`, `obligatorio`, `disponible`). El dashboard y las métricas
funcionan igual sin tocar nada más.
