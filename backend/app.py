from flask import Flask, request, jsonify
import xml.etree.ElementTree as ET
from models import Recurso, Categoria, Configuracion, Cliente, Instancia, Consumo, Factura, RecursoConfiguracion
from utils import extraer_fecha, extraer_fecha_hora
import os

app = Flask(__name__)

def limpiar_xml(xml_data):
    """Limpia el XML removiendo BOM y espacios innecesarios"""
    # Convertir a string si son bytes
    if isinstance(xml_data, bytes):
        # Remover BOM si existe
        if xml_data.startswith(b'\xef\xbb\xbf'):
            xml_data = xml_data[3:]
        xml_str = xml_data.decode('utf-8').strip()
    else:
        xml_str = str(xml_data).strip()
    
    # Remover espacios extraños al inicio
    xml_str = xml_str.lstrip()
    
    return xml_str

@app.route('/')
def home():
    return "Servicio 2 Backend - Tecnologías Chapinas, S.A."

@app.route('/configurar', methods=['POST'])
def configurar():
    try:
        print("=== INICIANDO PROCESAMIENTO CONFIGURACIÓN ===")
        
        # Obtener datos crudos
        xml_data = request.get_data()
        print(f"Datos recibidos (primeros 200 chars): {xml_data[:200]}")
        
        # Limpiar XML
        xml_str = limpiar_xml(xml_data)
        print(f"XML limpio (primeros 200 chars): {xml_str[:200]}")
        
        if not xml_str:
            return jsonify({
                'success': False,
                'message': 'El archivo XML está vacío'
            }), 400
        
        # Parsear XML
        root = ET.fromstring(xml_str)
        print(f"Elemento raíz encontrado: {root.tag}")
        
        resultados = {
            'clientes_creados': 0,
            'instancias_creadas': 0,
            'recursos_creados': 0,
            'categorias_creadas': 0,
            'configuraciones_creadas': 0
        }
        
        # --- Procesar Recursos ---
        lista_recursos = root.find('listaRecursos')
        if lista_recursos is not None:
            print(f"Procesando {len(lista_recursos)} recursos")
            for recurso_elem in lista_recursos:
                id_recurso = int(recurso_elem.get('id'))
                nombre = recurso_elem.find('nombre').text
                abreviatura = recurso_elem.find('abreviatura').text
                metrica = recurso_elem.find('metrica').text
                tipo = recurso_elem.find('tipo').text
                valor_hora = float(recurso_elem.find('valorXhora').text)
                
                print(f"  - Recurso {id_recurso}: {nombre}")
                
                nuevo_recurso = Recurso(id_recurso, nombre, abreviatura, metrica, tipo, valor_hora)
                if nuevo_recurso.guardar():
                    resultados['recursos_creados'] += 1
        
        # --- Procesar Categorías ---
        lista_categorias = root.find('listaCategorias')
        if lista_categorias is not None:
            print(f"Procesando {len(lista_categorias)} categorías")
            for categoria_elem in lista_categorias:
                id_categoria = int(categoria_elem.get('id'))
                nombre = categoria_elem.find('nombre').text
                descripcion_elem = categoria_elem.find('descripcion')
                descripcion = descripcion_elem.text if descripcion_elem is not None else ""
                carga_trabajo = categoria_elem.find('cargaTrabajo').text
                
                print(f"  - Categoría {id_categoria}: {nombre}")
                
                nueva_categoria = Categoria(id_categoria, nombre, descripcion, carga_trabajo)
                if nueva_categoria.guardar():
                    resultados['categorias_creadas'] += 1
                    
                    # --- Procesar Configuraciones dentro de la categoría ---
                    lista_configuraciones = categoria_elem.find('listaConfiguraciones')
                    if lista_configuraciones is not None:
                        for config_elem in lista_configuraciones:
                            id_config = int(config_elem.get('id'))
                            nombre_conf = config_elem.find('nombre').text
                            desc_conf_elem = config_elem.find('descripcion')
                            desc_conf = desc_conf_elem.text if desc_conf_elem is not None else ""
                            
                            print(f"    - Configuración {id_config}: {nombre_conf}")
                            
                            nueva_config = Configuracion(id_config, nombre_conf, desc_conf, id_categoria)
                            if nueva_config.guardar():
                                resultados['configuraciones_creadas'] += 1
                                
                                # --- Procesar Recursos de la Configuración ---
                                recursos_config = config_elem.find('recursosConfiguracion')
                                if recursos_config is not None:
                                    for recurso_conf in recursos_config:
                                        id_recurso_conf = int(recurso_conf.get('id'))
                                        cantidad = float(recurso_conf.text)
                                        print(f"      - Recurso config {id_recurso_conf}: {cantidad}")
                                        
                                        nueva_asoc = RecursoConfiguracion(id_config, id_recurso_conf, cantidad)
                                        nueva_asoc.guardar()
        
        # --- Procesar Clientes ---
        lista_clientes = root.find('listaClientes')
        if lista_clientes is not None:
            print(f"Procesando {len(lista_clientes)} clientes")
            for cliente_elem in lista_clientes:
                nit = cliente_elem.get('nit')  # ✅ NIT como string, NO convertir a int
                nombre = cliente_elem.find('nombre').text
                usuario = cliente_elem.find('usuario').text
                clave = cliente_elem.find('clave').text
                direccion = cliente_elem.find('direccion').text
                correo = cliente_elem.find('correoElectronico').text
                
                print(f"  - Cliente {nit}: {nombre}")
                
                nuevo_cliente = Cliente(nit, nombre, usuario, clave, direccion, correo)
                if nuevo_cliente.guardar():
                    resultados['clientes_creados'] += 1
                    
                    # --- Procesar Instancias del Cliente ---
                    lista_instancias = cliente_elem.find('listaInstancias')
                    if lista_instancias is not None:
                        for instancia_elem in lista_instancias:
                            id_inst = int(instancia_elem.get('id'))
                            id_config = int(instancia_elem.find('idConfiguracion').text)
                            nombre_inst = instancia_elem.find('nombre').text
                            fecha_inicio = extraer_fecha(instancia_elem.find('fechaInicio').text)
                            estado = instancia_elem.find('estado').text
                            fecha_final = None
                            if estado == 'Cancelada':
                                fecha_final_elem = instancia_elem.find('fechaFinal')
                                if fecha_final_elem is not None and fecha_final_elem.text:
                                    fecha_final = extraer_fecha(fecha_final_elem.text)
                            
                            print(f"    - Instancia {id_inst}: {nombre_inst} para cliente {nit}")
                            
                            nueva_instancia = Instancia(id_inst, nit, id_config, nombre_inst, fecha_inicio, estado, fecha_final)
                            if nueva_instancia.guardar():
                                resultados['instancias_creadas'] += 1
        
        print("=== PROCESAMIENTO COMPLETADO ===")
        print(f"Resultados: {resultados}")
        
        return jsonify({
            'success': True,
            'message': 'Mensaje de configuración procesado exitosamente',
            'resultados': resultados
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR DETALLADO: {error_details}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 400

@app.route('/consumo', methods=['POST'])
def consumo():
    try:
        print("=== INICIANDO PROCESAMIENTO CONSUMO ===")
        
        xml_data = request.get_data()
        print(f"Datos recibidos (primeros 200 chars): {xml_data[:200]}")
        
        xml_str = limpiar_xml(xml_data)
        print(f"XML limpio (primeros 200 chars): {xml_str[:200]}")
        
        if not xml_str:
            return jsonify({
                'success': False,
                'message': 'El archivo XML está vacío'
            }), 400
        
        root = ET.fromstring(xml_str)
        print(f"Elemento raíz encontrado: {root.tag}")
        
        consumos_procesados = 0
        
        # Buscar consumos directamente
        for consumo_elem in root.findall('consumo'):
            nit_cliente = consumo_elem.get('nitCliente')
            id_instancia = int(consumo_elem.get('idInstancia'))
            tiempo = float(consumo_elem.find('tiempo').text)
            
            fecha_hora_elem = consumo_elem.find('fechahora')
            if fecha_hora_elem is not None:
                fecha_hora_str = fecha_hora_elem.text
                fecha_hora = extraer_fecha_hora(fecha_hora_str)
                
                print(f"Procesando consumo: Instancia {id_instancia}, Cliente {nit_cliente}, Tiempo {tiempo}")
                
                nuevo_consumo = Consumo(id_instancia, nit_cliente, tiempo, fecha_hora)
                if nuevo_consumo.guardar():
                    consumos_procesados += 1
        
        print(f"Consumos procesados: {consumos_procesados}")
        
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

@app.route('/reset', methods=['DELETE'])
def reset_datos():
    try:
        # Crear estructura vacía
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

@app.route('/consultarDatos', methods=['GET'])
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

# --- APIs para operaciones individuales (usadas por el frontend) ---
@app.route('/crearRecurso', methods=['POST'])
def crear_recurso():
    try:
        data = request.get_json()
        r = Recurso(
            data['id'],
            data['nombre'],
            data['abreviatura'],
            data['metrica'],
            data['tipo'],
            float(data['valorXhora'])
        )
        if r.guardar():
            return jsonify({'success': True, 'recurso': r.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'No se pudo crear el recurso'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/crearCategoria', methods=['POST'])
def crear_categoria():
    try:
        data = request.get_json()
        c = Categoria(
            data['id'],
            data['nombre'],
            data['descripcion'],
            data['cargaTrabajo']
        )
        if c.guardar():
            return jsonify({'success': True, 'categoria': c.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'No se pudo crear la categoría'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/crearConfiguracion', methods=['POST'])
def crear_configuracion():
    try:
        data = request.get_json()
        conf = Configuracion(
            data['id'],
            data['nombre'],
            data['descripcion'],
            data['idCategoria']
        )
        if conf.guardar():
            return jsonify({'success': True, 'configuracion': conf.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'No se pudo crear la configuración'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/crearCliente', methods=['POST'])
def crear_cliente():
    try:
        data = request.get_json()
        cli = Cliente(
            data['nit'],
            data['nombre'],
            data['usuario'],
            data['clave'],
            data['direccion'],
            data['correoElectronico']
        )
        if cli.guardar():
            return jsonify({'success': True, 'cliente': cli.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'No se pudo crear el cliente'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/crearInstancia', methods=['POST'])
def crear_instancia():
    try:
        data = request.get_json()
        fecha_inicio = extraer_fecha(data['fechaInicio'])
        fecha_final = extraer_fecha(data['fechaFinal']) if data.get('fechaFinal') else None
        inst = Instancia(
            data['id'],
            data['idCliente'],
            data['idConfiguracion'],
            data['nombre'],
            fecha_inicio,
            data['estado'],
            fecha_final
        )
        if inst.guardar():
            return jsonify({'success': True, 'instancia': inst.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'No se pudo crear la instancia'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/cancelarInstancia', methods=['POST'])
def cancelar_instancia():
    try:
        data = request.get_json()
        id_instancia = data['id_instancia']
        fecha_cancelacion = extraer_fecha(data['fecha_cancelacion'])
        
        instancia = Instancia.obtener_por_id(id_instancia)
        if instancia:
            instancia.estado = 'Cancelada'
            instancia.fecha_final = fecha_cancelacion
            if instancia.guardar():
                return jsonify({
                    'success': True,
                    'message': f'Instancia {id_instancia} cancelada exitosamente'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': 'Error al guardar los cambios'
                })
        else:
            return jsonify({
                'success': False,
                'message': 'Instancia no encontrada'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 400

@app.route('/agregarRecursoConfiguracion', methods=['POST'])
def agregar_recurso_configuracion():
    try:
        data = request.get_json()
        id_configuracion = data['id_configuracion']
        id_recurso = data['id_recurso']
        cantidad = float(data['cantidad'])
        
        recurso_config = RecursoConfiguracion(id_configuracion, id_recurso, cantidad)
        if recurso_config.guardar():
            return jsonify({
                'success': True,
                'message': 'Recurso agregado a la configuración exitosamente'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Error al agregar recurso a la configuración'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 400

@app.route('/limpiarConsumosDuplicados', methods=['POST'])
def limpiar_consumos_duplicados():
    try:
        root = Recurso._obtener_root()
        consumos = root.find('consumos')
        
        # Encontrar consumos únicos
        consumos_unicos = {}
        for consumo in consumos.findall('consumo'):
            key = f"{consumo.get('idInstancia')}_{consumo.get('nitCliente')}_{consumo.find('fechaHora').text}"
            if key not in consumos_unicos:
                consumos_unicos[key] = consumo
        
        # Limpiar todos los consumos
        consumos.clear()
        
        # Agregar solo los consumos únicos
        for consumo in consumos_unicos.values():
            consumos.append(consumo)
        
        Recurso._guardar_xml(root)
        
        return jsonify({
            'success': True,
            'message': f'Consumos duplicados eliminados. Quedaron {len(consumos_unicos)} consumos únicos.'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 400

@app.route('/generarFactura', methods=['POST'])
def generar_factura():
    try:
        data = request.get_json()
        fecha_inicio = extraer_fecha(data['fechaInicio'])
        fecha_fin = extraer_fecha(data['fechaFin'])
        
        instancias = Instancia.obtener_todas()
        consumos = Consumo.obtener_todos()
        consumos_por_cliente = {}
        for c in consumos:
            if fecha_inicio <= c.fecha_hora <= fecha_fin:
                if c.nit_cliente not in consumos_por_cliente:
                    consumos_por_cliente[c.nit_cliente] = []
                consumos_por_cliente[c.nit_cliente].append(c)
        
        facturas_generadas = []
        for nit_cliente, lista_consumos in consumos_por_cliente.items():
            monto_total = 0.0
            detalles_factura = []
            for consumo in lista_consumos:
                instancia = Instancia.obtener_por_id(consumo.id_instancia)
                if instancia:
                    configuracion = Configuracion.obtener_por_id(instancia.id_configuracion)
                    if configuracion:
                        recursos_config = RecursoConfiguracion.obtener_por_configuracion(configuracion.id)
                        for recurso_conf in recursos_config:
                            recurso = Recurso.obtener_por_id(recurso_conf.id_recurso)
                            if recurso:
                                costo_recurso = recurso.valor_hora * recurso_conf.cantidad * consumo.tiempo_consumido
                                monto_total += costo_recurso
                                detalles_factura.append({
                                    'id_instancia': consumo.id_instancia,
                                    'nombre_instancia': instancia.nombre,
                                    'id_recurso': recurso.id,
                                    'nombre_recurso': recurso.nombre,
                                    'cantidad': recurso_conf.cantidad,
                                    'tiempo_consumido': consumo.tiempo_consumido,
                                    'costo_unitario': recurso.valor_hora,
                                    'costo_total': costo_recurso
                                })
            factura = Factura(nit_cliente, fecha_fin, monto_total, detalles_factura)
            factura.guardar()
            facturas_generadas.append(factura.to_dict())
        
        return jsonify({
            'success': True,
            'message': f'Se generaron {len(facturas_generadas)} facturas exitosamente',
            'facturas': facturas_generadas
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al generar facturas: {str(e)}'
        }), 500

# --- Rutas para consultas individuales ---
@app.route('/facturas', methods=['GET'])
def obtener_facturas():
    try:
        facturas = [f.to_dict() for f in Factura.obtener_todas()]
        return jsonify({'success': True, 'facturas': facturas})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/factura/<int:id_factura>', methods=['GET'])
def obtener_factura(id_factura):
    try:
        factura = Factura.obtener_por_id(id_factura)
        if factura:
            return jsonify({'success': True, 'factura': factura.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'Factura no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/instancia/<int:id_instancia>', methods=['GET'])
def obtener_instancia(id_instancia):
    try:
        instancia = Instancia.obtener_por_id(id_instancia)
        if instancia:
            return jsonify({'success': True, 'instancia': instancia.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'Instancia no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/configuracion/<int:id_configuracion>', methods=['GET'])
def obtener_configuracion(id_configuracion):
    try:
        configuracion = Configuracion.obtener_por_id(id_configuracion)
        if configuracion:
            return jsonify({'success': True, 'configuracion': configuracion.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'Configuración no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/categoria/<int:id_categoria>', methods=['GET'])
def obtener_categoria(id_categoria):
    try:
        categoria = Categoria.obtener_por_id(id_categoria)
        if categoria:
            return jsonify({'success': True, 'categoria': categoria.to_dict()})
        else:
            return jsonify({'success': False, 'message': 'Categoría no encontrada'}), 404
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/recursos-configuracion/<int:id_configuracion>', methods=['GET'])
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

if __name__ == '__main__':
    print("=== INICIANDO SERVIDOR BACKEND ===")
    app.run(debug=True, host='0.0.0.0', port=5000)