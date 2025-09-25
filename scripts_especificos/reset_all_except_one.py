#!/usr/bin/env python3
import pandas as pd
from datetime import datetime

def reset_all_except_one():
    """Resetear todos los números excepto 573168124099"""
    
    numero_excluido = '573168124099'
    
    print("🔧 RESETEO MASIVO EXCEPTO UN USUARIO")
    print("=" * 50)
    print(f"📞 Usuario que NO se reseteará: {numero_excluido}")
    
    try:
        # Cargar CSV
        df = pd.read_csv('control_envios.csv', dtype={'numero': str})
        print(f"✅ CSV cargado: {len(df)} registros")
        
        # Contar registros a resetear
        registros_resetear = df[df['numero'] != numero_excluido]
        total_resetear = len(registros_resetear)
        
        print(f"📊 Registros a resetear: {total_resetear}")
        print(f"📊 Usuario excluido: {len(df[df['numero'] == numero_excluido])} registros")
        
        # Confirmar operación automáticamente (para automatización)
        print(f"\n✅ Procediendo a resetear {total_resetear} registros...")
        
        # Resetear todos los campos excepto el usuario excluido
        for index, row in df.iterrows():
            numero = str(row['numero'])
            
            if numero != numero_excluido:
                df.at[index, 'enviado'] = 0
                df.at[index, 'fecha_envio'] = ''
                df.at[index, 'resultado'] = ''
                df.at[index, 'completado'] = 0
                df.at[index, 'intentos_envio'] = 0
                df.at[index, 'fecha_completado'] = ''
                df.at[index, 'ultimo_estado_botpress'] = 0
        
        # Guardar cambios
        df.to_csv('control_envios.csv', index=False)
        
        print(f"\n✅ RESETEO COMPLETADO:")
        print(f"   🔧 Registros reseteados: {total_resetear}")
        print(f"   📞 Usuario preservado: {numero_excluido}")
        print(f"   💾 CSV actualizado correctamente")
        
        # Mostrar estadísticas finales
        print(f"\n📈 ESTADÍSTICAS POST-RESETEO:")
        total_enviados = len(df[df['enviado'] == 1])
        total_completados = len(df[df['completado'] == 1])
        total_con_intentos = len(df[df['intentos_envio'] > 0])
        
        print(f"   📤 Total enviados: {total_enviados}")
        print(f"   ✅ Total completados: {total_completados}")
        print(f"   🔄 Total con intentos: {total_con_intentos}")
        
        # Mostrar detalles del usuario preservado
        usuario_preservado = df[df['numero'] == numero_excluido]
        if len(usuario_preservado) > 0:
            enviados_usuario = len(usuario_preservado[usuario_preservado['enviado'] == 1])
            completados_usuario = len(usuario_preservado[usuario_preservado['completado'] == 1])
            print(f"\n📞 USUARIO PRESERVADO ({numero_excluido}):")
            print(f"   📤 Enviados: {enviados_usuario}/30")
            print(f"   ✅ Completados: {completados_usuario}/30")
        
        print(f"\n🎉 Reseteo completado exitosamente!")
        
    except FileNotFoundError:
        print("❌ Archivo control_envios.csv no encontrado")
    except Exception as e:
        print(f"❌ Error durante el reseteo: {e}")

if __name__ == "__main__":
    reset_all_except_one()