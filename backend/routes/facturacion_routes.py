from flask import request, jsonify
from models import Instancia, Consumo, Factura, Configuracion, Recurso, RecursoConfiguracion
from utils import extraer_fecha
from datetime import datetime

def generar_factura():
    try:
        data = request.get_json()
        fecha_inicio = extraer_fecha(data['fechaInicio'])
        fecha_fin = extraer_fecha(data['fechaFin'])
        
        print(f"=== GENERANDO FACTURAS: {fecha_inicio} a {fecha_fin} ===")
        
        instancias = Instancia.obtener_todas()
        consumos = Consumo.obtener_todos()
        facturas_existentes = Factura.obtener_todas()
        
        consumos_facturados = set()
        for factura in facturas_existentes:
            for detalle in factura.detalles:
                key = f"{detalle['id_instancia']}_{detalle['id_recurso']}_{detalle['tiempo_consumido']}"
                consumos_facturados.add(key)
        
        consumos_por_cliente = {}
        for consumo in consumos:
            if fecha_inicio <= consumo.fecha_hora <= fecha_fin:
                instancia = Instancia.obtener_por_id(consumo.id_instancia)
                if instancia and instancia.estado == 'Vigente':
                    key = f"{consumo.id_instancia}_{consumo.id_instancia}_{consumo.tiempo_consumido}"
                    if key not in consumos_facturados:
                        if consumo.nit_cliente not in consumos_por_cliente:
                            consumos_por_cliente[consumo.nit_cliente] = []
                        consumos_por_cliente[consumo.nit_cliente].append(consumo)
        
        facturas_generadas = []
        for nit_cliente, lista_consumos in consumos_por_cliente.items():
            if not lista_consumos:
                continue
                
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
                                    'costo_total': costo_recurso,
                                    'fecha_consumo': consumo.fecha_hora.strftime('%d/%m/%Y %H:%M')
                                })
            
            if detalles_factura:
                fecha_emision = datetime.now()
                factura = Factura(nit_cliente, fecha_emision, monto_total, detalles_factura)
                if factura.guardar():
                    facturas_generadas.append(factura.to_dict())
                    print(f"Factura generada para cliente {nit_cliente}: ${monto_total:.2f}")
        
        return jsonify({
            'success': True,
            'message': f'Se generaron {len(facturas_generadas)} facturas exitosamente',
            'facturas': facturas_generadas
        })
        
    except Exception as e:
        import traceback
        print(f"ERROR en facturación: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'message': f'Error al generar facturas: {str(e)}'
        }), 500