from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from datetime import datetime
import os

def generar_pdf_factura(factura_data):
    """Genera un PDF con el detalle de una factura"""
    
    # Crear directorio para PDFs si no existe
    os.makedirs('pdfs', exist_ok=True)
    
    # Nombre del archivo
    filename = f"pdfs/factura_{factura_data['id']}.pdf"
    
    # Crear el documento
    doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=0.5*inch)
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=30,
        alignment=1  # Centrado
    )
    
    # Título
    title = Paragraph("Tecnologías Chapinas, S.A.", title_style)
    elements.append(title)
    
    subtitle = Paragraph("DETALLE DE FACTURA", styles['Heading2'])
    elements.append(subtitle)
    elements.append(Spacer(1, 20))
    
    # Información de la factura
    info_data = [
        [f"<b>Número de Factura:</b>", f"#{factura_data['id']}"],
        [f"<b>NIT Cliente:</b>", factura_data['nitCliente']],
        [f"<b>Fecha de Emisión:</b>", factura_data['fechaEmision']],
        [f"<b>Monto Total:</b>", f"Q{factura_data['montoTotal']:,.2f}"]
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 30))
    
    # Detalles de la factura
    detalles_header = ['Instancia', 'Recurso', 'Cantidad', 'Tiempo (h)', 'Costo Unitario', 'Costo Total']
    detalles_rows = [detalles_header]
    
    for detalle in factura_data['detalles']:
        row = [
            detalle['nombre_instancia'],
            detalle['nombre_recurso'],
            f"{detalle['cantidad']:.2f}",
            f"{detalle['tiempo_consumido']:.2f}",
            f"Q{detalle['costo_unitario']:.2f}",
            f"Q{detalle['costo_total']:.2f}"
        ]
        detalles_rows.append(row)
    
    # Agregar fila total
    detalles_rows.append(['', '', '', '', '<b>TOTAL:</b>', f"<b>Q{factura_data['montoTotal']:,.2f}</b>"])
    
    detalles_table = Table(detalles_rows, colWidths=[1.2*inch, 1.5*inch, 0.8*inch, 0.8*inch, 1*inch, 1*inch])
    detalles_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
        ('FONT', (0, 1), (-1, -2), 'Helvetica', 9),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 10),
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(detalles_table)
    
    # Pie de página
    elements.append(Spacer(1, 40))
    footer = Paragraph(f"<i>Generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", styles['Italic'])
    elements.append(footer)
    
    # Generar PDF
    doc.build(elements)
    
    return filename

def generar_pdf_analisis_ventas(fecha_inicio, fecha_fin, datos_analisis):
    """Genera un PDF con el análisis de ventas"""
    
    os.makedirs('pdfs', exist_ok=True)
    filename = f"pdfs/analisis_ventas_{fecha_inicio}_{fecha_fin}.pdf".replace('/', '-')
    
    doc = SimpleDocTemplate(filename, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Título
    title = Paragraph("Tecnologías Chapinas, S.A. - Análisis de Ventas", styles['Heading1'])
    elements.append(title)
    
    # Período
    periodo = Paragraph(f"Período: {fecha_inicio} al {fecha_fin}", styles['Heading2'])
    elements.append(periodo)
    elements.append(Spacer(1, 20))
    
    # Resumen
    resumen_data = [
        [f"<b>Total de Ingresos:</b>", f"Q{datos_analisis['total_ingresos']:,.2f}"],
        [f"<b>Total de Facturas:</b>", f"{datos_analisis['total_facturas']}"]
    ]
    
    resumen_table = Table(resumen_data, colWidths=[2*inch, 2*inch])
    resumen_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Helvetica', 12),
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(resumen_table)
    elements.append(Spacer(1, 30))
    
    # Categorías por ingresos
    if datos_analisis['categorias_ingresos']:
        elements.append(Paragraph("Categorías por Ingresos", styles['Heading3']))
        
        cat_data = [['Categoría', 'Ingresos (Q)', 'Porcentaje']]
        for cat, ingreso, porcentaje in datos_analisis['categorias_ingresos']:
            cat_data.append([cat, f"{ingreso:,.2f}", f"{porcentaje}%"])
        
        cat_table = Table(cat_data, colWidths=[3*inch, 1.5*inch, 1*inch])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(cat_table)
        elements.append(Spacer(1, 20))
    
    # Configuraciones por ingresos
    if datos_analisis['configuraciones_ingresos']:
        elements.append(Paragraph("Configuraciones por Ingresos", styles['Heading3']))
        
        conf_data = [['Configuración', 'Ingresos (Q)', 'Porcentaje']]
        for conf, ingreso, porcentaje in datos_analisis['configuraciones_ingresos']:
            conf_data.append([conf, f"{ingreso:,.2f}", f"{porcentaje}%"])
        
        conf_table = Table(conf_data, colWidths=[3*inch, 1.5*inch, 1*inch])
        conf_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(conf_table)
        elements.append(Spacer(1, 20))
    
    # Recursos por ingresos
    if datos_analisis['recursos_ingresos']:
        elements.append(Paragraph("Recursos por Ingresos", styles['Heading3']))
        
        rec_data = [['Recurso', 'Ingresos (Q)', 'Porcentaje']]
        for rec, ingreso, porcentaje in datos_analisis['recursos_ingresos']:
            rec_data.append([rec, f"{ingreso:,.2f}", f"{porcentaje}%"])
        
        rec_table = Table(rec_data, colWidths=[3*inch, 1.5*inch, 1*inch])
        rec_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(rec_table)
    
    # Pie de página
    elements.append(Spacer(1, 40))
    footer = Paragraph(f"<i>Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}</i>", styles['Italic'])
    elements.append(footer)
    
    doc.build(elements)
    
    return filename