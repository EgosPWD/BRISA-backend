# Documentación de Base de Datos - BRISA Backend

## Información General

- **Motor de Base de Datos**: MySQL 8.0+
- **Charset**: utf8mb4
- **Collation**: utf8mb4_unicode_ci
- **ORM**: SQLAlchemy
- **Migraciones**: Alembic

---

## Diagrama Entidad-Relación

### Vista General de Módulos

```
┌─────────────────────────────────────────────────────────────────┐
│                    MÓDULO DE USUARIOS                            │
│  ┌─────────┐      ┌──────────────┐      ┌──────────┐           │
│  │Usuarios │ ←──→ │usuario_roles │ ←──→ │  Roles   │           │
│  └────┬────┘      └──────────────┘      └────┬─────┘           │
│       │                                       │                  │
│       │                                  ┌────┴─────┐           │
│       │                                  │rol_      │           │
│       │                                  │permisos  │           │
│       │                                  └────┬─────┘           │
│       │                                       │                  │
│       │                              ┌────────┴────────┐        │
│       │                              │    Permisos     │        │
│       │                              └─────────────────┘        │
│       │                                                          │
│  ┌────┴────┐                                                    │
│  │Personas │                                                    │
│  └────┬────┘                                                    │
└───────┼─────────────────────────────────────────────────────────┘
        │
        ├──────────────────────────────────────┐
        │                                      │
┌───────┴────────┐                   ┌─────────┴──────────┐
│  Estudiantes   │                   │    Profesores      │
└───────┬────────┘                   └─────────┬──────────┘
        │                                      │
        │                                      │
┌───────┴────────────────────────────┐         │
│      MÓDULO DE ESQUELAS            │         │
│  ┌──────────┐                      │         │
│  │Esquelas  │ ←─────────────────────────────┘
│  └────┬─────┘                      │
│       │                            │
│  ┌────┴────────────┐               │
│  │Códigos Esquela  │               │
│  └─────────────────┘               │
└────────────────────────────────────┘

┌─────────────────────────────────────┐
│    MÓDULO DE ADMINISTRACIÓN         │
│  ┌────────┐                         │
│  │Cursos  │                         │
│  └────┬───┘                         │
│       │                             │
│  ┌────┴────────────┐                │
│  │Curso_Estudiante │                │
│  └─────────────────┘                │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│    MÓDULO DE AUDITORÍA              │
│  ┌──────────┐    ┌───────────┐     │
│  │Bitacora  │    │LoginLogs  │     │
│  └──────────┘    └───────────┘     │
└─────────────────────────────────────┘
```

---

## Tablas Principales

### 1. Módulo de Usuarios y Autenticación

#### Tabla: `personas`

Almacena información de todas las personas en el sistema (estudiantes, profesores, administrativos).

```sql
CREATE TABLE personas (
    id_persona INT AUTO_INCREMENT PRIMARY KEY,
    ci VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    genero ENUM('M', 'F', 'Otro'),
    direccion TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    tipo_persona ENUM('estudiante', 'profesor', 'administrativo', 'registrador', 'padre') NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_ci (ci),
    INDEX idx_tipo_persona (tipo_persona),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Descripción de Campos**:
- `id_persona`: Identificador único autogenerado
- `ci`: Cédula de identidad (única)
- `tipo_persona`: Tipo de persona en el sistema
- `activo`: Estado de la persona (activo/inactivo)

**Relaciones**:
- One-to-One con `usuarios`
- One-to-Many con `estudiantes` (si tipo_persona = 'estudiante')
- One-to-Many con `profesores` (si tipo_persona = 'profesor')

---

#### Tabla: `usuarios`

Credenciales de acceso al sistema.

```sql
CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    usuario VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    persona_id INT UNIQUE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_conexion TIMESTAMP NULL,
    intentos_fallidos INT DEFAULT 0,
    bloqueado_hasta TIMESTAMP NULL,
    
    FOREIGN KEY (persona_id) REFERENCES personas(id_persona) ON DELETE CASCADE,
    
    INDEX idx_usuario (usuario),
    INDEX idx_email (email),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Descripción de Campos**:
- `id_usuario`: Identificador único del usuario
- `usuario`: Nombre de usuario (único)
- `password_hash`: Contraseña hasheada con bcrypt
- `persona_id`: Referencia a la persona asociada
- `intentos_fallidos`: Contador de intentos fallidos de login
- `bloqueado_hasta`: Fecha/hora hasta la cual el usuario está bloqueado

