import re
from datetime import datetime

def extraer_fecha(texto):
    """
    Extrae la primera fecha válida en formato dd/mm/yyyy de un texto.
    """
    if not texto:
        return None
    
    patron = r'(\d{1,2}/\d{1,2}/\d{4})'
    coincidencias = re.findall(patron, texto)
    
    for fecha_str in coincidencias:
        try:
            return datetime.strptime(fecha_str, '%d/%m/%Y')
        except ValueError:
            continue
    
    return None

def extraer_fecha_hora(texto):
    """
    Extrae la primera fecha y hora válida en formato dd/mm/yyyy hh24:mi de un texto.
    """
    if not texto:
        return None
    
    patron = r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2})'
    coincidencias = re.findall(patron, texto)
    
    for fecha_hora_str in coincidencias:
        try:
            return datetime.strptime(fecha_hora_str, '%d/%m/%Y %H:%M')
        except ValueError:
            continue
    
    return None

def validar_nit(nit):
    """
    Valida que un NIT tenga el formato correcto según el enunciado.
    """
    if not nit:
        return False
    
    patron = r'^\d+-[0-9K]$'
    return bool(re.match(patron, nit))

def calcular_costo_recurso(valor_hora, cantidad, tiempo_consumido):
    """
    Calcula el costo total de un recurso basado en su valor por hora, cantidad y tiempo consumido.
    """
    return valor_hora * cantidad * tiempo_consumido

def limpiar_xml(xml_data):
    """Limpia el XML removiendo BOM y espacios innecesarios"""
    if isinstance(xml_data, bytes):
        if xml_data.startswith(b'\xef\xbb\xbf'):
            xml_data = xml_data[3:]
        xml_str = xml_data.decode('utf-8').strip()
    else:
        xml_str = str(xml_data).strip()
    
    xml_str = xml_str.lstrip()
    
    return xml_str