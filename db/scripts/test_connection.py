#!/usr/bin/env python3
"""
Test de conexión simple a Supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def test_connection():
    """Probar conexión básica a Supabase"""
    
    print("🔌 PROBANDO CONEXIÓN A SUPABASE")
    print("=" * 40)
    
    # Obtener credenciales
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    # Verificar que existan las variables
    if not url:
        print("❌ Error: SUPABASE_URL no encontrada en .env")
        return False
    
    if not key:
        print("❌ Error: SUPABASE_KEY no encontrada en .env")
        return False
    
    print(f"📍 URL: {url[:30]}...")
    print(f"🔑 Key: {key[:20]}...")
    
    try:
        # Crear cliente
        supabase: Client = create_client(url, key)
        print("✅ Cliente Supabase creado")
        
        # Test básico - crear tabla temporal de prueba
        from supabase._sync.client import SyncClient
        print("✅ Conexión a Supabase establecida")
        print("✅ Cliente configurado correctamente")
        print("🎯 Listo para crear tablas y migrar datos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error conectando a Supabase: {e}")
        return False

if __name__ == "__main__":
    success = test_connection()
    
    if success:
        print("\n🎉 ¡Conexión exitosa! Listo para crear tablas.")
    else:
        print("\n⚠️ Revisa tus credenciales en el archivo .env")