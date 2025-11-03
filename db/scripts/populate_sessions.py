#!/usr/bin/env python3
"""
Script para poblar las tablas de sesiones desde control_envios.csv
Migra el progreso real de cada usuario por sesión y día
"""

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv
from collections import defaultdict

# Cargar variables de entorno
load_dotenv()

def analyze_current_progress():
    """Analizar el progreso actual en el CSV"""
    
    print("🔍 ANALIZANDO PROGRESO ACTUAL")
    print("=" * 40)
    
    df = pd.read_csv('control_envios.csv', dtype={'numero': str})
    
    # Usuarios únicos
    total_users = df['numero'].nunique()
    print(f"👥 Total usuarios: {total_users}")
    
    # Usuarios con completados
    active_users = df[df['completado'] == 1]['numero'].nunique()
    print(f"🎯 Usuarios activos: {active_users}")
    
    # Progreso por sesión
    print("\n📊 COMPLETADOS POR SESIÓN:")
    for session in sorted(df['sesion'].unique()):
        completed_in_session = len(df[(df['sesion'] == session) & (df['completado'] == 1)])
        print(f"  Sesión {session}: {completed_in_session} completados")
    
    # Detalle de sesión 1
    print("\n📋 DETALLE SESIÓN 1 (ÚNICA CON DATOS):")
    session_1_completed = df[(df['sesion'] == 1) & (df['completado'] == 1)]
    for day in sorted(session_1_completed['day'].unique()):
        count = len(session_1_completed[session_1_completed['day'] == day])
        print(f"  Día {day}: {count} completados")
    
    return df

def build_user_progress(df):
    """Construir estructura de progreso por usuario"""
    
    print("\n🏗️ CONSTRUYENDO ESTRUCTURA DE PROGRESO")
    print("=" * 45)
    
    # Diccionario para almacenar progreso por usuario
    user_progress = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    
    # Procesar solo registros completados
    completed_df = df[df['completado'] == 1]
    
    for _, row in completed_df.iterrows():
        number = row['numero']
        session = row['sesion']
        day = row['day']
        
        # Marcar como completado (1)
        user_progress[number][session][day] = 1
    
    print(f"✅ Progreso construido para {len(user_progress)} usuarios activos")
    
    # Mostrar algunos ejemplos
    print("\n📋 EJEMPLOS DE PROGRESO:")
    for i, (number, sessions) in enumerate(list(user_progress.items())[:3]):
        progress_str = []
        for session, days in sessions.items():
            for day, completed in days.items():
                if completed:
                    progress_str.append(f"S{session}D{day}")
        print(f"  Usuario {number}: {' → '.join(progress_str)}")
    
    return user_progress

def populate_sessions_tables(user_progress):
    """Poblar tablas de sesiones en Supabase"""
    
    print("\n💾 POBLANDO TABLAS DE SESIONES")
    print("=" * 35)
    
    # Configurar Supabase
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    # Obtener todos los usuarios de la tabla users
    users_result = supabase.table('users').select('number').execute()
    all_users = [user['number'] for user in users_result.data]
    print(f"👥 Total usuarios en BD: {len(all_users)}")
    
    try:
        # Poblar cada tabla de sesión (1 a 9)
        for session_num in range(1, 10):
            print(f"\n📚 Procesando session_{session_num}...")
            
            session_data = []
            users_with_progress = 0
            
            for number in all_users:
                # Inicializar record con todos los días en 0
                record = {
                    'number': number,
                    'day_1': 0,
                    'day_2': 0,
                    'day_3': 0,
                    'day_4': 0,
                    'day_5': 0
                }
                
                # Si el usuario tiene progreso en esta sesión, actualizar
                if number in user_progress and session_num in user_progress[number]:
                    session_progress = user_progress[number][session_num]
                    
                    for day in range(1, 6):  # días 1-5
                        if day in session_progress:
                            record[f'day_{day}'] = session_progress[day]
                            users_with_progress += 1
                
                session_data.append(record)
            
            # Limpiar tabla antes de insertar
            print(f"🗑️ Limpiando tabla session_{session_num}...")
            supabase.table(f'session_{session_num}').delete().neq('number', '').execute()
            
            # Insertar datos en lotes
            batch_size = 50
            total_inserted = 0
            
            for i in range(0, len(session_data), batch_size):
                batch = session_data[i:i + batch_size]
                result = supabase.table(f'session_{session_num}').upsert(batch).execute()
                total_inserted += len(batch)
                print(f"  📦 Lote {i//batch_size + 1}: {len(batch)} usuarios insertados")
            
            print(f"✅ session_{session_num}: {total_inserted} usuarios, {users_with_progress} con progreso")
        
        print(f"\n🎉 ¡TODAS LAS TABLAS POBLADAS EXITOSAMENTE!")
        return True
        
    except Exception as e:
        print(f"❌ Error poblando tablas: {e}")
        return False

def verify_migration():
    """Verificar que la migración fue exitosa"""
    
    print("\n🔍 VERIFICANDO MIGRACIÓN")
    print("=" * 30)
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        for session_num in range(1, 10):
            # Contar usuarios con al menos un día completado
            result = supabase.table(f'session_{session_num}').select('*').execute()
            users_with_progress = 0
            total_completed_days = 0
            
            for user in result.data:
                has_progress = any([
                    user['day_1'], user['day_2'], user['day_3'], 
                    user['day_4'], user['day_5']
                ])
                if has_progress:
                    users_with_progress += 1
                
                total_completed_days += sum([
                    user['day_1'], user['day_2'], user['day_3'], 
                    user['day_4'], user['day_5']
                ])
            
            print(f"📚 session_{session_num}: {len(result.data)} usuarios, {users_with_progress} activos, {total_completed_days} días completados")
        
        # Verificación específica de session_1 (la única con datos reales)
        print(f"\n🎯 VERIFICACIÓN DETALLADA session_1:")
        s1_result = supabase.table('session_1').select('*').execute()
        
        day_counts = {'day_1': 0, 'day_2': 0, 'day_3': 0, 'day_4': 0, 'day_5': 0}
        for user in s1_result.data:
            for day in day_counts:
                if user[day] == 1:
                    day_counts[day] += 1
        
        for day, count in day_counts.items():
            print(f"  {day}: {count} usuarios completados")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando migración: {e}")
        return False

def main():
    """Función principal"""
    
    print("🚀 MIGRACIÓN DE DATOS A TABLAS DE SESIONES")
    print("=" * 50)
    
    # 1. Analizar progreso actual
    df = analyze_current_progress()
    
    # 2. Construir estructura de progreso
    user_progress = build_user_progress(df)
    
    # 3. Poblar tablas
    if not populate_sessions_tables(user_progress):
        return
    
    # 4. Verificar migración
    if not verify_migration():
        return
    
    print("\n✅ ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
    print("\n📊 RESUMEN:")
    print("  - session_1: Con datos reales de progreso")
    print("  - session_2 a session_9: Listas para futuros datos")
    print("  - Todos los usuarios inicializados en todas las sesiones")

if __name__ == "__main__":
    main()