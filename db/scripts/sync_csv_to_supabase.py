#!/usr/bin/env python3
"""
Script para sincronizar control_envios.csv con Supabase
Detecta cambios automáticamente y actualiza la base de datos
"""

import os
import pandas as pd
import requests
import io
from datetime import datetime
from collections import defaultdict
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_supabase_client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def download_latest_csv():
    """Descargar el CSV más reciente desde GitHub"""
    
    print("🌐 DESCARGANDO CSV REMOTO DESDE GITHUB")
    print("=" * 45)
    
    github_url = "https://raw.githubusercontent.com/Rodato/AMA-Bot_automation/main/control_envios.csv"
    
    try:
        response = requests.get(github_url, timeout=30)
        response.raise_for_status()
        
        csv_content = io.StringIO(response.text)
        df = pd.read_csv(csv_content, dtype={'numero': str})
        
        print(f"✅ CSV descargado: {len(df)} registros, {df['numero'].nunique()} usuarios")
        return df
        
    except Exception as e:
        print(f"❌ Error descargando CSV: {e}")
        return None

def determine_city(numero):
    """Determinar ciudad basada en el prefijo del número"""
    if numero.startswith('59'):
        return 'Lago Agrio'
    elif numero.startswith('51'):
        return 'Iquitos'
    else:
        return 'Desconocido'

def get_users_from_supabase():
    """Obtener usuarios actuales de Supabase"""
    
    print("\n📊 OBTENIENDO USUARIOS ACTUALES DE SUPABASE")
    print("=" * 50)
    
    try:
        supabase = get_supabase_client()
        result = supabase.table('users').select('number').execute()
        
        existing_users = set([user['number'] for user in result.data])
        print(f"✅ Usuarios en Supabase: {len(existing_users)}")
        
        return existing_users
        
    except Exception as e:
        print(f"❌ Error obteniendo usuarios de Supabase: {e}")
        return set()

def sync_new_users(df, existing_users):
    """Sincronizar usuarios nuevos"""
    
    print("\n➕ SINCRONIZANDO USUARIOS NUEVOS")
    print("=" * 35)
    
    # Identificar usuarios nuevos
    csv_users = set(df['numero'].unique())
    new_users = csv_users - existing_users
    
    if not new_users:
        print("✅ No hay usuarios nuevos para agregar")
        return True
    
    print(f"🆕 Usuarios nuevos detectados: {len(new_users)}")
    
    try:
        supabase = get_supabase_client()
        
        # Preparar datos de usuarios nuevos
        new_users_data = []
        for numero in new_users:
            user_row = df[df['numero'] == numero].iloc[0]
            
            user_record = {
                'number': numero,
                'location': user_row['location'],
                'location_name': user_row['location_name'],
                'salon': user_row['salon'] if pd.notna(user_row['salon']) else None,
                'city': determine_city(numero)
            }
            new_users_data.append(user_record)
        
        # Insertar nuevos usuarios
        print(f"👥 Insertando {len(new_users_data)} usuarios nuevos...")
        result = supabase.table('users').upsert(new_users_data).execute()
        print(f"✅ Usuarios insertados exitosamente")
        
        # Inicializar sesiones para usuarios nuevos
        for session_num in range(1, 10):
            session_data = []
            for numero in new_users:
                record = {
                    'number': numero,
                    'day_1': 0, 'day_2': 0, 'day_3': 0, 'day_4': 0, 'day_5': 0
                }
                session_data.append(record)
            
            print(f"📚 Inicializando session_{session_num} para {len(session_data)} usuarios...")
            result = supabase.table(f'session_{session_num}').upsert(session_data).execute()
        
        print(f"✅ {len(new_users)} usuarios nuevos sincronizados completamente")
        return True
        
    except Exception as e:
        print(f"❌ Error sincronizando usuarios nuevos: {e}")
        return False

