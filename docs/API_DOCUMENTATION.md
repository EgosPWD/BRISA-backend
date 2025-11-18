# Documentación API - BRISA Backend

## Información General

- **Título**: API Bienestar Estudiantil
- **Versión**: 1.0.0
- **Framework**: FastAPI
- **Base URL**: `http://localhost:8000`
- **Documentación Interactiva**: `http://localhost:8000/docs`
- **Documentación Alternativa**: `http://localhost:8000/redoc`

## Arquitectura

El sistema BRISA Backend utiliza una arquitectura modular basada en el patrón MVC (Model-View-Controller) adaptado para FastAPI:

```
├── Controllers: Controladores HTTP (routers FastAPI)
├── Services: Lógica de negocio
├── Repositories: Acceso a datos
├── DTOs: Esquemas de validación (Pydantic)
└── Models: Modelos de base de datos (SQLAlchemy)
```

## Autenticación

El sistema utiliza autenticación basada en JWT (JSON Web Tokens).

### Flujo de Autenticación

1. El usuario envía credenciales al endpoint `/api/auth/login`
2. El servidor valida las credenciales y genera un token JWT
3. El token se incluye en las peticiones subsiguientes mediante el header `Authorization: Bearer {token}`
4. El servidor valida el token en cada petición protegida

### Headers Requeridos

Para endpoints protegidos, incluir:

```http
Authorization: Bearer {access_token}
Content-Type: application/json
```

## Módulos del Sistema

### 1. Autenticación (`/api/auth`)

**Descripción**: Gestión de autenticación, login, registro y tokens.

#### Endpoints Principales

