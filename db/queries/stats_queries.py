#!/usr/bin/env python3
"""
Consultas SQL para estadísticas
"""

from ..connection import get_supabase_client
from typing import List, Dict, Any

def get_city_stats() -> List[Dict[str, Any]]:
    """
    Obtener estadísticas por ciudad
    
    Returns:
        List[Dict]: Lista de estadísticas por ciudad
    """
    supabase = get_supabase_client()
    
    result = supabase.table('city_stats').select('*').execute()
    return result.data

def get_location_progress() -> List[Dict[str, Any]]:
    """
    Obtener progreso por ubicación
    
    Returns:
        List[Dict]: Lista de progreso por ubicación
    """
    supabase = get_supabase_client()
    
    result = supabase.table('location_progress').select('*').execute()
    return result.data

def get_users_by_city(city: str) -> List[Dict[str, Any]]:
    """
    Obtener usuarios de una ciudad específica
    
    Args:
        city: Nombre de la ciudad
        
    Returns:
        List[Dict]: Lista de usuarios de la ciudad
    """
    supabase = get_supabase_client()
    
    result = supabase.table('users').select('*').eq('city', city).execute()
    return result.data

def get_session_stats(session_num: int) -> Dict[str, Any]:
    """
    Obtener estadísticas de una sesión específica
    
    Args:
        session_num: Número de sesión (1-9)
        
    Returns:
        Dict: Estadísticas de la sesión
    """
    supabase = get_supabase_client()
    
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
    
    return {
        'session': session_num,
        'total_users': len(result.data),
        'users_with_progress': users_with_progress,
        'total_completed_days': total_completed_days,
        'avg_days_per_user': total_completed_days / len(result.data) if result.data else 0
    }