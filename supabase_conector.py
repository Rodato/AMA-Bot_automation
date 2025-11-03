import os
from supabase import create_client, Client
from dotenv import load_dotenv
import pandas as pd

# Cargar variables de entorno
load_dotenv()

# Configurar Supabase
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Verificar conexión a Supabase

def test_connection():
    """Probar conexión a Supabase"""
    try:
          # Test simple de conexión
          result = supabase.table('_test').select("*").limit(1).execute()
          print("✅ Conexión a Supabase exitosa")
          return True
    except Exception as e:
          print(f"❌ Error conectando a Supabase: {e}")
          return False
    
# Test de conexión
if not test_connection():
    return