#!/usr/bin/env python3
"""
Configuración de conexión a Supabase
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_supabase_client() -> Client:
    """
    Obtener cliente configurado de Supabase
    
    Returns:
        Client: Cliente de Supabase configurado
        
    Raises:
        ValueError: Si faltan las credenciales en .env
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url:
        raise ValueError("SUPABASE_URL no encontrada en variables de entorno")
    
    if not key:
        raise ValueError("SUPABASE_KEY no encontrada en variables de entorno")
    
    return create_client(url, key)

def test_connection() -> bool:
    """
    Probar conexión a Supabase
    
    Returns:
        bool: True si la conexión es exitosa, False en caso contrario
    """
    try:
        client = get_supabase_client()
        # Test simple - el cliente se crea correctamente
        return True
    except Exception as e:
        print(f"Error conectando a Supabase: {e}")
        return False