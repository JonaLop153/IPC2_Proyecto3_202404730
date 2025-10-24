import re
from datetime import datetime

def extraer_fecha(texto):
    """
    Extrae la primera fecha válida en formato dd/mm/yyyy de un texto.
    
    Reglas del enunciado:
    - Puede contener cualquier texto, pero debe incluir una fecha dd/mm/yyyy válida.
    - Si hay múltiples fechas, se toma la primera.
    - Ejemplos válidos: "01/01/2025", "Guatemala, 01/01/2025", etc.
    
    Retorna:
        datetime: Objeto datetime si se encuentra una fecha válida.
        None: Si no se encuentra ninguna fecha válida.
    """
    if not texto:
        return None
    
    # Patrón para encontrar fechas en formato dd/mm/yyyy
    patron = r'(\d{1,2}/\d{1,2}/\d{4})'
    coincidencias = re.findall(patron, texto)
    
    for fecha_str in coincidencias:
        try:
            # Validar que la fecha sea real (evita 99/99/9999)
            return datetime.strptime(fecha_str, '%d/%m/%Y')
        except ValueError:
            continue  # Ignorar fechas inválidas como 32/01/2025
    
    return None

def extraer_fecha_hora(texto):
    """
    Extrae la primera fecha y hora válida en formato dd/mm/yyyy hh24:mi de un texto.
    
    Reglas del enunciado:
    - Mismas reglas que para fechas, pero con hora.
    - Formato esperado: dd/mm/yyyy hh24:mi (ej. "15/10/2025 14:30")
    
    Retorna:
        datetime: Objeto datetime si se encuentra una fecha y hora válidas.
        None: Si no se encuentra ninguna.
    """
    if not texto:
        return None
    
    # Patrón para encontrar fechas y horas en formato dd/mm/yyyy hh24:mi
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
    
    Formato válido:
        - Números seguidos de guion y dígito de validación (0-9 o K)
        - Ejemplos: "34300-4", "110339001-K"
    
    Retorna:
        bool: True si el NIT es válido, False en caso contrario.
    """
    if not nit:
        return False
    
    # Patrón: uno o más dígitos, guion, y un dígito o 'K' al final
    patron = r'^\d+-[0-9K]$'
    return bool(re.match(patron, nit))

def calcular_costo_recurso(valor_hora, cantidad, tiempo_consumido):
    """
    Calcula el costo total de un recurso basado en su valor por hora, cantidad y tiempo consumido.
    
    Parámetros:
        valor_hora (float): Costo por hora del recurso.
        cantidad (float): Cantidad del recurso asignada.
        tiempo_consumido (float): Tiempo en horas que se usó el recurso.
    
    Retorna:
        float: Costo total.
    """
    return valor_hora * cantidad * tiempo_consumido