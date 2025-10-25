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
from models import Factura
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
    """Genera y descarga el PDF de una factura - Versión robusta"""
    try:
        print(f"=== SOLICITUD PDF PARA FACTURA {id_factura} ===")
        
        # Método robusto: Usar obtener_todas() que sabemos que funciona
        print("🔍 Buscando factura usando obtener_todas()...")
        facturas_todas = Factura.obtener_todas()
        print(f"📄 Facturas disponibles: {len(facturas_todas)}")
        
        factura_encontrada = None
        for factura in facturas_todas:
            print(f"   - Factura ID: {factura.id}")
            if factura.id == id_factura:
                factura_encontrada = factura
                break
        
        if not factura_encontrada:
            return jsonify({'success': False, 'message': f'Factura {id_factura} no encontrada'}), 404
        
        print(f"✅ Factura encontrada: ID {factura_encontrada.id}")
        
        # Convertir a diccionario
        factura_dict = factura_encontrada.to_dict()
        
        # Validar estructura
        required_fields = ['id', 'nitCliente', 'fechaEmision', 'montoTotal', 'detalles']
        for field in required_fields:
            if field not in factura_dict:
                return jsonify({'success': False, 'message': f'Campo {field} faltante en factura'}), 400
        
        print(f"📊 Detalles: {len(factura_dict['detalles'])} items")
        
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
        import traceback
        print(f"❌ ERROR al generar PDF: {str(e)}")
        print(traceback.format_exc())
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
            as_attachment=True,
            download_name=f"analisis_ventas_{fecha_inicio}_{fecha_fin}.pdf".replace('/', '-'),
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al generar PDF: {str(e)}'}), 500

# Rutas de diagnóstico y debug
@app.route('/debug-facturas', methods=['GET'])
def debug_facturas():
    """Muestra todas las facturas disponibles"""
    try:
        facturas = Factura.obtener_todas()
        result = {
            'total_facturas': len(facturas),
            'facturas': []
        }
        
        for factura in facturas:
            factura_info = {
                'id': factura.id,
                'nitCliente': factura.nit_cliente,
                'fechaEmision': factura.fecha_emision.strftime('%d/%m/%Y'),
                'montoTotal': factura.monto_total,
                'detalles_count': len(factura.detalles)
            }
            result['facturas'].append(factura_info)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug-factura/<int:id_factura>', methods=['GET'])
def debug_factura(id_factura):
    """Ruta temporal para depurar la estructura de una factura"""
    try:
        print(f"🔍 Debug factura ID: {id_factura}")
        
        # Método 1: Usar obtener_todas
        facturas_todas = Factura.obtener_todas()
        factura_encontrada = None
        
        for factura in facturas_todas:
            if factura.id == id_factura:
                factura_encontrada = factura
                break
        
        result = {
            'total_facturas': len(facturas_todas),
            'factura_encontrada': factura_encontrada is not None,
            'factura_id_buscado': id_factura
        }
        
        if factura_encontrada:
            result['factura_info'] = {
                'id': factura_encontrada.id,
                'nitCliente': factura_encontrada.nit_cliente,
                'fechaEmision': factura_encontrada.fecha_emision.strftime('%d/%m/%Y'),
                'montoTotal': factura_encontrada.monto_total,
                'detalles_count': len(factura_encontrada.detalles),
                'tiene_to_dict': hasattr(factura_encontrada, 'to_dict')
            }
            
            # Listar IDs de todas las facturas disponibles
            result['facturas_disponibles'] = [f.id for f in facturas_todas]
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/debug-pdf-factura/<int:id_factura>', methods=['GET'])
def debug_pdf_factura(id_factura):
    """Prueba la generación de PDF sin descargar"""
    try:
        print(f"=== PRUEBA PDF PARA FACTURA {id_factura} ===")
        
        # Buscar factura
        facturas_todas = Factura.obtener_todas()
        factura_encontrada = None
        
        for factura in facturas_todas:
            if factura.id == id_factura:
                factura_encontrada = factura
                break
        
        if not factura_encontrada:
            return jsonify({'success': False, 'message': f'Factura {id_factura} no encontrada'}), 404
        
        # Convertir a diccionario
        factura_dict = factura_encontrada.to_dict()
        
        # Validar estructura
        required_fields = ['id', 'nitCliente', 'fechaEmision', 'montoTotal', 'detalles']
        for field in required_fields:
            if field not in factura_dict:
                return jsonify({'success': False, 'message': f'Campo {field} faltante'}), 400
        
        # Probar generación de PDF
        pdf_path = generar_pdf_factura(factura_dict)
        
        return jsonify({
            'success': True,
            'message': 'PDF generado exitosamente',
            'pdf_path': pdf_path,
            'factura': {
                'id': factura_dict['id'],
                'nitCliente': factura_dict['nitCliente'],
                'fechaEmision': factura_dict['fechaEmision'],
                'montoTotal': factura_dict['montoTotal'],
                'detalles_count': len(factura_dict['detalles'])
            }
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    print("=== INICIANDO SERVIDOR BACKEND ===")
    print("=== RUTAS DISPONIBLES ===")
    print("GET  /debug-facturas          - Lista todas las facturas")
    print("GET  /debug-factura/<id>      - Depura una factura específica")
    print("GET  /debug-pdf-factura/<id>  - Prueba generación de PDF")
    print("GET  /generar-pdf-factura/<id> - Descarga PDF de factura")
    print("POST /generar-pdf-analisis-ventas - Genera PDF de análisis")
    print("================================")
    app.run(debug=True, host='0.0.0.0', port=5000)