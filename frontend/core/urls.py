from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('configuracion/', views.enviar_mensaje_configuracion, name='configuracion'),
    path('consumo/', views.enviar_mensaje_consumo, name='consumo'),
    path('operaciones/', views.operaciones_sistema, name='operaciones'),
    path('facturacion/', views.proceso_facturacion, name='facturacion'),
    path('reportes/', views.reportes_pdf, name='reportes'),
    path('detalle-factura/', views.detalle_factura, name='detalle_factura'),
    path('analisis-ventas/', views.analisis_ventas, name='analisis_ventas'),
    path('ayuda/', views.ayuda, name='ayuda'),
    path('descargar-pdf-factura/<int:id_factura>/', views.descargar_pdf_factura, name='descargar_pdf_factura'),
    path('descargar-pdf-analisis/', views.descargar_pdf_analisis, name='descargar_pdf_analisis'),
    #  NUEVA RUTA
]