from flask import jsonify
from models import Recurso, Categoria, Configuracion, Cliente, Instancia, Consumo, Factura, RecursoConfiguracion
import xml.etree.ElementTree as ET
import os

def reset_datos():
    try:
        root = ET.Element('database')
        ET.SubElement(root, 'recursos')
        ET.SubElement(root, 'categorias')
        ET.SubElement(root, 'configuraciones')
        ET.SubElement(root, 'clientes')
        ET.SubElement(root, 'instancias')
        ET.SubElement(root, 'consumos')
        ET.SubElement(root, 'facturas')
        
        tree = ET.ElementTree(root)
        os.makedirs('data', exist_ok=True)
        tree.write('data/database.xml', encoding='utf-8', xml_declaration=True)
        
        return jsonify({
            'success': True,
            'message': 'Base de datos reiniciada correctamente'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al reiniciar: {str(e)}'
        }), 500

def consultar_datos():
    try:
        datos = {
            'recursos': [r.to_dict() for r in Recurso.obtener_todos()],
            'categorias': [c.to_dict() for c in Categoria.obtener_todas()],
            'configuraciones': [conf.to_dict() for conf in Configuracion.obtener_todas()],
            'clientes': [cli.to_dict() for cli in Cliente.obtener_todos()],
            'instancias': [inst.to_dict() for inst in Instancia.obtener_todas()],
            'consumos': [cons.to_dict() for cons in Consumo.obtener_todos()],
            'facturas': [fact.to_dict() for fact in Factura.obtener_todas()]
        }
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'}), 500

def obtener_facturas():
    try:
        facturas = [f.to_dict() for f in Factura.obtener_todas()]
        return jsonify({'success': True, 'facturas': facturas})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def obtener_factura(id_factura):
    try:
        factura = Factura.obtener_por_id(id_factura)
        if factura:
            return jsonify({'success': True, 'factura': factura.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'Factura no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def obtener_instancia(id_instancia):
    try:
        instancia = Instancia.obtener_por_id(id_instancia)
        if instancia:
            return jsonify({'success': True, 'instancia': instancia.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'Instancia no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def obtener_configuracion(id_configuracion):
    try:
        configuracion = Configuracion.obtener_por_id(id_configuracion)
        if configuracion:
            return jsonify({'success': True, 'configuracion': configuracion.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'Configuración no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def obtener_categoria(id_categoria):
    try:
        categoria = Categoria.obtener_por_id(id_categoria)
        if categoria:
            return jsonify({'success': True, 'categoria': categoria.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'Categoría no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

def obtener_recursos_configuracion(id_configuracion):
    try:
        recursos_config = RecursoConfiguracion.obtener_por_configuracion(id_configuracion)
        recursos_data = []
        for rc in recursos_config:
            recurso = Recurso.obtener_por_id(rc.id_recurso)
            if recurso:
                recursos_data.append({
                    'id_recurso': rc.id_recurso,
                    'nombre_recurso': recurso.nombre,
                    'cantidad': rc.cantidad,
                    'valor_hora': recurso.valor_hora
                })
        return jsonify({'success': True, 'recursos': recursos_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500