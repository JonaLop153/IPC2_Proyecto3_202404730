from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import requests
from datetime import datetime
from .forms import (
    ConfiguracionForm, ConsumoForm, FechaRangoForm,
    CrearRecursoForm, CrearCategoriaForm, CrearConfiguracionForm,
    CrearClienteForm, CrearInstanciaForm, FacturaForm
)
import json

# URL del backend Flask
BACKEND_URL = 'http://localhost:5000'

def index(request):
    return render(request, 'core/inicio.html')

def enviar_mensaje_configuracion(request):
    if request.method == 'POST':
        form = ConfiguracionForm(request.POST, request.FILES)
        if form.is_valid():
            xml_file = request.FILES['xml_file']
            try:
                xml_content = xml_file.read()
                if not xml_content.strip():
                    context = {'form': form, 'error': 'El archivo XML está vacío.'}
                else:
                    response = requests.post(
                        'http://localhost:5000/configurar',
                        data=xml_content,
                        headers={'Content-Type': 'application/xml'}
                    )
                    result = response.json()
                    if result.get('success'):
                        context = {
                            'form': form,
                            'success': True,
                            'message': result.get('message', 'Mensaje procesado exitosamente'),
                            'resultados': result.get('resultados', {})
                        }
                    else:
                        context = {'form': form, 'error': result.get('message', 'Error desconocido')}
            except requests.exceptions.ConnectionError:
                context = {'form': form, 'error': 'No se pudo conectar con el backend. ¿Está corriendo en el puerto 5000?'}
            except Exception as e:
                context = {'form': form, 'error': f'Error: {str(e)}'}
        else:
            context = {'form': form, 'error': 'Formulario inválido'}
    else:
        form = ConfiguracionForm()
        context = {'form': form}
    return render(request, 'core/config_message.html', context)

def enviar_mensaje_consumo(request):
    if request.method == 'POST':
        form = ConsumoForm(request.POST, request.FILES)
        if form.is_valid():
            xml_file = request.FILES['xml_file']
            try:
                xml_content = xml_file.read()
                if not xml_content.strip():
                    context = {'form': form, 'error': 'El archivo XML está vacío.'}
                else:
                    response = requests.post(
                        'http://localhost:5000/consumo',
                        data=xml_content,
                        headers={'Content-Type': 'application/xml'}
                    )
                    result = response.json()
                    if result.get('success'):
                        context = {
                            'form': form,
                            'success': True,
                            'message': result.get('message', 'Mensaje procesado exitosamente'),
                            'consumos_procesados': result.get('consumos_procesados', 0)
                        }
                    else:
                        context = {'form': form, 'error': result.get('message', 'Error desconocido')}
            except requests.exceptions.ConnectionError:
                context = {'form': form, 'error': 'No se pudo conectar con el backend.'}
            except Exception as e:  # ✅ CORREGIDO: Especificar el tipo de excepción
                context = {'form': form, 'error': f'Error: {str(e)}'}
        else:
            context = {'form': form, 'error': 'Formulario inválido'}
    else:
        form = ConsumoForm()
        context = {'form': form}
    return render(request, 'core/consumption_message.html', context)

