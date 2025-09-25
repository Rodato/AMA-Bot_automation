#!/usr/bin/env python3
import requests
import json
import time

# Configuración del webhook
webhook_url = "https://webhook.botpress.cloud/2d63c736-0910-47a8-b06a-c82c12372106"
headers = {
    "x-bp-secret": "73c380fc550ad6b061d4d8ec3547731eprod",
    "Content-Type": "application/json"
}

def test_webhook_basic():
    """Hacer una petición básica de test al webhook"""
    print("🔍 TESTING WEBHOOK BÁSICO...")
    
    # Usar un número de prueba
    test_data = {
        "clientNumber": 573000000000,  # Número de prueba
        "session": 1,
        "day": 1
    }
    
    try:
        print(f"📤 Enviando petición de test...")
        print(f"   URL: {webhook_url}")
        print(f"   Headers: {headers}")
        print(f"   Data: {test_data}")
        
        response = requests.post(webhook_url, headers=headers, json=test_data, timeout=10)
        
        print(f"\n📊 RESPUESTA DEL WEBHOOK:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        print(f"   Content: {response.text}")
        print(f"   Tiempo respuesta: {response.elapsed.total_seconds():.2f}s")
        
        return response.status_code, response.text
        
    except requests.exceptions.Timeout:
        print("❌ TIMEOUT: El webhook tardó más de 10 segundos en responder")
        return None, "Timeout"
    except requests.exceptions.ConnectionError:
        print("❌ CONNECTION ERROR: No se pudo conectar al webhook")
        return None, "Connection Error"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None, str(e)

def test_webhook_real_numbers():
    """Probar con los números que fallaron"""
    print("\n🔍 TESTING NÚMEROS PROBLEMÁTICOS...")
    
    numeros_problema = [573159267303, 573155503266]
    
    for numero in numeros_problema:
        print(f"\n📞 Probando número: {numero}")
        
        test_data = {
            "clientNumber": numero,
            "session": 1,
            "day": 1
        }
        
        try:
            response = requests.post(webhook_url, headers=headers, json=test_data, timeout=10)
            
            print(f"   Status: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
            if response.status_code == 200:
                print("   ✅ Webhook respondió OK")
            else:
                print("   ❌ Webhook falló")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)  # Pausa entre pruebas

def test_webhook_formats():
    """Probar diferentes formatos de datos"""
    print("\n🔍 TESTING FORMATOS DE DATOS...")
    
    formats_to_test = [
        {"clientNumber": 573159267303, "session": 1, "day": 1},  # int
        {"clientNumber": "573159267303", "session": "1", "day": "1"},  # string
        {"clientNumber": "573159267303", "session": 1, "day": 1},  # mixed
    ]
    
    for i, data in enumerate(formats_to_test, 1):
        print(f"\n📋 Formato {i}: {data}")
        
        try:
            response = requests.post(webhook_url, headers=headers, json=data, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Respuesta: {response.text[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)

def test_webhook_headers():
    """Probar con diferentes headers"""
    print("\n🔍 TESTING HEADERS...")
    
    headers_to_test = [
        # Headers actuales
        {
            "x-bp-secret": "73c380fc550ad6b061d4d8ec3547731eprod",
            "Content-Type": "application/json"
        },
        # Sin Content-Type
        {
            "x-bp-secret": "73c380fc550ad6b061d4d8ec3547731eprod"
        },
        # Con User-Agent
        {
            "x-bp-secret": "73c380fc550ad6b061d4d8ec3547731eprod",
            "Content-Type": "application/json",
            "User-Agent": "AMA-Bot/1.0"
        }
    ]
    
    test_data = {
        "clientNumber": 573000000000,
        "session": 1,
        "day": 1
    }
    
    for i, test_headers in enumerate(headers_to_test, 1):
        print(f"\n🏷️  Headers {i}: {test_headers}")
        
        try:
            response = requests.post(webhook_url, headers=test_headers, json=test_data, timeout=10)
            print(f"   Status: {response.status_code}")
            print(f"   Respuesta: {response.text[:100]}...")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    print("🔍 DIAGNÓSTICO COMPLETO DEL WEBHOOK")
    print("=" * 50)
    
    # Test 1: Básico
    status, response = test_webhook_basic()
    
    # Test 2: Números problemáticos
    test_webhook_real_numbers()
    
    # Test 3: Formatos diferentes
    test_webhook_formats()
    
    # Test 4: Headers diferentes
    test_webhook_headers()
    
    print("\n" + "=" * 50)
    print("✅ DIAGNÓSTICO COMPLETADO")