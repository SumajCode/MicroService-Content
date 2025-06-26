from domain.cloudflare.MegaService import ServicioMega
import shutil
import os

mega = ServicioMega()
megaCliente = mega.client

def subirArchivos(opciones: dict):
    try:
        rutasArchivos = []
        if 'archivos' in opciones.keys() and opciones.get('archivos') and isinstance(opciones.get('archivos'), list):
            for archivo in opciones.get('archivos'):
                routeTemp = f"{mega.tempPath}/{opciones.get('carpeta_nombre')}"
                if 'modulo' in opciones.keys():
                    routeTemp += f"/{opciones.get('modulo')}"
                crearCarpeta(routeTemp, routeTemp)
                rutaArchivo = crearArchivoServidor(routeTemp, archivo.get('nombre_archivo'), archivo.get('archivo'))
                archivoSubido = megaCliente.upload(rutaArchivo)
                os.remove(rutaArchivo)
                rutasArchivos.append(str(megaCliente.get_upload_link(archivoSubido)))
            return rutasArchivos
        return rutasArchivos
    except Exception as excep:
        print(f"Hubo un error al subir los archivos.{excep}")
        return []

def convertirDictArchivo(archivos: list):
    try:
        if len(archivos) > 0:
            dictArchivos = []
            for archivo in archivos:
                dictArchivo = {}
                dictArchivo['nombre_archivo'] = archivo.filename
                dictArchivo['archivo'] = archivo
                dictArchivos.append(dictArchivo)
            return dictArchivos
        return None
    except Exception as excep:
        print(f"Hubo un error con los archivos: {excep}")
        return []

def crearCarpeta(nombreCarpeta: str, nombreCarpetaServidor: str):
    os.makedirs(nombreCarpetaServidor, exist_ok=True)
    carpetaEncontrada = megaCliente.find(nombreCarpeta)
    if not carpetaEncontrada:
        megaCliente.create_folder(nombreCarpeta)

def crearArchivoServidor(ruta, nombreArchivo, archivo):
    rutaArchivo = os.path.join(ruta, nombreArchivo)
    with open(rutaArchivo, 'wb') as archivoTemp:
        archivoTemp.write(archivo.read())
    return rutaArchivo

def eliminarCarpeta(routeTemp):
    if os.path.exists(routeTemp):
        shutil.rmtree(routeTemp)