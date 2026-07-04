import io
from fastapi import APIRouter, Depends, Request, Query, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import date
from core.database import get_db
from core.security import get_current_user_from_cookie
from services.export import generate_excel_report
from models.schemas import Proveedor, Productos, Estado  
from services.history import get_filtered_estados, get_folio_details, get_filtered_history
from typing import List


router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
def root(request: Request):
    # Redirigir al login si no hay token
    if not request.cookies.get("access_token"):
        return RedirectResponse(url="/login")
    return RedirectResponse(url="/dashboard")

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request, db: Session = Depends(get_db), username: str = Depends(get_current_user_from_cookie)):
    # Consultamos la tabla Proveedores para llenar el dropdown dinámicamente
    proveedores = db.query(Proveedor).order_by(Proveedor.Nombre).all()
    productos = db.query(Productos).order_by(Productos.Nombre).all()
    
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request, 
        "username": username,
        "system_name": "RECEPCION DE CARNE",
        "proveedores": proveedores,
        "productos": productos
    })
@router.get("/api/data")
def get_data(
    start_date: date = Query(None),
    end_date: date = Query(None),
    folio: List[int] = Query(None),
    status: str = Query(None),
    proveedor: List[int] = Query(None), # <-- CAMBIO A LISTA
    producto: List[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user_from_cookie)
):
    if not start_date or not end_date:
        return {"total": 0, "records": [], "message": "Rango de fechas requerido."}

    skip = (page - 1) * limit
    total, records = get_filtered_estados(
        db=db, 
        start_date=start_date, 
        end_date=end_date, 
        folios=folio, 
        status=status, 
        proveedor_ids=proveedor, 
        producto_ids=producto,
        skip=skip, 
        limit=limit
    )
    return {"total": total, "records": records}

@router.get("/api/export")
def export_data(
    start_date: date = Query(...),
    end_date: date = Query(...),
    folio: int = Query(None),
    status: str = Query(None),
    proveedor: List[int] = Query(None),
    producto: List[int] = Query(None),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_user_from_cookie)
):
    _, records = get_filtered_history(
        db, start_date, end_date, folio, status, proveedor,producto, skip=0, limit=100000
    )
    excel_file = generate_excel_report(records)
    
    headers = {
        'Content-Disposition': 'attachment; filename="Reporte_Entradas.xlsx"'
    }
    return StreamingResponse(excel_file, headers=headers, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@router.get("/api/folio/{folio}")
def api_folio_details(folio: int, db: Session = Depends(get_db)):
    detalles = get_folio_details(db, folio)
    if not detalles:
        raise HTTPException(status_code=404, detail="No se encontraron registros para este folio")
    return {"records": detalles}

@router.get("/api/pdf/{folio}")
def download_pdf(folio: int, db: Session = Depends(get_db)):
    # Buscamos únicamente el archivo pesado para no saturar memoria en otras peticiones
    estado = db.query(Estado).filter(Estado.folio == folio).first()
    if not estado or not estado.PDF_Firmado:
        raise HTTPException(status_code=404, detail="Este folio no contiene un documento PDF")
    
    # Transmitimos el BLOB directamente como archivo
    return StreamingResponse(
        io.BytesIO(estado.PDF_Firmado), 
        media_type="application/pdf", 
        headers={"Content-Disposition": f'attachment; filename="Recepción_Folio_{folio}.pdf"'}
    )