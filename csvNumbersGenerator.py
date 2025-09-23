import pandas as pd

def generar_csv_inicial():
    """Generar CSV inicial con números de ejemplo"""
    
    # LISTA TUS NÚMEROS AQUÍ - EJEMPLO COMPLETO
    numeros_telefono = [
        573156617659,
        573159267303,  
        573155503266,
        573168124099,   # Agrega más números
        #573159267303,
        #573155503266,
        # Puedes agregar tantos como necesites
        # 573XXXXXXXXX,
        # 573XXXXXXXXX,
    ]
    
    datos = []
    
    print("🔄 Generando registros...")
    
    for numero in numeros_telefono:
        for sesion in range(1, 7):  # Sesiones 1-6
            for day in range(1, 6):  # Días 1-5
                datos.append({
                    'numero': numero,
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
    generar_csv_inicial()