def operaciones_sistema(request):
    context = {}
    
    # Obtener datos para mostrar en consultas
    try:
        response = requests.get(f'{BACKEND_URL}/consultarDatos')
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                context['datos_sistema'] = result['data']
    except Exception:  # ✅ CORREGIDO: Especificar el tipo de excepción
        pass 
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'inicializar':
            try:
                response = requests.delete(f'{BACKEND_URL}/reset')
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        context['message'] = result.get('message', 'Sistema inicializado correctamente')
                        context['datos_sistema'] = None
                    else:
                        context['error'] = result.get('message', 'Error desconocido')
                else:
                    context['error'] = 'Error al inicializar el sistema'
            except Exception as e:
                context['error'] = f'Error al conectar con el backend: {str(e)}'
        
        elif action == 'consultar':
            pass
        
        elif action == 'crear_recurso':
            form = CrearRecursoForm(request.POST)
            if form.is_valid():
                data = {
                    'id': form.cleaned_data['id'],
                    'nombre': form.cleaned_data['nombre'],
                    'abreviatura': form.cleaned_data['abreviatura'],
                    'metrica': form.cleaned_data['metrica'],
                    'tipo': form.cleaned_data['tipo'],
                    'valorXhora': float(form.cleaned_data['valorXhora'])
                }
                
                try:
                    response = requests.post(f'{BACKEND_URL}/crearRecurso', json=data)
                    result = response.json()
                    
                    if result.get('success'):
                        context['message'] = result.get('message', 'Recurso creado exitosamente')
                        response = requests.get(f'{BACKEND_URL}/consultarDatos')
                        if response.status_code == 200:
                            result_data = response.json()
                            if result_data.get('success'):
                                context['datos_sistema'] = result_data['data']
                    else:
                        context['error'] = result.get('message', 'Error desconocido al crear recurso')
                except Exception as e:
                    context['error'] = f'Error al conectar con el backend: {str(e)}'
            else:
                context['error'] = 'Formulario inválido'
        
        elif action == 'crear_categoria':
            form = CrearCategoriaForm(request.POST)
            if form.is_valid():
                data = {
                    'id': form.cleaned_data['id'],
                    'nombre': form.cleaned_data['nombre'],
                    'descripcion': form.cleaned_data['descripcion'],
                    'cargaTrabajo': form.cleaned_data['cargaTrabajo']
                }
                
                try:
                    response = requests.post(f'{BACKEND_URL}/crearCategoria', json=data)
                    result = response.json()
                    
                    if result.get('success'):
                        context['message'] = result.get('message', 'Categoría creada exitosamente')
                        response = requests.get(f'{BACKEND_URL}/consultarDatos')
                        if response.status_code == 200:
                            result_data = response.json()
                            if result_data.get('success'):
                                context['datos_sistema'] = result_data['data']
                    else:
                        context['error'] = result.get('message', 'Error desconocido al crear categoría')
                except Exception as e:
                    context['error'] = f'Error al conectar con el backend: {str(e)}'
            else:
                context['error'] = 'Formulario inválido'
        
        elif action == 'crear_configuracion':
            form = CrearConfiguracionForm(request.POST)
            if form.is_valid():
                data = {
                    'id': form.cleaned_data['id'],
                    'nombre': form.cleaned_data['nombre'],
                    'descripcion': form.cleaned_data['descripcion'],
                    'idCategoria': form.cleaned_data['idCategoria']
                }
                
                try:
                    response = requests.post(f'{BACKEND_URL}/crearConfiguracion', json=data)
                    result = response.json()
                    
                    if result.get('success'):
                        context['message'] = result.get('message', 'Configuración creada exitosamente')
                        response = requests.get(f'{BACKEND_URL}/consultarDatos')
                        if response.status_code == 200:
                            result_data = response.json()
                            if result_data.get('success'):
                                context['datos_sistema'] = result_data['data']
                    else:
                        context['error'] = result.get('message', 'Error desconocido al crear configuración')
                except Exception as e:
                    context['error'] = f'Error al conectar con el backend: {str(e)}'
            else:
                context['error'] = 'Formulario inválido'
        
        elif action == 'crear_cliente':
            form = CrearClienteForm(request.POST)
            if form.is_valid():
                data = {
                    'nit': form.cleaned_data['nit'],
                    'nombre': form.cleaned_data['nombre'],
                    'usuario': form.cleaned_data['usuario'],
                    'clave': form.cleaned_data['clave'],
                    'direccion': form.cleaned_data['direccion'],
                    'correoElectronico': form.cleaned_data['correoElectronico']
                }
                
                try:
                    response = requests.post(f'{BACKEND_URL}/crearCliente', json=data)
                    result = response.json()
                    
                    if result.get('success'):
                        context['message'] = result.get('message', 'Cliente creado exitosamente')
                        response = requests.get(f'{BACKEND_URL}/consultarDatos')
                        if response.status_code == 200:
                            result_data = response.json()
                            if result_data.get('success'):
                                context['datos_sistema'] = result_data['data']
                    else:
                        context['error'] = result.get('message', 'Error desconocido al crear cliente')
                except Exception as e:
                    context['error'] = f'Error al conectar con el backend: {str(e)}'
            else:
                context['error'] = 'Formulario inválido'
        
        elif action == 'crear_instancia':
            form = CrearInstanciaForm(request.POST)
            if form.is_valid():
                data = {
                    'id': form.cleaned_data['id'],
                    'idCliente': form.cleaned_data['idCliente'],
                    'idConfiguracion': form.cleaned_data['idConfiguracion'],
                    'nombre': form.cleaned_data['nombre'],
                    'fechaInicio': form.cleaned_data['fechaInicio'],
                    'estado': form.cleaned_data['estado'],
                }
                
                if form.cleaned_data['estado'] == 'Cancelada' and form.cleaned_data.get('fechaFinal'):
                    data['fechaFinal'] = form.cleaned_data['fechaFinal']
                
                try:
                    response = requests.post(f'{BACKEND_URL}/crearInstancia', json=data)
                    result = response.json()
                    
                    if result.get('success'):
                        context['message'] = result.get('message', 'Instancia creada exitosamente')
                        response = requests.get(f'{BACKEND_URL}/consultarDatos')
                        if response.status_code == 200:
                            result_data = response.json()
                            if result_data.get('success'):
                                context['datos_sistema'] = result_data['data']
                    else:
                        context['error'] = result.get('message', 'Error desconocido al crear instancia')
                except Exception as e:
                    context['error'] = f'Error al conectar con el backend: {str(e)}'
            else:
                context['error'] = 'Formulario inválido'
        
        elif action == 'cancelar_instancia':
            id_instancia = request.POST.get('id_instancia')
            fecha_cancelacion = request.POST.get('fecha_cancelacion')
            
            if id_instancia and fecha_cancelacion:
                try:
                    data = {
                        'id_instancia': int(id_instancia),
                        'fecha_cancelacion': fecha_cancelacion
                    }
                    response = requests.post(f'{BACKEND_URL}/cancelarInstancia', json=data)
                    result = response.json()
                    
                    if result.get('success'):
                        context['message'] = result.get('message', 'Instancia cancelada exitosamente')
                        response = requests.get(f'{BACKEND_URL}/consultarDatos')
                        if response.status_code == 200:
                            result_data = response.json()
                            if result_data.get('success'):
                                context['datos_sistema'] = result_data['data']
                    else:
                        context['error'] = result.get('message', 'Error desconocido al cancelar instancia')
                except Exception as e:
                    context['error'] = f'Error al conectar con el backend: {str(e)}'
            else:
                context['error'] = 'Datos incompletos para cancelar instancia'
        
        elif action == 'limpiar_consumos':
            try:
                response = requests.post(f'{BACKEND_URL}/limpiarConsumosDuplicados')
                result = response.json()
                
                if result.get('success'):
                    context['message'] = result.get('message', 'Consumos duplicados eliminados')
                    response = requests.get(f'{BACKEND_URL}/consultarDatos')
                    if response.status_code == 200:
                        result_data = response.json()
                        if result_data.get('success'):
                            context['datos_sistema'] = result_data['data']
                else:
                    context['error'] = result.get('message', 'Error al limpiar consumos')
            except Exception as e:
                context['error'] = f'Error al conectar con el backend: {str(e)}'
    
    context.update({
        'crear_recurso_form': CrearRecursoForm(),
        'crear_categoria_form': CrearCategoriaForm(),
        'crear_configuracion_form': CrearConfiguracionForm(),
        'crear_cliente_form': CrearClienteForm(),
        'crear_instancia_form': CrearInstanciaForm()
    })
    
    return render(request, 'core/operations.html', context)

