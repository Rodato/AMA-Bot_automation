#!/usr/bin/env python3
import pandas as pd
import requests
import time
from datetime import datetime

def reset_and_send_specific_users():
    """Resetear y reenviar a usuarios específicos"""
    
    # Números a resetear y reenviar
    numeros_resetear = ['573159267303', '573155503266']
    
    print("🔧 RESETEO Y REENVÍO DE USUARIOS ESPECÍFICOS")
    print("=" * 50)
    
    # Cargar CSV
    try:
        df = pd.read_csv('control_envios.csv', dtype={'numero': str})
        print(f"✅ CSV cargado: {len(df)} registros")
    except Exception as e:
        print(f"❌ Error cargando CSV: {e}")
        return
    
    # Webhook config
    webhook_url = "https://webhook.botpress.cloud/2d63c736-0910-47a8-b06a-c82c12372106"
    headers = {
        "x-bp-secret": "73c380fc550ad6b061d4d8ec3547731eprod",
        "Content-Type": "application/json"
    }
    
    enviados_exitosos = 0
    
    for numero in numeros_resetear:
        print(f"\n📞 PROCESANDO: {numero}")
        
        # 1. Resetear en CSV (sesión 1, día 1)
        filtro = (df['numero'] == numero) & (df['sesion'] == 1) & (df['day'] == 1)
        registros = df[filtro]
        
        if len(registros) == 0:
            print(f"   ❌ No se encontró registro para {numero} sesión 1 día 1")
            continue
        
        index = registros.index[0]
        
        # Resetear valores
        df.at[index, 'enviado'] = 0
        df.at[index, 'intentos_envio'] = 0
        df.at[index, 'fecha_envio'] = ''
        df.at[index, 'resultado'] = ''
        df.at[index, 'completado'] = 0
        df.at[index, 'fecha_completado'] = ''
        df.at[index, 'ultimo_estado_botpress'] = 0
        
        print(f"   🔧 Usuario reseteado en CSV")
        
        # 2. Enviar mensaje
        data = {
            "clientNumber": int(numero),
            "session": 1,
            "day": 1
        }
        
        print(f"   📤 Enviando mensaje...")
        print(f"      Data: {data}")
        
        try:
            response = requests.post(webhook_url, headers=headers, json=data, timeout=10)
            
            # Actualizar CSV con resultado
            df.at[index, 'intentos_envio'] = 1
            df.at[index, 'fecha_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            df.at[index, 'resultado'] = f"Status: {response.status_code} (Reset y reenvío)"
            
            if response.status_code == 200:
                df.at[index, 'enviado'] = 1
                print(f"   ✅ ENVIADO EXITOSAMENTE")
                print(f"      Status: {response.status_code}")
                print(f"      Respuesta: {response.text}")
                enviados_exitosos += 1
            else:
                df.at[index, 'enviado'] = 0
                print(f"   ❌ ERROR EN ENVÍO")
                print(f"      Status: {response.status_code}")
                print(f"      Respuesta: {response.text}")
                
        except Exception as e:
            df.at[index, 'enviado'] = 0
            df.at[index, 'resultado'] = f"Error: {str(e)}"
            print(f"   ❌ EXCEPCIÓN: {e}")
        
        # Pausa entre envíos
        time.sleep(3)
    
    # Guardar cambios
    try:
        df.to_csv('control_envios.csv', index=False)
        print(f"\n💾 CSV actualizado correctamente")
    except Exception as e:
        print(f"\n❌ Error guardando CSV: {e}")
    
    # Resumen
    print(f"\n📊 RESUMEN:")
    print(f"   🔧 Usuarios reseteados: {len(numeros_resetear)}")
    print(f"   ✅ Envíos exitosos: {enviados_exitosos}")
    print(f"   ❌ Envíos fallidos: {len(numeros_resetear) - enviados_exitosos}")
    
    if enviados_exitosos > 0:
        print(f"\n📋 USUARIOS CON ENVÍO EXITOSO:")
        for numero in numeros_resetear:
            filtro = (df['numero'] == numero) & (df['sesion'] == 1) & (df['day'] == 1)
            registro = df[filtro].iloc[0] if len(df[filtro]) > 0 else None
            if registro is not None and registro['enviado'] == 1:
                print(f"   📞 {numero} → Sesión 1, Día 1")
    
    print(f"\n✅ PROCESO COMPLETADO")
    print("=" * 50)

if __name__ == "__main__":
    reset_and_send_specific_users()