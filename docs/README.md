# Documentación BRISA Backend

Bienvenido a la documentación completa del sistema BRISA Backend - API REST para gestión institucional de la Universidad Católica Boliviana.

## 📚 Tabla de Contenidos

### 🚀 Inicio Rápido

1. **[README Principal](../README.md)** - Visión general del proyecto y configuración rápida
2. **[Guía de Equipos](GUIA_EQUIPOS.md)** - Guía para trabajo colaborativo en equipo

### 📖 Documentación Técnica

#### Para Usuarios de la API

- **[Documentación de API](API_DOCUMENTATION.md)** - Referencia completa de todos los endpoints
  - Autenticación y autorización
  - Endpoints de usuarios, roles y permisos
  - Bitácora y auditoría
  - Esquelas y reconocimientos
  - Administración de cursos y estudiantes
  - Ejemplos de uso y códigos de respuesta

#### Para Desarrolladores

- **[Guía de Desarrollo](GUIA_DESARROLLADOR.md)** - Guía completa para desarrolladores
  - Configuración del entorno de desarrollo
  - Estructura de un módulo
  - Ejemplos de código completos (Models, DTOs, Services, Controllers)
  - Mejores prácticas
  - Testing y debugging
  - Troubleshooting

- **[Arquitectura del Sistema](ARQUITECTURA.md)** - Diseño y arquitectura técnica
  - Arquitectura de capas
  - Patrones de diseño implementados
  - Estructura de módulos
  - Flujos de datos
  - Seguridad y permisos
  - Escalabilidad

- **[Base de Datos](DATABASE.md)** - Documentación de base de datos
  - Diagrama entidad-relación
  - Descripción detallada de tablas
  - Índices y optimizaciones
  - Migraciones con Alembic
  - Backup y recuperación

#### Para DevOps

- **[Despliegue y Configuración](DEPLOYMENT.md)** - Guía de despliegue
  - Configuración de desarrollo
  - Configuración de producción
  - Despliegue con Docker
  - Despliegue en servidor Linux
  - Variables de entorno
  - Seguridad
  - Monitoreo y logs
  - Backup y recuperación

---

## 🎯 Accesos Rápidos

### Documentación Interactiva

Cuando el servidor está en ejecución, puedes acceder a la documentación interactiva automática de FastAPI:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Estructura del Proyecto

```
BRISA-backend/
├── app/                          # Código fuente de la aplicación
│   ├── main.py                   # Punto de entrada
│   ├── config/                   # Configuraciones
│   ├── core/                     # Funcionalidad central (DB, utils)
│   ├── shared/                   # Componentes compartidos
│   │   ├── models/              # Modelos base
│   │   ├── services/            # Servicios base
│   │   ├── exceptions/          # Excepciones personalizadas
│   │   ├── decorators/          # Decoradores (auth, permisos)
│   │   └── security.py          # Funciones de seguridad
│   └── modules/                  # Módulos funcionales
│       ├── auth/                # Autenticación
│       ├── usuarios/            # Usuarios, roles, permisos
│       ├── bitacora/            # Auditoría
│       ├── esquelas/            # Esquelas
│       ├── administracion/      # Cursos, estudiantes
│       └── ...                  # Otros módulos
├── tests/                        # Tests
├── docs/                         # Documentación (estás aquí)
├── alembic/                      # Migraciones de BD
├── scripts/                      # Scripts de utilidad
├── requirements.txt              # Dependencias Python
└── .env.example                  # Plantilla de variables de entorno
```

---

## 🔑 Conceptos Clave

### Arquitectura en Capas

El sistema utiliza una arquitectura limpia dividida en 4 capas:

1. **Controllers** (Presentación) - Endpoints HTTP con FastAPI
2. **Services** (Lógica de Negocio) - Reglas de negocio y validaciones
3. **Repositories** (Acceso a Datos) - Consultas a base de datos
4. **Models** (Persistencia) - Definición de tablas con SQLAlchemy

### Flujo de una Petición

```
Cliente → Controller → Service → Repository → Database
        ← Response  ← DTO     ← Model     ← Query Result
```