def proceso_facturacion(request):
    if request.method == 'POST':
        form = FacturaForm(request.POST)
        if form.is_valid():
            data = {
                'fechaInicio': form.cleaned_data['fechaInicio'],
                'fechaFin': form.cleaned_data['fechaFin']
            }
            
            try:
                response = requests.post(f'{BACKEND_URL}/generarFactura', json=data)
                result = response.json()
                
                if result.get('success'):
                    context = {
                        'form': form,
                        'success': True,
                        'message': result.get('message', 'Facturas generadas exitosamente'),
                        'facturas': result.get('facturas', [])
                    }
                else:
                    context = {
                        'form': form,
                        'error': result.get('message', 'Error al generar facturas')
                    }
            except Exception as e:
                context = {
                    'form': form,
                    'error': f'Error al conectar con el backend: {str(e)}'
                }
        else:
            context = {'form': form, 'error': 'Formulario inválido'}
    else:
        form = FacturaForm()
        context = {'form': form}
    
    return render(request, 'core/facturacion.html', context)

def reportes_pdf(request):
    return render(request, 'core/reportes.html')

def detalle_factura(request):
    print("🔍 Vista detalle_factura llamada")  # Debug
    
    # Siempre obtener la lista de facturas
    try:
        response = requests.get(f'{BACKEND_URL}/facturas')
        result = response.json()
        
        if result.get('success'):
            facturas = result['facturas']
            print(f"📊 Facturas obtenidas del backend: {len(facturas)}")  # Debug
            for factura in facturas:
                print(f"   - Factura {factura['id']}: {factura['nitCliente']} - Q{factura['montoTotal']}")
        else:
            facturas = []
            print(f"❌ Error al obtener facturas: {result.get('message')}")  # Debug
    except Exception as e:
        facturas = []
        print(f"❌ Error de conexión al obtener facturas: {str(e)}")  # Debug
    
    # Inicializar contexto
    context = {
        'facturas': facturas,
        'factura': None,
        'total_instancias': 0,
        'total_recursos': 0
    }
    
    # Si es POST, procesar la factura seleccionada
    if request.method == 'POST':
        factura_id = request.POST.get('factura_id')
        print(f"📋 Factura seleccionada: {factura_id}")  # Debug
        
        if factura_id:
            try:
                response = requests.get(f'{BACKEND_URL}/factura/{factura_id}')
                result = response.json()
                
                if result.get('success'):
                    factura = result['factura']
                    print(f"✅ Factura encontrada: ID {factura['id']}")  # Debug
                    print(f"📋 Detalles de la factura: {len(factura.get('detalles', []))} items")  # Debug
                    
                    # Calcular métricas
                    instancias_unicas = set()
                    recursos_unicos = set()
                    
                    for detalle in factura.get('detalles', []):
                        instancias_unicas.add(detalle['id_instancia'])
                        recursos_unicos.add(detalle['id_recurso'])
                    
                    context.update({
                        'factura': factura,
                        'total_instancias': len(instancias_unicas),
                        'total_recursos': len(recursos_unicos),
                        'factura_seleccionada_id': factura_id  # Para mantener la selección
                    })
                    
                    print(f"📊 Métricas calculadas: {len(instancias_unicas)} instancias, {len(recursos_unicos)} recursos")
                    
                else:
                    error_msg = result.get('message', 'Error al obtener factura')
                    print(f"❌ Error: {error_msg}")  # Debug
                    context['error'] = error_msg
                    
            except Exception as e:
                error_msg = f'Error al conectar con el backend: {str(e)}'
                print(f"❌ Error: {error_msg}")  # Debug
                context['error'] = error_msg
        else:
            context['error'] = 'Por favor seleccione una factura'
    
    return render(request, 'core/detalle_factura.html', context)

