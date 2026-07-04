from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from core.database import engine, Base
from api import auth, dashboard

# Inicializar Base de Datos (Crea tablas si no existen)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RECEPCION Y PESAJE")

# Montar archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Incluir Rutas
app.include_router(auth.router, tags=["Auth"])
app.include_router(dashboard.router, tags=["Dashboard"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)