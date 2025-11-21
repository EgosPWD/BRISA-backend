# Arquitectura del Sistema BRISA Backend

## Tabla de Contenidos
1. [Visión General](#visión-general)
2. [Arquitectura de Capas](#arquitectura-de-capas)
3. [Estructura de Módulos](#estructura-de-módulos)
4. [Base de Datos](#base-de-datos)
5. [Seguridad](#seguridad)
6. [Patrones de Diseño](#patrones-de-diseño)
7. [Flujos de Datos](#flujos-de-datos)

---

## Visión General

BRISA Backend es una API REST desarrollada con **FastAPI** que implementa un sistema de gestión institucional modular para la Universidad Católica Boliviana.

### Tecnologías Principales

- **Framework Web**: FastAPI 0.x
- **ORM**: SQLAlchemy
- **Validación**: Pydantic
- **Base de Datos**: MySQL 8.0+
- **Migraciones**: Alembic
- **Autenticación**: JWT (JSON Web Tokens)
- **Testing**: Pytest
- **ASGI Server**: Uvicorn

### Principios Arquitectónicos

1. **Separación de Responsabilidades**: Cada capa tiene una responsabilidad clara y definida
2. **Modularidad**: Sistema dividido en módulos independientes y cohesivos
3. **Inyección de Dependencias**: Uso extensivo del sistema de dependencias de FastAPI
4. **Tipado Fuerte**: Uso de type hints de Python y validación con Pydantic
5. **Domain-Driven Design**: Modelado centrado en el dominio de negocio

---

## Arquitectura de Capas

El sistema implementa una arquitectura en capas claramente definida:

```
┌─────────────────────────────────────────┐
│        CAPA DE PRESENTACIÓN             │
│    (Controllers/Routers FastAPI)        │
│  • Validación de entrada                │
│  • Autenticación/Autorización           │
│  • Formateo de respuestas               │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│      CAPA DE LÓGICA DE NEGOCIO          │
│            (Services)                   │
│  • Reglas de negocio                    │
│  • Validaciones complejas               │
│  • Orquestación de operaciones          │
│  • Transacciones                        │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│       CAPA DE ACCESO A DATOS            │
│          (Repositories)                 │
│  • Consultas a base de datos            │
│  • CRUD básico                          │
│  • Queries complejas                    │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│         CAPA DE PERSISTENCIA            │
│      (SQLAlchemy Models + MySQL)        │
│  • Definición de tablas                 │
│  • Relaciones                           │
│  • Constraints                          │
└─────────────────────────────────────────┘
```

### 1. Capa de Presentación (Controllers)

**Responsabilidades**:
- Definir rutas HTTP (endpoints)
- Validar datos de entrada con Pydantic DTOs
- Gestionar autenticación y autorización
- Manejar respuestas HTTP y códigos de estado
- Transformar excepciones en respuestas HTTP apropiadas

**Tecnologías**: FastAPI APIRouter, Pydantic, Depends

**Ejemplo**:
```python
@router.post("", status_code=status.HTTP_201_CREATED)
@requires_permission("crear_usuario")
async def crear_usuario(
    usuario_create: UsuarioCreateDTO,  # Validación con Pydantic
    db: Session = Depends(get_db),      # Inyección de dependencias
    current_user: Usuario = Depends(get_current_user_dependency)  # Auth
) -> dict:
    nuevo_usuario = UsuarioService.crear_usuario(db, usuario_create, current_user.id_usuario)
    return ResponseModel.success(message="Usuario creado", data=nuevo_usuario)
```

### 2. Capa de Lógica de Negocio (Services)

**Responsabilidades**:
- Implementar reglas de negocio
- Validaciones complejas que involucran múltiples entidades
- Orquestar operaciones entre múltiples repositories
- Gestionar transacciones
- Registrar auditoría

**Patrón**: Service Pattern con métodos estáticos o instancias

**Ejemplo**:
```python
class UsuarioService(BaseService):
    model_class = Usuario
    
    @classmethod
    def crear_usuario(cls, db: Session, usuario_dto: UsuarioCreateDTO, user_id: int):
        # 1. Validaciones de negocio
        if db.query(Usuario).filter(Usuario.usuario == usuario_dto.usuario).first():
            raise Conflict("Usuario ya existe")
        
        # 2. Hashear contraseña
        hashed_password = hash_password(usuario_dto.password)
        
        # 3. Crear usuario
        usuario = Usuario(**usuario_dto.dict(exclude={'password'}))
        usuario.password_hash = hashed_password
        
        # 4. Guardar en DB
        db.add(usuario)
        db.commit()
        
        # 5. Auditoría
        BitacoraService.registrar(db, "CREAR_USUARIO", user_id)
        
        return usuario
```

### 3. Capa de Acceso a Datos (Repositories)

**Responsabilidades**:
- Abstraer consultas a base de datos
- Implementar CRUD básico
- Queries complejas con filtros, joins, paginación
- Optimización de consultas (eager loading, etc.)

**Patrón**: Repository Pattern

**Ejemplo**:
```python
class UsuarioRepository(BaseRepository):
    model_class = Usuario
    
    @classmethod
    def buscar_por_username(cls, db: Session, username: str) -> Optional[Usuario]:
        return db.query(Usuario).filter(Usuario.usuario == username).first()
    
    @classmethod
    def listar_activos(cls, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Usuario)\
            .filter(Usuario.activo == True)\
            .offset(skip)\
            .limit(limit)\
            .all()
```

### 4. Capa de Persistencia (Models)

**Responsabilidades**:
- Definir estructura de tablas
- Definir relaciones entre entidades
- Constraints y validaciones a nivel de BD
- Métodos auxiliares del modelo

**Tecnología**: SQLAlchemy ORM

**Ejemplo**:
```python
class Usuario(Base):
    __tablename__ = "usuarios"
    
    id_usuario = Column(Integer, primary_key=True)
    usuario = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    activo = Column(Boolean, default=True)
    
    # Relaciones
    persona = relationship("Persona1", back_populates="usuario")
    roles = relationship("Rol", secondary=usuario_roles_table, back_populates="usuarios")
```

---

## Estructura de Módulos

### Organización del Código

```
app/
├── main.py                    # Punto de entrada de la aplicación
├── config/                    # Configuraciones
│   └── config.py             # Configuración por ambiente
├── core/                      # Funcionalidad central
│   ├── database.py           # Conexión a BD
│   ├── extensions.py         # Extensiones
│   └── utils.py              # Utilidades generales
├── shared/                    # Componentes compartidos
│   ├── models/               # Modelos base
│   ├── dto/                  # DTOs base
│   ├── services/             # Servicios base
│   ├── decorators/           # Decoradores (auth, permisos)
│   ├── exceptions/           # Excepciones personalizadas
│   ├── security.py           # Funciones de seguridad
│   ├── response.py           # Modelos de respuesta
│   └── permissions.py        # Sistema de permisos
└── modules/                   # Módulos funcionales
    ├── auth/                 # Autenticación
    ├── usuarios/             # Usuarios, roles, permisos
    ├── bitacora/             # Auditoría
    ├── esquelas/             # Esquelas y reconocimientos
    ├── administracion/       # Admin (cursos, estudiantes)
    ├── profesores/           # Gestión de profesores
    ├── incidentes/           # Incidentes
    ├── retiros_tempranos/    # Retiros tempranos
    └── reportes/             # Reportes e integración
```

### Estructura Estándar de un Módulo

Cada módulo sigue la misma estructura:

```
modules/[nombre_modulo]/
├── __init__.py
├── controllers/              # Capa de presentación
│   ├── __init__.py
│   └── [modulo]_controller.py
├── services/                 # Lógica de negocio
│   ├── __init__.py
│   └── [modulo]_service.py
├── repositories/             # Acceso a datos
│   ├── __init__.py
│   └── [modulo]_repository.py
├── dto/                      # Data Transfer Objects
│   ├── __init__.py
│   └── [modulo]_dto.py
└── models/                   # Modelos de BD
    ├── __init__.py
    └── [modulo]_models.py
```

---

## Base de Datos

### Diseño de Base de Datos

El sistema utiliza MySQL con las siguientes características:

- **Charset**: utf8mb4 (soporte completo Unicode)
- **Collation**: utf8mb4_unicode_ci
- **Engine**: InnoDB (transaccional)
- **Foreign Keys**: Habilitadas con ON DELETE/UPDATE configurados

### Entidades Principales

#### 1. Usuarios y Autenticación

```
usuarios
├── id_usuario (PK)
├── usuario (UNIQUE)
├── password_hash
├── email (UNIQUE)
├── persona_id (FK → personas.id_persona)
├── activo
├── fecha_creacion
└── ultima_conexion

roles
├── id_rol (PK)
├── nombre (UNIQUE)
├── descripcion
└── es_sistema

permisos
├── id_permiso (PK)
├── codigo (UNIQUE)
├── descripcion
└── modulo

usuario_roles (many-to-many)
├── usuario_id (FK)
├── rol_id (FK)
└── fecha_asignacion

rol_permisos (many-to-many)
├── rol_id (FK)
└── permiso_id (FK)
```

#### 2. Personas

```
personas
├── id_persona (PK)
├── ci (UNIQUE)
├── nombre
├── apellido
├── fecha_nacimiento
├── genero
├── direccion
├── telefono
├── email
└── tipo_persona (ENUM: estudiante, profesor, admin, etc.)
```

#### 3. Auditoría

```
bitacora
├── id_bitacora (PK)
├── usuario_id (FK)
├── accion
├── entidad_afectada
├── id_entidad
├── valores_anteriores (JSON)
├── valores_nuevos (JSON)
├── ip_address
├── user_agent
└── fecha_hora

login_logs
├── id_log (PK)
├── usuario_id (FK)
├── exito (BOOLEAN)
├── ip_address
├── mensaje
└── fecha_hora
```

#### 4. Esquelas

```
esquelas
├── id_esquela (PK)
├── codigo (UNIQUE)
├── tipo (ENUM: reconocimiento, orientacion)
├── estudiante_id (FK)
├── profesor_id (FK)
├── curso_id (FK)
├── motivo
├── descripcion
├── estado
├── fecha_emision
└── fecha_revision

codigos_esquela
├── id_codigo (PK)
├── codigo (UNIQUE)
├── descripcion
└── tipo_esquela
```

### Relaciones Clave

- **Usuario → Persona**: One-to-One
- **Usuario → Roles**: Many-to-Many
- **Rol → Permisos**: Many-to-Many
- **Esquela → Estudiante**: Many-to-One
- **Esquela → Profesor**: Many-to-One
- **Curso → Estudiantes**: One-to-Many

### Migraciones

El sistema usa **Alembic** para manejar migraciones de base de datos:

```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1

# Ver historial
alembic history
```

---

## Seguridad

### 1. Autenticación JWT

**Flujo**:
```
1. Usuario envía credenciales → POST /api/auth/login
2. Sistema valida credenciales
3. Sistema genera token JWT con payload:
   {
     "sub": user_id,
     "username": username,
     "roles": [roles],
     "exp": timestamp_expiration
   }
4. Cliente guarda token
5. Cliente envía token en cada request: Authorization: Bearer {token}
6. Sistema valida token en cada request protegido
```

**Configuración**:
- **Algoritmo**: HS256
- **Secret Key**: Configurable por ambiente
- **Expiración**: 60 minutos (configurable)
- **Refresh Tokens**: No implementado (futuro)

### 2. Hash de Contraseñas

- **Algoritmo**: bcrypt
- **Rounds**: 12 (configurable)
- **Salting**: Automático por bcrypt

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash
hashed = pwd_context.hash(password)

# Verificar
is_valid = pwd_context.verify(plain_password, hashed)
```

### 3. Sistema de Permisos

**Modelo RBAC** (Role-Based Access Control):

```
Usuario → Roles → Permisos
```

**Implementación**:

```python
# Decorador de permisos
@requires_permission("crear_usuario")
async def crear_usuario(...):
    pass

# Verificación en runtime
if not check_permission(current_user, "eliminar_usuario"):
    raise HTTPException(status_code=403)
```

**Permisos Jerárquicos**:
- Algunos roles tienen permisos heredados
- Rol "admin" tiene todos los permisos

### 4. Validación de Entrada

**Pydantic DTOs**: Validación automática de tipos y valores

```python
class UsuarioCreateDTO(BaseModel):
    usuario: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)
    email: EmailStr
    
    @validator('password')
    def password_complexity(cls, v):
        if not any(char.isupper() for char in v):
            raise ValueError('Debe contener al menos una mayúscula')
        return v
```

### 5. Protección CORS

Configuración en `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6. SQL Injection Prevention

- **ORM SQLAlchemy**: Todas las queries usan parámetros
- **No SQL raw queries sin parametrizar**
- **Validación de entrada con Pydantic**

### 7. Rate Limiting (Futuro)

Planeado para producción:
- Límite por IP
- Límite por usuario
- Backoff exponencial

---

## Patrones de Diseño

### 1. Repository Pattern

Abstrae el acceso a datos:

```python
class BaseRepository:
    model_class = None
    
    @classmethod
    def get_by_id(cls, db: Session, id: int):
        return db.query(cls.model_class).filter_by(id=id).first()
    
    @classmethod
    def create(cls, db: Session, obj_data):
        obj = cls.model_class(**obj_data)
        db.add(obj)
        db.commit()
        return obj
```

### 2. Service Pattern

Encapsula lógica de negocio:

```python
class BaseService:
    @classmethod
    def create(cls, db: Session, dto: BaseModel):
        # Validaciones
        # Lógica de negocio
        # Llamadas a repository
        # Auditoría
        pass
```

### 3. DTO Pattern

Transferencia de datos validada:

```python
class UsuarioResponseDTO(BaseModel):
    id_usuario: int
    usuario: str
    email: str
    
    class Config:
        orm_mode = True  # Permite from_orm(usuario_model)
```

### 4. Dependency Injection

FastAPI nativo:

```python
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    # Validar token y retornar usuario
    pass

@router.get("/protected")
def protected_route(current_user: Usuario = Depends(get_current_user)):
    # current_user inyectado automáticamente
    pass
```

### 5. Decorator Pattern

Decoradores para cross-cutting concerns:

```python
@requires_permission("crear_usuario")
@validar_puede_modificar_usuario
async def actualizar_usuario(...):
    pass
```

### 6. Factory Pattern

Para creación de objetos complejos:

```python
class UsuarioFactory:
    @staticmethod
    def crear_admin(data):
        usuario = Usuario(**data)
        usuario.roles = [RolRepository.get_admin_role()]
        return usuario
```

---

## Flujos de Datos

### 1. Flujo de Autenticación

```
┌──────┐          ┌─────────────┐          ┌──────────┐          ┌──────────┐
│Client│          │Auth         │          │Auth      │          │Database  │
│      │          │Controller   │          │Service   │          │          │
└───┬──┘          └──────┬──────┘          └────┬─────┘          └────┬─────┘
    │                    │                      │                     │
    │ POST /auth/login   │                      │                     │
    ├───────────────────>│                      │                     │
    │                    │                      │                     │
    │                    │ validate_credentials │                     │
    │                    ├─────────────────────>│                     │
    │                    │                      │                     │
    │                    │                      │ query user          │
    │                    │                      ├────────────────────>│
    │                    │                      │                     │
    │                    │                      │<────────────────────┤
    │                    │                      │ user data           │
    │                    │                      │                     │
    │                    │                      │ verify password     │
    │                    │                      │                     │
    │                    │                      │ generate JWT        │
    │                    │                      │                     │
    │                    │<─────────────────────┤                     │
    │                    │ token                │                     │
    │                    │                      │                     │
    │<───────────────────┤                      │                     │
    │ {access_token}     │                      │                     │
    │                    │                      │                     │
```

### 2. Flujo de Creación de Recurso con Permisos

```
┌──────┐     ┌────────────┐     ┌─────────┐     ┌────────────┐     ┌─────┐
│Client│     │Controller  │     │Service  │     │Repository  │     │ DB  │
└───┬──┘     └─────┬──────┘     └────┬────┘     └─────┬──────┘     └──┬──┘
    │              │                 │                │               │
    │ POST /users  │                 │                │               │
    ├─────────────>│                 │                │               │
    │              │                 │                │               │
    │              │ @requires_permission             │               │
    │              │ check_permission                 │               │
    │              │                 │                │               │
    │              │ validate DTO    │                │               │
    │              │                 │                │               │
    │              │ create_usuario  │                │               │
    │              ├────────────────>│                │               │
    │              │                 │                │               │
    │              │                 │ validate business rules       │
    │              │                 │                │               │
    │              │                 │ create         │               │
    │              │                 ├───────────────>│               │
    │              │                 │                │               │
    │              │                 │                │ INSERT        │
    │              │                 │                ├──────────────>│
    │              │                 │                │               │
    │              │                 │                │<──────────────┤
    │              │                 │                │ created obj   │
    │              │                 │<───────────────┤               │
    │              │                 │ created obj    │               │
    │              │                 │                │               │
    │              │                 │ registrar_bitacora             │
    │              │                 │                │               │
    │              │<────────────────┤                │               │
    │              │ DTO response    │                │               │
    │<─────────────┤                 │                │               │
    │ 201 Created  │                 │                │               │
```

### 3. Flujo de Consulta con Filtros y Paginación

```
GET /api/usuarios?skip=0&limit=10&activo=true

Controller → Service → Repository → Database
           ← DTO list ← Model list ← SQL Query
```

---

## Manejo de Errores

### Jerarquía de Excepciones

```
Exception
└── HTTPException (FastAPI)
    └── CustomBaseException
        ├── NotFound (404)
        ├── Conflict (409)
        ├── Unauthorized (401)
        ├── Forbidden (403)
        ├── ValidationException (422)
        └── DatabaseException (500)
```

### Exception Handlers

Registrados en `main.py`:

```python
@app.exception_handler(NotFound)
async def not_found_handler(request: Request, exc: NotFound):
    return JSONResponse(
        status_code=404,
        content={"success": false, "message": str(exc)}
    )
```

---

## Configuración por Ambiente

```python
# config/config.py

class DevelopmentConfig:
    DATABASE_URL = "mysql+pymysql://..."
    DEBUG = True
    SECRET_KEY = "dev-secret"

class ProductionConfig:
    DATABASE_URL = os.getenv("DATABASE_URL")
    DEBUG = False
    SECRET_KEY = os.getenv("SECRET_KEY")

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

Selección de ambiente:

```bash
export ENV=production
```

---

## Mejores Prácticas Implementadas

1. **Separation of Concerns**: Cada capa tiene responsabilidades claras
2. **DRY (Don't Repeat Yourself)**: Clases base reutilizables
3. **SOLID Principles**: 
   - Single Responsibility
   - Open/Closed
   - Dependency Inversion
4. **Type Safety**: Type hints en todo el código
5. **Validation First**: Validación temprana con Pydantic
6. **Fail Fast**: Errores tempranos y claros
7. **Explicit over Implicit**: Código explícito y legible
8. **Testing**: Estructura preparada para testing

---

## Escalabilidad y Performance

### Estrategias Implementadas

1. **Connection Pooling**: SQLAlchemy pool
2. **Lazy Loading**: Relaciones lazy por defecto
3. **Eager Loading**: Joins explícitos cuando necesario
4. **Paginación**: En todos los listados
5. **Índices de BD**: En campos de búsqueda frecuente

### Optimizaciones Futuras

- Caché (Redis)
- CDN para assets estáticos
- Compresión de respuestas (gzip)
- Load balancing
- Database read replicas

---

## Monitoreo y Logging

```python
import logging

logger = logging.getLogger(__name__)

# Niveles
logger.debug("Detalle de ejecución")
logger.info("Operación exitosa")
logger.warning("Situación anormal pero manejada")
logger.error("Error que afecta funcionalidad")
logger.critical("Error crítico del sistema")
```

### Logs Registrados

- Autenticación (login exitoso/fallido)
- Operaciones CRUD importantes
- Errores y excepciones
- Cambios de permisos/roles
- Acceso a recursos sensibles

---

## Mantenibilidad

### Documentación del Código

- **Docstrings**: En todas las funciones públicas
- **Type Hints**: En todos los parámetros y retornos
- **Comentarios**: Solo para lógica compleja
- **README**: Por módulo importante

### Testing

Estructura preparada:
```
tests/
├── unit/              # Tests unitarios
├── integration/       # Tests de integración
└── e2e/              # Tests end-to-end
```

### Convenciones de Código

- PEP 8 compliance
- Nombres en español para dominio de negocio
- Nombres en inglés para código técnico
- Max line length: 100 caracteres
- Imports ordenados (stdlib, third-party, local)

---

## Conclusión

Esta arquitectura proporciona:

✅ **Modularidad**: Fácil agregar nuevos módulos
✅ **Mantenibilidad**: Código limpio y organizado
✅ **Escalabilidad**: Diseño preparado para crecer
✅ **Seguridad**: Múltiples capas de protección
✅ **Testabilidad**: Fácil de testear por capas
✅ **Documentación**: API autodocumentada con Swagger

El sistema está diseñado para desarrollo colaborativo entre múltiples equipos, manteniendo consistencia y calidad en toda la aplicación.
