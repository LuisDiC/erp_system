from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Numeric,LargeBinary
from sqlalchemy.orm import relationship
from core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

class Proveedor(Base):
    __tablename__ = "Proveedores"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(100), unique=True, nullable=False)

class Estado(Base):
    __tablename__ = "ESTADO"
    Fecha = Column(DateTime, nullable=False)
    folio = Column(Integer, primary_key=True)
    status = Column(String(50), nullable=False)
    Proveedor_ID = Column(Integer, ForeignKey("Proveedores.ID"), nullable=False)
    Observacion = Column(Text, nullable=True)
    PDF_Firmado = Column(LargeBinary, nullable=True)

class Productos(Base):
    __tablename__ = "Productos"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Nombre = Column(String(100), unique=True, nullable=False)

class Registro(Base):
    __tablename__ = "Registros"
    ID = Column(Integer, primary_key=True, autoincrement=True)
    Folio = Column(Integer, nullable=False, default=0)
    Fecha = Column(DateTime, nullable=False)
    Id_Proveedores = Column(Integer, ForeignKey("Proveedores.ID"), nullable=False)
    Folio_pesada = Column(String(50), nullable=True)
    Peso_Bruto = Column(Numeric(10, 2), nullable=False)
    Tara = Column(Numeric(10, 2), nullable=False, default=0.00)
    Peso_Neto = Column(Numeric(10, 2), nullable=False, default=0.00)
    Descripcion = Column(String(255), nullable=False)
    Id_Productos = Column(Integer, ForeignKey("Productos.ID"), nullable=False)
    Cantidad = Column(Integer, nullable=False)
    Temperatura = Column(Numeric(5, 2), nullable=True)
    
    # Relación con el proveedor
    proveedor = relationship("Proveedor")
    productos = relationship("Productos")