def sync_session_progress(df):
    """Sincronizar progreso de sesiones desde CSV"""
    
    print("\n🔄 SINCRONIZANDO PROGRESO DE SESIONES")
    print("=" * 40)
    
    try:
        supabase = get_supabase_client()
        
        # Construir estructura de progreso por usuario
        user_progress = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        
        # Procesar solo registros completados
        completed_df = df[df['completado'] == 1]
        print(f"📊 Procesando {len(completed_df)} registros completados...")
        
        for _, row in completed_df.iterrows():
            number = row['numero']
            session = row['sesion']
            day = row['day']
            user_progress[number][session][day] = 1
        
        print(f"✅ Progreso construido para {len(user_progress)} usuarios activos")
        
        # Actualizar cada tabla de sesión
        updates_summary = {}
        
        for session_num in range(1, 10):
            print(f"\n📚 Actualizando session_{session_num}...")
            
            # Obtener estado actual de la sesión
            current_result = supabase.table(f'session_{session_num}').select('*').execute()
            current_data = {user['number']: user for user in current_result.data}
            
            updates_needed = []
            
            for number, current_user in current_data.items():
                # Calcular nuevo estado basado en CSV
                new_state = {
                    'number': number,
                    'day_1': 0, 'day_2': 0, 'day_3': 0, 'day_4': 0, 'day_5': 0
                }
                
                # Si el usuario tiene progreso en esta sesión
                if number in user_progress and session_num in user_progress[number]:
                    session_progress = user_progress[number][session_num]
                    for day in range(1, 6):
                        if day in session_progress:
                            new_state[f'day_{day}'] = 1
                
                # Verificar si hay cambios
                needs_update = False
                for day in range(1, 6):
                    if current_user[f'day_{day}'] != new_state[f'day_{day}']:
                        needs_update = True
                        break
                
                if needs_update:
                    updates_needed.append(new_state)
            
            # Aplicar actualizaciones si hay cambios
            if updates_needed:
                print(f"  📝 Actualizando {len(updates_needed)} usuarios...")
                result = supabase.table(f'session_{session_num}').upsert(updates_needed).execute()
                updates_summary[session_num] = len(updates_needed)
            else:
                print(f"  ✅ Sin cambios necesarios")
                updates_summary[session_num] = 0
        
        # Resumen de actualizaciones
        print(f"\n📊 RESUMEN DE ACTUALIZACIONES:")
        total_updates = 0
        for session_num, count in updates_summary.items():
            if count > 0:
                print(f"  session_{session_num}: {count} usuarios actualizados")
                total_updates += count
        
        if total_updates == 0:
            print("  ✅ Todas las sesiones ya estaban actualizadas")
        else:
            print(f"  🎉 Total: {total_updates} actualizaciones aplicadas")
        
        return True
        
    except Exception as e:
        print(f"❌ Error sincronizando progreso: {e}")
        return False

def verify_sync():
    """Verificar que la sincronización fue exitosa"""
    
    print("\n🔍 VERIFICANDO SINCRONIZACIÓN")
    print("=" * 30)
    
    try:
        supabase = get_supabase_client()
        
        # Verificar tabla users
        users_result = supabase.table('users').select('*').execute()
        print(f"👥 Usuarios en BD: {len(users_result.data)}")
        
        # Verificar progreso por sesión
        for session_num in range(1, 10):
            result = supabase.table(f'session_{session_num}').select('*').execute()
            
            users_with_progress = 0
            total_completed_days = 0
            
            for user in result.data:
                days_completed = sum([
                    user['day_1'], user['day_2'], user['day_3'], 
                    user['day_4'], user['day_5']
                ])
                
                if days_completed > 0:
                    users_with_progress += 1
                
                total_completed_days += days_completed
            
            if users_with_progress > 0:
                print(f"📚 session_{session_num}: {users_with_progress} usuarios activos, {total_completed_days} días completados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando sincronización: {e}")
        return False

def main():
    """Función principal"""
    
    print("🔄 SINCRONIZACIÓN CSV → SUPABASE")
    print("=" * 40)
    print(f"🕒 Ejecutado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. Descargar CSV más reciente
    df = download_latest_csv()
    if df is None:
        return False
    
    # 2. Obtener usuarios actuales de Supabase
    existing_users = get_users_from_supabase()
    
    # 3. Sincronizar usuarios nuevos
    if not sync_new_users(df, existing_users):
        return False
    
    # 4. Sincronizar progreso de sesiones
    if not sync_session_progress(df):
        return False
    
    # 5. Verificar sincronización
    if not verify_sync():
        return False
    
    print("\n🎉 ¡SINCRONIZACIÓN COMPLETADA EXITOSAMENTE!")
    print("📈 Dashboard actualizada con datos más recientes")
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n❌ Sincronización falló")
        sys.exit(1)
    else:
        print("\n✅ Sincronización exitosa")
        sys.exit(0)