### Sistema de Permisos

**Modelo RBAC** (Role-Based Access Control):
- Usuarios tienen uno o más **Roles**
- Roles tienen uno o más **Permisos**
- Endpoints protegidos requieren permisos específicos

---

## 📋 Guías Específicas por Perfil

### Soy un Desarrollador Nuevo

**Empezar aquí**:
1. Leer [README principal](../README.md) para entender el proyecto
2. Seguir [Guía de Desarrollo](GUIA_DESARROLLADOR.md) para configurar el entorno
3. Revisar [Arquitectura](ARQUITECTURA.md) para entender la estructura
4. Ver [Ejemplos de Código](GUIA_DESARROLLADOR.md#ejemplos-de-código) para aprender patrones

### Soy un Desarrollador Frontend

**Enfocarte en**:
1. [Documentación de API](API_DOCUMENTATION.md) - Todos los endpoints disponibles
2. Documentación interactiva Swagger UI (http://localhost:8000/docs)
3. Sección de autenticación y manejo de tokens JWT

### Soy un DevOps / SysAdmin

**Enfocarte en**:
1. [Guía de Despliegue](DEPLOYMENT.md) - Configuración de servidores
2. [Base de Datos](DATABASE.md) - Schema y migraciones
3. Variables de entorno y seguridad

### Soy un Arquitecto / Tech Lead

**Revisar**:
1. [Arquitectura del Sistema](ARQUITECTURA.md) - Diseño y patrones
2. [Base de Datos](DATABASE.md) - Modelo de datos
3. Escalabilidad y consideraciones de performance

---

## 🛠️ Tecnologías Utilizadas

### Backend

- **Framework**: FastAPI 0.x
- **Lenguaje**: Python 3.12+
- **ORM**: SQLAlchemy
- **Validación**: Pydantic
- **Migraciones**: Alembic
- **Testing**: Pytest

### Base de Datos

- **Motor**: MySQL 8.0+
- **Charset**: utf8mb4
- **Engine**: InnoDB (transaccional)

### Seguridad

- **Autenticación**: JWT (JSON Web Tokens)
- **Hashing**: bcrypt
- **CORS**: Configurado con FastAPI middleware

### Deployment

- **ASGI Server**: Uvicorn
- **Process Manager**: Supervisor
- **Reverse Proxy**: Nginx
- **SSL**: Let's Encrypt (Certbot)
- **Containerización**: Docker (opcional)

---

## 🔐 Seguridad

### Autenticación

El sistema utiliza **JWT (JSON Web Tokens)** para autenticación:

```http
POST /api/auth/login
Content-Type: application/json

{
  "usuario": "username",
  "password": "password"
}
```

Respuesta incluye un `access_token` que debe incluirse en peticiones protegidas:

```http
Authorization: Bearer {access_token}
```

### Permisos

Endpoints protegidos requieren permisos específicos. Ejemplos:

- `crear_usuario` - Crear nuevos usuarios
- `actualizar_rol` - Modificar roles
- `ver_bitacora` - Acceder a registros de auditoría

---

## 📊 Diagramas

### Diagrama de Arquitectura

```
┌─────────────────┐
│   Frontend      │
│  (React/Vue)    │
└────────┬────────┘
         │ HTTP/JSON
         ↓
┌─────────────────┐
│  API Gateway    │
│    (Nginx)      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  FastAPI App    │
│  (Controllers)  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Services      │
│ (Business Logic)│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Repositories   │
│ (Data Access)   │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  MySQL Database │
└─────────────────┘
```

### Flujo de Autenticación

```
Usuario → Login → Validar Credenciales → Generar JWT → Retornar Token
                                                             ↓
Cliente guarda token ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ← ┘
                                                             
                                                             ↓
Cliente envía request con token → Validar token → Autorizar → Ejecutar
```

---

## 🧪 Testing

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=app

# Tests específicos
pytest tests/unit/test_services/

# Verbose
pytest -v -s
```

### Estructura de Tests

```
tests/
├── unit/              # Tests unitarios
│   ├── test_services/
│   └── test_repositories/
└── integration/       # Tests de integración
    └── test_api/
```

---

## 📝 Convenciones de Código

### Nomenclatura

- **Archivos**: `snake_case.py`
- **Clases**: `PascalCase`
- **Funciones/Variables**: `snake_case`
- **Constantes**: `UPPER_SNAKE_CASE`

### Estructura de Archivos

```python
"""
Docstring del módulo
"""
# Imports estándar
import os
from typing import List

# Imports de terceros
from fastapi import FastAPI
from sqlalchemy import Column

# Imports locales
from app.core.database import Base

# Código
```

### Docstrings

```python
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
        ValidationException: Si los datos son inválidos
    """
    pass
```

---

## 🤝 Contribución

### Proceso de Desarrollo

1. **Crear feature branch**: `git checkout -b feature/nombre-funcionalidad`
2. **Desarrollar** siguiendo las convenciones del proyecto
3. **Escribir tests** para nueva funcionalidad
4. **Commit** con mensajes descriptivos
5. **Push** a GitHub: `git push origin feature/nombre-funcionalidad`
6. **Crear Pull Request** hacia `develop`
7. **Code Review** por el equipo
8. **Merge** tras aprobación

### Convenciones de Commits

```
tipo(scope): descripción

feat(usuarios): implementar endpoint de login
fix(esquelas): corregir validación de fecha
docs(readme): actualizar guía de instalación
test(auth): añadir tests de autenticación
refactor(services): optimizar consultas a BD
```

---

## 🐛 Troubleshooting

### Problemas Comunes

#### No se puede conectar a la base de datos

```bash
# Verificar que MySQL esté corriendo
sudo systemctl status mysql

# Verificar credenciales en .env
cat .env | grep DATABASE_URL
```

#### Import errors

```bash
# Verificar entorno virtual activado
which python

# Reinstalar dependencias
pip install -r requirements.txt
```

#### Token JWT inválido

- Verificar que SECRET_KEY sea la misma en `.env`
- Regenerar token con `/api/auth/login`
- Verificar que el token no haya expirado

Para más detalles, ver [Troubleshooting en Guía de Desarrollo](GUIA_DESARROLLADOR.md#troubleshooting).

---

## 📞 Soporte

### Recursos

- **Repositorio**: https://github.com/EgosPWD/BRISA-backend
- **Issues**: https://github.com/EgosPWD/BRISA-backend/issues
- **Documentación API Interactiva**: http://localhost:8000/docs

### Contacto

Para preguntas sobre el proyecto:
- Crear un **Issue** en GitHub
- Contactar al equipo de desarrollo

---

## 📄 Licencia

Este proyecto es propiedad de la Universidad Católica Boliviana y está destinado únicamente para uso académico e institucional.

---

## 🗺️ Roadmap

### Versión Actual: 1.0.0

- ✅ Sistema de autenticación JWT
- ✅ Gestión de usuarios, roles y permisos
- ✅ Auditoría completa (bitácora)
- ✅ Gestión de esquelas
- ✅ Administración de cursos y estudiantes

### Próximas Versiones

- 🔜 **v1.1.0**: Módulo de incidentes completo
- 🔜 **v1.2.0**: Módulo de retiros tempranos
- 🔜 **v2.0.0**: Sistema de notificaciones
- 🔜 **v2.1.0**: Reportes avanzados y analytics
- 🔜 **v3.0.0**: API GraphQL

---

## 📚 Recursos Adicionales

### Documentación de Tecnologías

- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://docs.sqlalchemy.org/)
- [Pydantic](https://docs.pydantic.dev/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [MySQL](https://dev.mysql.com/doc/)

### Tutoriales y Guías

- [FastAPI Tutorial](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [Pydantic Models](https://docs.pydantic.dev/usage/models/)

---

## 📑 Historial de Cambios

### v1.0.0 (2025-11-18)

- 🎉 Lanzamiento inicial
- ✨ Sistema completo de autenticación y autorización
- ✨ Módulos de usuarios, bitácora, esquelas, administración
- 📝 Documentación completa generada

---

**Última actualización**: 2025-11-18
**Versión de la documentación**: 1.0.0
