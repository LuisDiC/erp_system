# ERP Recepción y Pesaje de Carne

Sistema web desarrollado para la gestión, control y visualización de registros de pesaje y recepción de carne. Construido con una arquitectura moderna de backend y renderizado de plantillas, optimizado para entornos de operación continua.

## Características Principales

* Autenticación segura mediante tokens JWT almacenados en cookies HttpOnly.
* Panel de control interactivo con filtros dinámicos (fechas, folios, proveedores, productos, estado).
* Visualización detallada de pesadas (peso bruto, tara, peso neto, temperatura).
* Generación y descarga de reportes estructurados en Microsoft Excel.
* Descarga de comprobantes en formato PDF directamente desde la base de datos (BLOB).

## Stack Tecnológico

| Componente | Tecnología |
| :--- | :--- |
| **Backend** | Python, FastAPI, Uvicorn |
| **Base de Datos** | MariaDB, SQLAlchemy (ORM) |
| **Seguridad** | Passlib, Bcrypt, PyJWT |
| **Frontend** | HTML5, Bootstrap 5, Jinja2, Vanilla JS |
| **Exportación** | Openpyxl (Excel) |

## Requisitos Previos

* Python 3.9 o superior.
* Servidor de base de datos MariaDB/MySQL en ejecución.

## Instalación y Configuración Local

**1. Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd ERP

**2. Llenar las variables de entorno .env con tus datos**