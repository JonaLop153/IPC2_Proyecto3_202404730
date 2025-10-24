from django import forms
import xml.etree.ElementTree as ET
from datetime import datetime

class ConfiguracionForm(forms.Form):
    xml_file = forms.FileField(label='Archivo XML de configuración', help_text='Seleccione un archivo XML con la configuración del sistema')

class ConsumoForm(forms.Form):
    xml_file = forms.FileField(label='Archivo XML de consumo', help_text='Seleccione un archivo XML con los consumos de recursos')

class FechaRangoForm(forms.Form):
    fecha_inicio = forms.DateField(label='Fecha de inicio', widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_fin = forms.DateField(label='Fecha de fin', widget=forms.DateInput(attrs={'type': 'date'}))

class CrearRecursoForm(forms.Form):
    id = forms.IntegerField(label='ID del recurso')
    nombre = forms.CharField(max_length=255, label='Nombre del recurso')
    abreviatura = forms.CharField(max_length=50, label='Abreviatura')
    metrica = forms.CharField(max_length=50, label='Métrica')
    tipo = forms.ChoiceField(choices=[('Hardware', 'Hardware'), ('Software', 'Software')], label='Tipo de recurso')
    valorXhora = forms.DecimalField(label='Valor por hora', max_digits=10, decimal_places=2)

class CrearCategoriaForm(forms.Form):
    id = forms.IntegerField(label='ID de la categoría')
    nombre = forms.CharField(max_length=255, label='Nombre de la categoría')
    descripcion = forms.CharField(widget=forms.Textarea, label='Descripción')
    cargaTrabajo = forms.CharField(widget=forms.Textarea, label='Carga de trabajo')

class CrearConfiguracionForm(forms.Form):
    id = forms.IntegerField(label='ID de la configuración')
    nombre = forms.CharField(max_length=255, label='Nombre de la configuración')
    descripcion = forms.CharField(widget=forms.Textarea, label='Descripción')
    idCategoria = forms.IntegerField(label='ID de la categoría')

class CrearClienteForm(forms.Form):
    nit = forms.CharField(max_length=20, label='NIT')
    nombre = forms.CharField(max_length=255, label='Nombre del cliente')
    usuario = forms.CharField(max_length=100, label='Usuario')
    clave = forms.CharField(max_length=100, widget=forms.PasswordInput, label='Clave')
    direccion = forms.CharField(widget=forms.Textarea, label='Dirección')
    correoElectronico = forms.EmailField(label='Correo electrónico')

class CrearInstanciaForm(forms.Form):
    id = forms.IntegerField(label='ID de la instancia')
    idCliente = forms.CharField(max_length=20, label='NIT del cliente')
    idConfiguracion = forms.IntegerField(label='ID de la configuración')
    nombre = forms.CharField(max_length=255, label='Nombre de la instancia')
    fechaInicio = forms.CharField(max_length=100, label='Fecha de inicio (dd/mm/yyyy)')
    estado = forms.ChoiceField(choices=[('Vigente', 'Vigente'), ('Cancelada', 'Cancelada')], label='Estado')
    fechaFinal = forms.CharField(max_length=100, required=False, label='Fecha final (dd/mm/yyyy)')

class FacturaForm(forms.Form):
    fechaInicio = forms.CharField(max_length=100, label='Fecha de inicio (dd/mm/yyyy)')
    fechaFin = forms.CharField(max_length=100, label='Fecha de fin (dd/mm/yyyy)')