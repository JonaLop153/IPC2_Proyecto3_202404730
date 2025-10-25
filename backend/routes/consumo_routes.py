from flask import request, jsonify
import xml.etree.ElementTree as ET
from models import Consumo
from utils import extraer_fecha_hora, limpiar_xml
def consumo():
    try:
        print("=== INICIANDO PROCESAMIENTO CONSUMO ===")
        
        xml_data = request.get_data()
        xml_str = limpiar_xml(xml_data)
        
        if not xml_str:
            return jsonify({
                'success': False,
                'message': 'El archivo XML está vacío'
            }), 400
        
        root = ET.fromstring(xml_str)
        print(f"Elemento raíz encontrado: {root.tag}")
        
        consumos_procesados = 0
        
        for consumo_elem in root.findall('consumo'):
            nit_cliente = consumo_elem.get('nitCliente')
            id_instancia = int(consumo_elem.get('idInstancia'))
            tiempo = float(consumo_elem.find('tiempo').text)
            
            # ✅ BUSCAR TODAS LAS POSIBLES VARIANTES
            fecha_hora_elem = None
            for tag_name in ['fechahora', 'fechaHora', 'fecha_hora']:
                fecha_hora_elem = consumo_elem.find(tag_name)
                if fecha_hora_elem is not None:
                    break
            
            if fecha_hora_elem is not None and fecha_hora_elem.text:
                fecha_hora_str = fecha_hora_elem.text
                fecha_hora = extraer_fecha_hora(fecha_hora_str)
                
                if fecha_hora:
                    print(f"✅ Procesando consumo: Instancia {id_instancia}, Tiempo {tiempo}h, Fecha {fecha_hora}")
                    
                    nuevo_consumo = Consumo(id_instancia, nit_cliente, tiempo, fecha_hora)
                    if nuevo_consumo.guardar():
                        consumos_procesados += 1
                else:
                    print(f"❌ Fecha inválida o no extraíble: {fecha_hora_str}")
            else:
                print("❌ No se encontró elemento de fecha/hora")
        
        print(f"📊 Consumos procesados: {consumos_procesados}")
        
        return jsonify({
            'success': True,
            'message': 'Mensaje de consumo procesado exitosamente',
            'consumos_procesados': consumos_procesados
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR DETALLADO: {error_details}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 400