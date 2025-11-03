#!/usr/bin/env python3
"""
Script para poblar la tabla users desde BotNumbers_Production.csv
"""

import os
import pandas as pd
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def determine_city(numero):
    """Determinar ciudad basada en el prefijo del número"""
    if numero.startswith('59'):
        return 'Lago Agrio'
    elif numero.startswith('51'):
        return 'Iquitos'
    else:
        return 'Desconocido'

def populate_users_table():
    """Poblar tabla users desde CSV"""
    
    print("👥 POBLANDO TABLA USERS")
    print("=" * 40)
    
    # Configurar Supabase
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # 1. Leer CSV
        print("📊 Leyendo BotNumbers_Production.csv...")
        df = pd.read_csv('BotNumbers_Production.csv', dtype={'numero': str})
        print(f"✅ CSV cargado: {len(df)} usuarios")
        
        # 2. Procesar datos
        print("🔄 Procesando datos...")
        
        # Limpiar datos y agregar ciudad
        df_clean = df.copy()
        df_clean['city'] = df_clean['numero'].apply(determine_city)
        
        # Convertir a formato para Supabase
        users_data = []
        for _, row in df_clean.iterrows():
            user_record = {
                'number': row['numero'],
                'location': row['location'],
                'location_name': row['location_name'],
                'salon': row['salon'] if pd.notna(row['salon']) else None,
                'city': row['city']
            }
            users_data.append(user_record)
        
        print(f"✅ {len(users_data)} registros preparados")
        
        # 3. Mostrar estadísticas
        print("\n📋 ESTADÍSTICAS DE DATOS:")
        city_stats = df_clean['city'].value_counts()
        for city, count in city_stats.items():
            print(f"  🏙️ {city}: {count} usuarios")
        
        location_stats = df_clean.groupby(['location', 'location_name']).size()
        print("\n📍 Por ubicación:")
        for (location, location_name), count in location_stats.items():
            print(f"  {location} - {location_name}: {count} usuarios")
        
        # 4. Insertar en Supabase
        print(f"\n💾 Insertando {len(users_data)} usuarios en Supabase...")
        
        # Limpiar tabla primero (opcional)
        confirm = input("¿Limpiar tabla users antes de insertar? (s/N): ").strip().lower()
        if confirm == 's':
            print("🗑️ Limpiando tabla users...")
            supabase.table('users').delete().neq('number', '').execute()
        
        # Insertar datos en lotes de 100
        batch_size = 100
        total_inserted = 0
        
        for i in range(0, len(users_data), batch_size):
            batch = users_data[i:i + batch_size]
            print(f"📦 Insertando lote {i//batch_size + 1}: {len(batch)} usuarios...")
            
            result = supabase.table('users').upsert(batch).execute()
            total_inserted += len(batch)
            print(f"✅ Lote insertado exitosamente")
        
        print(f"\n🎉 ¡INSERCIÓN COMPLETADA!")
        print(f"📊 Total usuarios insertados: {total_inserted}")
        
        # 5. Verificar inserción
        print("\n🔍 Verificando inserción...")
        result = supabase.table('users').select('*').execute()
        print(f"✅ Verificación: {len(result.data)} usuarios en la tabla")
        
        # Estadísticas finales
        cities_in_db = {}
        for user in result.data:
            city = user['city']
            cities_in_db[city] = cities_in_db.get(city, 0) + 1
        
        print("\n📊 ESTADÍSTICAS FINALES EN BD:")
        for city, count in cities_in_db.items():
            print(f"  🏙️ {city}: {count} usuarios")
        
        return True
        
    except Exception as e:
        print(f"❌ Error poblando tabla users: {e}")
        return False

def verify_users_table():
    """Verificar contenido de la tabla users"""
    
    print("\n🔍 VERIFICACIÓN DETALLADA")
    print("=" * 30)
    
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    
    try:
        # Obtener todos los usuarios
        result = supabase.table('users').select('*').execute()
        users = result.data
        
        print(f"👥 Total usuarios en BD: {len(users)}")
        
        # Verificar por ciudad
        city_counts = {}
        location_counts = {}
        
        for user in users:
            # Por ciudad
            city = user['city']
            city_counts[city] = city_counts.get(city, 0) + 1
            
            # Por ubicación
            location_key = f"{user['location']} - {user['location_name']}"
            location_counts[location_key] = location_counts.get(location_key, 0) + 1
        
        print("\n🏙️ USUARIOS POR CIUDAD:")
        for city, count in city_counts.items():
            print(f"  {city}: {count} usuarios")
        
        print("\n📍 USUARIOS POR UBICACIÓN:")
        for location, count in location_counts.items():
            print(f"  {location}: {count} usuarios")
        
        # Mostrar algunos ejemplos
        print("\n📋 EJEMPLOS DE USUARIOS:")
        for i, user in enumerate(users[:5]):
            print(f"  {i+1}. {user['number']} - {user['city']} - {user['location']} {user['location_name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error verificando tabla: {e}")
        return False

def main():
    """Función principal"""
    
    # Poblar tabla
    if not populate_users_table():
        return
    
    # Verificar resultado
    verify_users_table()
    
    print("\n✅ Tabla users poblada exitosamente!")

if __name__ == "__main__":
    main()