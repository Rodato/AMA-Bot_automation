import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os
import sys

parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

st.set_page_config(
    page_title="AMA Bot - Dashboard de Monitoreo",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data
def load_data():
    csv_path = os.path.join(parent_dir, 'control_envios.csv')
    if not os.path.exists(csv_path):
        st.error(f"No se encontró el archivo: {csv_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(csv_path)
    return df

def get_position_label(sesion, day):
    return f"S{sesion}D{day}"

def get_metrics_by_location(df):
    metrics = {}
    
    for location_name in df['location_name'].unique():
        location_df = df[df['location_name'] == location_name]
        
        total_users = len(location_df['numero'].unique())
        total_records = len(location_df)
        sent_records = len(location_df[location_df['enviado'] == 1])
        completed_records = len(location_df[location_df['completado'] == 1])
        excluded_users = len(location_df[location_df['usuario_excluido'] == 1]['numero'].unique())
        
        send_rate = (sent_records / total_records * 100) if total_records > 0 else 0
        completion_rate = (completed_records / sent_records * 100) if sent_records > 0 else 0
        exclusion_rate = (excluded_users / total_users * 100) if total_users > 0 else 0
        
        current_positions = {}
        for _, row in location_df.iterrows():
            numero = row['numero']
            position = get_position_label(row['sesion'], row['day'])
            
            if numero not in current_positions:
                current_positions[numero] = {'sesion': 0, 'day': 0, 'position': 'S0D0'}
            
            if row['sesion'] > current_positions[numero]['sesion'] or \
               (row['sesion'] == current_positions[numero]['sesion'] and row['day'] > current_positions[numero]['day']):
                current_positions[numero] = {
                    'sesion': row['sesion'],
                    'day': row['day'],
                    'position': position,
                    'completado': row['completado'],
                    'enviado': row['enviado']
                }
        
        active_users = sum(1 for user_data in current_positions.values() 
                          if user_data['sesion'] > 1 or user_data['day'] > 1)
        
        stuck_s1d1 = []
        for numero, user_data in current_positions.items():
            if user_data['sesion'] == 1 and user_data['day'] == 1 and user_data['enviado'] == 1 and user_data['completado'] == 0:
                stuck_s1d1.append(numero)
        
        metrics[location_name] = {
            'total_users': total_users,
            'total_records': total_records,
            'sent_records': sent_records,
            'completed_records': completed_records,
            'excluded_users': excluded_users,
            'send_rate': send_rate,
            'completion_rate': completion_rate,
            'exclusion_rate': exclusion_rate,
            'active_users': active_users,
            'active_rate': (active_users / total_users * 100) if total_users > 0 else 0,
            'current_positions': current_positions,
            'stuck_s1d1': stuck_s1d1
        }
    
    return metrics

def create_position_distribution_chart(current_positions):
    position_counts = {}
    for user_data in current_positions.values():
        position = user_data['position']
        status = 'Completado' if user_data['completado'] == 1 else 'Pendiente' if user_data['enviado'] == 1 else 'No iniciado'
        
        if position not in position_counts:
            position_counts[position] = {'Completado': 0, 'Pendiente': 0, 'No iniciado': 0}
        position_counts[position][status] += 1
    
    positions = sorted(position_counts.keys(), key=lambda x: (int(x[1]), int(x[3])))
    completados = [position_counts[pos]['Completado'] for pos in positions]
    pendientes = [position_counts[pos]['Pendiente'] for pos in positions]
    no_iniciados = [position_counts[pos]['No iniciado'] for pos in positions]
    
    fig = go.Figure(data=[
        go.Bar(name='Completados', x=positions, y=completados, marker_color='#2E8B57'),
        go.Bar(name='Pendientes', x=positions, y=pendientes, marker_color='#FF6B35'),
        go.Bar(name='No iniciados', x=positions, y=no_iniciados, marker_color='#D3D3D3')
    ])
    
    fig.update_layout(
        barmode='stack',
        title='Distribución de Usuarios por Posición',
        xaxis_title='Posición (Sesión-Día)',
        yaxis_title='Número de Usuarios',
        height=400
    )
    
    return fig

def main():
    st.title("📊 AMA Bot - Dashboard de Monitoreo")
    st.markdown("### Sistema de Envíos Automatizados por Ubicaciones")
    
    df = load_data()
    
    if df.empty:
        st.error("No se pudieron cargar los datos.")
        return
    
    st.sidebar.header("Filtros")
    
    locations = ['Todas'] + sorted(df['location_name'].unique().tolist())
    selected_location = st.sidebar.selectbox("Seleccionar Ubicación:", locations)
    
    if selected_location != 'Todas':
        df_filtered = df[df['location_name'] == selected_location]
    else:
        df_filtered = df.copy()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    metrics = get_metrics_by_location(df_filtered)
    
    if selected_location == 'Todas':
        st.header("📈 Resumen General")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_users = sum(m['total_users'] for m in metrics.values())
        total_sent = sum(m['sent_records'] for m in metrics.values())
        total_completed = sum(m['completed_records'] for m in metrics.values())
        total_excluded = sum(m['excluded_users'] for m in metrics.values())
        
        with col1:
            st.metric("👥 Total Usuarios", f"{total_users:,}")
        with col2:
            st.metric("📤 Envíos Realizados", f"{total_sent:,}")
        with col3:
            st.metric("✅ Completados", f"{total_completed:,}")
        with col4:
            st.metric("🚫 Usuarios Excluidos", f"{total_excluded:,}")
        
        st.header("📊 Progreso Detallado por Ubicación")
        
        tabs = st.tabs(list(metrics.keys()))
        
        for tab, (location_name, location_metrics) in zip(tabs, metrics.items()):
            with tab:
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("👥 Usuarios Activos", 
                             f"{location_metrics['active_users']}/{location_metrics['total_users']}")
                    st.metric("📊 Tasa Completado", 
                             f"{location_metrics['completion_rate']:.1f}%")
                
                with col2:
                    st.metric("📈 Tasa Envío", 
                             f"{location_metrics['send_rate']:.1f}%")
                    st.metric("🚫 Tasa Exclusión", 
                             f"{location_metrics['exclusion_rate']:.1f}%")
                
                with col3:
                    st.metric("🔄 Tasa Actividad", 
                             f"{location_metrics['active_rate']:.1f}%")
                    st.metric("⚠️ Atascados S1D1", 
                             len(location_metrics['stuck_s1d1']))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig = create_position_distribution_chart(location_metrics['current_positions'])
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    if location_metrics['stuck_s1d1']:
                        st.subheader("⚠️ Usuarios Atascados en S1D1")
                        stuck_df = pd.DataFrame({
                            'Número': location_metrics['stuck_s1d1']
                        })
                        st.dataframe(stuck_df, use_container_width=True)
                    else:
                        st.success("✅ No hay usuarios atascados en S1D1")
                    
                    position_summary = {}
                    for user_data in location_metrics['current_positions'].values():
                        pos = user_data['position']
                        position_summary[pos] = position_summary.get(pos, 0) + 1
                    
                    st.subheader("📋 Resumen por Posición")
                    summary_df = pd.DataFrame(list(position_summary.items()), 
                                            columns=['Posición', 'Usuarios'])
                    summary_df = summary_df.sort_values('Posición')
                    st.dataframe(summary_df, use_container_width=True)
    
    else:
        location_metrics = metrics[selected_location]
        
        st.header(f"📍 Detalle: {selected_location}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👥 Total Usuarios", location_metrics['total_users'])
        with col2:
            st.metric("📤 Envíos", location_metrics['sent_records'])
        with col3:
            st.metric("✅ Completados", location_metrics['completed_records'])
        with col4:
            st.metric("🚫 Excluidos", location_metrics['excluded_users'])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📈 Tasa Envío", f"{location_metrics['send_rate']:.1f}%")
        with col2:
            st.metric("📊 Tasa Completado", f"{location_metrics['completion_rate']:.1f}%")
        with col3:
            st.metric("🔄 Usuarios Activos", f"{location_metrics['active_rate']:.1f}%")
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = create_position_distribution_chart(location_metrics['current_positions'])
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            if location_metrics['stuck_s1d1']:
                st.subheader("⚠️ Usuarios Atascados en S1D1")
                stuck_df = pd.DataFrame({
                    'Número': location_metrics['stuck_s1d1']
                })
                st.dataframe(stuck_df, use_container_width=True)
            else:
                st.success("✅ No hay usuarios atascados en S1D1")
    
    st.header("📋 Datos Detallados")
    
    if st.checkbox("Mostrar datos completos"):
        st.dataframe(df_filtered, use_container_width=True)
    
    with st.expander("ℹ️ Información del Sistema"):
        st.markdown("""
        **Métricas Explicadas:**
        - **Usuarios Activos**: Usuarios que han progresado más allá de S1D1
        - **Tasa de Envío**: Porcentaje de registros enviados vs total
        - **Tasa de Completado**: Porcentaje de sesiones completadas vs enviadas
        - **Usuarios Atascados S1D1**: Usuarios con envío en S1D1 pero no completado
        
        **Estados de Posición:**
        - **Completado**: Usuario completó la sesión
        - **Pendiente**: Sesión enviada pero no completada
        - **No iniciado**: Sesión no enviada aún
        """)

if __name__ == "__main__":
    main()