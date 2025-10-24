from django.shortcuts import render, redirect
from django.http import JsonResponse
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
                # Leer el contenido como bytes
                xml_content = xml_file.read()
                if not xml_content.strip():
                    context = {'form': form, 'error': 'El archivo XML está vacío.'}
                else:
                    # Enviar como cuerpo crudo (bytes)
                    response = requests.post(
                        'http://localhost:5000/configurar',
                        data=xml_content,  # bytes, no string
                        headers={'Content-Type': 'application/xml'}
                    )
                    result = response.json()
                    if result['success']:
                        context = {
                            'form': form,
                            'success': True,
                            'message': result['message'],
                            'resultados': result['resultados']
                        }
                    else:
                        context = {'form': form, 'error': result['message']}
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
                    if result['success']:
                        context = {
                            'form': form,
                            'success': True,
                            'message': result['message'],
                            'consumos_procesados': result['consumos_procesados']
                        }
                    else:
                        context = {'form': form, 'error': result['message']}
            except requests.exceptions.ConnectionError:
                context = {'form': form, 'error': 'No se pudo conectar con el backend.'}
            except Exception as e:
                context = {'form': form, 'error': f'Error: {str(e)}'}
        else:
            context = {'form': form, 'error': 'Formulario inválido'}
    else:
        form = ConsumoForm()
        context = {'form': form}
    return render(request, 'core/consumption_message.html', context)

