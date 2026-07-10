from sqlalchemy.orm import Session
from sqlalchemy import and_, case, func
from models.schemas import Registro, Estado, Proveedor, Productos
from datetime import date
from typing import List

# 1. NUEVA FUNCIÓN PARA LA TABLA PRINCIPAL (MAESTRO)
def get_filtered_estados(
        db: Session, 
        start_date: date, 
        end_date: date, 
        folios: List[int] = None,
        status: str = None, 
        proveedor_ids: List[int] = None, 
        producto_ids: List[int] = None,  
        skip: int = 0, 
        limit: int = 50
        ):
    if not start_date or not end_date:
        return 0, []

    # Consultamos solo la tabla ESTADO, y verificamos dinámicamente si hay PDF sin descargar el archivo pesado
    query = db.query(
        Estado.folio,
        Estado.Fecha,
        Estado.status,
        Estado.Observacion,
        Proveedor.Nombre.label("proveedor_nombre"),
        case((Estado.PDF_Firmado != None, True), else_=False).label("has_pdf")
    ).join(
        Proveedor, Proveedor.ID == Estado.Proveedor_ID
    ).join(
        Registro, Registro.Folio == Estado.folio # Join necesario para filtrar por fecha y producto
    )
    
    filters = [
        Registro.Fecha >= start_date,
        Registro.Fecha <= end_date
    ]
    if folios: 
        filters.append(Estado.folio.in_(folios))
    if status: filters.append(Estado.status == status)
    if proveedor_ids: 
        filters.append(Estado.Proveedor_ID.in_(proveedor_ids))
    if producto_ids: 
        filters.append(Registro.Id_Productos.in_(producto_ids))

    query = query.filter(and_(*filters))
    
    
    # Conteo de registros únicos
    total = query.with_entities(func.count(func.distinct(Estado.folio))).scalar()
    # Agrupamos por folio para que no se dupliquen las filas en la pantalla principal
    query = query.group_by(Estado.folio)
    # Paginación y ordenamiento
    records = query.order_by(Estado.Fecha.desc()).offset(skip).limit(limit).all()
    
    results = []
    for rec in records:
        results.append({
            "Folio": rec.folio,
            "Fecha": rec.Fecha.strftime("%Y-%m-%d %H:%M:%S"),
            "Proveedor": rec.proveedor_nombre,
            "Observacion": rec.Observacion or "-",
            "Status": rec.status,
            "Has_PDF": rec.has_pdf
        })
    return total, results

# 2. NUEVA FUNCIÓN PARA LA VENTANA MODAL (DETALLE)
def get_folio_details(db: Session, folio: int):
    registros = db.query(
        Registro.Peso_Bruto,
        Registro.Tara,
        Registro.Peso_Neto,
        Registro.Descripcion,
        Registro.Cantidad,
        Registro.Temperatura
    ).filter(Registro.Folio == folio).all()
    
    return [
        {
            "Peso_Bruto": float(r.Peso_Bruto),
            "Tara": float(r.Tara),
            "Peso_Neto": float(r.Peso_Neto),
            "Descripcion": r.Descripcion,
            "Cantidad": r.Cantidad,
            "Temperatura": float(r.Temperatura) if r.Temperatura else 0.0
        } for r in registros
    ]

def get_filtered_history(
    db: Session, 
    start_date: date, 
    end_date: date, 
    folios: List[int] = None,
    status: str = None, 
    proveedor_ids: List[int] = None,
    producto_ids: List[int] = None,
    skip: int = 0,
    limit: int = 50
):
    if not start_date or not end_date:
        return 0, []

    # Construimos la consulta base uniendo las 3 tablas
    # Seleccionamos Registro completo, status de ESTADO y el nombre del Proveedor
    query = db.query(
        Registro, 
        Estado.status.label("estado_status"),
        Estado.Observacion.label("estado_observacion"),
        Proveedor.Nombre.label("proveedor_nombre"),
        Productos.Nombre.label("producto_nombre")
    ).join(
        Estado, Estado.folio == Registro.Folio
    ).join(
        Proveedor, Proveedor.ID == Registro.Id_Proveedores
    ).join(
        Productos, Productos.ID == Registro.Id_Productos
    )
    
    # Filtros obligatorios de fecha
    filters = [
        Registro.Fecha >= start_date,
        Registro.Fecha <= end_date
    ]
    
    # Filtros dinámicos
    if folios: 
        filters.append(Registro.Folio.in_(folios))
    if status:
        filters.append(Estado.status == status)
    if proveedor_ids: 
        filters.append(Registro.Id_Proveedores.in_(proveedor_ids))
    if producto_ids: 
        filters.append(Registro.Id_Productos.in_(producto_ids))

    # Aplicamos filtros y contamos totales
    query = query.filter(and_(*filters))
    total = query.count()

    # Obtenemos registros paginados ordenados por fecha
    records = query.order_by(Registro.Fecha.desc()).offset(skip).limit(limit).all()
    
    # Formateamos la salida para que el Frontend y Excel la entiendan fácilmente
    results = []
    for reg, estado_status, estado_obs, prov_nombre, prod_nombre in records:
        results.append({
            "Fecha": reg.Fecha.strftime("%Y-%m-%d %H:%M:%S"),
            "Folio": reg.Folio,
            "Proveedor": prov_nombre,
            "Folio_pesada": reg.Folio_pesada or "-",
            "Cantidad": reg.Cantidad,
            "Descripcion": prod_nombre,
            "Peso_Neto": float(reg.Peso_Neto),
            "Temperatura": float(reg.Temperatura) if reg.Temperatura else 0.0,
            "Status": estado_status,
            "Observacion": estado_obs or "-"
        })
    
    return total, results
