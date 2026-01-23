import os
from fastapi import FastAPI, Request
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.templating import Jinja2Templates
from datetime import datetime
import pytz

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Configuración de MongoDB y Zona Horaria
MONGO_URL = os.environ.get("MONGO_URL")
client = AsyncIOMotorClient(MONGO_URL)
db = client.rastreador_db
mexico_tz = pytz.timezone('America/Mexico_City')

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/update/{trailer_id}")
async def update_location(trailer_id: str, data: dict):
    ahora = datetime.now(mexico_tz)
    nuevo_estado_panico = data.get("panic", False)
    
    # 1. Verificar si el estado de pánico cambió para el historial
    ultimo_registro = await db.posiciones.find_one(
        {"trailer_id": trailer_id}, sort=[("timestamp", -1)]
    )
    estado_anterior = ultimo_registro.get("panic", False) if ultimo_registro else False

    if nuevo_estado_panico != estado_anterior:
        await db.historial_alertas.insert_one({
            "trailer_id": trailer_id,
            "evento": "ACTIVADO" if nuevo_estado_panico else "RESUELTO",
            "timestamp": ahora,
            "hora": ahora.strftime("%H:%M:%S"),
            "fecha": ahora.strftime("%Y-%m-%d"),
            "coords": f"{data.get('lat')}, {data.get('lng')}"
        })

    # 2. Guardar posición actual
    registro = {
        "trailer_id": trailer_id,
        "lat": data.get("lat"),
        "lng": data.get("lng"),
        "battery": data.get("battery", "OK"),
        "panic": nuevo_estado_panico,
        "timestamp": ahora,
        "hora_lectura": ahora.strftime("%H:%M:%S")
    }
    await db.posiciones.insert_one(registro)
    return {"status": "ok"}

@app.get("/fleet")
async def get_fleet():
    ids_trailers = await db.posiciones.distinct("trailer_id")
    estado_flota = {}
    for tid in ids_trailers:
        cursor = db.posiciones.find({"trailer_id": tid}).sort("timestamp", -1).limit(1)
        ultimo = await cursor.to_list(length=1)
        if ultimo:
            historia_cursor = db.posiciones.find({"trailer_id": tid}).sort("timestamp", -1).limit(30)
            historia = await historia_cursor.to_list(length=30)
            camino = [[p["lat"], p["lng"]] for p in reversed(historia)]
            
            estado_flota[tid] = {
                "lat": ultimo[0]["lat"],
                "lng": ultimo[0]["lng"],
                "battery": ultimo[0].get("battery", "--"),
                "panic": ultimo[0].get("panic", False),
                "last_seen": ultimo[0].get("hora_lectura", "--:--"),
                "path": camino
            }
    return estado_flota