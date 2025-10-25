from flask import Flask, request, jsonify, send_file
from routes.configuracion_routes import configurar
from routes.consumo_routes import consumo
from routes.operaciones_routes import (
    crear_recurso, crear_categoria, crear_configuracion, 
    crear_cliente, crear_instancia, cancelar_instancia,
    agregar_recurso_configuracion, limpiar_consumos_duplicados
)
from routes.facturacion_routes import generar_factura
from routes.consultas_routes import (
    reset_datos, consultar_datos, obtener_facturas,
    obtener_factura, obtener_instancia, obtener_configuracion,
    obtener_categoria, obtener_recursos_configuracion
)
from pdf_generator import generar_pdf_factura, generar_pdf_analisis_ventas
import os

# ✅ CORREGIDO: Importar desde el archivo pdf_generator directamente
try:
    from pdf_generator import generar_pdf_factura, generar_pdf_analisis_ventas
except ImportError:
    # Si falla, intentar desde utils
    from backend.pdf_generator import generar_pdf_factura, generar_pdf_analisis_ventas

import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Servicio 2 Backend - Tecnologías Chapinas, S.A."

# Rutas principales
@app.route('/configurar', methods=['POST'])
def configurar_route():
    return configurar()

@app.route('/consumo', methods=['POST'])
def consumo_route():
    return consumo()

@app.route('/reset', methods=['DELETE'])
def reset_datos_route():
    return reset_datos()

@app.route('/consultarDatos', methods=['GET'])
def consultar_datos_route():
    return consultar_datos()

# Operaciones individuales
@app.route('/crearRecurso', methods=['POST'])
def crear_recurso_route():
    return crear_recurso()

@app.route('/crearCategoria', methods=['POST'])
def crear_categoria_route():
    return crear_categoria()

@app.route('/crearConfiguracion', methods=['POST'])
def crear_configuracion_route():
    return crear_configuracion()

@app.route('/crearCliente', methods=['POST'])
def crear_cliente_route():
    return crear_cliente()

@app.route('/crearInstancia', methods=['POST'])
def crear_instancia_route():
    return crear_instancia()

@app.route('/cancelarInstancia', methods=['POST'])
def cancelar_instancia_route():
    return cancelar_instancia()

@app.route('/agregarRecursoConfiguracion', methods=['POST'])
def agregar_recurso_configuracion_route():
    return agregar_recurso_configuracion()

@app.route('/limpiarConsumosDuplicados', methods=['POST'])
def limpiar_consumos_duplicados_route():
    return limpiar_consumos_duplicados()

# Facturación
@app.route('/generarFactura', methods=['POST'])
def generar_factura_route():
    return generar_factura()

# Consultas individuales
@app.route('/facturas', methods=['GET'])
def obtener_facturas_route():
    return obtener_facturas()

@app.route('/factura/<int:id_factura>', methods=['GET'])
def obtener_factura_route(id_factura):
    return obtener_factura(id_factura)

@app.route('/instancia/<int:id_instancia>', methods=['GET'])
def obtener_instancia_route(id_instancia):
    return obtener_instancia(id_instancia)

@app.route('/configuracion/<int:id_configuracion>', methods=['GET'])
def obtener_configuracion_route(id_configuracion):
    return obtener_configuracion(id_configuracion)

@app.route('/categoria/<int:id_categoria>', methods=['GET'])
def obtener_categoria_route(id_categoria):
    return obtener_categoria(id_categoria)

@app.route('/recursos-configuracion/<int:id_configuracion>', methods=['GET'])
def obtener_recursos_configuracion_route(id_configuracion):
    return obtener_recursos_configuracion(id_configuracion)

# PDF Routes
@app.route('/generar-pdf-factura/<int:id_factura>', methods=['GET'])
def generar_pdf_factura_route(id_factura):
    """Genera y descarga el PDF de una factura"""
    try:
        # Obtener datos de la factura
        factura_data = obtener_factura(id_factura)
        if not factura_data:
            return jsonify({'success': False, 'message': 'Factura no encontrada'}), 404
        
        # Convertir a dict si es necesario
        if hasattr(factura_data, 'to_dict'):
            factura_dict = factura_data.to_dict()
        else:
            factura_dict = factura_data
        
        # Generar PDF
        pdf_path = generar_pdf_factura(factura_dict)
        
        # Enviar archivo para descarga
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"factura_{id_factura}.pdf",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al generar PDF: {str(e)}'}), 500

@app.route('/generar-pdf-analisis-ventas', methods=['POST'])
def generar_pdf_analisis_ventas_route():
    """Genera y descarga el PDF de análisis de ventas"""
    try:
        data = request.get_json()
        fecha_inicio = data.get('fecha_inicio')
        fecha_fin = data.get('fecha_fin')
        datos_analisis = data.get('datos_analisis')
        
        if not all([fecha_inicio, fecha_fin, datos_analisis]):
            return jsonify({'success': False, 'message': 'Datos incompletos'}), 400
        
        # Generar PDF
        pdf_path = generar_pdf_analisis_ventas(fecha_inicio, fecha_fin, datos_analisis)
        
        # Enviar archivo para descarga
        return send_file(
            pdf_path,
            as_achment=True,
            download_name=f"analisis_ventas_{fecha_inicio}_{fecha_fin}.pdf".replace('/', '-'),
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al generar PDF: {str(e)}'}), 500

if __name__ == '__main__':
    print("=== INICIANDO SERVIDOR BACKEND ===")
    app.run(debug=True, host='0.0.0.0', port=5000)