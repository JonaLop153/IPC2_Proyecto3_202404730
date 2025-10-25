from flask import request, jsonify
from models import Instancia, Consumo, Factura, Configuracion, Recurso, RecursoConfiguracion
from utils import extraer_fecha
from datetime import datetime, timedelta

def generar_factura():
    try:
        data = request.get_json()
        fecha_inicio = extraer_fecha(data['fechaInicio'])
        fecha_fin = extraer_fecha(data['fechaFin'])
        
        print(f"=== GENERANDO FACTURAS: {fecha_inicio} a {fecha_fin} ===")
        
        instancias = Instancia.obtener_todas()
        consumos = Consumo.obtener_todos()
        facturas_existentes = Factura.obtener_todas()
        
        print(f"Instancias encontradas: {len(instancias)}")
        print(f"Consumos encontrados: {len(consumos)}")
        print(f"Facturas existentes: {len(facturas_existentes)}")
        
        # Listar todos los consumos para debug
        for i, consumo in enumerate(consumos):
            print(f"Consumo {i+1}: Instancia {consumo.id_instancia}, Fecha: {consumo.fecha_hora}, Tiempo: {consumo.tiempo_consumido}")
        
        consumos_facturados = set()
        for factura in facturas_existentes:
            for detalle in factura.detalles:
                key = f"{detalle['id_instancia']}_{detalle['id_recurso']}_{detalle['tiempo_consumido']}"
                consumos_facturados.add(key)
        
        consumos_por_cliente = {}
        for consumo in consumos:
            # Verificar que el consumo esté en el rango y no esté facturado
            if fecha_inicio <= consumo.fecha_hora <= fecha_fin:
                print(f"✅ Consumo en rango: {consumo.id_instancia} - {consumo.fecha_hora}")
                
                instancia = Instancia.obtener_por_id(consumo.id_instancia)
                if instancia:
                    print(f"  🔍 Instancia {instancia.id} encontrada, estado: {instancia.estado}")
                    
                    # ✅ CORREGIDO: Comparar con el valor exacto del XML
                    if instancia.estado == 'VIGENTE':  # ← USAR 'VIGENTE' en mayúsculas
                        key = f"{consumo.id_instancia}_{consumo.id_instancia}_{consumo.tiempo_consumido}"
                        if key not in consumos_facturados:
                            if consumo.nit_cliente not in consumos_por_cliente:
                                consumos_por_cliente[consumo.nit_cliente] = []
                            consumos_por_cliente[consumo.nit_cliente].append(consumo)
                            print("  ✅ Consumo agregado para facturación")
                        else:
                            print("  ⚠️ Consumo ya facturado")
                    else:
                        print(f"  ❌ Instancia no vigente: {instancia.id} (estado: {instancia.estado})")
                else:
                    print(f"  ❌ Instancia no encontrada: {consumo.id_instancia}")
            else:
                print(f"❌ Consumo fuera de rango: {consumo.id_instancia} - {consumo.fecha_hora}")
        
        print(f"Consumos en rango de fecha: {len([c for c in consumos if fecha_inicio <= c.fecha_hora <= fecha_fin])}")
        print(f"Clientes con consumos a facturar: {len(consumos_por_cliente)}")
        
        facturas_generadas = []
        for nit_cliente, lista_consumos in consumos_por_cliente.items():
            if not lista_consumos:
                continue
                
            monto_total = 0.0
            detalles_factura = []
            
            print(f"💰 Procesando factura para cliente {nit_cliente} con {len(lista_consumos)} consumos")
            
            for consumo in lista_consumos:
                instancia = Instancia.obtener_por_id(consumo.id_instancia)
                if instancia:
                    configuracion = Configuracion.obtener_por_id(instancia.id_configuracion)
                    if configuracion:
                        print(f"  📋 Configuración encontrada: {configuracion.nombre}")
                        recursos_config = RecursoConfiguracion.obtener_por_configuracion(configuracion.id)
                        print(f"  🔧 Recursos en configuración: {len(recursos_config)}")
                        
                        for recurso_conf in recursos_config:
                            recurso = Recurso.obtener_por_id(recurso_conf.id_recurso)
                            if recurso:
                                # Calcular costo para este consumo específico
                                costo_recurso = recurso.valor_hora * recurso_conf.cantidad * consumo.tiempo_consumido
                                monto_total += costo_recurso
                                
                                print(f"    💰 Recurso {recurso.nombre}: {recurso_conf.cantidad} × {recurso.valor_hora} × {consumo.tiempo_consumido} = {costo_recurso}")
                                
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
                    print(f"✅ Factura generada para cliente {nit_cliente}: Q{monto_total:.2f}")
        
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