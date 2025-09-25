#!/usr/bin/env python3
"""
Script para probar el GitHub Runner localmente antes de hacer push
"""
import sys
import os
from utilities.ama_bot_github_runner import AMABotGitHubRunner

def test_runner_local():
    """Probar el runner en modo local"""
    print("🧪 PRUEBA LOCAL DEL GITHUB RUNNER")
    print("=" * 50)
    
    # Verificar archivos necesarios
    required_files = ['control_envios.csv']
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Archivo requerido no encontrado: {file}")
            return False
    
    print("✅ Archivos requeridos encontrados")
    
    # Crear instancia del runner
    runner = AMABotGitHubRunner('control_envios.csv')
    
    # Solo cargar y verificar datos (sin enviar)
    print("\n📊 VERIFICANDO CARGA DE DATOS...")
    if not runner.load_data():
        print("❌ Error cargando datos")
        return False
    
    print(f"✅ CSV cargado: {len(runner.df)} registros")
    print(f"👥 Usuarios únicos: {runner.df['numero'].nunique()}")
    
    # Verificar conexión a Botpress (opcional)
    print("\n🔄 PROBANDO CONEXIÓN BOTPRESS...")
    try:
        if runner.refresh_botpress_data():
            print("✅ Conexión a Botpress exitosa")
            print(f"📊 Datos de Botpress: {len(runner.botpress_data)} usuarios")
        else:
            print("⚠️ No se pudo conectar a Botpress (normal en pruebas)")
    except Exception as e:
        print(f"⚠️ Error de conexión Botpress: {e}")
    
    # Analizar registros pendientes
    print("\n📤 ANALIZANDO REGISTROS PENDIENTES...")
    condicion_pendientes = (
        (runner.df['usuario_excluido'] == 0) &
        (
            (runner.df['enviado'] == 0) |
            (
                (runner.df['enviado'] == 1) &
                (runner.df['completado'] == 0) &
                (runner.df['intentos_envio'] < 2)
            )
        )
    )
    pendientes = runner.df[condicion_pendientes]
    
    print(f"📋 Total registros: {len(runner.df)}")
    print(f"📤 Registros pendientes: {len(pendientes)}")
    
    if len(pendientes) > 0:
        print("\n📊 RESUMEN PENDIENTES POR SESIÓN/DÍA:")
        resumen = pendientes.groupby(['sesion', 'day']).size().reset_index(name='count')
        for _, row in resumen.iterrows():
            print(f"   📚 Sesión {row['sesion']}, Día {row['day']}: {row['count']} pendientes")
        
        print("\n🏫 RESUMEN PENDIENTES POR UBICACIÓN:")
        if 'location' in pendientes.columns:
            resumen_loc = pendientes.groupby(['location', 'location_name']).size().reset_index(name='count')
            for _, row in resumen_loc.iterrows():
                print(f"   📍 {row['location']} - {row['location_name']}: {row['count']} pendientes")
    
    print("\n✅ PRUEBA LOCAL COMPLETADA EXITOSAMENTE")
    print("🚀 El runner está listo para ejecutarse en GitHub Actions")
    
    return True

def test_monitoring():
    """Probar el sistema de monitoreo"""
    print("\n📈 PROBANDO SISTEMA DE MONITOREO...")
    
    try:
        from monitor_ubicaciones import MonitorUbicaciones
        
        monitor = MonitorUbicaciones('control_envios.csv')
        
        print("✅ Monitor cargado correctamente")
        print(f"📊 {len(monitor.df)} registros para monitoreo")
        
        # Verificar que tiene datos de ubicación
        if 'location' in monitor.df.columns:
            locations = monitor.df['location'].nunique()
            location_names = monitor.df['location_name'].nunique()
            print(f"🏫 {locations} locations, {location_names} location_names")
        else:
            print("⚠️ Sin datos de ubicación (usando CSV legacy)")
        
        print("✅ Sistema de monitoreo funcionando")
        
    except Exception as e:
        print(f"❌ Error en monitoreo: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🧪 SUITE DE PRUEBAS PARA GITHUB ACTIONS")
    print("=" * 60)
    
    # Test 1: Runner
    if not test_runner_local():
        print("❌ Prueba del runner falló")
        sys.exit(1)
    
    # Test 2: Monitoreo
    if not test_monitoring():
        print("❌ Prueba del monitoreo falló")
        sys.exit(1)
    
    print("\n🎉 TODAS LAS PRUEBAS EXITOSAS")
    print("✅ El sistema está listo para GitHub Actions")
    print("🚀 Puedes hacer push del código con confianza")

if __name__ == "__main__":
    main()