def operaciones_sistema(request):
    context = {}
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'inicializar':
            # Limpiar todos los datos
            try:
                response = requests.delete(f'{BACKEND_URL}/reset')  # Asumiendo que implementamos esta ruta
                if response.status_code == 200:
                    context['message'] = 'Sistema inicializado correctamente'
                else:
                    context['error'] = 'Error al inicializar el sistema'
            except Exception as e:
                context['error'] = f'Error al conectar con el backend: {str(e)}'
        
        elif action == 'consultar':
            # Consultar datos del sistema
            try:
                response = requests.get(f'{BACKEND_URL}/consultarDatos')
                result = response.json()
                
                if result['success']:
                    context['datos'] = result['data']
                else:
                    context['error'] = result['message']
            except Exception as e:
                context['error'] = f'Error al conectar con el backend: {str(e)}'
        
        elif action == 'crear_recurso':
            form = CrearRecursoForm(request.POST)
            if form.is_valid():
                data = {
                    'id': form.cleaned_data['id'],
                    'nombre': form.cleaned_data['nombre'],
                    'abreviatura': form.cleaned_data['abreviatura'],
                    'metrica': form.cleaned_data['metrica'],
                    'tipo': form.cleaned_data['tipo'],
                    'valorXhora': form.cleaned_data['valorXhora']
                }
                
                try:
                    response = requests.post(f'{BACKEND_URL}/crearRecurso', json=data)
                    result = response.json()
                    
                    if result['success']:
                        context['message'] = result['message']
                        context['recurso'] = result['recurso']
                    else:
                        context['error'] = result['message']
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
                    
                    if result['success']:
                        context['message'] = result['message']
                        context['categoria'] = result['categoria']
                    else:
                        context['error'] = result['message']
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
                    
                    if result['success']:
                        context['message'] = result['message']
                        context['configuracion'] = result['configuracion']
                    else:
                        context['error'] = result['message']
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
                    
                    if result['success']:
                        context['message'] = result['message']
                        context['cliente'] = result['cliente']
                    else:
                        context['error'] = result['message']
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
                    'fechaFinal': form.cleaned_data['fechaFinal'] if form.cleaned_data['estado'] == 'Cancelada' else None
                }
                
                try:
                    response = requests.post(f'{BACKEND_URL}/crearInstancia', json=data)
                    result = response.json()
                    
                    if result['success']:
                        context['message'] = result['message']
                        context['instancia'] = result['instancia']
                    else:
                        context['error'] = result['message']
                except Exception as e:
                    context['error'] = f'Error al conectar con el backend: {str(e)}'
            else:
                context['error'] = 'Formulario inválido'
        
        elif action == 'cancelar_instancia':
            # Implementar cancelación de instancia
            pass
    
    # Mostrar formulario para operaciones
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
                
                if result['success']:
                    context = {
                        'form': form,
                        'success': True,
                        'message': result['message'],
                        'facturas': result['facturas']
                    }
                else:
                    context = {
                        'form': form,
                        'error': result['message']
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
    # Esta vista será para seleccionar el tipo de reporte
    if request.method == 'POST':
        reporte_type = request.POST.get('reporte_type')
        
        if reporte_type == 'detalle_factura':
            # Redirigir a la vista de detalle de factura
            return redirect('detalle_factura')
        elif reporte_type == 'analisis_ventas':
            # Redirigir a la vista de análisis de ventas
            return redirect('analisis_ventas')
    
    return render(request, 'core/reportes.html')

def detalle_factura(request):
    if request.method == 'POST':
        factura_id = request.POST.get('factura_id')
        
        try:
            response = requests.get(f'{BACKEND_URL}/factura/{factura_id}')
            result = response.json()
            
            if result['success']:
                factura = result['factura']
                context = {
                    'factura': factura,
                    'total_instancias': len(set([d['id_instancia'] for d in factura['detalles']])),
                    'total_recursos': len(set([d['id_recurso'] for d in factura['detalles']]))
                }
                return render(request, 'core/detalle_factura.html', context)
            else:
                context = {'error': result['message']}
        except Exception as e:
            context = {'error': f'Error al conectar con el backend: {str(e)}'}
    else:
        # Obtener todas las facturas para mostrar en el formulario
        try:
            response = requests.get(f'{BACKEND_URL}/facturas')
            result = response.json()
            
            if result['success']:
                facturas = result['facturas']
                context = {'facturas': facturas}
            else:
                context = {'error': result['message']}
        except Exception as e:
            context = {'error': f'Error al conectar con el backend: {str(e)}'}
    
    return render(request, 'core/detalle_factura.html', context)

def analisis_ventas(request):
    if request.method == 'POST':
        form = FechaRangoForm(request.POST)
        if form.is_valid():
            fecha_inicio = form.cleaned_data['fecha_inicio']
            fecha_fin = form.cleaned_data['fecha_fin']
            
            # Obtener datos para análisis
            try:
                # Primero obtener todas las facturas en el rango
                response = requests.get(f'{BACKEND_URL}/facturas')
                result = response.json()
                
                if result['success']:
                    facturas = result['facturas']
                    facturas_rango = []
                    
                    for factura in facturas:
                        fecha_emision = datetime.strptime(factura['fechaEmision'], '%d/%m/%Y')
                        if fecha_inicio <= fecha_emision <= fecha_fin:
                            facturas_rango.append(factura)
                    
                    # Análisis por categorías y configuraciones
                    categorias_ingresos = {}
                    configuraciones_ingresos = {}
                    recursos_ingresos = {}
                    
                    for factura in facturas_rango:
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
                    
                    # Ordenar por ingresos
                    categorias_ingresos_sorted = sorted(categorias_ingresos.items(), key=lambda x: x[1], reverse=True)
                    configuraciones_ingresos_sorted = sorted(configuraciones_ingresos.items(), key=lambda x: x[1], reverse=True)
                    recursos_ingresos_sorted = sorted(recursos_ingresos.items(), key=lambda x: x[1], reverse=True)
                    
                    context = {
                        'form': form,
                        'fecha_inicio': fecha_inicio,
                        'fecha_fin': fecha_fin,
                        'categorias_ingresos': categorias_ingresos_sorted,
                        'configuraciones_ingresos': configuraciones_ingresos_sorted,
                        'recursos_ingresos': recursos_ingresos_sorted,
                        'total_ingresos': sum([f['montoTotal'] for f in facturas_rango])
                    }
                else:
                    context = {'form': form, 'error': result['message']}
            except Exception as e:
                context = {'form': form, 'error': f'Error al conectar con el backend: {str(e)}'}
        else:
            context = {'form': form, 'error': 'Formulario inválido'}
    else:
        form = FechaRangoForm()
        context = {'form': form}
    
    return render(request, 'core/analisis_ventas.html', context)

def ayuda(request):
    # Información del estudiante
    estudiante_info = {
        'nombre': 'Jonathan Gabriel López Reyes',
        'carnet': '202404730',
        'carrera': 'Ingeniería en Ciencias y Sistemas',
        'universidad': 'Universidad de San Carlos de Guatemala',
        'semestre': 'IV Semestre',
        'curso': 'Introducción a la Programación y a la Computación II',
    }
    
    # Documentación del programa
    documentacion = """
    Sistema de Facturación de Infraestructura en la Nube - Tecnologías Chapinas, S.A.
    
    Este sistema permite gestionar la infraestructura en la nube de Tecnologías Chapinas, S.A., 
    incluyendo la creación de recursos, categorías, configuraciones, clientes e instancias, 
    así como el procesamiento de consumos y la generación de facturas.
    
    Funcionalidades principales:
    1. Envío de mensajes de configuración (XML)
    2. Envío de mensajes de consumo (XML)
    3. Operaciones del sistema (crear, consultar, eliminar)
    4. Proceso de facturación periódica
    5. Generación de reportes en PDF
    
    Arquitectura:
    - Frontend: Django (MVT)
    - Backend: Flask (API REST)
    - Almacenamiento: XML (base de datos)
    
    Para más información, consulte la documentación completa en el repositorio del proyecto.
    """
    
    context = {
        'estudiante_info': estudiante_info,
        'documentacion': documentacion
    }
    
    return render(request, 'core/ayuda.html', context)

# Funciones auxiliares para obtener datos desde el backend
def get_instancia_by_id(id_instancia):
    try:
        response = requests.get(f'{BACKEND_URL}/instancia/{id_instancia}')
        result = response.json()
        if result['success']:
            return result['instancia']
    except Exception:  
        return None

def get_configuracion_by_id(id_configuracion):
    try:
        response = requests.get(f'{BACKEND_URL}/configuracion/{id_configuracion}')
        result = response.json()
        if result['success']:
            return result['configuracion']
    except Exception:   
        return None

def get_categoria_by_id(id_categoria):
    try:
        response = requests.get(f'{BACKEND_URL}/categoria/{id_categoria}')
        result = response.json()
        if result['success']:
            return result['categoria']
    except Exception:  
        return None