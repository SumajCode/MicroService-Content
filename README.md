# MicroService-Content

Microservicio backend para la gestión de archivos en una plataforma educativa.

## 🛠️ Tecnologías

- **Flask**: Framework web para la API REST
- **MongoDB**: Base de datos para metadatos
- **MEGA**: Almacenamiento en la nube
- **Render.com**: Despliegue automático

## 🚀 Instalación

1. Clonar el repositorio:
\`\`\`bash
git clone <repository-url>
cd MicroService-Content
\`\`\`

2. Crear entorno virtual:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
\`\`\`

3. Instalar dependencias:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. Configurar variables de entorno:
\`\`\`bash
cp .env.example .env
# Editar .env con tus credenciales
\`\`\`

5. Ejecutar la aplicación:
\`\`\`bash
python app.py
\`\`\`

## 📚 API Endpoints

### Archivos

- `POST /archivos/subir` - Subir archivo
- `PUT /archivos/<archivo_id>` - Reemplazar archivo
- `DELETE /archivos/<archivo_id>` - Eliminar archivo
- `GET /archivos/usuario/<usuario_id>` - Obtener archivos de usuario

### Usuarios

- `DELETE /usuarios/<usuario_id>` - Eliminar todo el contenido de un usuario

### Utilidades

- `GET /health` - Estado del servicio
- `GET /` - Información de la API

## 🧪 Ejemplos de uso

### Subir archivo personal
\`\`\`bash
curl -X POST http://localhost:5000/archivos/subir \
  -F "archivo=@documento.pdf" \
  -F "usuario_id=u999" \
  -F "tipo_contenido=personal"
\`\`\`

### Subir archivo educativo
\`\`\`bash
curl -X POST http://localhost:5000/archivos/subir \
  -F "archivo=@tarea.docx" \
  -F "usuario_id=u777" \
  -F "tipo_contenido=educativo"
\`\`\`

### Reemplazar archivo
\`\`\`bash
curl -X PUT http://localhost:5000/archivos/<archivo_id> \
  -F "archivo=@nuevo_documento.pdf"
\`\`\`

### Eliminar archivo
\`\`\`bash
curl -X DELETE http://localhost:5000/archivos/<archivo_id>
\`\`\`

### Obtener archivos de usuario
\`\`\`bash
curl -X GET http://localhost:5000/archivos/usuario/u999
\`\`\`

### Eliminar todo el contenido de un usuario
\`\`\`bash
curl -X DELETE http://localhost:5000/usuarios/u777
\`\`\`

## 📁 Estructura del proyecto

\`\`\`
MicroService-Content/
├── src/
│   ├── config/settings.py          # Configuración
│   ├── controllers/archivo_controller.py  # Lógica de negocio
│   ├── models/archivo_model.py     # Modelos de datos
│   ├── routes/archivo_routes.py    # Rutas de la API
│   ├── services/
│   │   ├── mega_service.py         # Servicio MEGA
│   │   ├── mongo_service.py        # Servicio MongoDB
│   │   └── api_externa_service.py  # Servicio API externa
│   └── utils/file_utils.py         # Utilidades para archivos
├── app.py                          # Aplicación principal
├── wsgi.py                         # Punto de entrada WSGI
├── requirements.txt                # Dependencias
├── .env.example                    # Variables de entorno ejemplo
└── README.md                       # Documentación
\`\`\`

## 🗃️ Organización de datos

### MEGA
\`\`\`
/Contenido Personal/{usuario_id}/archivo.ext
/Contenido Educativo/{usuario_id}/archivo.ext
\`\`\`

### MongoDB

**Colección: archivos_subidos**
- `_id`: ObjectId autogenerado
- `usuario_id`: ID del usuario
- `nombre_usuario`: Nombre del usuario
- `tipo_contenido`: "personal" o "educativo"
- `archivo`: Detalles del archivo (nombre, tipo, peso, link, ruta)
- `fecha_subida`: Timestamp
- `etiquetas`: Array de strings (opcional)
- `estado`: "activo", "archivado", "eliminado"

**Colección: carpetas_usuarios**
- `_id`: ObjectId autogenerado
- `usuario_id`: ID del usuario
- `nombre_usuario`: Nombre del usuario
- `carpetas`: Objeto con rutas personal y educativo

## 🔧 Desarrollo

### Formateo de código
\`\`\`bash
black src/
isort src/
\`\`\`

### Variables de entorno requeridas
- `MONGO_URI`: URI de conexión a MongoDB
- `MEGA_EMAIL`: Email de cuenta MEGA
- `MEGA_PASSWORD`: Contraseña de cuenta MEGA
- `API_USUARIOS_URL`: URL de la API externa de usuarios

## 🚀 Despliegue

El proyecto está configurado para desplegarse automáticamente en Render.com cuando se hace push a la rama principal.

## 📝 Notas

- El servicio usa datos mock para la API externa durante el desarrollo
- Los archivos se almacenan temporalmente antes de subirse a MEGA
- Se implementa retry automático para las llamadas a la API externa
- Todos los errores se registran en logs para debugging
