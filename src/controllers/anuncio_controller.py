from flask import request, jsonify
from src.services.educativo_service import EducativoService
from src.services.mega_service import MegaService
from src.models.anuncio_model import AnuncioModel
from src.utils.file_utils import FileUtils
from src.config.settings import Config
import logging
import tempfile
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

class AnuncioController:
    def __init__(self):
        self.educativo_service = EducativoService(Config.MONGO_URI)
        self.mega_service = MegaService(Config.MEGA_EMAIL, Config.MEGA_PASSWORD)
        self.anuncio_model = AnuncioModel()
    
    def _response_format(self, status: str, code: int, message: str, data=None):
        """Formato estándar de respuesta"""
        return jsonify({
            "status": status,
            "code": code,
            "message": message,
            "data": data
        }), code
    
    def obtener_anuncios(self):
        """Obtener anuncios por curso"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            id_curso = data.get('id_curso')
            if not id_curso:
                return self._response_format("error", 400, "id_curso es requerido")
            
            anuncios = self.educativo_service.obtener_anuncios_por_curso(id_curso)
            
            # Formatear respuesta
            anuncios_formateados = []
            for anuncio in anuncios:
                anuncios_formateados.append({
                    "id": str(anuncio['_id']),
                    "id_curso": anuncio['id_curso'],
                    "titulo": anuncio['titulo'],
                    "contenido": anuncio['contenido'],
                    "autor_id": anuncio['autor_id'],
                    "tipo_usuario": anuncio['tipo_usuario'],
                    "archivos": anuncio.get('archivos', []),
                    "fecha_creacion": anuncio['fecha_creacion'].isoformat()
                })
            
            return self._response_format("success", 200, "Anuncios obtenidos exitosamente", {
                "id_curso": id_curso,
                "total_anuncios": len(anuncios_formateados),
                "anuncios": anuncios_formateados
            })
            
        except Exception as e:
            logger.error(f"Error al obtener anuncios: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def crear_anuncio(self):
        """Crear un nuevo anuncio"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            # Validar datos
            es_valido, mensaje = AnuncioModel.validar_datos_anuncio(data)
            if not es_valido:
                return self._response_format("error", 400, mensaje)
            
            # Crear documento
            documento = AnuncioModel.crear_documento_anuncio(
                id_curso=data['id_curso'],
                titulo=data['titulo'],
                contenido=data['contenido'],
                autor_id=data['autor_id'],
                tipo_usuario=data['tipo_usuario'],
                archivos=data.get('archivos', [])
            )
            
            # Insertar en base de datos
            anuncio_id = self.educativo_service.insertar_anuncio(documento)
            
            return self._response_format("success", 201, "Anuncio creado exitosamente", {
                "anuncio_id": anuncio_id,
                "id_curso": data['id_curso'],
                "titulo": data['titulo']
            })
            
        except Exception as e:
            logger.error(f"Error al crear anuncio: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def actualizar_anuncio(self):
        """Actualizar un anuncio existente"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            anuncio_id = data.get('_id')
            if not anuncio_id:
                return self._response_format("error", 400, "_id es requerido")
            
            # Preparar datos de actualización
            datos_actualizacion = {}
            if 'titulo' in data:
                datos_actualizacion['titulo'] = data['titulo']
            if 'contenido' in data:
                datos_actualizacion['contenido'] = data['contenido']
            if 'archivos' in data:
                datos_actualizacion['archivos'] = data['archivos']
            
            if not datos_actualizacion:
                return self._response_format("error", 400, "No hay datos para actualizar")
            
            # Actualizar en base de datos
            actualizado = self.educativo_service.actualizar_anuncio(anuncio_id, datos_actualizacion)
            
            if actualizado:
                return self._response_format("success", 200, "Anuncio actualizado exitosamente", {
                    "anuncio_id": anuncio_id,
                    "campos_actualizados": list(datos_actualizacion.keys())
                })
            else:
                return self._response_format("error", 404, "Anuncio no encontrado o no se pudo actualizar")
                
        except Exception as e:
            logger.error(f"Error al actualizar anuncio: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def eliminar_anuncio(self):
        """Eliminar un anuncio"""
        try:
            data = request.get_json()
            if not data:
                return self._response_format("error", 400, "Datos JSON requeridos")
            
            anuncio_id = data.get('_id')
            if not anuncio_id:
                return self._response_format("error", 400, "_id es requerido")
            
            # Eliminar anuncio (soft delete)
            eliminado = self.educativo_service.eliminar_anuncio(anuncio_id)
            
            if eliminado:
                return self._response_format("success", 200, "Anuncio eliminado exitosamente", {
                    "anuncio_id": anuncio_id
                })
            else:
                return self._response_format("error", 404, "Anuncio no encontrado o no se pudo eliminar")
                
        except Exception as e:
            logger.error(f"Error al eliminar anuncio: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
    
    def subir_archivo_anuncio(self):
        """Subir múltiples archivos para un anuncio"""
        try:
            # Validar que se enviaron archivos
            if 'archivos' not in request.files:
                return self._response_format("error", 400, "No se enviaron archivos")
            
            archivos = request.files.getlist('archivos')
            if not archivos or all(archivo.filename == '' for archivo in archivos):
                return self._response_format("error", 400, "No se seleccionaron archivos")
            
            # Obtener datos del formulario
            anuncio_id = request.form.get('anuncio_id')  # ID del anuncio
            autor_id = request.form.get('autor_id')  # ID del autor
            tipo_usuario = request.form.get('tipo_usuario', 'docente')
            
            if not anuncio_id or not autor_id:
                return self._response_format("error", 400, "anuncio_id y autor_id son requeridos")
            
            archivos_subidos = []
            errores = []
            
            # Crear carpeta en MEGA si no existe
            ruta_mega = f"/Archivo/anuncio/{anuncio_id}/"
            
            for archivo in archivos:
                try:
                    if archivo.filename == '':
                        continue
                        
                    # Validaciones
                    if not FileUtils.archivo_permitido(archivo.filename):
                        errores.append(f"Archivo {archivo.filename}: tipo no permitido")
                        continue
                    
                    # Obtener información del archivo
                    archivo_info = FileUtils.obtener_info_archivo(archivo)
                    
                    # Generar nombre único
                    nombre_unico = f"{uuid.uuid4()}_{archivo_info['nombre']}"
                    
                    # Guardar archivo temporalmente
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = FileUtils.guardar_archivo_temporal(archivo, temp_dir)
                        
                        # Subir a MEGA
                        resultado_mega = self.mega_service.subir_archivo(
                            temp_path, 
                            ruta_mega, 
                            nombre_unico
                        )
                        
                        if not resultado_mega:
                            errores.append(f"Error al subir {archivo.filename} a MEGA")
                            continue
                        
                        # Crear documento de archivo
                        documento_archivo = {
                            "usuario_id": autor_id,
                            "tipo_usuario": tipo_usuario,
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes'],
                            "modulo_origen": "anuncio",
                            "referencia_id": anuncio_id,
                            "fecha_subida": datetime.utcnow()
                        }
                        
                        # Guardar en MongoDB
                        archivo_id = self.educativo_service.insertar_archivo_educativo(documento_archivo)
                        
                        archivos_subidos.append({
                            "archivo_id": archivo_id,
                            "nombre_original": archivo.filename,
                            "nombre_almacenado": nombre_unico,
                            "url": resultado_mega['link'],
                            "tipo": archivo_info['mime'],
                            "peso": archivo_info['peso_bytes']
                        })
                        
                except Exception as e:
                    errores.append(f"Error al procesar {archivo.filename}: {str(e)}")
            
            if archivos_subidos:
                message = f"Se subieron {len(archivos_subidos)} archivos exitosamente"
                if errores:
                    message += f". {len(errores)} archivos fallaron"
                
                return self._response_format("success", 201, message, {
                    "anuncio_id": anuncio_id,
                    "autor_id": autor_id,
                    "archivos": archivos_subidos,
                    "errores": errores if errores else None
                })
            else:
                return self._response_format("error", 400, "No se pudo subir ningún archivo", {
                    "errores": errores
                })
                
        except Exception as e:
            logger.error(f"Error al subir archivos de anuncio: {e}")
            return self._response_format("error", 500, "Error interno del servidor")