def analisis_ventas(request):
    if request.method == 'POST':
        form = FechaRangoForm(request.POST)
        if form.is_valid():
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            
            print(f"📊 Análisis de ventas solicitado: {fecha_inicio} a {fecha_fin}")  # Debug
            
            try:
                # Obtener todas las facturas
                response = requests.get(f'{BACKEND_URL}/facturas')
                result = response.json()
                
                if result.get('success'):
                    facturas = result['facturas']
                    facturas_rango = []
                    
                    print(f"📋 Total de facturas disponibles: {len(facturas)}")  # Debug
                    
                    for factura in facturas:
                        fecha_emision_str = factura['fechaEmision']
                        print(f"   - Factura {factura['id']}: Fecha emisión string = '{fecha_emision_str}'")  # Debug
                        
                        try:
                            # Intentar parsear la fecha
                            fecha_emision = datetime.strptime(fecha_emision_str, '%d/%m/%Y').date()
                            print(f"     Fecha parseada: {fecha_emision}")  # Debug
                            
                            if fecha_inicio <= fecha_emision <= fecha_fin:
                                facturas_rango.append(factura)
                                print(f"     ✅ EN RANGO")  # Debug
                            else:
                                print(f"     ❌ FUERA DE RANGO (buscando {fecha_inicio} a {fecha_fin})")  # Debug
                                
                        except ValueError as e:
                            print(f"     ❌ ERROR parseando fecha: {e}")  # Debug
                            continue
                    
                    print(f"📊 Facturas en rango: {len(facturas_rango)}")  # Debug
                    
                    if facturas_rango:
                        # Análisis por categorías y configuraciones
                        categorias_ingresos = {}
                        configuraciones_ingresos = {}
                        recursos_ingresos = {}
                        
                        for factura in facturas_rango:
                            print(f"📋 Procesando factura {factura['id']} con {len(factura['detalles'])} detalles")  # Debug
                            
                            for detalle in factura['detalles']:
                                # Obtener configuración
                                instancia = get_instancia_by_id(detalle['id_instancia'])
                                if instancia:
                                    configuracion = get_configuracion_by_id(instancia['idConfiguracion'])
                                    if configuracion:
                                        categoria = get_categoria_by_id(configuracion['idCategoria'])
                                        
                                        # Categorías
                                        if categoria:
                                            cat_nombre = categoria['nombre']
                                            if cat_nombre not in categorias_ingresos:
                                                categorias_ingresos[cat_nombre] = 0
                                            categorias_ingresos[cat_nombre] += detalle['costo_total']
                                        
                                        # Configuraciones
                                        conf_nombre = configuracion['nombre']
                                        if conf_nombre not in configuraciones_ingresos:
                                            configuraciones_ingresos[conf_nombre] = 0
                                        configuraciones_ingresos[conf_nombre] += detalle['costo_total']
                                
                                # Recursos
                                recurso_nombre = detalle['nombre_recurso']
                                if recurso_nombre not in recursos_ingresos:
                                    recursos_ingresos[recurso_nombre] = 0
                                recursos_ingresos[recurso_nombre] += detalle['costo_total']
                        
                        total_ingresos_valor = sum([f['montoTotal'] for f in facturas_rango])
                        
                        print(f"💰 Total ingresos: {total_ingresos_valor}")  # Debug
                        print(f"📊 Categorías: {len(categorias_ingresos)}")  # Debug
                        print(f"📊 Configuraciones: {len(configuraciones_ingresos)}")  # Debug
                        print(f"📊 Recursos: {len(recursos_ingresos)}")  # Debug
                        
                        # Ordenar por ingresos y calcular porcentajes
                        categorias_con_porcentaje = []
                        for categoria, ingreso in sorted(categorias_ingresos.items(), key=lambda x: x[1], reverse=True):
                            porcentaje = (ingreso / total_ingresos_valor * 100) if total_ingresos_valor > 0 else 0
                            categorias_con_porcentaje.append((categoria, ingreso, round(porcentaje, 1)))
                        
                        configuraciones_con_porcentaje = []
                        for configuracion, ingreso in sorted(configuraciones_ingresos.items(), key=lambda x: x[1], reverse=True):
                            porcentaje = (ingreso / total_ingresos_valor * 100) if total_ingresos_valor > 0 else 0
                            configuraciones_con_porcentaje.append((configuracion, ingreso, round(porcentaje, 1)))
                        
                        recursos_con_porcentaje = []
                        for recurso, ingreso in sorted(recursos_ingresos.items(), key=lambda x: x[1], reverse=True):
                            porcentaje = (ingreso / total_ingresos_valor * 100) if total_ingresos_valor > 0 else 0
                            recursos_con_porcentaje.append((recurso, ingreso, round(porcentaje, 1)))
                        
                        context = {
                            'form': form,
                            'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                            'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                            'categorias_ingresos': categorias_con_porcentaje,
                            'configuraciones_ingresos': configuraciones_con_porcentaje,
                            'recursos_ingresos': recursos_con_porcentaje,
                            'total_ingresos': total_ingresos_valor,
                            'total_facturas': len(facturas_rango),
                            'hay_datos': True
                        }
                    else:
                        # ✅ MOSTRAR FACTURAS DISPONIBLES PARA AYUDAR
                        fechas_disponibles = []
                        for factura in facturas:
                            fechas_disponibles.append(factura['fechaEmision'])
                        
                        context = {
                            'form': form,
                            'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                            'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                            'hay_datos': False,
                            'message': f'No hay facturas emitidas en el rango seleccionado. Fechas disponibles: {", ".join(set(fechas_disponibles))}'
                        }
                else:
                    context = {'form': form, 'error': result.get('message', 'Error al obtener datos')}
            except Exception as e:
                context = {'form': form, 'error': f'Error al conectar con el backend: {str(e)}'}
        else:
            context = {'form': form, 'error': 'Formulario inválido'}
    else:
        form = FechaRangoForm()
        context = {'form': form}
    
    return render(request, 'core/analisis_ventas.html', context)

