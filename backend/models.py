import xml.etree.ElementTree as ET
import os
from datetime import datetime

# Ruta al archivo XML de base de datos
DATABASE_PATH = 'data/database.xml'

# Asegurar que el directorio de datos exista
os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

# Si el archivo no existe, crearlo con estructura básica
if not os.path.exists(DATABASE_PATH):
    with open(DATABASE_PATH, 'w', encoding='utf-8') as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<database>
    <recursos/>
    <categorias/>
    <configuraciones/>
    <clientes/>
    <instancias/>
    <consumos/>
    <facturas/>
</database>''')

class ModeloBase:
    @staticmethod
    def _obtener_root():
        tree = ET.parse(DATABASE_PATH)
        return tree.getroot()
    
    @staticmethod
    def _guardar_xml(root):
        tree = ET.ElementTree(root)
        # Intentar usar ET.indent si está disponible (Python 3.9+)
        try:
            ET.indent(tree, space="  ", level=0)
        except AttributeError:
            pass  # Ignorar si no está disponible
        tree.write(DATABASE_PATH, encoding='utf-8', xml_declaration=True)
    
    @staticmethod
    def _extraer_elemento(root, tag, id_value, id_attr='id'):
        for elem in root.findall(tag):
            if elem.get(id_attr) and int(elem.get(id_attr)) == id_value:
                return elem
        return None

class Recurso(ModeloBase):
    def __init__(self, id, nombre, abreviatura, metrica, tipo, valor_hora):
        self.id = id
        self.nombre = nombre
        self.abreviatura = abreviatura
        self.metrica = metrica
        self.tipo = tipo
        self.valor_hora = valor_hora
    
    def guardar(self):
        root = self._obtener_root()
        recursos = root.find('recursos')
        
        recurso_existente = self._extraer_elemento(recursos, 'recurso', self.id)
        if recurso_existente is not None:
            recurso_existente.find('nombre').text = self.nombre
            recurso_existente.find('abreviatura').text = self.abreviatura
            recurso_existente.find('metrica').text = self.metrica
            recurso_existente.find('tipo').text = self.tipo
            recurso_existente.find('valorXhora').text = str(self.valor_hora)
        else:
            nuevo_recurso = ET.SubElement(recursos, 'recurso')
            nuevo_recurso.set('id', str(self.id))
            ET.SubElement(nuevo_recurso, 'nombre').text = self.nombre
            ET.SubElement(nuevo_recurso, 'abreviatura').text = self.abreviatura
            ET.SubElement(nuevo_recurso, 'metrica').text = self.metrica
            ET.SubElement(nuevo_recurso, 'tipo').text = self.tipo
            ET.SubElement(nuevo_recurso, 'valorXhora').text = str(self.valor_hora)
        
        self._guardar_xml(root)
        return True
    
    @staticmethod
    def obtener_por_id(id_recurso):
        root = Recurso._obtener_root()
        recursos = root.find('recursos')
        recurso_elem = Recurso._extraer_elemento(recursos, 'recurso', id_recurso)
        if recurso_elem is not None:
            return Recurso(
                int(recurso_elem.get('id')),
                recurso_elem.find('nombre').text,
                recurso_elem.find('abreviatura').text,
                recurso_elem.find('metrica').text,
                recurso_elem.find('tipo').text,
                float(recurso_elem.find('valorXhora').text)
            )
        return None
    
    @staticmethod
    def obtener_todos():
        root = Recurso._obtener_root()
        recursos = []
        recursos_elem = root.find('recursos')
        if recursos_elem is not None:
            for recurso_elem in recursos_elem.findall('recurso'):
                recursos.append(Recurso(
                    int(recurso_elem.get('id')),
                    recurso_elem.find('nombre').text,
                    recurso_elem.find('abreviatura').text,
                    recurso_elem.find('metrica').text,
                    recurso_elem.find('tipo').text,
                    float(recurso_elem.find('valorXhora').text)
                ))
        return recursos
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'abreviatura': self.abreviatura,
            'metrica': self.metrica,
            'tipo': self.tipo,
            'valorXhora': self.valor_hora
        }

class Categoria(ModeloBase):
    def __init__(self, id, nombre, descripcion, carga_trabajo):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.carga_trabajo = carga_trabajo
    
    def guardar(self):
        root = self._obtener_root()
        categorias = root.find('categorias')
        
        categoria_existente = self._extraer_elemento(categorias, 'categoria', self.id)
        if categoria_existente is not None:
            categoria_existente.find('nombre').text = self.nombre
            categoria_existente.find('descripcion').text = self.descripcion
            categoria_existente.find('cargaTrabajo').text = self.carga_trabajo
        else:
            nueva_categoria = ET.SubElement(categorias, 'categoria')
            nueva_categoria.set('id', str(self.id))
            ET.SubElement(nueva_categoria, 'nombre').text = self.nombre
            ET.SubElement(nueva_categoria, 'descripcion').text = self.descripcion
            ET.SubElement(nueva_categoria, 'cargaTrabajo').text = self.carga_trabajo
        
        self._guardar_xml(root)
        return True
    
    @staticmethod
    def obtener_por_id(id_categoria):
        root = Categoria._obtener_root()
        categorias = root.find('categorias')
        categoria_elem = Categoria._extraer_elemento(categorias, 'categoria', id_categoria)
        if categoria_elem is not None:
            desc_elem = categoria_elem.find('descripcion')
            desc = desc_elem.text if desc_elem is not None else ""
            return Categoria(
                int(categoria_elem.get('id')),
                categoria_elem.find('nombre').text,
                desc,
                categoria_elem.find('cargaTrabajo').text
            )
        return None
    
    @staticmethod
    def obtener_todas():
        root = Categoria._obtener_root()
        categorias = []
        categorias_elem = root.find('categorias')
        if categorias_elem is not None:
            for categoria_elem in categorias_elem.findall('categoria'):
                desc_elem = categoria_elem.find('descripcion')
                desc = desc_elem.text if desc_elem is not None else ""
                categorias.append(Categoria(
                    int(categoria_elem.get('id')),
                    categoria_elem.find('nombre').text,
                    desc,
                    categoria_elem.find('cargaTrabajo').text
                ))
        return categorias
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'cargaTrabajo': self.carga_trabajo
        }

class Configuracion(ModeloBase):
    def __init__(self, id, nombre, descripcion, id_categoria):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.id_categoria = id_categoria
    
    def guardar(self):
        root = self._obtener_root()
        configuraciones = root.find('configuraciones')
        
        config_existente = self._extraer_elemento(configuraciones, 'configuracion', self.id)
        if config_existente is not None:
            config_existente.find('nombre').text = self.nombre
            config_existente.find('descripcion').text = self.descripcion
            config_existente.find('idCategoria').text = str(self.id_categoria)
        else:
            nueva_config = ET.SubElement(configuraciones, 'configuracion')
            nueva_config.set('id', str(self.id))
            ET.SubElement(nueva_config, 'nombre').text = self.nombre
            ET.SubElement(nueva_config, 'descripcion').text = self.descripcion
            ET.SubElement(nueva_config, 'idCategoria').text = str(self.id_categoria)
        
        self._guardar_xml(root)
        return True
    
    @staticmethod
    def obtener_por_id(id_configuracion):
        root = Configuracion._obtener_root()
        configuraciones = root.find('configuraciones')
        config_elem = Configuracion._extraer_elemento(configuraciones, 'configuracion', id_configuracion)
        if config_elem is not None:
            desc_elem = config_elem.find('descripcion')
            desc = desc_elem.text if desc_elem is not None else ""
            return Configuracion(
                int(config_elem.get('id')),
                config_elem.find('nombre').text,
                desc,
                int(config_elem.find('idCategoria').text)
            )
        return None
    
    @staticmethod
    def obtener_todas():
        root = Configuracion._obtener_root()
        configs = []
        configuraciones_elem = root.find('configuraciones')
        if configuraciones_elem is not None:
            for config_elem in configuraciones_elem.findall('configuracion'):
                desc_elem = config_elem.find('descripcion')
                desc = desc_elem.text if desc_elem is not None else ""
                configs.append(Configuracion(
                    int(config_elem.get('id')),
                    config_elem.find('nombre').text,
                    desc,
                    int(config_elem.find('idCategoria').text)
                ))
        return configs
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'idCategoria': self.id_categoria
        }

class RecursoConfiguracion(ModeloBase):
    def __init__(self, id_configuracion, id_recurso, cantidad):
        self.id_configuracion = id_configuracion
        self.id_recurso = id_recurso
        self.cantidad = cantidad
    
    def guardar(self):
        root = self._obtener_root()
        config_elem = self._extraer_elemento(root.find('configuraciones'), 'configuracion', self.id_configuracion)
        if config_elem is None:
            return False
        
        recursos_config_elem = config_elem.find('recursosConfiguracion')
        if recursos_config_elem is None:
            recursos_config_elem = ET.SubElement(config_elem, 'recursosConfiguracion')
        
        recurso_conf_existente = None
        for r in recursos_config_elem.findall('recurso'):
            if int(r.get('id')) == self.id_recurso:
                recurso_conf_existente = r
                break
        
        if recurso_conf_existente is not None:
            recurso_conf_existente.text = str(self.cantidad)
        else:
            nuevo_recurso = ET.SubElement(recursos_config_elem, 'recurso')
            nuevo_recurso.set('id', str(self.id_recurso))
            nuevo_recurso.text = str(self.cantidad)
        
        self._guardar_xml(root)
        return True
    
    @staticmethod
    def obtener_por_configuracion(id_configuracion):
        root = RecursoConfiguracion._obtener_root()
        config_elem = RecursoConfiguracion._extraer_elemento(root.find('configuraciones'), 'configuracion', id_configuracion)
        if config_elem is None:
            return []
        
        recursos_config = []
        recursos_elem = config_elem.find('recursosConfiguracion')
        if recursos_elem is not None:
            for r in recursos_elem.findall('recurso'):
                recursos_config.append(RecursoConfiguracion(
                    id_configuracion,
                    int(r.get('id')),
                    float(r.text)
                ))
        return recursos_config

class Cliente(ModeloBase):
    def __init__(self, nit, nombre, usuario, clave, direccion, correo_electronico):
        self.nit = nit  # ✅ Debe permanecer como string
        self.nombre = nombre
        self.usuario = usuario
        self.clave = clave
        self.direccion = direccion
        self.correo_electronico = correo_electronico
    
    def guardar(self):
        root = self._obtener_root()
        clientes = root.find('clientes')
        
        # ✅ Buscar por NIT como string
        cliente_existente = None
        for cliente_elem in clientes.findall('cliente'):
            if cliente_elem.get('nit') == self.nit:
                cliente_existente = cliente_elem
                break
        
        if cliente_existente is not None:
            cliente_existente.find('nombre').text = self.nombre
            cliente_existente.find('usuario').text = self.usuario
            cliente_existente.find('clave').text = self.clave
            cliente_existente.find('direccion').text = self.direccion
            cliente_existente.find('correoElectronico').text = self.correo_electronico
        else:
            nuevo_cliente = ET.SubElement(clientes, 'cliente')
            nuevo_cliente.set('nit', self.nit)  # ✅ NIT como string
            ET.SubElement(nuevo_cliente, 'nombre').text = self.nombre
            ET.SubElement(nuevo_cliente, 'usuario').text = self.usuario
            ET.SubElement(nuevo_cliente, 'clave').text = self.clave
            ET.SubElement(nuevo_cliente, 'direccion').text = self.direccion
            ET.SubElement(nuevo_cliente, 'correoElectronico').text = self.correo_electronico
        
        self._guardar_xml(root)
        return True
    
    @staticmethod
    def obtener_por_nit(nit):
        root = Cliente._obtener_root()
        clientes = root.find('clientes')
        # ✅ Buscar por NIT como string
        for cliente_elem in clientes.findall('cliente'):
            if cliente_elem.get('nit') == nit:
                return Cliente(
                    cliente_elem.get('nit'),
                    cliente_elem.find('nombre').text,
                    cliente_elem.find('usuario').text,
                    cliente_elem.find('clave').text,
                    cliente_elem.find('direccion').text,
                    cliente_elem.find('correoElectronico').text
                )
        return None
    
    @staticmethod
    def obtener_todos():
        root = Cliente._obtener_root()
        clientes = []
        clientes_elem = root.find('clientes')
        if clientes_elem is not None:
            for cliente_elem in clientes_elem.findall('cliente'):
                clientes.append(Cliente(
                    cliente_elem.get('nit'),
                    cliente_elem.find('nombre').text,
                    cliente_elem.find('usuario').text,
                    cliente_elem.find('clave').text,
                    cliente_elem.find('direccion').text,
                    cliente_elem.find('correoElectronico').text
                ))
        return clientes
    
    def to_dict(self):
        return {
            'nit': self.nit,
            'nombre': self.nombre,
            'usuario': self.usuario,
            'clave': self.clave,
            'direccion': self.direccion,
            'correoElectronico': self.correo_electronico
        }

class Instancia(ModeloBase):
    def __init__(self, id, id_cliente, id_configuracion, nombre, fecha_inicio, estado, fecha_final=None):
        self.id = id
        self.id_cliente = id_cliente
        self.id_configuracion = id_configuracion
        self.nombre = nombre
        self.fecha_inicio = fecha_inicio
        self.estado = estado
        self.fecha_final = fecha_final
    
    def guardar(self):
        root = self._obtener_root()
        instancias = root.find('instancias')
        
        instancia_existente = self._extraer_elemento(instancias, 'instancia', self.id)
        if instancia_existente is not None:
            instancia_existente.find('idCliente').text = self.id_cliente
            instancia_existente.find('idConfiguracion').text = str(self.id_configuracion)
            instancia_existente.find('nombre').text = self.nombre
            instancia_existente.find('fechaInicio').text = self.fecha_inicio.strftime('%d/%m/%Y')
            instancia_existente.find('estado').text = self.estado
            if self.fecha_final:
                fecha_final_elem = instancia_existente.find('fechaFinal')
                if fecha_final_elem is None:
                    ET.SubElement(instancia_existente, 'fechaFinal').text = self.fecha_final.strftime('%d/%m/%Y')
                else:
                    fecha_final_elem.text = self.fecha_final.strftime('%d/%m/%Y')
            else:
                # Eliminar <fechaFinal> si existe y no se necesita
                fecha_final_elem = instancia_existente.find('fechaFinal')
                if fecha_final_elem is not None:
                    instancia_existente.remove(fecha_final_elem)
        else:
            nueva_instancia = ET.SubElement(instancias, 'instancia')
            nueva_instancia.set('id', str(self.id))
            ET.SubElement(nueva_instancia, 'idCliente').text = self.id_cliente
            ET.SubElement(nueva_instancia, 'idConfiguracion').text = str(self.id_configuracion)
            ET.SubElement(nueva_instancia, 'nombre').text = self.nombre
            ET.SubElement(nueva_instancia, 'fechaInicio').text = self.fecha_inicio.strftime('%d/%m/%Y')
            ET.SubElement(nueva_instancia, 'estado').text = self.estado
            if self.fecha_final:
                ET.SubElement(nueva_instancia, 'fechaFinal').text = self.fecha_final.strftime('%d/%m/%Y')
        
        self._guardar_xml(root)
        return True
    
    @staticmethod
    def obtener_por_id(id_instancia):
        root = Instancia._obtener_root()
        instancias = root.find('instancias')
        instancia_elem = Instancia._extraer_elemento(instancias, 'instancia', id_instancia)
        if instancia_elem is not None:
            id_cliente = instancia_elem.find('idCliente').text
            fecha_inicio_str = instancia_elem.find('fechaInicio').text
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%d/%m/%Y')
            estado = instancia_elem.find('estado').text
            fecha_final = None
            if estado == 'Cancelada':
                fecha_final_elem = instancia_elem.find('fechaFinal')
                if fecha_final_elem is not None and fecha_final_elem.text:
                    fecha_final = datetime.strptime(fecha_final_elem.text, '%d/%m/%Y')
            
            return Instancia(
                int(instancia_elem.get('id')),
                id_cliente,
                int(instancia_elem.find('idConfiguracion').text),
                instancia_elem.find('nombre').text,
                fecha_inicio,
                estado,
                fecha_final
            )
        return None
    
    @staticmethod
    def obtener_todas():
        root = Instancia._obtener_root()
        instancias = []
        instancias_elem = root.find('instancias')
        if instancias_elem is not None:
            for instancia_elem in instancias_elem.findall('instancia'):
                id_cliente = instancia_elem.find('idCliente').text
                fecha_inicio_str = instancia_elem.find('fechaInicio').text
                fecha_inicio = datetime.strptime(fecha_inicio_str, '%d/%m/%Y')
                estado = instancia_elem.find('estado').text
                fecha_final = None
                if estado == 'Cancelada':
                    fecha_final_elem = instancia_elem.find('fechaFinal')
                    if fecha_final_elem is not None and fecha_final_elem.text:
                        fecha_final = datetime.strptime(fecha_final_elem.text, '%d/%m/%Y')
                
                instancias.append(Instancia(
                    int(instancia_elem.get('id')),
                    id_cliente,
                    int(instancia_elem.find('idConfiguracion').text),
                    instancia_elem.find('nombre').text,
                    fecha_inicio,
                    estado,
                    fecha_final
                ))
        return instancias
    
    def to_dict(self):
        return {
            'id': self.id,
            'idCliente': self.id_cliente,
            'idConfiguracion': self.id_configuracion,
            'nombre': self.nombre,
            'fechaInicio': self.fecha_inicio.strftime('%d/%m/%Y'),
            'estado': self.estado,
            'fechaFinal': self.fecha_final.strftime('%d/%m/%Y') if self.fecha_final else None
        }

class Consumo(ModeloBase):
    def __init__(self, id_instancia, nit_cliente, tiempo_consumido, fecha_hora):
        self.id_instancia = id_instancia
        self.nit_cliente = nit_cliente
        self.tiempo_consumido = tiempo_consumido
        self.fecha_hora = fecha_hora
    
    def guardar(self):
        root = self._obtener_root()
        consumos = root.find('consumos')
        
        nuevo_consumo = ET.SubElement(consumos, 'consumo')
        nuevo_consumo.set('idInstancia', str(self.id_instancia))
        nuevo_consumo.set('nitCliente', self.nit_cliente)
        ET.SubElement(nuevo_consumo, 'tiempo').text = str(self.tiempo_consumido)
        ET.SubElement(nuevo_consumo, 'fechaHora').text = self.fecha_hora.strftime('%d/%m/%Y %H:%M')
        
        self._guardar_xml(root)
        return True
    
    @staticmethod
    def obtener_por_instancia(id_instancia):
        root = Consumo._obtener_root()
        consumos = []
        consumos_elem = root.find('consumos')
        if consumos_elem is not None:
            for consumo_elem in consumos_elem.findall('consumo'):
                if int(consumo_elem.get('idInstancia')) == id_instancia:
                    tiempo = float(consumo_elem.find('tiempo').text)
                    fecha_hora_str = consumo_elem.find('fechaHora').text
                    fecha_hora = datetime.strptime(fecha_hora_str, '%d/%m/%Y %H:%M')
                    consumos.append(Consumo(
                        id_instancia,
                        consumo_elem.get('nitCliente'),
                        tiempo,
                        fecha_hora
                    ))
        return consumos
    
    @staticmethod
    def obtener_todos():
        root = Consumo._obtener_root()
        consumos = []
        consumos_elem = root.find('consumos')
        if consumos_elem is not None:
            for consumo_elem in consumos_elem.findall('consumo'):
                tiempo = float(consumo_elem.find('tiempo').text)
                fecha_hora_str = consumo_elem.find('fechaHora').text
                fecha_hora = datetime.strptime(fecha_hora_str, '%d/%m/%Y %H:%M')
                consumos.append(Consumo(
                    int(consumo_elem.get('idInstancia')),
                    consumo_elem.get('nitCliente'),
                    tiempo,
                    fecha_hora
                ))
        return consumos
    
    def to_dict(self):
        return {
            'idInstancia': self.id_instancia,
            'nitCliente': self.nit_cliente,
            'tiempo': self.tiempo_consumido,
            'fechaHora': self.fecha_hora.strftime('%d/%m/%Y %H:%M')
        }

class Factura(ModeloBase):
    def __init__(self, nit_cliente, fecha_emision, monto_total, detalles):
        self.id = self._generar_id_factura()
        self.nit_cliente = nit_cliente
        self.fecha_emision = fecha_emision
        self.monto_total = monto_total
        self.detalles = detalles
    
    def _generar_id_factura(self):
        # ✅ CORREGIDO: Usar timestamp más un random para evitar duplicados
        import time
        import random
        return int(time.time() * 1000) + random.randint(100, 999)  # ✅ También necesita datetime aquí
    
    def to_dict(self):
        return {
            'id': self.id,
            'nitCliente': self.nit_cliente,
            'fechaEmision': self.fecha_emision.strftime('%d/%m/%Y'),
            'montoTotal': self.monto_total,
            'detalles': self.detalles
        }

    def guardar(self):
        root = self._obtener_root()
        facturas = root.find('facturas')
        
        nueva_factura = ET.SubElement(facturas, 'factura')
        nueva_factura.set('id', str(self.id))
        ET.SubElement(nueva_factura, 'nitCliente').text = self.nit_cliente
        ET.SubElement(nueva_factura, 'fechaEmision').text = self.fecha_emision.strftime('%d/%m/%Y')  # ✅ Formatear correctamente
        ET.SubElement(nueva_factura, 'montoTotal').text = str(self.monto_total)
        
        detalles_elem = ET.SubElement(nueva_factura, 'detalles')
        for detalle in self.detalles:
            detalle_elem = ET.SubElement(detalles_elem, 'detalle')
            ET.SubElement(detalle_elem, 'idInstancia').text = str(detalle['id_instancia'])
            ET.SubElement(detalle_elem, 'nombreInstancia').text = detalle['nombre_instancia']
            ET.SubElement(detalle_elem, 'idRecurso').text = str(detalle['id_recurso'])
            ET.SubElement(detalle_elem, 'nombreRecurso').text = detalle['nombre_recurso']
            ET.SubElement(detalle_elem, 'cantidad').text = str(detalle['cantidad'])
            ET.SubElement(detalle_elem, 'tiempoConsumido').text = str(detalle['tiempo_consumido'])
            ET.SubElement(detalle_elem, 'costoUnitario').text = str(detalle['costo_unitario'])
            ET.SubElement(detalle_elem, 'costoTotal').text = str(detalle['costo_total'])
        
        self._guardar_xml(root)
        return True
    
    @staticmethod
    def obtener_por_id(id_factura):
        root = Factura._obtener_root()
        facturas = root.find('facturas')
        factura_elem = Factura._extraer_elemento(facturas, 'factura', id_factura)
        if factura_elem is not None:
            nit_cliente = factura_elem.find('nitCliente').text
            fecha_emision_str = factura_elem.find('fechaEmision').text
            fecha_emision = datetime.strptime(fecha_emision_str, '%d/%m/%Y')
            monto_total = float(factura_elem.find('montoTotal').text)
            
            detalles = []
            detalles_elem = factura_elem.find('detalles')
            if detalles_elem is not None:
                for detalle_elem in detalles_elem.findall('detalle'):
                    detalles.append({
                        'id_instancia': int(detalle_elem.find('idInstancia').text),
                        'nombre_instancia': detalle_elem.find('nombreInstancia').text,
                        'id_recurso': int(detalle_elem.find('idRecurso').text),
                        'nombre_recurso': detalle_elem.find('nombreRecurso').text,
                        'cantidad': float(detalle_elem.find('cantidad').text),
                        'tiempo_consumido': float(detalle_elem.find('tiempoConsumido').text),
                        'costo_unitario': float(detalle_elem.find('costoUnitario').text),
                        'costo_total': float(detalle_elem.find('costoTotal').text)
                    })
            
            factura = Factura(nit_cliente, fecha_emision, monto_total, detalles)
            factura.id = int(factura_elem.get('id'))
            return factura
        return None
    
    @staticmethod
    def obtener_todas():
        root = Factura._obtener_root()
        facturas = []
        facturas_elem = root.find('facturas')
        if facturas_elem is not None:
            for factura_elem in facturas_elem.findall('factura'):
                nit_cliente = factura_elem.find('nitCliente').text
                fecha_emision_str = factura_elem.find('fechaEmision').text
                fecha_emision = datetime.strptime(fecha_emision_str, '%d/%m/%Y')
                monto_total = float(factura_elem.find('montoTotal').text)
                
                detalles = []
                detalles_elem = factura_elem.find('detalles')
                if detalles_elem is not None:
                    for detalle_elem in detalles_elem.findall('detalle'):
                        detalles.append({
                            'id_instancia': int(detalle_elem.find('idInstancia').text),
                            'nombre_instancia': detalle_elem.find('nombreInstancia').text,
                            'id_recurso': int(detalle_elem.find('idRecurso').text),
                            'nombre_recurso': detalle_elem.find('nombreRecurso').text,
                            'cantidad': float(detalle_elem.find('cantidad').text),
                            'tiempo_consumido': float(detalle_elem.find('tiempoConsumido').text),
                            'costo_unitario': float(detalle_elem.find('costoUnitario').text),
                            'costo_total': float(detalle_elem.find('costoTotal').text)
                        })
                
                factura = Factura(nit_cliente, fecha_emision, monto_total, detalles)
                factura.id = int(factura_elem.get('id'))
                facturas.append(factura)
        return facturas
    
    def to_dict(self):
        return {
            'id': self.id,
            'nitCliente': self.nit_cliente,
            'fechaEmision': self.fecha_emision.strftime('%d/%m/%Y'),
            'montoTotal': self.monto_total,
            'detalles': self.detalles
        }