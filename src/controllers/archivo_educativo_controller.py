from flask import request, jsonify
from services.educativo_service import EducativoService
from config.settings import Config
import logging

logger = logging.getLogger(__name__)

class ArchivoEducativoController:
    def __init__(self):
        self.educativo_service = EducativoService(Config.MONGO_URI)
    
    def _response_format(self, status: str, code: int, message: str, data=None):
        """Formato estándar de respuesta"""
        return jsonify({
            "status": status,
            "code": code,
            "message": message,
            "data": data
        }), code
    
    def obtener_archivos_usuario(self):
        """Obtener archivos por usuario"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            usuario_id = data.get('usuario_id')
            tipo_usuario = data.get('tipo_usuario')
            
            if not usuario_id or not tipo_usuario:
                return self._response_format("error", 400, "usuario_id y tipo_usuario son requeridos")
            
            archivos = self.educativo_service.obtener_archivos_por_usuario(usuario_id, tipo_usuario)
            
            # Formatear respuesta
            archivos_formateados = []
            for archivo in archivos:
                archivos_formateados.append({
                    "id": str(archivo['_id']),
                    "usuario_id": archivo['usuario_id'],
                    "tipo_usuario": archivo['tipo_usuario'],
                    "nombre_original": archivo['nombre_original'],
                    "nombre_almacenado": archivo['nombre_almacenado'],
                    "url": archivo['url'],
                    "tipo": archivo['tipo'],
                    "peso": archivo['peso'],
                    "modulo_origen": archivo['modulo_origen'],
                    "referencia_id": archivo['referencia_id'],
                    "fecha_subida": archivo['fecha_subida'].isoformat()
                })
            
            return self._response_format("success", 200, "Archivos obtenidos exitosamente", {
                "usuario_id": usuario_id,
                "tipo_usuario": tipo_usuario,
                "total_archivos": len(archivos_formateados),
                "archivos": archivos_formateados
            })
            
        except Exception as e:
            logger.error(f"Error al obtener archivos por usuario: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def obtener_archivos_modulo(self):
        """Obtener archivos por módulo"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            modulo_origen = data.get('modulo_origen')
            referencia_id = data.get('referencia_id')
            
            if not modulo_origen or not referencia_id:
                return self._response_format("error", 400, "modulo_origen y referencia_id son requeridos")
            
            archivos = self.educativo_service.obtener_archivos_por_modulo(modulo_origen, referencia_id)
            
            # Formatear respuesta
            archivos_formateados = []
            for archivo in archivos:
                archivos_formateados.append({
                    "id": str(archivo['_id']),
                    "usuario_id": archivo['usuario_id'],
                    "tipo_usuario": archivo['tipo_usuario'],
                    "nombre_original": archivo['nombre_original'],
                    "nombre_almacenado": archivo['nombre_almacenado'],
                    "url": archivo['url'],
                    "tipo": archivo['tipo'],
                    "peso": archivo['peso'],
                    "modulo_origen": archivo['modulo_origen'],
                    "referencia_id": archivo['referencia_id'],
                    "fecha_subida": archivo['fecha_subida'].isoformat()
                })
            
            return self._response_format("success", 200, "Archivos obtenidos exitosamente", {
                "modulo_origen": modulo_origen,
                "referencia_id": referencia_id,
                "total_archivos": len(archivos_formateados),
                "archivos": archivos_formateados
            })
            
        except Exception as e:
            logger.error(f"Error al obtener archivos por módulo: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def listar_todos_archivos(self):
        """Listar todos los archivos educativos"""
        try:
            # Obtener todos los archivos (puedes agregar filtros si es necesario)
            archivos = list(self.educativo_service.archivos_collection.find().sort("fecha_subida", -1))
            
            # Formatear respuesta
            archivos_formateados = []
            for archivo in archivos:
                archivos_formateados.append({
                    "id": str(archivo['_id']),
                    "usuario_id": archivo['usuario_id'],
                    "tipo_usuario": archivo['tipo_usuario'],
                    "nombre_original": archivo['nombre_original'],
                    "nombre_almacenado": archivo['nombre_almacenado'],
                    "url": archivo['url'],
                    "tipo": archivo['tipo'],
                    "peso": archivo['peso'],
                    "modulo_origen": archivo['modulo_origen'],
                    "referencia_id": archivo['referencia_id'],
                    "fecha_subida": archivo['fecha_subida'].isoformat()
                })
            
            return self._response_format("success", 200, "Todos los archivos obtenidos exitosamente", {
                "total_archivos": len(archivos_formateados),
                "archivos": archivos_formateados
            })
            
        except Exception as e:
            logger.error(f"Error al listar todos los archivos: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def eliminar_archivo(self):
        """Eliminar un archivo educativo"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            archivo_id = data.get('_id')
            if not archivo_id:
                return self._response_format("error", 400, "_id es requerido")
            
            # Eliminar archivo
            eliminado = self.educativo_service.eliminar_archivo_educativo(archivo_id)
            
            if eliminado:
                return self._response_format("success", 200, "Archivo eliminado exitosamente", {
                    "archivo_id": archivo_id
                })
            else:
                return self._response_format("error", 404, "Archivo no encontrado o no se pudo eliminar")
                
        except Exception as e:
            logger.error(f"Error al eliminar archivo: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def registrar_archivo(self):
        """Registrar un archivo manualmente"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            # Validar campos requeridos
            campos_requeridos = ['usuario_id', 'tipo_usuario', 'nombre_original', 'nombre_almacenado', 
                               'url', 'tipo', 'peso', 'modulo_origen', 'referencia_id']
            
            for campo in campos_requeridos:
                if campo not in data:
                    return self._response_format("error", 400, f"{campo} es requerido")
            
            # Crear documento
            documento_archivo = {
                "usuario_id": data['usuario_id'],
                "tipo_usuario": data['tipo_usuario'],
                "nombre_original": data['nombre_original'],
                "nombre_almacenado": data['nombre_almacenado'],
                "url": data['url'],
                "tipo": data['tipo'],
                "peso": data['peso'],
                "modulo_origen": data['modulo_origen'],
                "referencia_id": data['referencia_id'],
                "fecha_subida": datetime.utcnow()
            }
            
            # Insertar en base de datos
            archivo_id = self.educativo_service.insertar_archivo_educativo(documento_archivo)
            
            return self._response_format("success", 201, "Archivo registrado exitosamente", {
                "archivo_id": archivo_id,
                "nombre_original": data['nombre_original']
            })
            
        except Exception as e:
            logger.error(f"Error al registrar archivo: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
