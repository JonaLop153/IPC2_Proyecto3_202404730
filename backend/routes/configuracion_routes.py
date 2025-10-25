from flask import request, jsonify
import xml.etree.ElementTree as ET
from models import Recurso, Categoria, Configuracion, Cliente, Instancia, RecursoConfiguracion
from utils import extraer_fecha, limpiar_xml 
def configurar():
    try:
        print("=== INICIANDO PROCESAMIENTO CONFIGURACIÓN ===")
        
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
        
        resultados = {
            'clientes_creados': 0,
            'instancias_creadas': 0,
            'recursos_creados': 0,
            'categorias_creadas': 0,
            'configuraciones_creadas': 0
        }
        
        # ... (el resto del código igual)
        
        # Procesar Recursos
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
        
        # Procesar Categorías
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
                                
                                recursos_config = config_elem.find('recursosConfiguracion')
                                if recursos_config is not None:
                                    for recurso_conf in recursos_config:
                                        id_recurso_conf = int(recurso_conf.get('id'))
                                        cantidad = float(recurso_conf.text)
                                        print(f"      - Recurso config {id_recurso_conf}: {cantidad}")
                                        
                                        nueva_asoc = RecursoConfiguracion(id_config, id_recurso_conf, cantidad)
                                        nueva_asoc.guardar()
        
        # Procesar Clientes
        lista_clientes = root.find('listaClientes')
        if lista_clientes is not None:
            print(f"Procesando {len(lista_clientes)} clientes")
            for cliente_elem in lista_clientes:
                nit = cliente_elem.get('nit')
                nombre = cliente_elem.find('nombre').text
                usuario = cliente_elem.find('usuario').text
                clave = cliente_elem.find('clave').text
                direccion = cliente_elem.find('direccion').text
                correo = cliente_elem.find('correoElectronico').text
                
                print(f"  - Cliente {nit}: {nombre}")
                
                nuevo_cliente = Cliente(nit, nombre, usuario, clave, direccion, correo)
                if nuevo_cliente.guardar():
                    resultados['clientes_creados'] += 1
                    
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