**Relaciones**:
- One-to-One con `personas`
- Many-to-Many con `roles` (a través de `usuario_roles`)
- One-to-Many con `bitacora`
- One-to-Many con `login_logs`

---

#### Tabla: `roles`

Roles del sistema para control de acceso.

```sql
CREATE TABLE roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    es_sistema BOOLEAN DEFAULT FALSE,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_nombre (nombre),
    INDEX idx_activo (activo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Descripción de Campos**:
- `id_rol`: Identificador único del rol
- `nombre`: Nombre del rol (único)
- `es_sistema`: Indica si es un rol del sistema (no se puede eliminar)
- `activo`: Estado del rol

**Roles Predefinidos**:
- `admin`: Administrador del sistema (todos los permisos)
- `profesor`: Profesor
- `estudiante`: Estudiante
- `registrador`: Personal de registro
- `bienestar`: Personal de bienestar estudiantil

**Relaciones**:
- Many-to-Many con `usuarios` (a través de `usuario_roles`)
- Many-to-Many con `permisos` (a través de `rol_permisos`)

---

#### Tabla: `permisos`

Permisos granulares del sistema.

```sql
CREATE TABLE permisos (
    id_permiso INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    modulo VARCHAR(50),
    activo BOOLEAN DEFAULT TRUE,
    
    INDEX idx_codigo (codigo),
    INDEX idx_modulo (modulo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Descripción de Campos**:
- `id_permiso`: Identificador único del permiso
- `codigo`: Código único del permiso (ej. "crear_usuario")
- `modulo`: Módulo al que pertenece el permiso

**Ejemplos de Permisos**:
```
usuarios:
  - crear_usuario
  - listar_usuarios
  - actualizar_usuario
  - eliminar_usuario
  - asignar_rol
  - crear_rol
  - actualizar_rol
  - eliminar_rol

bitacora:
  - ver_bitacora

esquelas:
  - crear_esquela
  - actualizar_esquela
  - eliminar_esquela
  - aprobar_esquela

cursos:
  - crear_curso
  - actualizar_curso
  - eliminar_curso
```

**Relaciones**:
- Many-to-Many con `roles` (a través de `rol_permisos`)

---

#### Tabla: `usuario_roles`

Tabla de asociación entre usuarios y roles (Many-to-Many).

```sql
CREATE TABLE usuario_roles (
    usuario_id INT NOT NULL,
    rol_id INT NOT NULL,
    fecha_asignacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    asignado_por INT,
    
    PRIMARY KEY (usuario_id, rol_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (rol_id) REFERENCES roles(id_rol) ON DELETE CASCADE,
    FOREIGN KEY (asignado_por) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    
    INDEX idx_usuario (usuario_id),
    INDEX idx_rol (rol_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

#### Tabla: `rol_permisos`

Tabla de asociación entre roles y permisos (Many-to-Many).

```sql
CREATE TABLE rol_permisos (
    rol_id INT NOT NULL,
    permiso_id INT NOT NULL,
    
    PRIMARY KEY (rol_id, permiso_id),
    FOREIGN KEY (rol_id) REFERENCES roles(id_rol) ON DELETE CASCADE,
    FOREIGN KEY (permiso_id) REFERENCES permisos(id_permiso) ON DELETE CASCADE,
    
    INDEX idx_rol (rol_id),
    INDEX idx_permiso (permiso_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

### 2. Módulo de Auditoría

#### Tabla: `bitacora`

Registro de auditoría de todas las acciones importantes del sistema.

```sql
CREATE TABLE bitacora (
    id_bitacora INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    accion VARCHAR(100) NOT NULL,
    entidad_afectada VARCHAR(100),
    id_entidad INT,
    valores_anteriores JSON,
    valores_nuevos JSON,
    ip_address VARCHAR(45),
    user_agent TEXT,
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    
    INDEX idx_usuario (usuario_id),
    INDEX idx_accion (accion),
    INDEX idx_entidad (entidad_afectada, id_entidad),
    INDEX idx_fecha (fecha_hora)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Descripción de Campos**:
- `usuario_id`: Usuario que realizó la acción
- `accion`: Tipo de acción (CREATE, UPDATE, DELETE, LOGIN, etc.)
- `entidad_afectada`: Nombre de la tabla/entidad afectada
- `id_entidad`: ID del registro afectado
- `valores_anteriores`: JSON con valores antes del cambio
- `valores_nuevos`: JSON con valores después del cambio
- `ip_address`: Dirección IP del cliente
- `user_agent`: User agent del navegador

**Acciones Registradas**:
- LOGIN, LOGOUT
- CREATE_USUARIO, UPDATE_USUARIO, DELETE_USUARIO
- ASIGNAR_ROL, REMOVER_ROL
- CREATE_ESQUELA, UPDATE_ESQUELA
- CREATE_CURSO, UPDATE_CURSO
- etc.

---

#### Tabla: `login_logs`

Registro específico de intentos de login (exitosos y fallidos).

```sql
CREATE TABLE login_logs (
    id_log INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    usuario_intento VARCHAR(50),
    exito BOOLEAN NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    mensaje VARCHAR(255),
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id_usuario) ON DELETE SET NULL,
    
    INDEX idx_usuario (usuario_id),
    INDEX idx_exito (exito),
    INDEX idx_fecha (fecha_hora),
    INDEX idx_ip (ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Descripción de Campos**:
- `usuario_id`: ID del usuario (solo si login exitoso)
- `usuario_intento`: Nombre de usuario que se intentó usar
- `exito`: Indica si el login fue exitoso
- `mensaje`: Razón del fallo (ej. "Contraseña incorrecta")

---

### 3. Módulo de Esquelas

#### Tabla: `esquelas`

Registro de esquelas (reconocimientos y orientaciones).

```sql
CREATE TABLE esquelas (
    id_esquela INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    tipo ENUM('RECONOCIMIENTO', 'ORIENTACION') NOT NULL,
    estudiante_id INT NOT NULL,
    profesor_id INT,
    curso_id INT,
    codigo_esquela_id INT,
    motivo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    estado ENUM('PENDIENTE', 'REVISADA', 'APROBADA', 'RECHAZADA') DEFAULT 'PENDIENTE',
    fecha_emision DATE NOT NULL,
    fecha_revision DATE,
    revisado_por INT,
    observaciones TEXT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (estudiante_id) REFERENCES personas(id_persona),
    FOREIGN KEY (profesor_id) REFERENCES personas(id_persona),
    FOREIGN KEY (curso_id) REFERENCES cursos(id_curso),
    FOREIGN KEY (codigo_esquela_id) REFERENCES codigos_esquela(id_codigo),
    FOREIGN KEY (revisado_por) REFERENCES usuarios(id_usuario),
    
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo),
    INDEX idx_estudiante (estudiante_id),
    INDEX idx_estado (estado),
    INDEX idx_fecha_emision (fecha_emision)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Descripción de Campos**:
- `codigo`: Código único de la esquela (autogenerado)
- `tipo`: Tipo de esquela (reconocimiento u orientación)
- `estudiante_id`: Estudiante al que se refiere la esquela
- `profesor_id`: Profesor que emitió la esquela
- `codigo_esquela_id`: Referencia al código de esquela predefinido
- `estado`: Estado actual de la esquela
- `revisado_por`: Usuario que revisó/aprobó la esquela

**Estados de Esquela**:
- `PENDIENTE`: Recién creada, esperando revisión
- `REVISADA`: Revisada por el encargado
- `APROBADA`: Aprobada oficialmente
- `RECHAZADA`: Rechazada

---

#### Tabla: `codigos_esquela`

Catálogo de códigos predefinidos para esquelas.

```sql
CREATE TABLE codigos_esquela (
    id_codigo INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    descripcion VARCHAR(255) NOT NULL,
    tipo_esquela ENUM('RECONOCIMIENTO', 'ORIENTACION') NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    
    INDEX idx_codigo (codigo),
    INDEX idx_tipo (tipo_esquela)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Ejemplos**:
```
RECONOCIMIENTO:
  - REC001: Excelencia académica
  - REC002: Participación destacada
  - REC003: Mejora continua

ORIENTACION:
  - ORI001: Bajo rendimiento académico
  - ORI002: Comportamiento inadecuado
  - ORI003: Ausentismo
```

---

### 4. Módulo de Administración

#### Tabla: `cursos`

Información de cursos/clases.

```sql
CREATE TABLE cursos (
    id_curso INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    nivel ENUM('INICIAL', 'PRIMARIA', 'SECUNDARIA') NOT NULL,
    grado INT NOT NULL,
    paralelo VARCHAR(5),
    año_escolar INT NOT NULL,
    profesor_tutor_id INT,
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (profesor_tutor_id) REFERENCES personas(id_persona),
    
    UNIQUE KEY unique_curso (nivel, grado, paralelo, año_escolar),
    INDEX idx_año (año_escolar),
    INDEX idx_nivel (nivel)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

**Descripción de Campos**:
- `nombre`: Nombre del curso (ej. "1ro Primaria A")
- `nivel`: Nivel educativo
- `grado`: Grado (1-6 para primaria, 1-6 para secundaria)
- `paralelo`: Paralelo (A, B, C, etc.)
- `año_escolar`: Año escolar (ej. 2025)
- `profesor_tutor_id`: Profesor tutor del curso

---

#### Tabla: `estudiantes`

Información específica de estudiantes.

```sql
CREATE TABLE estudiantes (
    id_estudiante INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT UNIQUE NOT NULL,
    codigo_estudiante VARCHAR(20) UNIQUE,
    fecha_ingreso DATE,
    curso_actual_id INT,
    estado ENUM('ACTIVO', 'RETIRADO', 'GRADUADO', 'SUSPENDIDO') DEFAULT 'ACTIVO',
    
    FOREIGN KEY (persona_id) REFERENCES personas(id_persona) ON DELETE CASCADE,
    FOREIGN KEY (curso_actual_id) REFERENCES cursos(id_curso),
    
    INDEX idx_codigo (codigo_estudiante),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

#### Tabla: `curso_estudiante`

Historial de cursos de cada estudiante (Many-to-Many).

```sql
CREATE TABLE curso_estudiante (
    id INT AUTO_INCREMENT PRIMARY KEY,
    estudiante_id INT NOT NULL,
    curso_id INT NOT NULL,
    año_escolar INT NOT NULL,
    fecha_inscripcion DATE NOT NULL,
    fecha_retiro DATE,
    estado ENUM('INSCRITO', 'CURSANDO', 'APROBADO', 'REPROBADO', 'RETIRADO') DEFAULT 'INSCRITO',
    
    FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id_estudiante) ON DELETE CASCADE,
    FOREIGN KEY (curso_id) REFERENCES cursos(id_curso),
    
    UNIQUE KEY unique_estudiante_curso_año (estudiante_id, curso_id, año_escolar),
    INDEX idx_estudiante (estudiante_id),
    INDEX idx_curso (curso_id),
    INDEX idx_año (año_escolar)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

#### Tabla: `profesores`

Información específica de profesores.

```sql
CREATE TABLE profesores (
    id_profesor INT AUTO_INCREMENT PRIMARY KEY,
    persona_id INT UNIQUE NOT NULL,
    codigo_profesor VARCHAR(20) UNIQUE,
    especialidad VARCHAR(100),
    fecha_ingreso DATE,
    estado ENUM('ACTIVO', 'INACTIVO', 'LICENCIA') DEFAULT 'ACTIVO',
    
    FOREIGN KEY (persona_id) REFERENCES personas(id_persona) ON DELETE CASCADE,
    
    INDEX idx_codigo (codigo_profesor),
    INDEX idx_estado (estado)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## Índices y Optimizaciones

### Índices Principales

```sql
-- Búsquedas frecuentes de usuarios
CREATE INDEX idx_usuario_activo ON usuarios(usuario, activo);
CREATE INDEX idx_email_activo ON usuarios(email, activo);

-- Búsquedas de personas
CREATE INDEX idx_persona_ci_tipo ON personas(ci, tipo_persona);

-- Consultas de auditoría
CREATE INDEX idx_bitacora_fecha_usuario ON bitacora(fecha_hora, usuario_id);
CREATE INDEX idx_bitacora_entidad ON bitacora(entidad_afectada, id_entidad);

-- Búsquedas de esquelas
CREATE INDEX idx_esquela_estudiante_fecha ON esquelas(estudiante_id, fecha_emision);
CREATE INDEX idx_esquela_estado_tipo ON esquelas(estado, tipo);

-- Consultas de cursos
CREATE INDEX idx_curso_año_nivel ON cursos(año_escolar, nivel);
```

### Consideraciones de Performance

1. **Foreign Keys con Índices**: Todas las FK tienen índices automáticos
2. **Campos de Búsqueda**: CI, usuario, email, códigos tienen índices
3. **Filtros Comunes**: activo, estado, tipo tienen índices
4. **Ordenamiento**: fecha_creacion, fecha_hora tienen índices

---

## Constraints y Validaciones

### Constraints a Nivel de Base de Datos

```sql
-- Usuarios únicos
UNIQUE (usuario)
UNIQUE (email)

-- CIs únicos
UNIQUE (ci) ON personas

-- Códigos únicos
UNIQUE (codigo) ON esquelas
UNIQUE (codigo_estudiante) ON estudiantes

-- Relaciones obligatorias
NOT NULL ON usuarios.password_hash
NOT NULL ON personas.ci
NOT NULL ON esquelas.estudiante_id

-- Valores por defecto
DEFAULT TRUE ON activo
DEFAULT CURRENT_TIMESTAMP ON fecha_creacion
DEFAULT 'PENDIENTE' ON esquelas.estado
```

### Validaciones a Nivel de Aplicación

Implementadas en Pydantic DTOs:

```python
class PersonaCreateDTO(BaseModel):
    ci: str = Field(..., min_length=7, max_length=20)
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    
    @validator('ci')
    def validar_ci(cls, v):
        # Validación específica de CI boliviano
        return v
```

---

## Datos Iniciales (Seeds)

### Roles Iniciales

```sql
INSERT INTO roles (nombre, descripcion, es_sistema) VALUES
('admin', 'Administrador del sistema con todos los permisos', TRUE),
('profesor', 'Profesor de la institución', TRUE),
('estudiante', 'Estudiante de la institución', TRUE),
('registrador', 'Personal de registro y admisión', TRUE),
('bienestar', 'Personal de bienestar estudiantil', TRUE);
```

### Permisos Iniciales

```sql
-- Permisos de usuarios
INSERT INTO permisos (codigo, descripcion, modulo) VALUES
('crear_usuario', 'Crear nuevos usuarios', 'usuarios'),
('listar_usuarios', 'Ver lista de usuarios', 'usuarios'),
('actualizar_usuario', 'Modificar usuarios', 'usuarios'),
('eliminar_usuario', 'Eliminar usuarios', 'usuarios'),
('asignar_rol', 'Asignar roles a usuarios', 'usuarios'),
-- ... más permisos
```

### Asignación de Permisos a Roles

```sql
-- Admin tiene todos los permisos
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 1, id_permiso FROM permisos;

-- Profesor tiene permisos específicos
INSERT INTO rol_permisos (rol_id, permiso_id)
SELECT 2, id_permiso FROM permisos 
WHERE codigo IN ('crear_esquela', 'ver_bitacora');
```

---

## Migraciones con Alembic

### Estructura de Migraciones

```
alembic/
├── versions/
│   ├── 001_initial_schema.py
│   ├── 002_add_bitacora.py
│   ├── 003_add_esquelas.py
│   └── ...
├── env.py
└── script.py.mako
```

### Comandos Útiles

```bash
# Crear migración automática
alembic revision --autogenerate -m "Descripción del cambio"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history

# Ver SQL sin ejecutar
alembic upgrade head --sql
```

### Ejemplo de Migración

```python
"""add_esquelas_table

Revision ID: 003
Revises: 002
Create Date: 2025-11-18 01:29:16

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'esquelas',
        sa.Column('id_esquela', sa.Integer(), primary_key=True),
        sa.Column('codigo', sa.String(20), unique=True, nullable=False),
        # ... más columnas
    )

def downgrade():
    op.drop_table('esquelas')
```

---

## Backup y Recuperación

### Backup Regular

```bash
# Backup completo
mysqldump -u usuario -p brisa_db > backup_$(date +%Y%m%d).sql

# Backup solo estructura
mysqldump -u usuario -p --no-data brisa_db > schema.sql

# Backup solo datos
mysqldump -u usuario -p --no-create-info brisa_db > data.sql
```

### Restauración

```bash
# Restaurar desde backup
mysql -u usuario -p brisa_db < backup_20251118.sql
```

### Estrategia de Backup

- **Frecuencia**: Diario (automatizado)
- **Retención**: 30 días
- **Ubicación**: Servidor de backups + Cloud
- **Tipo**: Full backup diario, incremental cada hora (en producción)

---

## Consideraciones de Seguridad

### 1. Contraseñas

- **Nunca** almacenar contraseñas en texto plano
- Usar bcrypt con salt automático
- Mínimo 12 rounds para hashing

### 2. SQL Injection

- **Siempre** usar ORM (SQLAlchemy)
- **Nunca** concatenar SQL raw
- Parametrizar todas las queries

### 3. Datos Sensibles

- Encriptar en reposo (campo nivel BD)
- Logs no deben contener contraseñas
- Auditar acceso a datos sensibles

### 4. Privilegios de Usuario BD

```sql
-- Usuario de aplicación (limitado)
GRANT SELECT, INSERT, UPDATE, DELETE 
ON brisa_db.* 
TO 'app_user'@'localhost';

-- Usuario de migraciones
GRANT ALL PRIVILEGES 
ON brisa_db.* 
TO 'migration_user'@'localhost';

-- Usuario de solo lectura (reportes)
GRANT SELECT 
ON brisa_db.* 
TO 'readonly_user'@'localhost';
```

---

## Monitoreo y Mantenimiento

### Queries de Monitoreo

```sql
-- Tamaño de tablas
SELECT 
    table_name,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS "Size (MB)"
FROM information_schema.TABLES 
WHERE table_schema = "brisa_db"
ORDER BY (data_length + index_length) DESC;

-- Conteo de registros
SELECT 
    table_name, 
    table_rows 
FROM information_schema.TABLES 
WHERE table_schema = 'brisa_db';

-- Índices no usados
SELECT * FROM sys.schema_unused_indexes 
WHERE object_schema = 'brisa_db';
```

### Mantenimiento Regular

```sql
-- Optimizar tablas
OPTIMIZE TABLE usuarios, personas, bitacora;

-- Analizar tablas (actualizar estadísticas)
ANALYZE TABLE usuarios, personas;

-- Verificar integridad
CHECK TABLE usuarios, personas;
```

---

## Diagrama ER Detallado

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SISTEMA BRISA - ER DIAGRAM                   │
└─────────────────────────────────────────────────────────────────────┘

personas (1) ──────────────────── (1) usuarios
    │                                   │
    │                                   │
    │ (1)                               │ (M)
    │                                   │
    ├── (M) estudiantes                 └── (M) usuario_roles ── (M) roles
    │                                                                  │
    │ (1)                                                              │
    │                                                                  │
    ├── (M) profesores                                     rol_permisos (M)
    │                                                                  │
    │                                                                  │
    │                                                              permisos
    │
    │
    └── (M) esquelas ──── (M) codigos_esquela
            │
            │
            └── (M) cursos
                    │
                    │
                    └── (M) curso_estudiante

usuarios (1) ──── (M) bitacora
usuarios (1) ──── (M) login_logs
```

---

## Convenciones de Nomenclatura

### Tablas

- Plural en español: `usuarios`, `personas`, `roles`
- Snake_case para nombres compuestos: `usuario_roles`
- Prefijo por módulo si es necesario

### Columnas

- Snake_case: `id_usuario`, `fecha_creacion`
- Sufijos:
  - `_id` para foreign keys: `persona_id`
  - `_hash` para valores hasheados: `password_hash`
  - `_at` o `fecha_` para timestamps: `created_at`, `fecha_creacion`

### Índices

- Prefijo `idx_`: `idx_usuario`, `idx_email`
- Descriptivo del campo: `idx_usuario_activo`

### Constraints

- FK: `fk_tabla_campo`
- Unique: `unique_tabla_campo`
- Check: `chk_tabla_condicion`

---

## Conclusión

Esta estructura de base de datos proporciona:

✅ **Integridad Referencial**: Foreign keys y constraints apropiados
✅ **Performance**: Índices en campos de búsqueda frecuente
✅ **Auditoría Completa**: Registro de todas las acciones importantes
✅ **Escalabilidad**: Diseño preparado para crecer
✅ **Seguridad**: Separación de permisos, hashing de contraseñas
✅ **Mantenibilidad**: Migraciones con Alembic, nomenclatura clara

La base de datos está diseñada siguiendo mejores prácticas de normalización, performance y seguridad.
