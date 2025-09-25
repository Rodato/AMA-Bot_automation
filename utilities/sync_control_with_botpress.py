#!/usr/bin/env python3
import pandas as pd
from datetime import datetime

def sync_control_with_botpress():
    """Sincronizar control_envios.csv con datos de botpress_data.csv"""
    
    print("🔄 Sincronizando control_envios.csv con datos de Botpress...")
    
    try:
        # Cargar archivos
        control_df = pd.read_csv('control_envios.csv', dtype={'numero': str})
        botpress_df = pd.read_csv('botpress_data.csv', dtype={'clientNumber': str})
        
        print(f"✅ CSV de control cargado: {len(control_df)} registros")
        print(f"✅ CSV de Botpress cargado: {len(botpress_df)} registros")
        
        # Crear diccionario de progreso de Botpress para acceso rápido
        botpress_progress = {}
        for _, row in botpress_df.iterrows():
            client_num = str(row['clientNumber'])
            botpress_progress[client_num] = {
                'session1_day1': row.get('session1_day1', '0'),
                'session1_day2': row.get('session1_day2', '0'),
                'session1_day3': row.get('session1_day3', '0'),
                'session1_day4': row.get('session1_day4', '0'),
                'session1_day5': row.get('session1_day5', '0'),
            }
        
        # Contadores para reporte
        actualizados = 0
        nuevos_completados = 0
        
        # Actualizar registros del CSV de control
        for index, row in control_df.iterrows():
            numero = str(row['numero'])
            sesion = row['sesion']
            day = row['day']
            
            # Solo procesar sesión 1 por ahora (los datos de Botpress son solo session1)
            if sesion != 1:
                continue
            
            # Verificar si existe en datos de Botpress
            if numero in botpress_progress:
                day_key = f'session1_day{day}'
                botpress_status = str(botpress_progress[numero].get(day_key, '0'))
                
                # Actualizar ultimo_estado_botpress
                control_df.at[index, 'ultimo_estado_botpress'] = int(botpress_status) if botpress_status.isdigit() else 0
                
                # Si el estado es 2 (completado) y no estaba marcado como completado
                if botpress_status == '2' and row['completado'] == 0:
                    control_df.at[index, 'completado'] = 1
                    control_df.at[index, 'fecha_completado'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    nuevos_completados += 1
                    print(f"   ✅ Marcado como completado: {numero} - Sesión {sesion}, Día {day}")
                
                # Si el estado es 1 (enviado) y no estaba marcado como enviado
                elif botpress_status == '1' and row['enviado'] == 0:
                    control_df.at[index, 'enviado'] = 1
                    if row['intentos_envio'] == 0:
                        control_df.at[index, 'intentos_envio'] = 1
                    control_df.at[index, 'fecha_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    control_df.at[index, 'resultado'] = 'Sincronizado desde Botpress'
                    print(f"   📤 Marcado como enviado: {numero} - Sesión {sesion}, Día {day}")
                
                actualizados += 1
            else:
                print(f"   ⚠️ Usuario {numero} no encontrado en datos de Botpress")
        
        # Guardar cambios
        control_df.to_csv('control_envios.csv', index=False)
        
        print(f"\n📊 REPORTE DE SINCRONIZACIÓN:")
        print(f"   🔄 Registros procesados: {actualizados}")
        print(f"   🎯 Nuevos completados: {nuevos_completados}")
        print(f"   💾 Archivo actualizado: control_envios.csv")
        
        # Mostrar estadísticas finales
        total_enviados = len(control_df[control_df['enviado'] == 1])
        total_completados = len(control_df[control_df['completado'] == 1])
        
        print(f"\n📈 ESTADÍSTICAS ACTUALIZADAS:")
        print(f"   📤 Total enviados: {total_enviados}")
        print(f"   ✅ Total completados: {total_completados}")
        print(f"   📊 Tasa de completado: {(total_completados/total_enviados)*100:.1f}%" if total_enviados > 0 else "   📊 Tasa de completado: 0%")
        
    except FileNotFoundError as e:
        print(f"❌ Archivo no encontrado: {e}")
    except Exception as e:
        print(f"❌ Error durante sincronización: {e}")

if __name__ == "__main__":
    sync_control_with_botpress()