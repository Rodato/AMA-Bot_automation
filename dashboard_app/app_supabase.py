#!/usr/bin/env python3
"""
🏫 AMA BOT - Dashboard Profesional conectada a Supabase
Dashboard con identidad de marca y seguimiento completo por ciudad
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
import os

# Agregar el directorio padre al path para importar db
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import get_supabase_client
from db.queries.stats_queries import get_city_stats, get_users_by_city
from db.queries.progress_queries import get_active_users, get_user_progress

# ========================
# CONFIGURACIÓN DE PÁGINA
# ========================

st.set_page_config(
    page_title="AMA Bot - Dashboard",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ========================
# ESTILOS PERSONALIZADOS
# ========================

def load_custom_css():
    """Cargar estilos personalizados con identidad de marca"""
    
    st.markdown("""
    <style>
    /* Importar fuentes Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Bungee:wght@400&display=swap');
    
    /* Variables de colores de marca */
    :root {
        --brand-bg: #CAD6EF;
        --brand-text: #133F0E;
        --brand-accent: #2E8B57;
        --brand-light: #E8F0FE;
    }
    
    /* Fondo principal */
    .main .block-container {
        background-color: var(--brand-bg);
        padding-top: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    /* Header personalizado */
    .custom-header {
        background: linear-gradient(135deg, var(--brand-light) 0%, var(--brand-bg) 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        border: 2px solid var(--brand-text);
        box-shadow: 0 4px 12px rgba(19, 63, 14, 0.1);
    }
    
    .custom-header h1 {
        color: var(--brand-text);
        font-family: 'Bungee', cursive;
        font-weight: 400;
        font-size: 2.5rem;
        text-align: center;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        letter-spacing: 2px;
    }
    
    .custom-header .subtitle {
        color: var(--brand-text);
        font-size: 1.2rem;
        text-align: center;
        margin-top: 0.5rem;
        font-weight: 400;
        opacity: 0.8;
    }
    
    /* Métricas personalizadas */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid var(--brand-text);
        box-shadow: 0 2px 8px rgba(19, 63, 14, 0.1);
        margin-bottom: 1rem;
    }
    
    .metric-card h3 {
        color: var(--brand-text);
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        font-size: 1.1rem;
    }
    
    .metric-card .metric-value {
        color: var(--brand-accent);
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    
    .metric-card .metric-delta {
        color: var(--brand-text);
        font-size: 0.9rem;
        margin-top: 0.3rem;
        opacity: 0.7;
    }
    
    /* Pestañas personalizadas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: white;
        border-radius: 10px;
        padding: 5px;
        border: 2px solid var(--brand-text);
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: var(--brand-text);
        font-weight: 600;
        font-family: 'Inter', sans-serif;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--brand-text) !important;
        color: white !important;
    }
    
    /* Selectores personalizados */
    .stSelectbox label {
        color: var(--brand-text) !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Gráficos */
    .plot-container {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid rgba(19, 63, 14, 0.2);
        box-shadow: 0 2px 8px rgba(19, 63, 14, 0.1);
    }
    
    /* Logo */
    .logo-container {
        text-align: center;
        margin-bottom: 1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# ========================
# FUNCIONES DE DATOS
# ========================

@st.cache_data(ttl=300)  # Cache por 5 minutos
def load_users_data():
    """Cargar datos de usuarios desde Supabase"""
    try:
        supabase = get_supabase_client()
        result = supabase.table('users').select('*').execute()
        return pd.DataFrame(result.data)
    except Exception as e:
        st.error(f"Error cargando usuarios: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_session_data(session_num):
    """Cargar datos de una sesión específica"""
    try:
        supabase = get_supabase_client()
        result = supabase.table(f'session_{session_num}').select('*').execute()
        return pd.DataFrame(result.data)
    except Exception as e:
        st.error(f"Error cargando session_{session_num}: {e}")
        return pd.DataFrame()

def get_user_stats_by_city(users_df, session_data):
    """Calcular estadísticas por ciudad"""
    
    if users_df.empty:
        return {}
    
    stats = {}
    
    for city in users_df['city'].unique():
        city_users = users_df[users_df['city'] == city]
        city_numbers = set(city_users['number'].tolist())
        
        # Estadísticas de sesiones
        total_users = len(city_users)
        
        # Usuarios activos (con al menos un día completado en cualquier sesión)
        active_users = 0
        total_completed_days = 0
        
        for session_num in range(1, 10):
            if session_num in session_data:
                session_df = session_data[session_num]
                city_session = session_df[session_df['number'].isin(city_numbers)]
                
                for _, user in city_session.iterrows():
                    days_completed = sum([
                        user['day_1'], user['day_2'], user['day_3'], 
                        user['day_4'], user['day_5']
                    ])
                    total_completed_days += days_completed
                    
                    if days_completed > 0:
                        active_users += 1
                        break  # Contar usuario solo una vez
        
        stats[city] = {
            'total_users': total_users,
            'active_users': active_users,
            'inactive_users': total_users - active_users,
            'completion_rate': (active_users / total_users * 100) if total_users > 0 else 0,
            'total_completed_days': total_completed_days,
            'avg_days_per_user': total_completed_days / total_users if total_users > 0 else 0
        }
    
    return stats

def get_location_stats(users_df, session_data, city, location_type=None):
    """Obtener estadísticas por ubicación específica"""
    
    if users_df.empty:
        return pd.DataFrame()
    
    # Filtrar por ciudad
    city_users = users_df[users_df['city'] == city]
    
    # Filtrar por tipo de ubicación si se especifica
    if location_type:
        city_users = city_users[city_users['location'] == location_type]
    
    # Agrupar por ubicación
    location_stats = []
    
    for location_name in city_users['location_name'].unique():
        location_users = city_users[city_users['location_name'] == location_name]
        location_numbers = set(location_users['number'].tolist())
        
        total_users = len(location_users)
        active_users = 0
        completed_days = 0
        
        # Contar progreso en todas las sesiones
        for session_num in range(1, 10):
            if session_num in session_data:
                session_df = session_data[session_num]
                location_session = session_df[session_df['number'].isin(location_numbers)]
                
                for _, user in location_session.iterrows():
                    days = sum([user['day_1'], user['day_2'], user['day_3'], user['day_4'], user['day_5']])
                    completed_days += days
                    if days > 0 and active_users < total_users:
                        active_users += 1
        
        location_stats.append({
            'location': location_users.iloc[0]['location'],
            'location_name': location_name,
            'total_users': total_users,
            'active_users': active_users,
            'completion_rate': (active_users / total_users * 100) if total_users > 0 else 0,
            'completed_days': completed_days
        })
    
    return pd.DataFrame(location_stats)

# ========================
# COMPONENTES UI
# ========================

def render_header():
    """Renderizar header con identidad de marca"""
    
    # Crear columnas para centrar el logo
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo centrado
        st.image("logoAMA.png", width=120)
    
    st.markdown("""
    <div class="custom-header" style="padding-top: 1rem;">
        <h1>AMA BOT DASHBOARD</h1>
    </div>
    """, unsafe_allow_html=True)

def render_metrics_cards(stats):
    """Renderizar tarjetas de métricas"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>👥 Total Usuarios</h3>
            <div class="metric-value">{stats['total_users']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>✅ Usuarios Activos</h3>
            <div class="metric-value">{stats['active_users']}</div>
            <div class="metric-delta">{stats['completion_rate']:.1f}% del total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>❌ Usuarios Inactivos</h3>
            <div class="metric-value">{stats['inactive_users']}</div>
            <div class="metric-delta">{100-stats['completion_rate']:.1f}% del total</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>📊 Días Completados</h3>
            <div class="metric-value">{stats['total_completed_days']}</div>
            <div class="metric-delta">{stats['avg_days_per_user']:.1f} promedio por usuario</div>
        </div>
        """, unsafe_allow_html=True)

def render_session_progress_matrix(users_df, session_data, city, location_filter=None):
    """Renderizar matriz de progreso por sesión/día"""
    
    # Filtrar usuarios por ciudad y ubicación
    filtered_users = users_df[users_df['city'] == city]
    if location_filter:
        filtered_users = filtered_users[filtered_users['location_name'] == location_filter]
    
    user_numbers = set(filtered_users['number'].tolist())
    
    # Crear matriz de progreso
    progress_matrix = []
    
    for session_num in range(1, 7):  # Solo mostrar sesiones 1-6 para mejor visualización
        session_row = [f"Sesión {session_num}"]
        
        if session_num in session_data:
            session_df = session_data[session_num]
            filtered_session = session_df[session_df['number'].isin(user_numbers)]
            
            for day in range(1, 6):
                completed_count = filtered_session[f'day_{day}'].sum()
                session_row.append(completed_count)
        else:
            session_row.extend([0, 0, 0, 0, 0])
        
        progress_matrix.append(session_row)
    
    # Crear DataFrame para visualización
    matrix_df = pd.DataFrame(progress_matrix, columns=['Sesión', 'Día 1', 'Día 2', 'Día 3', 'Día 4', 'Día 5'])
    
    # Crear heatmap
    fig = go.Figure(data=go.Heatmap(
        z=matrix_df.iloc[:, 1:].values,
        x=['Día 1', 'Día 2', 'Día 3', 'Día 4', 'Día 5'],
        y=[f'Sesión {i+1}' for i in range(6)],
        colorscale='Greens',
        text=matrix_df.iloc[:, 1:].values,
        texttemplate="%{text}",
        textfont={"size": 12},
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Matriz de Progreso: Usuarios Completados por Sesión/Día",
        xaxis_title="Días",
        yaxis_title="Sesiones",
        font=dict(family="Inter, sans-serif", color="#133F0E"),
        plot_bgcolor='white',
        paper_bgcolor='white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ========================
# APLICACIÓN PRINCIPAL
# ========================

def main():
    """Función principal de la aplicación"""
    
    # Cargar estilos
    load_custom_css()
    
    # Header
    render_header()
    
    # Cargar datos
    with st.spinner("📡 Cargando datos desde Supabase..."):
        users_df = load_users_data()
        
        # Cargar datos de todas las sesiones
        session_data = {}
        for session_num in range(1, 10):
            session_data[session_num] = load_session_data(session_num)
    
    if users_df.empty:
        st.error("❌ No se pudieron cargar los datos. Verifica la conexión a Supabase.")
        return
    
    # Obtener estadísticas por ciudad
    city_stats = get_user_stats_by_city(users_df, session_data)
    
    # Pestañas por ciudad
    cities = list(city_stats.keys())
    if len(cities) >= 2:
        tab1, tab2 = st.tabs([f"🏙️ {cities[0]}", f"🏙️ {cities[1]}"])
        tabs = [tab1, tab2]
    else:
        tab1 = st.tabs([f"🏙️ {cities[0]}"])[0]
        tabs = [tab1]
    
    # Renderizar contenido para cada ciudad
    for i, city in enumerate(cities):
        if i < len(tabs):
            with tabs[i]:
                st.markdown(f"### 📊 Resumen General - {city}")
                
                # Métricas generales
                render_metrics_cards(city_stats[city])
                
                st.markdown("---")
                
                # Selectores de ubicación
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    location_types = users_df[users_df['city'] == city]['location'].unique()
                    selected_type = st.selectbox(
                        "📍 Tipo de Ubicación:",
                        options=['Todos'] + list(location_types),
                        key=f"type_{city}"
                    )
                
                with col2:
                    if selected_type != 'Todos':
                        available_locations = users_df[
                            (users_df['city'] == city) & 
                            (users_df['location'] == selected_type)
                        ]['location_name'].unique()
                        
                        selected_location = st.selectbox(
                            f"🏢 {selected_type} Específico:",
                            options=['Todos'] + list(available_locations),
                            key=f"location_{city}"
                        )
                    else:
                        selected_location = 'Todos'
                
                # Filtrar datos según selección
                location_filter = None
                if selected_type != 'Todos' and selected_location != 'Todos':
                    location_filter = selected_location
                elif selected_type != 'Todos':
                    # Mostrar estadísticas por ubicación
                    location_stats_df = get_location_stats(users_df, session_data, city, selected_type)
                    
                    if not location_stats_df.empty:
                        st.markdown(f"### 📋 Estadísticas por {selected_type}")
                        st.dataframe(location_stats_df, use_container_width=True)
                
                st.markdown("---")
                
                # Matriz de progreso
                st.markdown("### 📈 Resumen por Día/Sesión")
                render_session_progress_matrix(users_df, session_data, city, location_filter)
                
                # Información adicional
                with st.expander("ℹ️ Información Adicional"):
                    st.write(f"""
                    **Última actualización**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                    
                    **Leyenda**:
                    - 🟢 Verde oscuro: Más usuarios completados
                    - 🟢 Verde claro: Pocos usuarios completados  
                    - ⚪ Blanco: Sin completar
                    
                    **Filtros aplicados**:
                    - Ciudad: {city}
                    - Tipo: {selected_type}
                    - Ubicación: {selected_location if 'selected_location' in locals() else 'N/A'}
                    """)

if __name__ == "__main__":
    main()