##### POST `/api/auth/register`
- **Descripción**: Registrar nuevo usuario
- **Autenticación**: No requerida
- **Body**:
```json
{
  "usuario": "string",
  "password": "string",
  "email": "string",
  "persona_id": "integer"
}
```
- **Respuesta Exitosa** (201):
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "data": {
    "id_usuario": 1,
    "usuario": "string",
    "email": "string"
  }
}
```

##### POST `/api/auth/login`
- **Descripción**: Iniciar sesión
- **Autenticación**: No requerida
- **Body**:
```json
{
  "usuario": "string",
  "password": "string"
}
```
- **Respuesta Exitosa** (200):
```json
{
  "success": true,
  "message": "Login exitoso",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "usuario": {
      "id_usuario": 1,
      "usuario": "string",
      "email": "string",
      "roles": ["admin"]
    }
  }
}
```

##### GET `/api/auth/me`
- **Descripción**: Obtener información del usuario actual
- **Autenticación**: Requerida
- **Headers**: `Authorization: Bearer {token}`
- **Respuesta Exitosa** (200):
```json
{
  "success": true,
  "data": {
    "id_usuario": 1,
    "usuario": "string",
    "email": "string",
    "persona": {
      "id_persona": 1,
      "nombre": "string",
      "apellido": "string"
    },
    "roles": ["admin"]
  }
}
```

##### POST `/api/auth/change-password`
- **Descripción**: Cambiar contraseña del usuario actual
- **Autenticación**: Requerida
- **Body**:
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

---

### 2. Usuarios (`/api/usuarios`)

**Descripción**: Gestión completa de usuarios, roles y permisos del sistema.

#### Endpoints de Usuarios

##### POST `/api/usuarios`
- **Descripción**: Crear nuevo usuario
- **Autenticación**: Requerida
- **Permisos**: `crear_usuario`
- **Body**:
```json
{
  "usuario": "string",
  "password": "string",
  "email": "string",
  "persona_id": "integer",
  "activo": true
}
```

##### GET `/api/usuarios/{id_usuario}`
- **Descripción**: Obtener detalles de un usuario específico
- **Autenticación**: Requerida
- **Parámetros**: 
  - `id_usuario` (path): ID del usuario
- **Respuesta**:
```json
{
  "success": true,
  "data": {
    "id_usuario": 1,
    "usuario": "string",
    "email": "string",
    "activo": true,
    "persona": {...},
    "roles": [...]
  }
}
```

##### GET `/api/usuarios`
- **Descripción**: Listar todos los usuarios con paginación
- **Autenticación**: Requerida
- **Permisos**: `listar_usuarios`
- **Query Parameters**:
  - `skip` (opcional): Número de registros a omitir (default: 0)
  - `limit` (opcional): Número máximo de registros (default: 100)
  - `activo` (opcional): Filtrar por estado activo (boolean)
- **Respuesta**:
```json
{
  "success": true,
  "data": [
    {
      "id_usuario": 1,
      "usuario": "string",
      "email": "string"
    }
  ],
  "total": 10
}
```

##### PUT `/api/usuarios/{id_usuario}`
- **Descripción**: Actualizar datos de un usuario
- **Autenticación**: Requerida
- **Permisos**: `actualizar_usuario`
- **Body**:
```json
{
  "email": "string",
  "activo": true
}
```

##### DELETE `/api/usuarios/{id_usuario}`
- **Descripción**: Eliminar (desactivar) un usuario
- **Autenticación**: Requerida
- **Permisos**: `eliminar_usuario`

#### Endpoints de Roles

##### POST `/api/usuarios/roles`
- **Descripción**: Crear nuevo rol
- **Autenticación**: Requerida
- **Permisos**: `crear_rol`
- **Body**:
```json
{
  "nombre": "string",
  "descripcion": "string"
}
```

##### GET `/api/usuarios/roles`
- **Descripción**: Listar todos los roles
- **Autenticación**: Requerida
- **Respuesta**:
```json
{
  "success": true,
  "data": [
    {
      "id_rol": 1,
      "nombre": "admin",
      "descripcion": "Administrador del sistema"
    }
  ]
}
```

##### PUT `/api/usuarios/roles/{id_rol}`
- **Descripción**: Actualizar un rol
- **Autenticación**: Requerida
- **Permisos**: `actualizar_rol`

##### DELETE `/api/usuarios/roles/{id_rol}`
- **Descripción**: Eliminar un rol
- **Autenticación**: Requerida
- **Permisos**: `eliminar_rol`

#### Endpoints de Permisos

##### GET `/api/usuarios/permisos`
- **Descripción**: Listar todos los permisos disponibles
- **Autenticación**: Requerida
- **Respuesta**:
```json
{
  "success": true,
  "data": [
    {
      "id_permiso": 1,
      "codigo": "crear_usuario",
      "descripcion": "Crear nuevos usuarios"
    }
  ]
}
```

##### POST `/api/usuarios/asignar-rol`
- **Descripción**: Asignar rol a un usuario
- **Autenticación**: Requerida
- **Permisos**: `asignar_rol`
- **Body**:
```json
{
  "usuario_id": 1,
  "rol_id": 2
}
```

---

### 3. Bitácora / Auditoría (`/api/bitacora`)

**Descripción**: Registro de auditoría de todas las acciones realizadas en el sistema.

##### GET `/api/bitacora`
- **Descripción**: Listar registros de auditoría
- **Autenticación**: Requerida
- **Permisos**: `ver_bitacora`
- **Query Parameters**:
  - `skip`: Paginación
  - `limit`: Límite de registros
  - `usuario_id`: Filtrar por usuario
  - `accion`: Filtrar por tipo de acción
  - `fecha_inicio`: Fecha inicial (ISO 8601)
  - `fecha_fin`: Fecha final (ISO 8601)
- **Respuesta**:
```json
{
  "success": true,
  "data": [
    {
      "id_bitacora": 1,
      "usuario_id": 1,
      "accion": "LOGIN",
      "detalle": "Inicio de sesión exitoso",
      "fecha": "2025-11-18T01:29:16Z",
      "ip_address": "192.168.1.1"
    }
  ]
}
```

##### GET `/api/bitacora/{id_bitacora}`
- **Descripción**: Obtener detalles de un registro de auditoría
- **Autenticación**: Requerida
- **Permisos**: `ver_bitacora`

---

### 4. Esquelas (`/api/esquelas`)

**Descripción**: Gestión de esquelas (reconocimientos y orientaciones).

##### POST `/api/esquelas`
- **Descripción**: Crear nueva esquela
- **Autenticación**: Requerida
- **Permisos**: `crear_esquela`
- **Body**:
```json
{
  "tipo": "RECONOCIMIENTO",
  "estudiante_id": 1,
  "profesor_id": 2,
  "motivo": "string",
  "descripcion": "string",
  "fecha": "2025-11-18"
}
```

##### GET `/api/esquelas`
- **Descripción**: Listar esquelas
- **Autenticación**: Requerida
- **Query Parameters**:
  - `skip`, `limit`: Paginación
  - `tipo`: Filtrar por tipo (RECONOCIMIENTO, ORIENTACION)
  - `estudiante_id`: Filtrar por estudiante
  - `estado`: Filtrar por estado

##### GET `/api/esquelas/{id_esquela}`
- **Descripción**: Obtener detalles de una esquela
- **Autenticación**: Requerida

##### PUT `/api/esquelas/{id_esquela}`
- **Descripción**: Actualizar una esquela
- **Autenticación**: Requerida
- **Permisos**: `actualizar_esquela`

---

### 5. Administración (`/api/admin`)

**Descripción**: Gestión administrativa de cursos, estudiantes y personas.

#### Cursos

##### POST `/api/cursos`
- **Descripción**: Crear nuevo curso
- **Autenticación**: Requerida
- **Permisos**: `crear_curso`
- **Body**:
```json
{
  "nombre": "1ro Primaria A",
  "nivel": "PRIMARIA",
  "grado": 1,
  "paralelo": "A",
  "año_escolar": 2025
}
```

##### GET `/api/cursos`
- **Descripción**: Listar cursos
- **Autenticación**: Requerida

##### GET `/api/cursos/{id_curso}`
- **Descripción**: Obtener detalles de un curso
- **Autenticación**: Requerida

#### Estudiantes

##### GET `/api/estudiantes`
- **Descripción**: Listar estudiantes registrados
- **Autenticación**: Requerida
- **Query Parameters**:
  - `skip`, `limit`: Paginación
  - `curso_id`: Filtrar por curso
  - `activo`: Filtrar por estado

##### GET `/api/estudiantes/{id_estudiante}`
- **Descripción**: Obtener detalles de un estudiante
- **Autenticación**: Requerida

#### Personas

##### POST `/api/personas/estudiantes`
- **Descripción**: Crear nueva persona con rol de estudiante
- **Autenticación**: Requerida
- **Permisos**: `crear_persona`

##### POST `/api/personas/profesores`
- **Descripción**: Crear nueva persona con rol de profesor
- **Autenticación**: Requerida
- **Permisos**: `crear_persona`

##### POST `/api/personas/registradores`
- **Descripción**: Crear nueva persona con rol de registrador
- **Autenticación**: Requerida
- **Permisos**: `crear_persona`

---

## Códigos de Estado HTTP

### Exitosos (2xx)

- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `204 No Content`: Solicitud exitosa sin contenido de respuesta

### Errores del Cliente (4xx)

- `400 Bad Request`: Datos de entrada inválidos
- `401 Unauthorized`: Autenticación requerida o token inválido
- `403 Forbidden`: No tiene permisos suficientes
- `404 Not Found`: Recurso no encontrado
- `409 Conflict`: Conflicto con el estado actual (ej. duplicado)
- `422 Unprocessable Entity`: Error de validación de datos

### Errores del Servidor (5xx)

- `500 Internal Server Error`: Error interno del servidor
- `503 Service Unavailable`: Servicio no disponible temporalmente

---

## Formato de Respuestas

### Respuesta Exitosa

```json
{
  "success": true,
  "message": "Operación exitosa",
  "data": {
    // Datos de respuesta
  }
}
```

### Respuesta de Error

```json
{
  "success": false,
  "message": "Descripción del error",
  "error": "Detalles técnicos del error",
  "status_code": 400
}
```

### Respuesta con Paginación

```json
{
  "success": true,
  "data": [...],
  "total": 100,
  "skip": 0,
  "limit": 10,
  "has_more": true
}
```

---

## Manejo de Errores

### Errores de Validación

Cuando los datos de entrada no cumplen con las validaciones de Pydantic:

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### Errores de Autenticación

```json
{
  "detail": "Could not validate credentials",
  "status_code": 401
}
```

### Errores de Permisos

```json
{
  "detail": "No tiene permisos suficientes para realizar esta acción",
  "status_code": 403
}
```

---

## Ejemplos de Uso

### Flujo Completo de Autenticación

#### 1. Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "admin",
    "password": "password123"
  }'
```

