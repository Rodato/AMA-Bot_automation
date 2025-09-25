#!/usr/bin/env python3
import requests
import json

# Configuración
TOKEN = "bp_pat_t3Qzk5mKulbKTudzrZHEJ2Rjqkb6z9f6qrw9"
BOT_ID = "f70c360d-ed8d-402f-9cd2-488d9f1d358c"
TABLE_NAME = "DataJsonProgressTable"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "x-bot-id": BOT_ID,
    "Content-Type": "application/json"
}

print("🔗 Obteniendo filas usando findTableRows...")

# Usar el endpoint correcto: findTableRows
url = f"https://api.botpress.cloud/v1/tables/{TABLE_NAME}/rows/find"

# Payload para obtener todas las filas (sin filtro)
payload = {
    "limit": 1000  # Límite alto para obtener todas las filas
}

try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Filas obtenidas!")
        print(f"Claves: {list(data.keys())}")
        
        if 'rows' in data and isinstance(data['rows'], list):
            rows = data['rows']
            print(f"📊 Número de filas: {len(rows)}")
            
            # Mostrar cada fila
            for i, row in enumerate(rows):
                client_num = row.get('clientNumber', 'N/A')
                session1 = row.get('session1', {})
                print(f"\n{i+1:2d}. Cliente: {client_num}")
                print(f"    session1: {session1}")
                
                # Mostrar estado del día 1
                if isinstance(session1, dict) and '1' in session1:
                    day1_status = session1['1']
                    status_text = "COMPLETADO" if day1_status == '2' else "ENVIADO" if day1_status == '1' else "NO ENVIADO"
                    print(f"    Día 1: {status_text} ({day1_status})")
                    
            print(f"\n💾 Guardando como CSV...")
            # Convertir a CSV simple
            with open('botpress_data.csv', 'w') as f:
                f.write('clientNumber,session1_day1,session1_day2,session1_day3,session1_day4,session1_day5\n')
                for row in rows:
                    client_num = row.get('clientNumber', '')
                    session1 = row.get('session1', {})
                    day1 = session1.get('1', '0')
                    day2 = session1.get('2', '0')
                    day3 = session1.get('3', '0')
                    day4 = session1.get('4', '0')
                    day5 = session1.get('5', '0')
                    f.write(f'{client_num},{day1},{day2},{day3},{day4},{day5}\n')
            print(f"✅ Guardado como botpress_data.csv")
                    
        else:
            print("❌ No se encontraron filas en la respuesta")
            print(f"Respuesta: {json.dumps(data, indent=2)}")
            
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")

print("\n✅ Proceso terminado")