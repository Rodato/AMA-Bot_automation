#!/usr/bin/env python3
"""
Consultas SQL para progreso de usuarios
"""

from ..connection import get_supabase_client
from ..models import User, SessionProgress, UserStats
from typing import List, Dict, Any, Optional

def get_user_progress(number: str) -> Dict[str, Any]:
    """
    Obtener progreso completo de un usuario
    
    Args:
        number: Número de teléfono del usuario
        
    Returns:
        Dict: Información del usuario y su progreso
    """
    supabase = get_supabase_client()
    
    # Obtener datos básicos del usuario
    user_result = supabase.table('users').select('*').eq('number', number).execute()
    if not user_result.data:
        return {}
    
    user_data = user_result.data[0]
    
    # Obtener progreso de todas las sesiones
    progress = {}
    for session_num in range(1, 10):
        session_result = supabase.table(f'session_{session_num}').select('*').eq('number', number).execute()
        if session_result.data:
            progress[f'session_{session_num}'] = session_result.data[0]
    
    return {
        'user': user_data,
        'progress': progress
    }

def get_users_by_current_position(session: int, day: int) -> List[Dict[str, Any]]:
    """
    Obtener usuarios que están en una posición específica
    
    Args:
        session: Número de sesión
        day: Número de día
        
    Returns:
        List[Dict]: Usuarios en esa posición
    """
    supabase = get_supabase_client()
    
    # Esta consulta es más compleja, necesitaría lógica personalizada
    # Por ahora retornamos lista vacía
    return []

def get_active_users() -> List[Dict[str, Any]]:
    """
    Obtener usuarios que han completado al menos un día
    
    Returns:
        List[Dict]: Usuarios activos
    """
    supabase = get_supabase_client()
    
    # Buscar en session_1 usuarios con al menos un día completado
    result = supabase.table('session_1').select('*').execute()
    
    active_users = []
    for user in result.data:
        if any([user['day_1'], user['day_2'], user['day_3'], user['day_4'], user['day_5']]):
            active_users.append(user)
    
    return active_users

def get_stuck_users(session: int = 1, day: int = 1) -> List[Dict[str, Any]]:
    """
    Obtener usuarios atascados en una posición específica
    
    Args:
        session: Número de sesión (default: 1)
        day: Número de día (default: 1)
        
    Returns:
        List[Dict]: Usuarios atascados
    """
    supabase = get_supabase_client()
    
    # Por simplicidad, buscar usuarios que no han completado el día especificado
    result = supabase.table(f'session_{session}').select('*').eq(f'day_{day}', 0).execute()
    
    return result.data

def update_user_progress(number: str, session: int, day: int, completed: bool) -> bool:
    """
    Actualizar progreso de un usuario
    
    Args:
        number: Número de teléfono
        session: Número de sesión
        day: Número de día
        completed: Si completó o no
        
    Returns:
        bool: True si se actualizó correctamente
    """
    supabase = get_supabase_client()
    
    try:
        result = supabase.table(f'session_{session}').update({
            f'day_{day}': 1 if completed else 0
        }).eq('number', number).execute()
        
        return len(result.data) > 0
    except Exception as e:
        print(f"Error actualizando progreso: {e}")
        return False