#### 2. Usar Token
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Crear Usuario con Rol

#### 1. Crear Usuario
```bash
curl -X POST http://localhost:8000/api/usuarios \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": "nuevo_usuario",
    "password": "pass123",
    "email": "usuario@example.com",
    "persona_id": 1
  }'
```

#### 2. Asignar Rol
```bash
curl -X POST http://localhost:8000/api/usuarios/asignar-rol \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "usuario_id": 5,
    "rol_id": 2
  }'
```

---

## Sistema de Permisos

El sistema utiliza permisos granulares para controlar el acceso a diferentes funcionalidades:

### Permisos de Usuarios
- `crear_usuario`: Crear nuevos usuarios
- `listar_usuarios`: Ver lista de usuarios
- `actualizar_usuario`: Modificar usuarios
- `eliminar_usuario`: Desactivar usuarios

### Permisos de Roles
- `crear_rol`: Crear nuevos roles
- `actualizar_rol`: Modificar roles
- `eliminar_rol`: Eliminar roles
- `asignar_rol`: Asignar roles a usuarios

### Permisos de Bitácora
- `ver_bitacora`: Ver registros de auditoría

### Permisos de Esquelas
- `crear_esquela`: Crear esquelas
- `actualizar_esquela`: Modificar esquelas
- `eliminar_esquela`: Eliminar esquelas

### Permisos de Administración
- `crear_curso`: Crear cursos
- `actualizar_curso`: Modificar cursos
- `crear_persona`: Crear personas (estudiantes, profesores, etc.)

---

## Límites y Restricciones

- **Tamaño máximo de request**: 10 MB
- **Rate limiting**: 100 requests por minuto por IP (en producción)
- **Longitud máxima de campos de texto**: 
  - Texto corto: 255 caracteres
  - Texto largo: 5000 caracteres
- **Límite de paginación**: Máximo 100 registros por página
- **Tiempo de expiración de token**: 60 minutos (configurable)

---

## Versionado de API

Actualmente la API está en versión `1.0.0`. 

Futuras versiones se manejarán mediante:
- URL: `/api/v2/...`
- Header: `API-Version: 2.0`

---

## Soporte y Contacto

Para preguntas o problemas con la API:

- **Repositorio**: https://github.com/EgosPWD/BRISA-backend
- **Documentación adicional**: `/docs` folder en el repositorio
- **Swagger UI**: http://localhost:8000/docs

---

## Changelog

### v1.0.0 (2025-11-18)
- Implementación inicial de módulos de autenticación, usuarios, bitácora, esquelas y administración
- Sistema de permisos granulares
- Autenticación JWT
- Documentación API completa
