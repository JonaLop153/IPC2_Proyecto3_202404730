import requests
import time
import os

def test_configuracion():
    print("=== Probando configuración ===")
    
    # Verificar que el archivo existe
    if not os.path.exists('configuracion.xml'):
        print("ERROR: configuracion.xml no existe")
        return
    
    with open('configuracion.xml', 'rb') as f:
        data = f.read()
    
    print(f"Tamaño: {len(data)} bytes")
    print(f"Primeros 200 bytes: {data[:200]}")
    
    try:
        response = requests.post(
            'http://localhost:5000/configurar',
            data=data,
            headers={'Content-Type': 'application/xml'}
        )
        print("Respuesta:", response.json())
        return response.json()
    except Exception as e:
        print(f"Error en la petición: {e}")
        return None

def test_consumo():
    print("\n=== Probando consumo ===")
    
    if not os.path.exists('consumo.xml'):
        print("ERROR: consumo.xml no existe")
        return
    
    with open('consumo.xml', 'rb') as f:
        data = f.read()
    
    print(f"Tamaño: {len(data)} bytes")
    print(f"Primeros 200 bytes: {data[:200]}")
    
    try:
        response = requests.post(
            'http://localhost:5000/consumo',
            data=data,
            headers={'Content-Type': 'application/xml'}
        )
        print("Respuesta:", response.json())
        return response.json()
    except Exception as e:
        print(f"Error en la petición: {e}")
        return None

def test_consultar():
    print("\n=== Probando consulta ===")
    try:
        response = requests.get('http://localhost:5000/consultarDatos')
        print("Respuesta:", response.json())
    except Exception as e:
        print(f"Error en la petición: {e}")

def test_reset():
    print("\n=== Probando reset ===")
    try:
        response = requests.delete('http://localhost:5000/reset')
        print("Respuesta:", response.json())
    except Exception as e:
        print(f"Error en la petición: {e}")

if __name__ == '__main__':
    # Esperar a que el servidor arranque
    print("Esperando que el servidor inicie...")
    time.sleep(3)
    
    # Probar reset primero
    test_reset()
    
    # Probar configuración
    test_configuracion()
    
    # Probar consumo
    test_consumo()
    
    # Probar consulta
    test_consultar()