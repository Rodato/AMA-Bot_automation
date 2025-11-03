#!/usr/bin/env python3
"""
Modelos de datos para AMA Bot
"""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    """Modelo para usuarios"""
    number: str
    location: str
    location_name: str
    salon: Optional[str]
    city: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class SessionProgress:
    """Modelo para progreso de sesiones"""
    number: str
    day_1: int = 0
    day_2: int = 0
    day_3: int = 0
    day_4: int = 0
    day_5: int = 0
    updated_at: Optional[datetime] = None
    
    def get_completed_days(self) -> int:
        """Contar días completados"""
        return sum([self.day_1, self.day_2, self.day_3, self.day_4, self.day_5])
    
    def is_session_completed(self) -> bool:
        """Verificar si la sesión está completada (todos los días)"""
        return self.get_completed_days() == 5

@dataclass
class UserStats:
    """Estadísticas de usuario"""
    number: str
    city: str
    location: str
    location_name: str
    total_completed_days: int
    current_session: int
    current_day: int
    is_active: bool

@dataclass
class LocationStats:
    """Estadísticas por ubicación"""
    location: str
    location_name: str
    city: str
    total_users: int
    active_users: int
    completed_sessions: int
    completion_rate: float