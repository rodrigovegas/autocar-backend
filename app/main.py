from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, vehiculos

app = FastAPI(
    title="AutoCar API",
    description="Plataforma móvil para gestión de mantenimiento preventivo vehicular",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(vehiculos.router)

@app.get("/")
def root():
    return {"mensaje": "AutoCar API funcionando correctamente"}

@app.get("/health")
def health_check():
    return {"estado": "activo", "version": "1.0.0"}
