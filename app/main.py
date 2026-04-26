from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    auth, auth_google, vehiculos, talleres, disponibilidad,
    reservas, asistente, mantenimientos, recordatorios,
    educativo, admin, especialidades, usuarios,
)

app = FastAPI(
    title="AutoCar API",
    description="Plataforma móvil para gestión de mantenimiento preventivo vehicular",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(auth_google.router)
app.include_router(vehiculos.router)
app.include_router(talleres.router)
app.include_router(disponibilidad.router)
app.include_router(reservas.router)
app.include_router(asistente.router)
app.include_router(mantenimientos.router)
app.include_router(recordatorios.router)
app.include_router(educativo.router)
app.include_router(admin.router)
app.include_router(especialidades.router)
app.include_router(usuarios.router)


@app.get("/")
def root():
    return {"mensaje": "AutoCar API funcionando correctamente"}


@app.get("/health")
def health_check():
    return {"estado": "activo", "version": "1.0.0"}