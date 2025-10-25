from flask import request, jsonify
from models import Recurso, Categoria, Configuracion, Cliente, Instancia, RecursoConfiguracion
from utils import extraer_fecha

def crear_recurso():
    try:
        data = request.get_json()
        
        recurso_existente = Recurso.obtener_por_id(data['id'])
        if recurso_existente:
            return jsonify({
                'success': False,
                'message': f'Ya existe un recurso con el ID {data["id"]}'
            }), 400
        
        r = Recurso(
            data['id'],
            data['nombre'],
            data['abreviatura'],
            data['metrica'],
            data['tipo'],
            float(data['valorXhora'])
        )
        if r.guardar():
            return jsonify({
                'success': True, 
                'message': 'Recurso creado exitosamente',
                'recurso': r.to_dict()
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'No se pudo crear el recurso'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error: {str(e)}'
        }), 400

def crear_categoria():
    try:
        data = request.get_json()
        
        categoria_existente = Categoria.obtener_por_id(data['id'])
        if categoria_existente:
            return jsonify({
                'success': False,
                'message': f'Ya existe una categoría con el ID {data["id"]}'
            }), 400
        
        c = Categoria(
            data['id'],
            data['nombre'],
            data['descripcion'],
            data['cargaTrabajo']
        )
        if c.guardar():
            return jsonify({
                'success': True, 
                'message': 'Categoría creada exitosamente',
                'categoria': c.to_dict()
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'No se pudo crear la categoría'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error: {str(e)}'
        }), 400

def crear_configuracion():
    try:
        data = request.get_json()
        
        config_existente = Configuracion.obtener_por_id(data['id'])
        if config_existente:
            return jsonify({
                'success': False,
                'message': f'Ya existe una configuración con el ID {data["id"]}'
            }), 400
        
        categoria = Categoria.obtener_por_id(data['idCategoria'])
        if not categoria:
            return jsonify({
                'success': False,
                'message': f'No existe la categoría con ID {data["idCategoria"]}'
            }), 400
        
        conf = Configuracion(
            data['id'],
            data['nombre'],
            data['descripcion'],
            data['idCategoria']
        )
        if conf.guardar():
            return jsonify({
                'success': True, 
                'message': 'Configuración creada exitosamente',
                'configuracion': conf.to_dict()
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'No se pudo crear la configuración'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error: {str(e)}'
        }), 400

def crear_cliente():
    try:
        data = request.get_json()
        
        cliente_existente = Cliente.obtener_por_nit(data['nit'])
        if cliente_existente:
            return jsonify({
                'success': False,
                'message': f'Ya existe un cliente con el NIT {data["nit"]}'
            }), 400
        
        cli = Cliente(
            data['nit'],
            data['nombre'],
            data['usuario'],
            data['clave'],
            data['direccion'],
            data['correoElectronico']
        )
        if cli.guardar():
            return jsonify({
                'success': True, 
                'message': 'Cliente creado exitosamente',
                'cliente': cli.to_dict()
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'No se pudo crear el cliente'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error: {str(e)}'
        }), 400

def crear_instancia():
    try:
        data = request.get_json()
        
        instancia_existente = Instancia.obtener_por_id(data['id'])
        if instancia_existente:
            return jsonify({
                'success': False,
                'message': f'Ya existe una instancia con el ID {data["id"]}'
            }), 400
        
        cliente = Cliente.obtener_por_nit(data['idCliente'])
        if not cliente:
            return jsonify({
                'success': False,
                'message': f'No existe el cliente con NIT {data["idCliente"]}'
            }), 400
        
        configuracion = Configuracion.obtener_por_id(data['idConfiguracion'])
        if not configuracion:
            return jsonify({
                'success': False,
                'message': f'No existe la configuración con ID {data["idConfiguracion"]}'
            }), 400
        
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
            return jsonify({
                'success': True, 
                'message': 'Instancia creada exitosamente',
                'instancia': inst.to_dict()
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'No se pudo crear la instancia'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False, 
            'message': f'Error: {str(e)}'
        }), 400

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

def limpiar_consumos_duplicados():
    try:
        root = Recurso._obtener_root()
        consumos = root.find('consumos')
        
        consumos_unicos = {}
        for consumo in consumos.findall('consumo'):
            key = f"{consumo.get('idInstancia')}_{consumo.get('nitCliente')}_{consumo.find('fechaHora').text}"
            if key not in consumos_unicos:
                consumos_unicos[key] = consumo
        
        consumos.clear()
        
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