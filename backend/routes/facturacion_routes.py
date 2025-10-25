from flask import request, jsonify
from models import Instancia, Consumo, Factura, Configuracion, Recurso, RecursoConfiguracion
from utils import extraer_fecha
from datetime import datetime, timedelta

def generar_factura():
    try:
        data = request.get_json()
        fecha_inicio = extraer_fecha(data['fechaInicio'])
        fecha_fin = extraer_fecha(data['fechaFin'])
        
        # ✅ CORREGIDO: Ajustar las fechas para incluir todo el día
        fecha_inicio = fecha_inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_fin.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        print(f"=== GENERANDO FACTURAS: {fecha_inicio} a {fecha_fin} ===")
        
        # Obtener todos los datos necesarios
        instancias = Instancia.obtener_todas()
        consumos = Consumo.obtener_todos()
        facturas_existentes = Factura.obtener_todas()
        
        print(f"Instancias encontradas: {len(instancias)}")
        print(f"Consumos encontrados: {len(consumos)}")
        print(f"Facturas existentes: {len(facturas_existentes)}")
        
        # DEBUG: Mostrar info de consumos
        for i, consumo in enumerate(consumos):
            print(f"Consumo {i+1}: Instancia {consumo.id_instancia}, Fecha: {consumo.fecha_hora}, Tiempo: {consumo.tiempo_consumido}")
        
        # Obtener consumos ya facturados
        consumos_facturados = set()
        for factura in facturas_existentes:
            for detalle in factura.detalles:
                key = f"{detalle['id_instancia']}_{detalle['id_recurso']}_{detalle['tiempo_consumido']}_{detalle.get('fecha_consumo', '')}"
                consumos_facturados.add(key)
        
        print(f"Consumos ya facturados: {len(consumos_facturados)}")
        
        # Agrupar consumos no facturados por cliente en el rango de fechas
        consumos_por_cliente = {}
        consumos_en_rango = 0
        
        for consumo in consumos:
            # Verificar que el consumo esté en el rango (✅ ahora incluye todo el día)
            if fecha_inicio <= consumo.fecha_hora <= fecha_fin:
                print(f"✅ Consumo en rango: {consumo.id_instancia} - {consumo.fecha_hora}")
                consumos_en_rango += 1
                
                instancia = Instancia.obtener_por_id(consumo.id_instancia)
                if instancia and instancia.estado == 'Vigente':
                    # Crear clave única para este consumo
                    key = f"{consumo.id_instancia}_{consumo.nit_cliente}_{consumo.fecha_hora}_{consumo.tiempo_consumido}"
                    
                    if key not in consumos_facturados:
                        if consumo.nit_cliente not in consumos_por_cliente:
                            consumos_por_cliente[consumo.nit_cliente] = []
                        consumos_por_cliente[consumo.nit_cliente].append(consumo)
                        print(f"  ✅ Agregado a facturación: Cliente {consumo.nit_cliente}")
                    else:
                        print(f"  ❌ Ya facturado: {key}")
                else:
                    estado = instancia.estado if instancia else "No encontrada"
                    print(f"  ❌ Instancia no vigente: {consumo.id_instancia} (estado: {estado})")
            else:
                print(f"❌ Consumo fuera de rango: {consumo.fecha_hora} (rango: {fecha_inicio} a {fecha_fin})")
        
        print(f"Consumos en rango de fecha: {consumos_en_rango}")
        print(f"Clientes con consumos a facturar: {len(consumos_por_cliente)}")
        
        facturas_generadas = []
        
        for nit_cliente, lista_consumos in consumos_por_cliente.items():
            print(f"Procesando cliente: {nit_cliente} con {len(lista_consumos)} consumos")
            
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
                        print(f"  Configuración {configuracion.id} tiene {len(recursos_config)} recursos")
                        
                        for recurso_conf in recursos_config:
                            recurso = Recurso.obtener_por_id(recurso_conf.id_recurso)
                            if recurso:
                                # Calcular costo para este consumo específico
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
                                
                                print(f"    Recurso {recurso.nombre}: {recurso_conf.cantidad} × {recurso.valor_hora} × {consumo.tiempo_consumido} = {costo_recurso}")
            
            if detalles_factura:
                fecha_emision = datetime.now()
                factura = Factura(nit_cliente, fecha_emision, monto_total, detalles_factura)
                if factura.guardar():
                    facturas_generadas.append(factura.to_dict())
                    print(f"✅ Factura generada para cliente {nit_cliente}: ${monto_total:.2f}")
            else:
                print(f"❌ No hay detalles para facturar al cliente {nit_cliente}")
        
        print(f"=== FACTURACIÓN COMPLETADA: {len(facturas_generadas)} facturas generadas ===")
        
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