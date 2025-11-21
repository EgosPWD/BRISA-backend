# Guía de Despliegue y Configuración - BRISA Backend

## Tabla de Contenidos

1. [Configuración de Desarrollo](#configuración-de-desarrollo)
2. [Configuración de Producción](#configuración-de-producción)
3. [Despliegue con Docker](#despliegue-con-docker)
4. [Despliegue en Servidor Linux](#despliegue-en-servidor-linux)
5. [Variables de Entorno](#variables-de-entorno)
6. [Seguridad](#seguridad)
7. [Monitoreo y Logs](#monitoreo-y-logs)
8. [Backup y Recuperación](#backup-y-recuperación)

---

## Configuración de Desarrollo

### Requisitos

- Python 3.12+
- MySQL 8.0+
- Git

### Instalación Local

```bash
# 1. Clonar repositorio
git clone https://github.com/EgosPWD/BRISA-backend.git
cd BRISA-backend

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.\.venv\Scripts\Activate  # Windows

# 3. Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# 5. Crear base de datos
mysql -u root -p << EOF
CREATE DATABASE brisa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'brisa_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON brisa_db.* TO 'brisa_user'@'localhost';
FLUSH PRIVILEGES;
EOF

# 6. Ejecutar migraciones
alembic upgrade head

# 7. (Opcional) Poblar datos iniciales
python scripts/seed_db.py

# 8. Ejecutar aplicación
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Archivo `.env` para Desarrollo

```env
# Ambiente
ENV=development

# Base de Datos
DATABASE_URL=mysql+pymysql://brisa_user:password@localhost:3306/brisa_db

# Seguridad
SECRET_KEY=dev-secret-key-change-in-production-!!!
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS (permitir frontend local)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080

# API
API_TITLE=API Bienestar Estudiantil - DEV
API_VERSION=1.0.0

# Logging
LOG_LEVEL=DEBUG
```

---

## Configuración de Producción

### Requisitos del Servidor

- **Sistema Operativo**: Ubuntu 20.04 LTS o superior (recomendado)
- **RAM**: Mínimo 2GB, recomendado 4GB+
- **CPU**: 2 cores mínimo
- **Disco**: 20GB mínimo
- **Python**: 3.12+
- **MySQL**: 8.0+
- **Nginx**: Latest (como reverse proxy)

### Instalación en Servidor de Producción

#### 1. Preparar el Servidor

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
sudo apt install -y python3.12 python3.12-venv python3-pip
sudo apt install -y mysql-server
sudo apt install -y nginx
sudo apt install -y git
sudo apt install -y supervisor  # Para gestión de procesos
```

#### 2. Configurar MySQL

```bash
# Ejecutar instalación segura de MySQL
sudo mysql_secure_installation

# Crear base de datos y usuario
sudo mysql << EOF
CREATE DATABASE brisa_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'brisa_prod'@'localhost' IDENTIFIED BY 'SUPER_SECURE_PASSWORD_HERE';
GRANT ALL PRIVILEGES ON brisa_db.* TO 'brisa_prod'@'localhost';
FLUSH PRIVILEGES;
EOF
```

#### 3. Configurar la Aplicación

```bash
# Crear usuario del sistema para la aplicación
sudo useradd -m -s /bin/bash brisa
sudo su - brisa

# Clonar repositorio
cd /home/brisa
git clone https://github.com/EgosPWD/BRISA-backend.git
cd BRISA-backend

# Crear entorno virtual
python3.12 -m venv .venv
source .venv/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt

# Crear archivo de configuración de producción
nano .env.production
```

**Contenido de `.env.production`**:

```env
# Ambiente
ENV=production

# Base de Datos
DATABASE_URL=mysql+pymysql://brisa_prod:SUPER_SECURE_PASSWORD_HERE@localhost:3306/brisa_db

# Seguridad - ¡CAMBIAR ESTOS VALORES!
SECRET_KEY=GENERAR_CLAVE_SECRETA_FUERTE_AQUI_!!!
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60

# CORS (dominios de producción)
CORS_ORIGINS=https://brisa.example.com,https://www.brisa.example.com

# API
API_TITLE=API Bienestar Estudiantil
API_VERSION=1.0.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/brisa/app.log

# Workers de Uvicorn
WORKERS=4
```

#### 4. Generar SECRET_KEY Segura

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copiar el resultado y usarlo como SECRET_KEY en `.env.production`.

#### 5. Ejecutar Migraciones

```bash
# Como usuario brisa
cd /home/brisa/BRISA-backend
source .venv/bin/activate
alembic upgrade head
```

#### 6. Configurar Supervisor (Gestor de Procesos)

```bash
# Salir del usuario brisa
exit

# Crear configuración de supervisor
sudo nano /etc/supervisor/conf.d/brisa.conf
```

**Contenido de `/etc/supervisor/conf.d/brisa.conf`**:

```ini
[program:brisa-api]
command=/home/brisa/BRISA-backend/.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4
directory=/home/brisa/BRISA-backend
user=brisa
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/brisa/error.log
stdout_logfile=/var/log/brisa/access.log
environment=ENV="production"
```

```bash
# Crear directorio de logs
sudo mkdir -p /var/log/brisa
sudo chown brisa:brisa /var/log/brisa

# Recargar supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start brisa-api

# Verificar estado
sudo supervisorctl status brisa-api
```

#### 7. Configurar Nginx como Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/brisa
```

**Contenido de `/etc/nginx/sites-available/brisa`**:

```nginx
server {
    listen 80;
    server_name api.brisa.example.com;

    # Redirigir HTTP a HTTPS (después de configurar SSL)
    # return 301 https://$server_name$request_uri;

    # Logs
    access_log /var/log/nginx/brisa-access.log;
    error_log /var/log/nginx/brisa-error.log;

    # Tamaño máximo de request
    client_max_body_size 10M;

    # Proxy a la aplicación FastAPI
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (si es necesario)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Servir archivos estáticos directamente (si los hay)
    location /static/ {
        alias /home/brisa/BRISA-backend/static/;
        expires 30d;
    }
}
```

```bash
# Habilitar el sitio
sudo ln -s /etc/nginx/sites-available/brisa /etc/nginx/sites-enabled/

# Probar configuración
sudo nginx -t

# Recargar Nginx
sudo systemctl reload nginx
```

#### 8. Configurar SSL con Let's Encrypt (HTTPS)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtener certificado SSL (cambiar el dominio)
sudo certbot --nginx -d api.brisa.example.com

# Renovación automática ya está configurada con un cron job
# Verificar:
sudo certbot renew --dry-run
```

Certbot modificará automáticamente la configuración de Nginx para usar HTTPS.

#### 9. Configurar Firewall

```bash
# Habilitar UFW
sudo ufw enable

# Permitir SSH
sudo ufw allow 22/tcp

# Permitir HTTP y HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Verificar estado
sudo ufw status
```

---

## Despliegue con Docker

### Dockerfile

**Archivo**: `Dockerfile`

```dockerfile
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

**Archivo**: `docker-compose.yml`

```yaml
version: '3.8'

services:
  # Servicio de MySQL
  db:
    image: mysql:8.0
    container_name: brisa-db
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: brisa_db
      MYSQL_USER: brisa_user
      MYSQL_PASSWORD: brisa_password
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    networks:
      - brisa-network
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

  # Servicio de la API
  api:
    build: .
    container_name: brisa-api
    restart: always
    ports:
      - "8000:8000"
    environment:
      ENV: production
      DATABASE_URL: mysql+pymysql://brisa_user:brisa_password@db:3306/brisa_db
      SECRET_KEY: ${SECRET_KEY}
      CORS_ORIGINS: ${CORS_ORIGINS}
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
    networks:
      - brisa-network
    command: >
      sh -c "
        alembic upgrade head &&
        uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
      "

  # Nginx como reverse proxy
  nginx:
    image: nginx:latest
    container_name: brisa-nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - api
    networks:
      - brisa-network

volumes:
  mysql_data:

networks:
  brisa-network:
    driver: bridge
```

### Archivo .env para Docker

**Archivo**: `.env` (en el directorio raíz)

```env
SECRET_KEY=GENERAR_CLAVE_SECRETA_AQUI
CORS_ORIGINS=http://localhost:3000,https://brisa.example.com
```

### Comandos Docker

```bash
# Construir y ejecutar
docker-compose up -d --build

# Ver logs
docker-compose logs -f api

# Detener
docker-compose down

# Reiniciar servicio específico
docker-compose restart api

# Ejecutar migraciones manualmente
docker-compose exec api alembic upgrade head

# Acceder al contenedor
docker-compose exec api bash
```

---

## Variables de Entorno

### Variables Requeridas

| Variable | Descripción | Ejemplo | Requerida |
|----------|-------------|---------|-----------|
| `ENV` | Ambiente de ejecución | `development`, `production` | Sí |
| `DATABASE_URL` | URL de conexión a MySQL | `mysql+pymysql://user:pass@host:3306/db` | Sí |
| `SECRET_KEY` | Clave secreta para JWT | `random-secret-key-32-chars` | Sí |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Expiración del token JWT | `60` | No (default: 60) |
| `CORS_ORIGINS` | Orígenes permitidos para CORS | `http://localhost:3000` | Sí |
| `API_TITLE` | Título de la API | `API Bienestar Estudiantil` | No |
| `API_VERSION` | Versión de la API | `1.0.0` | No |
| `LOG_LEVEL` | Nivel de logging | `DEBUG`, `INFO`, `WARNING`, `ERROR` | No (default: INFO) |
| `LOG_FILE` | Archivo de logs | `/var/log/brisa/app.log` | No |
| `WORKERS` | Número de workers de Uvicorn | `4` | No (default: 1) |

### Variables Opcionales Adicionales

```env
# Rate Limiting (futuro)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100

# Email (para notificaciones)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@brisa.com
SMTP_PASSWORD=smtp_password

# Almacenamiento de archivos
UPLOAD_DIR=/var/brisa/uploads
MAX_UPLOAD_SIZE=10485760  # 10MB en bytes

# Sentry (monitoreo de errores)
SENTRY_DSN=https://xxx@sentry.io/xxx
```

---

## Seguridad

### 1. Generar Claves Seguras

```bash
# SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Contraseña de base de datos
python -c "import secrets; print(secrets.token_urlsafe(16))"
```

### 2. Hardening de MySQL

```sql
-- Eliminar usuarios anónimos
DELETE FROM mysql.user WHERE User='';

-- Eliminar base de datos de prueba
DROP DATABASE IF EXISTS test;

-- Restringir acceso remoto al root
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Aplicar cambios
FLUSH PRIVILEGES;
```

### 3. Configuración de Permisos de Archivos

```bash
# Configuración solo lectura para el usuario de la app
chmod 600 /home/brisa/BRISA-backend/.env.production

# Logs escribibles
chmod 755 /var/log/brisa
chmod 644 /var/log/brisa/*.log
```

### 4. Headers de Seguridad en Nginx

Añadir a la configuración de Nginx:

```nginx
# Headers de seguridad
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

# Ocultar versión de Nginx
server_tokens off;
```

### 5. Rate Limiting (Nginx)

```nginx
# Definir zona de rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# Aplicar en location
location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    # ... resto de la configuración
}
```

---

## Monitoreo y Logs

### 1. Configurar Logging en la Aplicación

**Archivo**: `app/core/logging_config.py`

```python
import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    log_level = os.getenv("LOG_LEVEL", "INFO")
    log_file = os.getenv("LOG_FILE", "/var/log/brisa/app.log")
    
    # Formato de logs
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Handler para archivo con rotación
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
```

### 2. Monitoreo con Prometheus (Opcional)

Instalar:
```bash
pip install prometheus-fastapi-instrumentator
```

Configurar en `app/main.py`:
```python
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

# Habilitar métricas de Prometheus
Instrumentator().instrument(app).expose(app)
```

Acceder a métricas: http://localhost:8000/metrics

### 3. Logrotate

**Archivo**: `/etc/logrotate.d/brisa`

```
/var/log/brisa/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0644 brisa brisa
    sharedscripts
    postrotate
        supervisorctl restart brisa-api > /dev/null 2>&1 || true
    endscript
}
```

### 4. Monitorear Estado de la Aplicación

```bash
# Ver logs en tiempo real
sudo tail -f /var/log/brisa/app.log

# Ver estado de supervisor
sudo supervisorctl status

# Ver procesos
ps aux | grep uvicorn

# Ver uso de recursos
htop
```

---

## Backup y Recuperación

### 1. Backup Automático de Base de Datos

**Script**: `/home/brisa/backup_db.sh`

```bash
#!/bin/bash

# Configuración
DB_NAME="brisa_db"
DB_USER="brisa_prod"
DB_PASS="SUPER_SECURE_PASSWORD_HERE"
BACKUP_DIR="/var/backups/brisa"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

# Backup
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_DIR/backup_${DATE}.sql.gz

# Eliminar backups antiguos
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completado: backup_${DATE}.sql.gz"
```

```bash
# Hacer ejecutable
chmod +x /home/brisa/backup_db.sh

# Configurar cron para backup diario a las 2 AM
sudo crontab -e
# Añadir:
0 2 * * * /home/brisa/backup_db.sh >> /var/log/brisa/backup.log 2>&1
```

### 2. Restaurar desde Backup

```bash
# Descomprimir y restaurar
gunzip < /var/backups/brisa/backup_20251118_020000.sql.gz | \
mysql -u brisa_prod -p brisa_db
```

### 3. Backup de Código y Configuración

```bash
#!/bin/bash
# backup_app.sh

BACKUP_DIR="/var/backups/brisa/app"
DATE=$(date +%Y%m%d_%H%M%S)
APP_DIR="/home/brisa/BRISA-backend"

mkdir -p $BACKUP_DIR

# Backup de código y configuración (sin .venv y __pycache__)
tar -czf $BACKUP_DIR/app_${DATE}.tar.gz \
    --exclude='.venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    -C /home/brisa BRISA-backend
```

---

## Actualización de la Aplicación

### Proceso de Actualización en Producción

```bash
# 1. Conectarse al servidor
ssh user@server

# 2. Cambiar al usuario de la app
sudo su - brisa

# 3. Ir al directorio de la aplicación
cd /home/brisa/BRISA-backend

# 4. Hacer backup antes de actualizar
cd ..
tar -czf backup_pre_update_$(date +%Y%m%d).tar.gz BRISA-backend/

# 5. Actualizar código
cd BRISA-backend
git fetch origin
git checkout main  # o la rama de producción
git pull origin main

# 6. Activar entorno virtual
source .venv/bin/activate

# 7. Actualizar dependencias si es necesario
pip install -r requirements.txt --upgrade

# 8. Ejecutar migraciones
alembic upgrade head

# 9. Salir del usuario brisa
exit

# 10. Reiniciar la aplicación
sudo supervisorctl restart brisa-api

# 11. Verificar que está funcionando
sudo supervisorctl status brisa-api
curl http://localhost:8000/health
```

### Rollback en Caso de Problemas

```bash
# 1. Restaurar código anterior
cd /home/brisa
rm -rf BRISA-backend
tar -xzf backup_pre_update_YYYYMMDD.tar.gz

# 2. Revertir migraciones si es necesario
cd BRISA-backend
source .venv/bin/activate
alembic downgrade -1  # Revertir una migración

# 3. Reiniciar aplicación
sudo supervisorctl restart brisa-api
```

---

## Checklist de Despliegue

### Pre-Despliegue

- [ ] Código testeado localmente
- [ ] Migraciones creadas y probadas
- [ ] Variables de entorno configuradas
- [ ] SECRET_KEY generada de forma segura
- [ ] CORS_ORIGINS configurados correctamente
- [ ] Credenciales de base de datos configuradas

### Despliegue

- [ ] Servidor preparado con dependencias
- [ ] MySQL instalado y configurado
- [ ] Base de datos creada
- [ ] Usuario de base de datos creado con permisos
- [ ] Código desplegado
- [ ] Entorno virtual creado
- [ ] Dependencias instaladas
- [ ] Migraciones ejecutadas
- [ ] Supervisor configurado
- [ ] Nginx configurado
- [ ] SSL/HTTPS configurado
- [ ] Firewall configurado

### Post-Despliegue

- [ ] Aplicación accesible desde el dominio
- [ ] Endpoints de API respondiendo correctamente
- [ ] Documentación accesible en /docs
- [ ] Logs generándose correctamente
- [ ] Backup automático configurado
- [ ] Monitoreo configurado
- [ ] Pruebas de carga realizadas (opcional)

---

## Comandos Útiles de Mantenimiento

```bash
# Ver logs de la aplicación
sudo tail -f /var/log/brisa/app.log

# Ver logs de Nginx
sudo tail -f /var/log/nginx/brisa-access.log
sudo tail -f /var/log/nginx/brisa-error.log

# Reiniciar servicios
sudo supervisorctl restart brisa-api
sudo systemctl restart nginx
sudo systemctl restart mysql

# Ver estado de servicios
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status mysql

# Verificar uso de disco
df -h
du -sh /var/log/brisa/*
du -sh /var/backups/brisa/*

# Verificar uso de memoria
free -h
top

# Limpiar logs antiguos manualmente
sudo find /var/log/brisa -name "*.log.*" -mtime +30 -delete
```

---

Esta guía proporciona todo lo necesario para desplegar y mantener la aplicación BRISA Backend en diferentes entornos, desde desarrollo local hasta producción con Docker o servidores tradicionales.
