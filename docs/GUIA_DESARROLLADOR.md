# Guía de Desarrollo - BRISA Backend

## Tabla de Contenidos

1. [Configuración del Entorno](#configuración-del-entorno)
2. [Estructura de un Módulo](#estructura-de-un-módulo)
3. [Ejemplos de Código](#ejemplos-de-código)
4. [Mejores Prácticas](#mejores-prácticas)
5. [Testing](#testing)
6. [Debugging](#debugging)
7. [Troubleshooting](#troubleshooting)

---

## Configuración del Entorno

### 1. Requisitos Previos

- Python 3.12+
- MySQL 8.0+
- Git
- Editor de código (VS Code recomendado)

### 2. Instalación Paso a Paso

#### Clonar el Repositorio

```bash
git clone https://github.com/EgosPWD/BRISA-backend.git
cd BRISA-backend
```

#### Crear Entorno Virtual

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate

# Linux/Mac
python3 -m venv .venv
source .venv/bin/activate
```

#### Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus configuraciones
```

Ejemplo de `.env`:

```env
# Ambiente
ENV=development

# Base de Datos
DATABASE_URL=mysql+pymysql://usuario:password@localhost:3306/brisa_db

# Seguridad
SECRET_KEY=tu-clave-secreta-super-segura-cambiar-en-produccion
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# API
API_TITLE=API Bienestar Estudiantil
API_VERSION=1.0.0
```

#### Crear Base de Datos

```sql
-- Conectar a MySQL
mysql -u root -p

-- Crear base de datos
CREATE DATABASE brisa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Crear usuario
CREATE USER 'brisa_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON brisa_db.* TO 'brisa_user'@'localhost';
FLUSH PRIVILEGES;

-- Salir
exit;
```

#### Ejecutar Migraciones

```bash
# Aplicar migraciones
alembic upgrade head

# (Opcional) Poblar con datos iniciales
python scripts/seed_db.py
```

#### Ejecutar la Aplicación

```bash
# Modo desarrollo con auto-reload
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# O usando el script run.py
python run.py
```

Acceder a:
- API: http://localhost:8000
- Documentación Swagger: http://localhost:8000/docs
- Documentación ReDoc: http://localhost:8000/redoc

---

## Estructura de un Módulo

### Anatomía de un Módulo Completo

Cada módulo sigue una estructura estandarizada:

```
app/modules/mi_modulo/
├── __init__.py                 # Exportaciones del módulo
├── models/                     # Modelos de base de datos
│   ├── __init__.py
│   └── mi_modulo_models.py
├── dto/                        # Data Transfer Objects
│   ├── __init__.py
│   └── mi_modulo_dto.py
├── repositories/               # Acceso a datos
│   ├── __init__.py
│   └── mi_modulo_repository.py
├── services/                   # Lógica de negocio
│   ├── __init__.py
│   └── mi_modulo_service.py
└── controllers/                # Controladores HTTP
    ├── __init__.py
    └── mi_modulo_controller.py
```

---

## Ejemplos de Código

### 1. Crear un Modelo (SQLAlchemy)

**Archivo**: `app/modules/mi_modulo/models/producto_models.py`

```python
"""
Modelos de base de datos para el módulo de productos
"""
from sqlalchemy import Column, Integer, String, Numeric, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Producto(Base):
    """Modelo de Producto"""
    __tablename__ = "productos"
    
    # Columnas
    id_producto = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(String(500))
    precio = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0)
    activo = Column(Boolean, default=True)
    categoria_id = Column(Integer, ForeignKey('categorias.id_categoria'))
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    categoria = relationship("Categoria", back_populates="productos")
    ventas = relationship("VentaProducto", back_populates="producto")
    
    def __repr__(self):
        return f"<Producto(id={self.id_producto}, nombre='{self.nombre}')>"
    
    def to_dict(self):
        """Convertir a diccionario"""
        return {
            "id_producto": self.id_producto,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": float(self.precio),
            "stock": self.stock,
            "activo": self.activo,
            "categoria_id": self.categoria_id
        }


class Categoria(Base):
    """Modelo de Categoría"""
    __tablename__ = "categorias"
    
    id_categoria = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(255))
    activo = Column(Boolean, default=True)
    
    # Relaciones
    productos = relationship("Producto", back_populates="categoria")
    
    def __repr__(self):
        return f"<Categoria(id={self.id_categoria}, nombre='{self.nombre}')>"
```

### 2. Crear DTOs (Pydantic)

**Archivo**: `app/modules/mi_modulo/dto/producto_dto.py`

```python
"""
Esquemas de validación para el módulo de productos
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductoBaseDTO(BaseModel):
    """DTO base para producto"""
    nombre: str = Field(..., min_length=3, max_length=100, description="Nombre del producto")
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: Decimal = Field(..., gt=0, description="Precio debe ser mayor a 0")
    stock: int = Field(default=0, ge=0, description="Stock no puede ser negativo")
    categoria_id: int
    
    @validator('precio')
    def validar_precio(cls, v):
        """Validar que el precio tenga máximo 2 decimales"""
        if v.as_tuple().exponent < -2:
            raise ValueError('El precio no puede tener más de 2 decimales')
        return v


class ProductoCreateDTO(ProductoBaseDTO):
    """DTO para crear producto"""
    pass


class ProductoUpdateDTO(BaseModel):
    """DTO para actualizar producto (todos los campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=3, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    precio: Optional[Decimal] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    categoria_id: Optional[int] = None
    activo: Optional[bool] = None


class ProductoResponseDTO(ProductoBaseDTO):
    """DTO para respuesta de producto"""
    id_producto: int
    activo: bool
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime]
    
    class Config:
        orm_mode = True  # Permite crear desde modelos SQLAlchemy


class CategoriaCreateDTO(BaseModel):
    """DTO para crear categoría"""
    nombre: str = Field(..., min_length=3, max_length=50)
    descripcion: Optional[str] = Field(None, max_length=255)


class CategoriaResponseDTO(BaseModel):
    """DTO para respuesta de categoría"""
    id_categoria: int
    nombre: str
    descripcion: Optional[str]
    activo: bool
    
    class Config:
        orm_mode = True
```

### 3. Crear Repository

**Archivo**: `app/modules/mi_modulo/repositories/producto_repository.py`

```python
"""
Repository para acceso a datos de productos
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.modules.mi_modulo.models.producto_models import Producto, Categoria
from app.shared.repositories.base_repository import BaseRepository


class ProductoRepository(BaseRepository):
    """Repository de productos"""
    model_class = Producto
    
    @classmethod
    def buscar_por_nombre(cls, db: Session, nombre: str) -> Optional[Producto]:
        """Buscar producto por nombre exacto"""
        return db.query(Producto).filter(Producto.nombre == nombre).first()
    
    @classmethod
    def buscar_por_nombre_like(cls, db: Session, nombre: str) -> List[Producto]:
        """Buscar productos que contengan el nombre"""
        return db.query(Producto)\
            .filter(Producto.nombre.ilike(f"%{nombre}%"))\
            .all()
    
    @classmethod
    def listar_por_categoria(cls, db: Session, categoria_id: int, 
                            skip: int = 0, limit: int = 100) -> List[Producto]:
        """Listar productos de una categoría"""
        return db.query(Producto)\
            .filter(Producto.categoria_id == categoria_id)\
            .filter(Producto.activo == True)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @classmethod
    def listar_con_stock_bajo(cls, db: Session, umbral: int = 10) -> List[Producto]:
        """Listar productos con stock bajo"""
        return db.query(Producto)\
            .filter(Producto.stock < umbral)\
            .filter(Producto.activo == True)\
            .all()
    
    @classmethod
    def actualizar_stock(cls, db: Session, producto_id: int, cantidad: int) -> Producto:
        """Actualizar stock de un producto"""
        producto = cls.get_by_id(db, producto_id)
        if producto:
            producto.stock += cantidad
            db.commit()
            db.refresh(producto)
        return producto


class CategoriaRepository(BaseRepository):
    """Repository de categorías"""
    model_class = Categoria
    
    @classmethod
    def buscar_por_nombre(cls, db: Session, nombre: str) -> Optional[Categoria]:
        """Buscar categoría por nombre"""
        return db.query(Categoria).filter(Categoria.nombre == nombre).first()
    
    @classmethod
    def listar_activas(cls, db: Session) -> List[Categoria]:
        """Listar categorías activas"""
        return db.query(Categoria).filter(Categoria.activo == True).all()
```

### 4. Crear Service

**Archivo**: `app/modules/mi_modulo/services/producto_service.py`

```python
"""
Servicio de lógica de negocio para productos
"""
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from fastapi import HTTPException, status

from app.modules.mi_modulo.models.producto_models import Producto
from app.modules.mi_modulo.dto.producto_dto import (
    ProductoCreateDTO, ProductoUpdateDTO, ProductoResponseDTO
)
from app.modules.mi_modulo.repositories.producto_repository import (
    ProductoRepository, CategoriaRepository
)
from app.shared.exceptions.custom_exceptions import NotFound, Conflict, ValidationException
from app.shared.services.base_services import BaseService

logger = logging.getLogger(__name__)


class ProductoService(BaseService):
    """Servicio de productos"""
    model_class = Producto
    
    @classmethod
    def crear_producto(cls, db: Session, producto_dto: ProductoCreateDTO, 
                      user_id: Optional[int] = None) -> ProductoResponseDTO:
        """
        Crear nuevo producto
        
        Args:
            db: Sesión de base de datos
            producto_dto: Datos del producto a crear
            user_id: ID del usuario que crea el producto (para auditoría)
            
        Returns:
            ProductoResponseDTO: Producto creado
            
        Raises:
            Conflict: Si ya existe un producto con ese nombre
            NotFound: Si la categoría no existe
            ValidationException: Si los datos son inválidos
        """
        # 1. Validar que no exista producto con el mismo nombre
        producto_existente = ProductoRepository.buscar_por_nombre(db, producto_dto.nombre)
        if producto_existente:
            raise Conflict(f"Ya existe un producto con el nombre '{producto_dto.nombre}'")
        
        # 2. Validar que la categoría exista
        categoria = CategoriaRepository.get_by_id(db, producto_dto.categoria_id)
        if not categoria:
            raise NotFound(f"Categoría con ID {producto_dto.categoria_id} no encontrada")
        
        # 3. Validar reglas de negocio adicionales
        if producto_dto.precio < 0:
            raise ValidationException("El precio no puede ser negativo")
        
        try:
            # 4. Crear el producto
            data = producto_dto.dict()
            producto = Producto(**data)
            
            # 5. Guardar en base de datos
            db.add(producto)
            db.commit()
            db.refresh(producto)
            
            # 6. Registrar en auditoría (opcional)
            if user_id:
                from app.modules.bitacora.services.bitacora_service import BitacoraService
                BitacoraService.registrar_accion(
                    db, 
                    usuario_id=user_id,
                    accion="CREATE_PRODUCTO",
                    entidad_afectada="productos",
                    id_entidad=producto.id_producto
                )
            
            logger.info(f"Producto creado: ID={producto.id_producto}, nombre={producto.nombre}")
            
            # 7. Retornar DTO de respuesta
            return ProductoResponseDTO.from_orm(producto)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error al crear producto: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear producto: {str(e)}"
            )
    
    @classmethod
    def obtener_producto(cls, db: Session, producto_id: int) -> ProductoResponseDTO:
        """Obtener producto por ID"""
        producto = ProductoRepository.get_by_id(db, producto_id)
        if not producto:
            raise NotFound(f"Producto con ID {producto_id} no encontrado")
        return ProductoResponseDTO.from_orm(producto)
    
    @classmethod
    def listar_productos(cls, db: Session, skip: int = 0, limit: int = 100,
                        categoria_id: Optional[int] = None,
                        nombre: Optional[str] = None) -> List[ProductoResponseDTO]:
        """
        Listar productos con filtros opcionales
        
        Args:
            db: Sesión de base de datos
            skip: Registros a omitir (paginación)
            limit: Máximo de registros a retornar
            categoria_id: Filtrar por categoría (opcional)
            nombre: Buscar por nombre (búsqueda parcial, opcional)
            
        Returns:
            Lista de ProductoResponseDTO
        """
        # Aplicar filtros
        if categoria_id:
            productos = ProductoRepository.listar_por_categoria(db, categoria_id, skip, limit)
        elif nombre:
            productos = ProductoRepository.buscar_por_nombre_like(db, nombre)
        else:
            productos = ProductoRepository.list_all(db, skip, limit)
        
        return [ProductoResponseDTO.from_orm(p) for p in productos]
    
    @classmethod
    def actualizar_producto(cls, db: Session, producto_id: int, 
                           producto_dto: ProductoUpdateDTO,
                           user_id: Optional[int] = None) -> ProductoResponseDTO:
        """Actualizar producto existente"""
        # 1. Verificar que existe
        producto = ProductoRepository.get_by_id(db, producto_id)
        if not producto:
            raise NotFound(f"Producto con ID {producto_id} no encontrado")
        
        # 2. Guardar valores anteriores para auditoría
        valores_anteriores = producto.to_dict()
        
        try:
            # 3. Actualizar solo los campos proporcionados
            data = producto_dto.dict(exclude_unset=True)
            for key, value in data.items():
                setattr(producto, key, value)
            
            # 4. Guardar cambios
            db.commit()
            db.refresh(producto)
            
            # 5. Auditoría
            if user_id:
                from app.modules.bitacora.services.bitacora_service import BitacoraService
                BitacoraService.registrar_accion(
                    db,
                    usuario_id=user_id,
                    accion="UPDATE_PRODUCTO",
                    entidad_afectada="productos",
                    id_entidad=producto_id,
                    valores_anteriores=valores_anteriores,
                    valores_nuevos=producto.to_dict()
                )
            
            return ProductoResponseDTO.from_orm(producto)
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error al actualizar producto: {str(e)}")
            raise
    
    @classmethod
    def eliminar_producto(cls, db: Session, producto_id: int, 
                         user_id: Optional[int] = None) -> bool:
        """
        Eliminar (desactivar) producto
        
        Nota: Se hace eliminación lógica (soft delete)
        """
        producto = ProductoRepository.get_by_id(db, producto_id)
        if not producto:
            raise NotFound(f"Producto con ID {producto_id} no encontrado")
        
        try:
            # Soft delete
            producto.activo = False
            db.commit()
            
            # Auditoría
            if user_id:
                from app.modules.bitacora.services.bitacora_service import BitacoraService
                BitacoraService.registrar_accion(
                    db,
                    usuario_id=user_id,
                    accion="DELETE_PRODUCTO",
                    entidad_afectada="productos",
                    id_entidad=producto_id
                )
            
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error al eliminar producto: {str(e)}")
            raise
    
    @classmethod
    def actualizar_stock(cls, db: Session, producto_id: int, cantidad: int,
                        user_id: Optional[int] = None) -> ProductoResponseDTO:
        """
        Actualizar stock de un producto
        
        Args:
            producto_id: ID del producto
            cantidad: Cantidad a sumar/restar (positivo suma, negativo resta)
            
        Raises:
            ValidationException: Si el stock resultante sería negativo
        """
        producto = ProductoRepository.get_by_id(db, producto_id)
        if not producto:
            raise NotFound(f"Producto con ID {producto_id} no encontrado")
        
        # Validar que no quede en negativo
        nuevo_stock = producto.stock + cantidad
        if nuevo_stock < 0:
            raise ValidationException(
                f"Stock insuficiente. Stock actual: {producto.stock}, "
                f"se intentó restar: {abs(cantidad)}"
            )
        
        try:
            stock_anterior = producto.stock
            producto.stock = nuevo_stock
            db.commit()
            db.refresh(producto)
            
            # Auditoría
            if user_id:
                from app.modules.bitacora.services.bitacora_service import BitacoraService
                BitacoraService.registrar_accion(
                    db,
                    usuario_id=user_id,
                    accion="UPDATE_STOCK_PRODUCTO",
                    entidad_afectada="productos",
                    id_entidad=producto_id,
                    detalle=f"Stock: {stock_anterior} → {nuevo_stock} (cambio: {cantidad:+d})"
                )
            
            return ProductoResponseDTO.from_orm(producto)
            
        except Exception as e:
            db.rollback()
            raise
```

### 5. Crear Controller

**Archivo**: `app/modules/mi_modulo/controllers/producto_controller.py`

```python
"""
Controlador HTTP para productos
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.shared.response import ResponseModel
from app.shared.permissions import requires_permission
from app.modules.auth.services.auth_service import get_current_user_dependency
from app.modules.usuarios.models.usuario_models import Usuario

from app.modules.mi_modulo.dto.producto_dto import (
    ProductoCreateDTO, ProductoUpdateDTO, ProductoResponseDTO
)
from app.modules.mi_modulo.services.producto_service import ProductoService

router = APIRouter()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=dict)
@requires_permission("crear_producto")
async def crear_producto(
    producto: ProductoCreateDTO,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_dependency)
) -> dict:
    """
    Crear nuevo producto
    
    **Permisos requeridos**: crear_producto
    
    **Body**:
    - nombre: Nombre del producto (3-100 caracteres)
    - descripcion: Descripción opcional
    - precio: Precio (mayor a 0, máx 2 decimales)
    - stock: Stock inicial (default 0)
    - categoria_id: ID de la categoría
    
    **Respuesta**:
    - 201: Producto creado exitosamente
    - 400: Datos inválidos
    - 409: Ya existe producto con ese nombre
    - 404: Categoría no encontrada
    """
    try:
        nuevo_producto = ProductoService.crear_producto(
            db, 
            producto, 
            user_id=current_user.id_usuario
        )
        
        return ResponseModel.success(
            message="Producto creado exitosamente",
            data=nuevo_producto.dict(),
            status_code=status.HTTP_201_CREATED
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/{producto_id}", response_model=dict)
async def obtener_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_dependency)
) -> dict:
    """
    Obtener detalles de un producto
    
    **Parámetros**:
    - producto_id: ID del producto
    
    **Respuesta**:
    - 200: Producto encontrado
    - 404: Producto no encontrado
    """
    try:
        producto = ProductoService.obtener_producto(db, producto_id)
        
        return ResponseModel.success(
            message="Producto obtenido exitosamente",
            data=producto.dict()
        )
    except HTTPException as e:
        raise e


@router.get("", response_model=dict)
async def listar_productos(
    skip: int = Query(0, ge=0, description="Registros a omitir"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de registros"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    nombre: Optional[str] = Query(None, min_length=1, description="Buscar por nombre"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_dependency)
) -> dict:
    """
    Listar productos con filtros opcionales
    
    **Query Parameters**:
    - skip: Registros a omitir (paginación)
    - limit: Máximo de registros (1-100)
    - categoria_id: Filtrar por categoría (opcional)
    - nombre: Buscar por nombre parcial (opcional)
    
    **Respuesta**:
    - 200: Lista de productos
    """
    try:
        productos = ProductoService.listar_productos(
            db, 
            skip=skip, 
            limit=limit,
            categoria_id=categoria_id,
            nombre=nombre
        )
        
        return ResponseModel.success(
            message=f"{len(productos)} productos encontrados",
            data=[p.dict() for p in productos],
            metadata={
                "skip": skip,
                "limit": limit,
                "total": len(productos)
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/{producto_id}", response_model=dict)
@requires_permission("actualizar_producto")
async def actualizar_producto(
    producto_id: int,
    producto: ProductoUpdateDTO,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_dependency)
) -> dict:
    """
    Actualizar producto existente
    
    **Permisos requeridos**: actualizar_producto
    
    **Body**: Todos los campos son opcionales
    
    **Respuesta**:
    - 200: Producto actualizado
    - 404: Producto no encontrado
    """
    try:
        producto_actualizado = ProductoService.actualizar_producto(
            db,
            producto_id,
            producto,
            user_id=current_user.id_usuario
        )
        
        return ResponseModel.success(
            message="Producto actualizado exitosamente",
            data=producto_actualizado.dict()
        )
    except HTTPException as e:
        raise e


@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
@requires_permission("eliminar_producto")
async def eliminar_producto(
    producto_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_dependency)
):
    """
    Eliminar (desactivar) producto
    
    **Permisos requeridos**: eliminar_producto
    
    **Nota**: Se realiza eliminación lógica (soft delete)
    
    **Respuesta**:
    - 204: Producto eliminado exitosamente
    - 404: Producto no encontrado
    """
    try:
        ProductoService.eliminar_producto(
            db,
            producto_id,
            user_id=current_user.id_usuario
        )
        
        return None  # 204 No Content
    except HTTPException as e:
        raise e


@router.patch("/{producto_id}/stock", response_model=dict)
@requires_permission("actualizar_producto")
async def actualizar_stock(
    producto_id: int,
    cantidad: int = Query(..., description="Cantidad a sumar (positivo) o restar (negativo)"),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user_dependency)
) -> dict:
    """
    Actualizar stock de un producto
    
    **Permisos requeridos**: actualizar_producto
    
    **Query Parameters**:
    - cantidad: Cantidad a sumar/restar (puede ser positivo o negativo)
    
    **Respuesta**:
    - 200: Stock actualizado
    - 400: Stock resultante sería negativo
    - 404: Producto no encontrado
    """
    try:
        producto = ProductoService.actualizar_stock(
            db,
            producto_id,
            cantidad,
            user_id=current_user.id_usuario
        )
        
        return ResponseModel.success(
            message=f"Stock actualizado: {cantidad:+d}",
            data=producto.dict()
        )
    except HTTPException as e:
        raise e
```

### 6. Registrar el Router

**Archivo**: `app/main.py` (añadir)

```python
# Importar el router
from app.modules.mi_modulo.controllers import producto_controller

# Registrar el router
app.include_router(
    producto_controller.router, 
    prefix="/api/productos",
    tags=["Productos"]
)
```

---

## Mejores Prácticas

### 1. Nomenclatura

```python
# ✅ BIEN
class UsuarioService:
    def crear_usuario(self, db: Session, dto: UsuarioCreateDTO):
        pass

# ❌ MAL
class userSvc:
    def create(self, db, data):
        pass
```

### 2. Type Hints

```python
# ✅ BIEN
from typing import List, Optional

def obtener_usuarios(db: Session, skip: int = 0) -> List[Usuario]:
    pass

# ❌ MAL
def obtener_usuarios(db, skip=0):
    pass
```

### 3. Docstrings

```python
# ✅ BIEN
def crear_usuario(db: Session, usuario_dto: UsuarioCreateDTO) -> Usuario:
    """
    Crear nuevo usuario en el sistema
    
    Args:
        db: Sesión de base de datos
        usuario_dto: Datos del usuario a crear
        
    Returns:
        Usuario: Usuario creado
        
    Raises:
        Conflict: Si el usuario ya existe
    """
    pass
```

### 4. Manejo de Errores

```python
# ✅ BIEN
from app.shared.exceptions import NotFound, Conflict

def obtener_usuario(db: Session, user_id: int) -> Usuario:
    usuario = db.query(Usuario).filter_by(id=user_id).first()
    if not usuario:
        raise NotFound(f"Usuario {user_id} no encontrado")
    return usuario

# ❌ MAL
def obtener_usuario(db, user_id):
    return db.query(Usuario).filter_by(id=user_id).first()
```

### 5. Validación

```python
# ✅ BIEN - Validación temprana
class UsuarioCreateDTO(BaseModel):
    usuario: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)
    email: EmailStr
    
    @validator('password')
    def password_complexity(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Debe contener mayúscula')
        return v
```

### 6. Logging

```python
import logging

logger = logging.getLogger(__name__)

def operacion_importante():
    logger.info("Iniciando operación")
    try:
        # código
        logger.debug("Detalle de ejecución")
    except Exception as e:
        logger.error(f"Error en operación: {str(e)}", exc_info=True)
        raise
```

### 7. Transacciones

```python
# ✅ BIEN - Manejo explícito
def operacion_compleja(db: Session):
    try:
        # operaciones
        db.commit()
    except Exception as e:
        db.rollback()
        raise
```

---

## Testing

### Estructura de Tests

```
tests/
├── unit/                       # Tests unitarios
│   ├── test_services/
│   │   └── test_producto_service.py
│   └── test_repositories/
│       └── test_producto_repository.py
├── integration/                # Tests de integración
│   └── test_producto_api.py
└── conftest.py                # Configuración pytest
```

### Ejemplo de Test Unitario

```python
# tests/unit/test_services/test_producto_service.py
import pytest
from unittest.mock import Mock, patch
from app.modules.mi_modulo.services.producto_service import ProductoService
from app.modules.mi_modulo.dto.producto_dto import ProductoCreateDTO
from app.shared.exceptions import Conflict, NotFound


class TestProductoService:
    
    @patch('app.modules.mi_modulo.repositories.producto_repository.ProductoRepository')
    def test_crear_producto_exitoso(self, mock_repo):
        # Arrange
        mock_db = Mock()
        mock_repo.buscar_por_nombre.return_value = None
        producto_dto = ProductoCreateDTO(
            nombre="Producto Test",
            descripcion="Descripción",
            precio=99.99,
            stock=10,
            categoria_id=1
        )
        
        # Act
        resultado = ProductoService.crear_producto(mock_db, producto_dto)
        
        # Assert
        assert resultado is not None
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    @patch('app.modules.mi_modulo.repositories.producto_repository.ProductoRepository')
    def test_crear_producto_duplicado_lanza_excepcion(self, mock_repo):
        # Arrange
        mock_db = Mock()
        mock_repo.buscar_por_nombre.return_value = Mock()  # Producto ya existe
        producto_dto = ProductoCreateDTO(
            nombre="Producto Duplicado",
            precio=50.00,
            categoria_id=1
        )
        
        # Act & Assert
        with pytest.raises(Conflict):
            ProductoService.crear_producto(mock_db, producto_dto)
```

### Ejemplo de Test de Integración

```python
# tests/integration/test_producto_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_crear_producto_endpoint():
    # Arrange
    headers = {"Authorization": "Bearer test-token"}
    payload = {
        "nombre": "Producto API Test",
        "descripcion": "Test",
        "precio": 100.00,
        "stock": 5,
        "categoria_id": 1
    }
    
    # Act
    response = client.post("/api/productos", json=payload, headers=headers)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["success"] == True
    assert "id_producto" in data["data"]


def test_listar_productos_endpoint():
    # Act
    response = client.get("/api/productos?skip=0&limit=10")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["data"], list)
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Tests con cobertura
pytest --cov=app

# Tests de un módulo específico
pytest tests/unit/test_services/

# Tests con output detallado
pytest -v

# Tests con output de print
pytest -s
```

---

## Debugging

### 1. Usar el Debugger de Python

**VS Code**: Configuración `.vscode/launch.json`

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Python: FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "app.main:app",
                "--reload",
                "--host", "0.0.0.0",
                "--port", "8000"
            ],
            "jinja": true,
            "justMyCode": true
        }
    ]
}
```

### 2. Breakpoints en Código

```python
import pdb

def mi_funcion():
    # código
    pdb.set_trace()  # Breakpoint
    # más código
```

### 3. Logging Detallado

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.debug(f"Valor de variable: {variable}")
```

### 4. FastAPI Debug Mode

```python
# app/main.py
app = FastAPI(debug=True)  # Solo en desarrollo
```

---

## Troubleshooting

### Problema: Error de conexión a base de datos

```
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server")
```

**Solución**:
1. Verificar que MySQL esté corriendo: `sudo systemctl status mysql`
2. Verificar credenciales en `.env`
3. Verificar que el usuario tenga permisos

### Problema: Migraciones no se aplican

```bash
# Resetear Alembic
alembic stamp head
alembic revision --autogenerate -m "Nuevo cambio"
alembic upgrade head
```

### Problema: Import errors

```
ModuleNotFoundError: No module named 'app'
```

**Solución**:
- Asegurarse de estar en el directorio raíz
- Verificar que el entorno virtual esté activado
- Reinstalar dependencias: `pip install -r requirements.txt`

### Problema: Token JWT inválido

```
401 Unauthorized: Could not validate credentials
```

**Solución**:
1. Verificar que el token no haya expirado
2. Verificar SECRET_KEY en `.env`
3. Regenerar token con `/api/auth/login`

---

## Recursos Adicionales

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Pydantic Docs**: https://docs.pydantic.dev/
- **Alembic Docs**: https://alembic.sqlalchemy.org/

---

## Comandos Útiles

```bash
# Activar entorno virtual
source .venv/bin/activate  # Linux/Mac
.\.venv\Scripts\Activate   # Windows

# Ejecutar aplicación
uvicorn app.main:app --reload

# Tests
pytest
pytest --cov=app
pytest -v -s

# Migraciones
alembic revision --autogenerate -m "mensaje"
alembic upgrade head
alembic downgrade -1

# Formateo de código (opcional)
black app/
isort app/

# Linting (opcional)
flake8 app/
pylint app/
```

---

Esta guía proporciona todo lo necesario para comenzar a desarrollar en el proyecto BRISA Backend de manera efectiva y siguiendo las mejores prácticas establecidas.