def ayuda(request):
    estudiante_info = {
        'nombre': 'Jonathan Gabriel López Reyes',
        'carnet': '202404730',
        'carrera': 'Ingeniería en Ciencias y Sistemas',
        'universidad': 'Universidad de San Carlos de Guatemala',
        'semestre': 'IV Semestre',
        'curso': 'Introducción a la Programación y a la Computación II',
    }
    
    documentacion = """
    Sistema de Facturación de Infraestructura en la Nube - Tecnologías Chapinas, S.A.
    
    
    Arquitectura:
    - Frontend: Django (MVT)
    - Backend: Flask (API REST)
    - Almacenamiento: XML (base de datos)
    
    Para más información, consulte la documentación completa en el repositorio del proyecto: https://github.com/JonaLop153/IPC2_Proyecto3_202404730.
    """
    
    context = {
        'estudiante_info': estudiante_info,
        'documentacion': documentacion
    }
    
    return render(request, 'core/ayuda.html', context)

def descargar_pdf_factura(request, id_factura):
    """Descarga el PDF de una factura específica"""
    try:
        print(f"📄 Solicitando PDF para factura {id_factura}")  # Debug
        
        # Llamar al backend para generar el PDF
        response = requests.get(f'{BACKEND_URL}/generar-pdf-factura/{id_factura}')
        
        print(f"📊 Respuesta del backend: {response.status_code}")  # Debug
        
        if response.status_code == 200:
            # Verificar que la respuesta es un PDF
            content_type = response.headers.get('Content-Type', '')
            print(f"📋 Content-Type: {content_type}")  # Debug
            
            if 'application/pdf' in content_type:
                # Devolver el PDF como respuesta
                pdf_response = HttpResponse(
                    response.content,
                    content_type='application/pdf'
                )
                pdf_response['Content-Disposition'] = f'attachment; filename="factura_{id_factura}.pdf"'
                print(f"✅ PDF generado exitosamente para factura {id_factura}")  # Debug
                return pdf_response
            else:
                # Si no es PDF, puede ser un JSON de error
                try:
                    error_data = response.json()
                    error_msg = error_data.get('message', 'Error desconocido al generar PDF')
                    print(f"❌ Error del backend: {error_msg}")  # Debug
                    return HttpResponse(f"Error del backend: {error_msg}", status=400)
                except:
                    return HttpResponse("Error: La respuesta no es un PDF válido", status=400)
        else:
            # Intentar obtener mensaje de error del backend
            try:
                error_data = response.json()
                error_msg = error_data.get('message', f'Error HTTP {response.status_code}')
            except:
                error_msg = f'Error HTTP {response.status_code}'
            
            print(f"❌ Error del backend: {error_msg}")  # Debug
            return HttpResponse(f"Error: {error_msg}", status=400)
            
    except Exception as e:
        error_msg = f'Error al generar PDF: {str(e)}'
        print(f"❌ Error general: {error_msg}")  # Debug
        return HttpResponse(error_msg, status=500)

