"""
Punto de entrada principal para la aplicación BRISA Backend
"""

import os
import uvicorn
from app import create_app

# Obtener configuración del entorno
config_name = os.environ.get('ENV', 'development')

# Crear aplicación
app = create_app(config_name)

if __name__ == '__main__':
    # Configuración para desarrollo
    port = int(os.environ.get('PORT', 8000))
    reload = os.environ.get('ENV', 'development') == 'development'
    
    print(f"🚀 Iniciando BRISA Backend API en puerto {port}")
    print(f"📝 Entorno: {config_name}")
    print(f"🔧 Auto-reload: {reload}")
    print(f"🌐 URL: http://localhost:{port}")
    print(f"📖 Docs: http://localhost:{port}/docs")
    print(f"❤️  Health Check: http://localhost:{port}/api/health")
    
    uvicorn.run(
        "run:app",
        host='0.0.0.0',
        port=port,
        reload=reload,
        log_level="info"
    )