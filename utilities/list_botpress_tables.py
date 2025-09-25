#!/usr/bin/env python3
import requests
import json

# Configuración
TOKEN = "bp_pat_t3Qzk5mKulbKTudzrZHEJ2Rjqkb6z9f6qrw9"
BOT_ID = "f70c360d-ed8d-402f-9cd2-488d9f1d358c"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "x-bot-id": BOT_ID,
    "Content-Type": "application/json"
}

print("🔗 Conectando a Botpress API...")
print(f"Bot ID: {BOT_ID}")

# Listar todas las tablas
url = "https://api.botpress.cloud/v1/tables"


response = requests.get(url, headers=headers)
print(response.status_code)

if response.status_code == 200:
    print("✅ Conexión exitosa!")
else:
    print("❌ Error en la conexión")


response = requests.get(url, headers=headers)

data=response.json()
print(f"Estructura: {list(data.keys())}")

#print(json.dumps(data, indent=2))

#listamos todas las tablas en el workspace
tables = data['tables']
print(f"\n📊 TABLAS ENCONTRADAS ({len(tables)}):")
print("-" * 50)

for table in tables:
    name = table.get('name', 'Sin nombre')
    table_id = table.get('id', 'Sin ID')
    print(f"Nombre: {name}")
    print(f"ID: {table_id}")
    print()



url = "https://api.botpress.cloud/v1/tables/DataJsonProgressTable"

response = requests.get(url, headers=headers)

print(response.json())

# try:
#     response = requests.get(url, headers=headers)
#     print(f"Status: {response.status_code}")
    
#     if response.status_code == 200:
#         data = response.json()
#         print(f"✅ Respuesta exitosa!")
#         print(f"Estructura: {list(data.keys()) if isinstance(data, dict) else 'No es dict'}")
        
#         # Mostrar respuesta completa
#         print(f"\n📋 RESPUESTA COMPLETA:")
#         print(json.dumps(data, indent=2))
        
#         # Si hay tablas, listarlas
#         if 'tables' in data:
#             tables = data['tables']
#             print(f"\n📊 TABLAS ENCONTRADAS ({len(tables)}):")
#             print("-" * 50)
            
#             for i, table in enumerate(tables):
#                 name = table.get('name', 'Sin nombre')
#                 table_id = table.get('id', 'Sin ID')
#                 rows = table.get('rows', 'N/A')
#                 print(f"{i+1:2d}. {name}")
#                 print(f"     ID: {table_id}")
#                 print(f"     Filas: {rows}")
#                 print()
        
#     else:
#         print(f"❌ Error: {response.status_code}")
#         print(f"Response: {response.text}")
        
# except Exception as e:
#     print(f"❌ Exception: {e}")

# print("\n✅ Proceso terminado")