import pandas as pd
import os
import sys

def generar_csv_desde_xlsx(archivo_xlsx='numeros_usuarios.xlsx'):
    """Generar CSV de control desde archivo XLSX con estructura de ubicaciones"""
    
    print("🏫 GENERADOR CSV DESDE XLSX CON UBICACIONES")
    print("=" * 50)
    
    # Verificar que existe el archivo XLSX
    if not os.path.exists(archivo_xlsx):
        print(f"❌ Error: No se encontró el archivo {archivo_xlsx}")
        print(f"💡 Crea un archivo Excel con las columnas:")
        print(f"   - numero: Número de teléfono (ej: 573168124099)")
        print(f"   - location: Tipo de ubicación (ej: Colegio)")
        print(f"   - location_name: Nombre específico (ej: Maynas)")
        print(f"   - salon: Salón o aula (ej: 5H)")
        return False
    
    try:
        # Leer archivo XLSX
        print(f"📖 Leyendo archivo: {archivo_xlsx}")
        df_usuarios = pd.read_excel(archivo_xlsx)
        
        # Validar columnas requeridas
        columnas_requeridas = ['numero', 'location', 'location_name', 'salon']
        columnas_faltantes = [col for col in columnas_requeridas if col not in df_usuarios.columns]
        
        if columnas_faltantes:
            print(f"❌ Error: Columnas faltantes en el XLSX: {columnas_faltantes}")
            print(f"💡 El archivo debe tener las columnas: {columnas_requeridas}")
            return False
        
        # Convertir números a string para consistencia
        df_usuarios['numero'] = df_usuarios['numero'].astype(str)
        
        print(f"✅ Archivo leído correctamente:")
        print(f"   📊 Total usuarios: {len(df_usuarios)}")
        print(f"   🏫 Locations únicos: {df_usuarios['location'].nunique()}")
        print(f"   📍 Location names únicos: {df_usuarios['location_name'].nunique()}")
        print(f"   🚪 Salones únicos: {df_usuarios['salon'].nunique()}")
        
        # Mostrar resumen por location
        print(f"\n📋 RESUMEN POR LOCATION:")
        location_summary = df_usuarios.groupby(['location', 'location_name']).size().reset_index(name='usuarios')
        for _, row in location_summary.iterrows():
            print(f"   📍 {row['location']} - {row['location_name']}: {row['usuarios']} usuarios")
        
        # Generar registros de control
        datos = []
        print(f"\n🔄 Generando registros de control...")
        
        for _, usuario in df_usuarios.iterrows():
            numero = str(usuario['numero'])
            location = usuario['location']
            location_name = usuario['location_name']
            salon = usuario['salon']
            
            for sesion in range(1, 7):  # Sesiones 1-6
                for day in range(1, 6):  # Días 1-5
                    datos.append({
                        'numero': numero,
                        'location': location,
                        'location_name': location_name,
                        'salon': salon,
                        'sesion': sesion,
                        'day': day,
                        'enviado': 0,
                        'fecha_envio': '',
                        'resultado': '',
                        'completado': 0,
                        'intentos_envio': 0,
                        'fecha_completado': '',
                        'ultimo_estado_botpress': 0,
                        'reenvios_consecutivos_fallidos': 0,
                        'usuario_excluido': 0
                    })
            
            print(f"   ✅ {numero} ({location} - {location_name}, {salon})")
        
        # Crear DataFrame y guardar
        df_control = pd.DataFrame(datos)
        df_control.to_csv('control_envios.csv', index=False)
        
        print(f"\n🎉 CSV DE CONTROL GENERADO EXITOSAMENTE!")
        print(f"   📄 Archivo: control_envios.csv")
        print(f"   📊 Total registros: {len(df_control)}")
        print(f"   📱 Usuarios únicos: {len(df_usuarios)}")
        print(f"   📅 Sesiones: 6")
        print(f"   🗓️  Días por sesión: 5")
        print(f"   🏫 Incluye datos de ubicación para monitoreo")
        
        # Crear resumen adicional
        print(f"\n📈 ESTRUCTURA GENERADA:")
        print(f"   📊 Registros por usuario: {len(df_control) // len(df_usuarios)}")
        print(f"   📍 Locations: {', '.join(df_usuarios['location'].unique())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error procesando archivo: {e}")
        return False

def generar_csv_inicial():
    """Generar CSV inicial con números de ejemplo (método original para compatibilidad)"""
    
    print("⚠️  USANDO MÉTODO LEGACY - Se recomienda usar generar_csv_desde_xlsx()")
    
    # LISTA TUS NÚMEROS AQUÍ - EJEMPLO COMPLETO
    numeros_telefono = [
        573156617659,
        573159267303,  
        573155503266,
        573168124099,
    ]
    
    datos = []
    
    print("🔄 Generando registros...")
    
    for numero in numeros_telefono:
        for sesion in range(1, 7):  # Sesiones 1-6
            for day in range(1, 6):  # Días 1-5
                datos.append({
                    'numero': str(numero),
                    'location': 'Sin definir',
                    'location_name': 'Sin definir', 
                    'salon': 'Sin definir',
                    'sesion': sesion,
                    'day': day,
                    'enviado': 0,
                    'fecha_envio': '',
                    'resultado': '',
                    'completado': 0,
                    'intentos_envio': 0,
                    'fecha_completado': '',
                    'ultimo_estado_botpress': 0,
                    'reenvios_consecutivos_fallidos': 0,
                    'usuario_excluido': 0
                })
                
        print(f"✅ Completado número: {numero}")
    
    # Crear DataFrame y guardar
    df = pd.DataFrame(datos)
    df.to_csv('control_envios.csv', index=False)
    
    print(f"\n🎉 CSV generado exitosamente!")
    print(f"   📄 Archivo: control_envios.csv")
    print(f"   📊 Total registros: {len(df)}")
    print(f"   📱 Números: {len(numeros_telefono)}")
    print(f"   📅 Sesiones: 6")
    print(f"   🗓️  Días por sesión: 5")

if __name__ == "__main__":
    # Usar el archivo XLSX existente
    generar_csv_desde_xlsx('botNumbers_test.xlsx')