def descargar_pdf_analisis(request):
    """Descarga el PDF de análisis de ventas"""
    if request.method == 'POST':
        try:
            fecha_inicio = request.POST.get('fecha_inicio')
            fecha_fin = request.POST.get('fecha_fin')
            
            form = FechaRangoForm(request.POST)
            if form.is_valid():
                fecha_inicio = form.cleaned_data['fecha_inicio']
                fecha_fin = form.cleaned_data['fecha_fin']
                
                response = requests.get(f'{BACKEND_URL}/facturas')
                result = response.json()
                
                if result.get('success'):
                    facturas = result['facturas']
                    facturas_rango = []
                    
                    for factura in facturas:
                        fecha_emision_str = factura['fechaEmision']
                        fecha_emision = datetime.strptime(fecha_emision_str, '%d/%m/%Y').date()
                        
                        if fecha_inicio <= fecha_emision <= fecha_fin:
                            facturas_rango.append(factura)
                    
                    if facturas_rango:
                        categorias_ingresos = {}
                        configuraciones_ingresos = {}
                        recursos_ingresos = {}
                        
                        for factura in facturas_rango:
                            for detalle in factura['detalles']:
                                instancia = get_instancia_by_id(detalle['id_instancia'])
                                if instancia:
                                    configuracion = get_configuracion_by_id(instancia['idConfiguracion'])
                                    if configuracion:
                                        categoria = get_categoria_by_id(configuracion['idCategoria'])
                                        
                                        if categoria:
                                            cat_nombre = categoria['nombre']
                                            if cat_nombre not in categorias_ingresos:
                                                categorias_ingresos[cat_nombre] = 0
                                            categorias_ingresos[cat_nombre] += detalle['costo_total']
                                        
                                        conf_nombre = configuracion['nombre']
                                        if conf_nombre not in configuraciones_ingresos:
                                            configuraciones_ingresos[conf_nombre] = 0
                                        configuraciones_ingresos[conf_nombre] += detalle['costo_total']
                                
                                recurso_nombre = detalle['nombre_recurso']
                                if recurso_nombre not in recursos_ingresos:
                                    recursos_ingresos[recurso_nombre] = 0
                                recursos_ingresos[recurso_nombre] += detalle['costo_total']
                        
                        total_ingresos_valor = sum([f['montoTotal'] for f in facturas_rango])
                        
                        categorias_con_porcentaje = []
                        for categoria, ingreso in sorted(categorias_ingresos.items(), key=lambda x: x[1], reverse=True):
                            porcentaje = (ingreso / total_ingresos_valor * 100) if total_ingresos_valor > 0 else 0
                            categorias_con_porcentaje.append((categoria, ingreso, round(porcentaje, 1)))
                        
                        configuraciones_con_porcentaje = []
                        for configuracion, ingreso in sorted(configuraciones_ingresos.items(), key=lambda x: x[1], reverse=True):
                            porcentaje = (ingreso / total_ingresos_valor * 100) if total_ingresos_valor > 0 else 0
                            configuraciones_con_porcentaje.append((configuracion, ingreso, round(porcentaje, 1)))
                        
                        recursos_con_porcentaje = []
                        for recurso, ingreso in sorted(recursos_ingresos.items(), key=lambda x: x[1], reverse=True):
                            porcentaje = (ingreso / total_ingresos_valor * 100) if total_ingresos_valor > 0 else 0
                            recursos_con_porcentaje.append((recurso, ingreso, round(porcentaje, 1)))
                        
                        datos_analisis = {
                            'fecha_inicio': fecha_inicio.strftime('%d/%m/%Y'),
                            'fecha_fin': fecha_fin.strftime('%d/%m/%Y'),
                            'categorias_ingresos': categorias_con_porcentaje,
                            'configuraciones_ingresos': configuraciones_con_porcentaje,
                            'recursos_ingresos': recursos_con_porcentaje,
                            'total_ingresos': total_ingresos_valor,
                            'total_facturas': len(facturas_rango)
                        }
                        
                        pdf_response = requests.post(
                            f'{BACKEND_URL}/generar-pdf-analisis-ventas',
                            json=datos_analisis
                        )
                        
                        if pdf_response.status_code == 200:
                            response = HttpResponse(
                                pdf_response.content,
                                content_type='application/pdf'
                            )
                            response['Content-Disposition'] = f'attachment; filename="analisis_ventas_{fecha_inicio.strftime("%d-%m-%Y")}_{fecha_fin.strftime("%d-%m-%Y")}.pdf"'
                            return response
                        else:
                            error_data = pdf_response.json()
                            return HttpResponse(f"Error: {error_data.get('message', 'Error al generar PDF')}", status=400)
                    else:
                        return HttpResponse("No hay datos para el rango de fechas seleccionado", status=400)
                else:
                    return HttpResponse("Error al obtener datos del backend", status=500)
            else:
                return HttpResponse("Formulario inválido", status=400)
                
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}", status=500)
    
    return HttpResponse("Método no permitido", status=405)

# Funciones auxiliares
def get_instancia_by_id(id_instancia):
    try:
        response = requests.get(f'{BACKEND_URL}/instancia/{id_instancia}')
        result = response.json()
        if result.get('success'):
            return result['instancia']
    except Exception:
        return None

def get_configuracion_by_id(id_configuracion):
    try:
        response = requests.get(f'{BACKEND_URL}/configuracion/{id_configuracion}')
        result = response.json()
        if result.get('success'):
            return result['configuracion']
    except Exception:
        return None

def get_categoria_by_id(id_categoria):
    try:
        response = requests.get(f'{BACKEND_URL}/categoria/{id_categoria}')
        result = response.json()
        if result.get('success'):
            return result['categoria']
    except Exception:
        return None