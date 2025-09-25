import requests
import time
import json

# Configuración
url = "https://webhook.botpress.cloud/2d63c736-0910-47a8-b06a-c82c12372106"
headers = {
    "x-bp-secret": "73c380fc550ad6b061d4d8ec3547731eprod",
    "Content-Type": "application/json"
}

# Lista de números de teléfono
numeros = [
    573128621393,
    573004117851
    # Agrega más números aquí
]

# Enviar request para cada número
for numero in numeros:
    data = {
        "clientNumber": numero,
        "session": 1,
        "day": 5
    }
    
    try:
        print(f"Enviando para número: {numero}")
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Status: {response.status_code}")
        print(f"Respuesta: {response.text}")
        print("-" * 30)
        
        # Pausa entre requests
        time.sleep(1)
        
    except Exception as e:
        print(f"Error con número {numero}: {e}")