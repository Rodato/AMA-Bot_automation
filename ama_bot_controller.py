#!/usr/bin/env python3
import pandas as pd
import requests
import time
import json
from datetime import datetime
import sys

class AMABotController:
    def __init__(self, csv_file='control_envios.csv'):
        self.csv_file = csv_file
        
        # Configuración para webhook (envíos)
        self.webhook_url = "https://webhook.botpress.cloud/2d63c736-0910-47a8-b06a-c82c12372106"
        self.webhook_headers = {
            "x-bp-secret": "73c380fc550ad6b061d4d8ec3547731eprod",
            "Content-Type": "application/json"
        }
        
        # Configuración para Tables API (consultas)
        self.botpress_token = "bp_pat_t3Qzk5mKulbKTudzrZHEJ2Rjqkb6z9f6qrw9"
        self.bot_id = "f70c360d-ed8d-402f-9cd2-488d9f1d358c"
        self.tables_base_url = "https://api.botpress.cloud/v1/tables"
        self.progress_table_name = "DataJsonProgressTable"
        self.tables_headers = {
            "Authorization": f"Bearer {self.botpress_token}",
            "x-bot-id": self.bot_id,
            "Content-Type": "application/json"
        }
        
        self.df = None
        self.botpress_data = {}
        self.load_data()
    
    def load_data(self):
        """Cargar datos del CSV de control"""
        try:
            self.df = pd.read_csv(self.csv_file, dtype={'numero': str})
            print(f"✅ CSV de control cargado: {len(self.df)} registros")
            
            # Verificar si tiene las nuevas columnas de ubicación
            if 'location' in self.df.columns:
                locations = self.df['location'].nunique()
                location_names = self.df['location_name'].nunique()
                print(f"   🏫 Locations: {locations}, Location names: {location_names}")
            else:
                print("   ⚠️  CSV sin datos de ubicación (estructura antigua)")
                
        except FileNotFoundError:
            print(f"❌ Error: No se encontró el archivo {self.csv_file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error al cargar CSV: {e}")
            sys.exit(1)
    
    def save_data(self):
        """Guardar cambios en el CSV"""
        try:
            self.df.to_csv(self.csv_file, index=False)
            print("💾 Datos guardados correctamente")
        except Exception as e:
            print(f"❌ Error al guardar: {e}")
    
    def refresh_botpress_data(self):
        """Obtener datos frescos de Botpress y actualizar CSV local"""
        print("🔄 Actualizando datos desde Botpress...")
        
        try:
            # Usar el método correcto de get_table_rows.py
            response = requests.post(
                f"{self.tables_base_url}/{self.progress_table_name}/rows/find",
                headers=self.tables_headers,
                json={"limit": 1000}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'rows' in data and isinstance(data['rows'], list):
                    rows = data['rows']
                    print(f"✅ Datos de Botpress actualizados: {len(rows)} usuarios")
                    
                    # Crear diccionario para acceso rápido
                    self.botpress_data = {}
                    for row in rows:
                        client_num = str(row.get('clientNumber', ''))
                        self.botpress_data[client_num] = row
                    
                    # Sincronizar con CSV local
                    self.sync_with_botpress_data()
                    return True
                else:
                    print("⚠️ No se encontraron datos en la respuesta")
                    return False
            else:
                print(f"❌ Error API: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error consultando Botpress: {e}")
            return False
    
    def sync_with_botpress_data(self):
        """Sincronizar estado del CSV con datos de Botpress"""
        print("🔄 Sincronizando estado local con Botpress...")
        
        actualizados = 0
        nuevos_completados = 0
        
        for index, row in self.df.iterrows():
            numero = str(row['numero'])
            sesion = row['sesion']
            day = row['day']
            
            # Solo procesar sesión 1 por ahora
            if sesion != 1:
                continue
            
            if numero in self.botpress_data:
                botpress_row = self.botpress_data[numero]
                session1_data = botpress_row.get('session1', {})
                
                if isinstance(session1_data, dict):
                    day_status = str(session1_data.get(str(day), '0'))
                    
                    # Actualizar ultimo_estado_botpress
                    self.df.at[index, 'ultimo_estado_botpress'] = int(day_status) if day_status.isdigit() else 0
                    
                    # Si está completado (estado 2) y no estaba marcado
                    if day_status == '2' and row['completado'] == 0:
                        self.df.at[index, 'completado'] = 1
                        self.df.at[index, 'fecha_completado'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        nuevos_completados += 1
                        print(f"   ✅ Completado: {numero} - Sesión {sesion}, Día {day}")
                    
                    # Si está enviado (estado 1) y no estaba marcado
                    elif day_status == '1' and row['enviado'] == 0:
                        self.df.at[index, 'enviado'] = 1
                        if row['intentos_envio'] == 0:
                            self.df.at[index, 'intentos_envio'] = 1
                        self.df.at[index, 'fecha_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        self.df.at[index, 'resultado'] = 'Sincronizado desde Botpress'
                    
                    actualizados += 1
        
        print(f"   🔄 Actualizados: {actualizados}, ✅ Nuevos completados: {nuevos_completados}")
    
    def can_send_message(self, numero, sesion, day, csv_row):
        """Verificar si se puede enviar mensaje basado en reglas de negocio"""
        
        # Verificar límite de intentos (máximo 2)
        if csv_row['intentos_envio'] >= 2:
            return False, f"Máximo intentos alcanzado ({csv_row['intentos_envio']}/2)"
        
        # Si ya está completado, no reenviar
        if csv_row['completado'] == 1:
            return False, "Ya completado"
        
        # Sesión 1, Día 1 siempre se permite (inicio de campaña)
        if sesion == 1 and day == 1:
            return True, "Inicio de campaña - siempre permitido"
        
        # Para otros días/sesiones, verificar prerrequisitos
        numero_str = str(numero)
        if numero_str not in self.botpress_data:
            return False, "Usuario no encontrado en Botpress"
        
        botpress_row = self.botpress_data[numero_str]
        session1_data = botpress_row.get('session1', {})
        
        if not isinstance(session1_data, dict):
            return False, "Datos de sesión inválidos"
        
        # Para días posteriores en sesión 1
        if sesion == 1 and day > 1:
            prev_day_status = str(session1_data.get(str(day - 1), '0'))
            if prev_day_status == '2':  # Día anterior completado
                return True, f"Día anterior completado (día {day-1})"
            else:
                return False, f"Día anterior no completado (día {day-1}: {prev_day_status})"
        
        # Para sesiones posteriores (implementar cuando se necesite)
        if sesion > 1:
            return False, "Sesiones > 1 no implementadas aún"
        
        return True, "Condiciones cumplidas"
    
    def enviar_mensaje(self, numero, sesion, day):
        """Enviar mensaje individual via webhook"""
        data = {
            "clientNumber": int(numero),
            "session": int(sesion),
            "day": int(day)
        }
        
        try:
            response = requests.post(self.webhook_url, headers=self.webhook_headers, json=data)
            return response.status_code == 200, response.status_code, response.text
        except Exception as e:
            return False, 0, str(e)
    
    def procesar_envios(self, limite=None, sesion_especifica=None, day_especifico=None):
        """Procesar envíos con validación completa"""
        
        # Primero actualizar datos de Botpress
        if not self.refresh_botpress_data():
            print("❌ No se pudieron actualizar datos de Botpress")
            return
        
        # Filtrar registros pendientes
        pendientes = self.df[self.df['enviado'] == 0]
        
        # Aplicar filtros adicionales si se especifican
        if sesion_especifica:
            pendientes = pendientes[pendientes['sesion'] == sesion_especifica]
        if day_especifico:
            pendientes = pendientes[pendientes['day'] == day_especifico]
        
        if len(pendientes) == 0:
            print("✅ No hay envíos pendientes")
            return
        
        if limite:
            pendientes = pendientes.head(limite)
        
        print(f"📤 Procesando {len(pendientes)} envíos...")
        
        exitosos = 0
        fallidos = 0
        omitidos = 0
        enviados_detalle = []  # Lista para almacenar detalles de envíos exitosos
        
        for index, row in pendientes.iterrows():
            numero = row['numero']
            sesion = row['sesion']
            day = row['day']
            
            print(f"\\n📞 Evaluando: {numero} - Sesión {sesion}, Día {day}")
            
            # Verificar si se puede enviar
            can_send, reason = self.can_send_message(numero, sesion, day, row)
            
            if not can_send:
                print(f"   ⏭️ Omitido: {reason}")
                self.df.at[index, 'resultado'] = f"Omitido: {reason}"
                omitidos += 1
                continue
            
            print(f"   ✅ Validado: {reason}")
            print(f"   📤 Enviando mensaje...")
            
            # Incrementar contador de intentos
            self.df.at[index, 'intentos_envio'] = self.df.at[index, 'intentos_envio'] + 1
            
            # Enviar mensaje
            exito, status_code, respuesta = self.enviar_mensaje(numero, sesion, day)
            
            # Actualizar registro
            self.df.at[index, 'enviado'] = 1 if exito else 0
            self.df.at[index, 'fecha_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.df.at[index, 'resultado'] = f"Status: {status_code} (Intento {self.df.at[index, 'intentos_envio']})"
            
            if exito:
                print(f"   ✅ Enviado exitosamente (Intento {self.df.at[index, 'intentos_envio']})")
                exitosos += 1
                # Almacenar detalles del envío exitoso
                enviados_detalle.append({
                    'numero': numero,
                    'sesion': sesion,
                    'day': day,
                    'intento': self.df.at[index, 'intentos_envio']
                })
            else:
                print(f"   ❌ Error: {status_code} - {respuesta}")
                fallidos += 1
            
            # Pausa entre envíos
            print(f"   ⏱️ Esperando 3 segundos...")
            time.sleep(3)
        
        # Guardar cambios
        self.save_data()
        
        # Actualizar datos de Botpress después de envíos
        print("\\n🔄 Actualizando progreso después de envíos...")
        self.refresh_botpress_data()
        
        print(f"\\n📊 RESUMEN DE ENVÍOS:")
        print(f"   ✅ Exitosos: {exitosos}")
        print(f"   ❌ Fallidos: {fallidos}")
        print(f"   ⏭️ Omitidos: {omitidos}")
        print(f"   📋 Total procesados: {exitosos + fallidos + omitidos}")
        
        # Mostrar detalles de envíos exitosos
        if enviados_detalle:
            print(f"\\n📋 DETALLES DE ENVÍOS EXITOSOS:")
            for envio in enviados_detalle:
                print(f"   📞 {envio['numero']} → Sesión {envio['sesion']}, Día {envio['day']} (Intento {envio['intento']})")
        
        # Mostrar resumen por sesión/día
        if enviados_detalle:
            print(f"\\n📈 RESUMEN POR SESIÓN/DÍA:")
            sesion_day_counts = {}
            for envio in enviados_detalle:
                key = f"Sesión {envio['sesion']}, Día {envio['day']}"
                sesion_day_counts[key] = sesion_day_counts.get(key, 0) + 1
            
            for sesion_day, count in sesion_day_counts.items():
                print(f"   📤 {sesion_day}: {count} envío{'s' if count != 1 else ''}")
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas completas"""
        # Actualizar datos primero
        self.refresh_botpress_data()
        
        total = len(self.df)
        enviados = len(self.df[self.df['enviado'] == 1])
        pendientes = total - enviados
        completados = len(self.df[self.df['completado'] == 1])
        con_intentos = len(self.df[self.df['intentos_envio'] > 0])
        
        print(f"\\n📊 ESTADÍSTICAS GENERALES:")
        print(f"   📋 Total registros: {total}")
        print(f"   📤 Enviados: {enviados}")
        print(f"   ⏳ Pendientes: {pendientes}")
        print(f"   ✅ Completados: {completados}")
        print(f"   📈 Tasa envío: {(enviados/total)*100:.1f}%")
        print(f"   🏆 Tasa completado: {(completados/con_intentos)*100:.1f}%" if con_intentos > 0 else "   🏆 Tasa completado: 0.0%")
        
        # Por ubicación si están disponibles
        if 'location' in self.df.columns:
            self.mostrar_estadisticas_por_ubicacion()
        
        # Por sesión
        print(f"\\n📋 ESTADÍSTICAS POR SESIÓN:")
        for sesion in range(1, 7):
            sesion_df = self.df[self.df['sesion'] == sesion]
            if len(sesion_df) > 0:
                enviados_sesion = len(sesion_df[sesion_df['enviado'] == 1])
                completados_sesion = len(sesion_df[sesion_df['completado'] == 1])
                total_sesion = len(sesion_df)
                print(f"   Sesión {sesion}: {enviados_sesion}/{total_sesion} enviados, {completados_sesion} completados")
    
    def mostrar_estadisticas_por_ubicacion(self):
        """Mostrar estadísticas detalladas por ubicación"""
        print(f"\\n🏫 ESTADÍSTICAS POR UBICACIÓN:")
        
        # Agrupar por location y location_name
        ubicaciones = self.df.groupby(['location', 'location_name']).agg({
            'numero': 'nunique',  # usuarios únicos
            'enviado': 'sum',     # total enviados
            'completado': 'sum',  # total completados
            'intentos_envio': lambda x: (x > 0).sum()  # con intentos
        }).reset_index()
        
        ubicaciones.columns = ['location', 'location_name', 'usuarios', 'enviados', 'completados', 'con_intentos']
        
        for _, row in ubicaciones.iterrows():
            location = row['location']
            location_name = row['location_name']
            usuarios = row['usuarios']
            enviados = row['enviados']
            completados = row['completados']
            con_intentos = row['con_intentos']
            
            # Calcular registros totales para esta ubicación
            registros_location = len(self.df[(self.df['location'] == location) & 
                                           (self.df['location_name'] == location_name)])
            
            tasa_envio = (enviados/registros_location)*100 if registros_location > 0 else 0
            tasa_completado = (completados/con_intentos)*100 if con_intentos > 0 else 0
            
            print(f"   📍 {location} - {location_name}:")
            print(f"      👥 {usuarios} usuarios, 📊 {registros_location} registros")
            print(f"      📤 {enviados} enviados ({tasa_envio:.1f}%)")
            print(f"      ✅ {completados} completados ({tasa_completado:.1f}%)")
            
        # Resumen por salones si hay múltiples
        salones = self.df['salon'].nunique() if 'salon' in self.df.columns else 0
        if salones > 1:
            print(f"\\n🚪 RESUMEN POR SALÓN:")
            salon_stats = self.df.groupby('salon').agg({
                'numero': 'nunique',
                'enviado': 'sum', 
                'completado': 'sum'
            }).reset_index()
            salon_stats.columns = ['salon', 'usuarios', 'enviados', 'completados']
            
            for _, row in salon_stats.iterrows():
                print(f"   🚪 {row['salon']}: {row['usuarios']} usuarios, {row['enviados']} enviados, {row['completados']} completados")

# Ejemplo de uso y menú
if __name__ == "__main__":
    controller = AMABotController('control_envios.csv')
    
    while True:
        print(f"\\n🤖 AMA BOT CONTROLLER - SISTEMA INTEGRADO")
        print("1. Ver estadísticas actualizadas")
        print("2. Procesar TODOS los pendientes")
        print("3. Procesar sesión/día específico")
        print("4. Procesar cantidad limitada")
        print("5. Actualizar datos desde Botpress")
        print("6. Salir")
        
        opcion = input("\\nSelecciona una opción: ")
        
        if opcion == "1":
            controller.mostrar_estadisticas()
        
        elif opcion == "2":
            controller.procesar_envios()
        
        elif opcion == "3":
            try:
                sesion = int(input("Sesión (1-6): "))
                day = int(input("Día (1-5): "))
                controller.procesar_envios(sesion_especifica=sesion, day_especifico=day)
            except ValueError:
                print("❌ Por favor ingresa números válidos")
        
        elif opcion == "4":
            try:
                limite = int(input("Cantidad a procesar: "))
                controller.procesar_envios(limite=limite)
            except ValueError:
                print("❌ Por favor ingresa un número válido")
        
        elif opcion == "5":
            controller.refresh_botpress_data()
            controller.save_data()
        
        elif opcion == "6":
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")