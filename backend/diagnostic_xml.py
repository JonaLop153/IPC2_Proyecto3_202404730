# diagnostic_xml.py
import os

def diagnosticar_xml():
    print("=== DIAGNÓSTICO DE ARCHIVOS XML ===")
    
    # Verificar archivo configuracion.xml
    print("\n1. Verificando configuracion.xml:")
    if os.path.exists('configuracion.xml'):
        with open('configuracion.xml', 'rb') as f:
            content = f.read()
        print("   - Existe: Sí")
        print(f"   - Tamaño: {len(content)} bytes")
        print(f"   - Primeros 100 bytes: {content[:100]}")
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            print("   - XML válido: Sí")
            print(f"   - Elemento raíz: {root.tag}")
        except Exception as e:
            print(f"   - XML válido: No - Error: {e}")
    else:
        print("   - Existe: No")
    
    # Verificar archivo consumo.xml
    print("\n2. Verificando consumo.xml:")
    if os.path.exists('consumo.xml'):
        with open('consumo.xml', 'rb') as f:
            content = f.read()
        print("   - Existe: Sí")
        print(f"   - Tamaño: {len(content)} bytes")
        print(f"   - Primeros 100 bytes: {content[:100]}")
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            print("   - XML válido: Sí")
            print(f"   - Elemento raíz: {root.tag}")
        except Exception as e:
            print(f"   - XML válido: No - Error: {e}")
    else:
        print("   - Existe: No")

if __name__ == '__main__':
    diagnosticar_xml()