import pandas as pd
import requests
import time
from datetime import datetime
import sys

class BotpressController:
    def __init__(self, csv_file='control_envios.csv', botpress_token=None, bot_id=None):
        self.csv_file = csv_file
        
        # Configuración para webhook
        self.webhook_url = "https://webhook.botpress.cloud/2d63c736-0910-47a8-b06a-c82c12372106"
        self.webhook_headers = {
            "x-bp-secret": "73c380fc550ad6b061d4d8ec3547731eprod",
            "Content-Type": "application/json"
        }
        
        # Configuración para Tables API
        self.botpress_token = botpress_token or "bp_pat_t3Qzk5mKulbKTudzrZHEJ2Rjqkb6z9f6qrw9"
        self.bot_id = bot_id or "f70c360d-ed8d-402f-9cd2-488d9f1d358c"
        self.tables_base_url = "https://api.botpress.cloud/v1/tables"
        self.tables_headers = {
            "Authorization": f"Bearer {self.botpress_token}",
            "x-bot-id": self.bot_id,
            "Content-Type": "application/json"
        }
        
        self.progress_table_name = "DataJsonProgressTable"
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Cargar datos del CSV"""
        try:
            self.df = pd.read_csv(self.csv_file, dtype={'numero': str})
            
            # Agregar nuevas columnas si no existen (compatibilidad con CSVs antiguos)
            required_columns = {
                'completado': 0,
                'intentos_envio': 0,
                'fecha_completado': '',
                'ultimo_estado_botpress': 0
            }
            
            for col, default_value in required_columns.items():
                if col not in self.df.columns:
                    self.df[col] = default_value
                    print(f"➕ Columna agregada: {col}")
            
            print(f"✅ CSV cargado: {len(self.df)} registros")
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
    
    def get_user_progress(self, client_number):
        """Obtener el progreso de un usuario desde la tabla de Botpress"""
        try:
            # Usar el método correcto basado en get_table_rows.py
            response = requests.post(
                f"{self.tables_base_url}/{self.progress_table_name}/rows/find",
                headers=self.tables_headers,
                json={"limit": 1000}
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'rows' in data and isinstance(data['rows'], list):
                    rows = data['rows']
                    
                    # Buscar usuario por clientNumber
                    for row in rows:
                        if str(row.get('clientNumber', '')) == str(client_number):
                            return row
                    
                    return None  # Usuario no encontrado
                else:
                    print(f"⚠️ No se encontraron filas en la respuesta")
                    return None
            else:
                print(f"⚠️ Error API: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error consultando progreso de {client_number}: {e}")
            return None
    
    def can_send_message(self, client_number, sesion, day, csv_row_index):
        """Verificar si se puede enviar un mensaje basado en el progreso del usuario y reenvíos"""
        
        # Obtener datos del CSV para este registro específico
        csv_row = self.df.loc[csv_row_index]
        intentos_actuales = csv_row['intentos_envio']
        completado_csv = csv_row['completado']
        
        # Si ya está completado en CSV, no reenviar
        if completado_csv == 1:
            return False, "Ya completado según CSV local"
        
        # Límite de intentos: máximo 2 envíos por sesión/día
        if intentos_actuales >= 2:
            return False, f"Máximo de intentos alcanzado ({intentos_actuales}/2)"
        
        # Sesión 1, Día 1 siempre se envía (primer contacto)
        if sesion == 1 and day == 1:
            return True, "Primer envío - siempre se permite"
        
        # Para reenvíos de la misma sesión/día (cuando no completó)
        if intentos_actuales >= 1:
            # Consultar estado actual en Botpress
            progress_data = self.get_user_progress(client_number)
            if not progress_data:
                return False, "Usuario no encontrado en tabla de progreso"
            
            # Verificar si completó desde el último envío
            session_column = f"session{sesion}"
            if session_column in progress_data:
                session_data = progress_data[session_column]
                if isinstance(session_data, dict):
                    day_key = str(day)
                    if day_key in session_data:
                        day_status = session_data[day_key]
                        if isinstance(day_status, str):
                            try:
                                day_status = int(day_status)
                            except ValueError:
                                day_status = 0
                        
                        if day_status == 2:  # Completado
                            return False, "Ya completado según Botpress (actualizará CSV)"
                        else:
                            return True, f"Reenvío permitido ({intentos_actuales + 1}/2) - estado día {day}: {day_status}"
                    else:
                        return True, f"Reenvío permitido ({intentos_actuales + 1}/2) - día {day} no encontrado"
                else:
                    return True, f"Reenvío permitido ({intentos_actuales + 1}/2) - sesión sin estructura de días"
            else:
                return True, f"Reenvío permitido ({intentos_actuales + 1}/2) - sesión no encontrada"
        
        # Para envíos normales (primer intento de días/sesiones posteriores)
        progress_data = self.get_user_progress(client_number)
        if not progress_data:
            return False, "Usuario no encontrado en tabla de progreso"
        
        # Verificar el día anterior
        if day > 1:
            # Verificar día anterior de la misma sesión
            session_column = f"session{sesion}"
            if session_column in progress_data:
                session_data = progress_data[session_column]
                if isinstance(session_data, dict):
                    prev_day_key = str(day - 1)
                    if prev_day_key in session_data:
                        prev_day_status = session_data[prev_day_key]
                        if isinstance(prev_day_status, str):
                            try:
                                prev_day_status = int(prev_day_status)
                            except ValueError:
                                prev_day_status = 0
                        
                        # Estado 2 = completado, estado 1 = enviado pero no completado, estado 0 = no enviado
                        if prev_day_status == 2:
                            return True, f"Día anterior completado (día {day-1}: estado {prev_day_status})"
                        else:
                            return False, f"Día anterior no completado (día {day-1}: estado {prev_day_status})"
                    else:
                        return False, f"Día anterior ({day-1}) no encontrado en sesión {sesion}"
                else:
                    return False, f"Sesión {sesion} no tiene estructura de días"
            else:
                return False, f"Sesión {sesion} no encontrada en progreso"
        
        # Para sesiones > 1, verificar que completó la sesión anterior
        if sesion > 1:
            # Verificar último día de sesión anterior (día 5)
            prev_session_column = f"session{sesion-1}"
            if prev_session_column in progress_data:
                prev_session_data = progress_data[prev_session_column]
                if isinstance(prev_session_data, dict):
                    # Verificar día 5 de la sesión anterior
                    last_day_key = "5"  # Día 5 es el último
                    if last_day_key in prev_session_data:
                        last_day_status = prev_session_data[last_day_key]
                        if isinstance(last_day_status, str):
                            try:
                                last_day_status = int(last_day_status)
                            except ValueError:
                                last_day_status = 0
                        
                        if last_day_status == 2:
                            return True, f"Sesión anterior completada (sesión {sesion-1} día 5: estado {last_day_status})"
                        else:
                            return False, f"Sesión anterior no completada (sesión {sesion-1} día 5: estado {last_day_status})"
                    else:
                        return False, f"Día 5 de sesión {sesion-1} no encontrado"
                else:
                    return False, f"Sesión {sesion-1} no tiene estructura de días"
            else:
                return False, f"Sesión anterior ({sesion-1}) no encontrada en progreso"
        
        return True, "Condiciones cumplidas"
    
    def enviar_mensaje(self, numero, sesion, day):
        """Enviar mensaje individual"""
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
    
    def update_completion_status(self, numero, sesion, day, index):
        """Actualizar estado de completado consultando Botpress"""
        try:
            progress_data = self.get_user_progress(numero)
            if not progress_data:
                return False
            
            session_column = f"session{sesion}"
            if session_column in progress_data:
                session_data = progress_data[session_column]
                
                # session_data es un objeto como {"1": "2", "2": "1", "3": 0, ...}
                if isinstance(session_data, dict):
                    day_key = str(day)  # Los días son strings en Botpress
                    if day_key in session_data:
                        day_status = session_data[day_key]
                        
                        # Convertir a int si es string
                        if isinstance(day_status, str):
                            try:
                                day_status = int(day_status)
                            except ValueError:
                                day_status = 0
                        
                        # Actualizar CSV con datos de Botpress
                        self.df.at[index, 'ultimo_estado_botpress'] = day_status
                        
                        if day_status == 2:  # Completado
                            self.df.at[index, 'completado'] = 1
                            self.df.at[index, 'fecha_completado'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            return True
                        else:
                            self.df.at[index, 'completado'] = 0
                            return False
                    else:
                        # Día no encontrado en sesión
                        self.df.at[index, 'ultimo_estado_botpress'] = 0
                        self.df.at[index, 'completado'] = 0
                        return False
                else:
                    print(f"⚠️ session{sesion} no es un objeto: {session_data}")
                    return False
            else:
                print(f"⚠️ session{sesion} no encontrada en progreso")
                return False
        except Exception as e:
            print(f"❌ Error actualizando estado de completado: {e}")
            return False
    
    def procesar_con_validacion(self, limite=None):
        """Procesar envíos validando el progreso de cada usuario"""
        pendientes = self.df[self.df['enviado'] == 0]
        
        if len(pendientes) == 0:
            print("✅ No hay envíos pendientes")
            return
        
        if limite:
            pendientes = pendientes.head(limite)
            print(f"📤 Procesando {len(pendientes)} envíos (límite aplicado)")
        else:
            print(f"📤 Procesando {len(pendientes)} envíos pendientes con validación")
        
        exitosos = 0
        fallidos = 0
        omitidos = 0
        
        for index, row in pendientes.iterrows():
            numero = row['numero']
            sesion = row['sesion'] 
            day = row['day']
            
            print(f"\n📞 Evaluando: {numero} - Sesión {sesion}, Día {day}")
            
            # Primero, verificar si ya completó (sincronizar con Botpress)
            self.update_completion_status(numero, sesion, day, index)
            
            # Verificar si se puede enviar
            can_send, reason = self.can_send_message(numero, sesion, day, index)
            
            if not can_send:
                print(f"   ⏭️  Omitido: {reason}")
                self.df.at[index, 'resultado'] = f"Omitido: {reason}"
                omitidos += 1
                continue
            
            print(f"   ✅ Validado: {reason}")
            print(f"   📤 Enviando mensaje...")
            
            # Incrementar contador de intentos ANTES del envío
            self.df.at[index, 'intentos_envio'] = self.df.at[index, 'intentos_envio'] + 1
            
            # Enviar mensaje
            exito, status_code, respuesta = self.enviar_mensaje(numero, sesion, day)
            
            # Actualizar registro local
            self.df.loc[index, 'enviado'] = 1 if exito else 0
            self.df.at[index, 'fecha_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.df.at[index, 'resultado'] = f"Status: {status_code} (Intento {self.df.at[index, 'intentos_envio']})"
            
            if exito:
                print(f"   ✅ Mensaje enviado exitosamente (Intento {self.df.at[index, 'intentos_envio']})")
                # Botpress actualiza automáticamente su tabla
                exitosos += 1
            else:
                print(f"   ❌ Error enviando: {status_code} - {respuesta}")
                fallidos += 1
            
            # Pausa entre envíos (5 segundos)
            print(f"   ⏱️  Esperando 5 segundos...")
            time.sleep(3)
        
        # Guardar cambios
        self.save_data()
        
        print(f"\n📊 Resumen:")
        print(f"   ✅ Exitosos: {exitosos}")
        print(f"   ❌ Fallidos: {fallidos}")
        print(f"   ⏭️  Omitidos: {omitidos}")
        print(f"   📋 Total procesados: {exitosos + fallidos + omitidos}")
    
    def procesar_sesion_dia_con_validacion(self, sesion, day):
        """Procesar una sesión y día específicos con validación"""
        filtro = (self.df['sesion'] == sesion) & (self.df['day'] == day) & (self.df['enviado'] == 0)
        registros = self.df[filtro]
        
        if len(registros) == 0:
            print(f"✅ No hay pendientes para Sesión {sesion}, Día {day}")
            return
        
        print(f"📤 Procesando Sesión {sesion}, Día {day}: {len(registros)} números")
        
        exitosos = 0
        fallidos = 0
        omitidos = 0
        
        for index, row in registros.iterrows():
            numero = row['numero']
            print(f"\n📞 Evaluando: {numero}")
            
            # Primero, verificar si ya completó (sincronizar con Botpress)
            self.update_completion_status(numero, sesion, day, index)
            
            # Verificar si se puede enviar
            can_send, reason = self.can_send_message(numero, sesion, day, index)
            
            if not can_send:
                print(f"   ⏭️  Omitido: {reason}")
                self.df.at[index, 'resultado'] = f"Omitido: {reason}"
                omitidos += 1
                continue
            
            print(f"   ✅ Validado: {reason}")
            print(f"   📤 Enviando mensaje...")
            
            # Incrementar contador de intentos ANTES del envío
            self.df.at[index, 'intentos_envio'] = self.df.at[index, 'intentos_envio'] + 1
            
            # Enviar mensaje
            exito, status_code, respuesta = self.enviar_mensaje(numero, sesion, day)
            
            self.df.loc[index, 'enviado'] = 1 if exito else 0
            self.df.at[index, 'fecha_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.df.at[index, 'resultado'] = f"Status: {status_code} (Intento {self.df.at[index, 'intentos_envio']})"
            
            if exito:
                print(f"   ✅ Mensaje enviado (Intento {self.df.at[index, 'intentos_envio']})")
                # Botpress actualiza automáticamente su tabla
                exitosos += 1
            else:
                print(f"   ❌ Error: {status_code}")
                fallidos += 1
            
            print(f"   ⏱️  Esperando 5 segundos...")
            time.sleep(3)
        
        self.save_data()
        
        print(f"\n📊 Resumen Sesión {sesion}, Día {day}:")
        print(f"   ✅ Exitosos: {exitosos}")
        print(f"   ❌ Fallidos: {fallidos}")
        print(f"   ⏭️  Omitidos: {omitidos}")
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas del CSV"""
        total = len(self.df)
        enviados = len(self.df[self.df['enviado'] == 1])
        pendientes = total - enviados
        completados = len(self.df[self.df['completado'] == 1])
        con_intentos = len(self.df[self.df['intentos_envio'] > 0])
        reenvios = len(self.df[self.df['intentos_envio'] > 1])
        
        print(f"\n📊 ESTADÍSTICAS GENERALES:")
        print(f"   📋 Total registros: {total}")
        print(f"   ✅ Enviados: {enviados}")
        print(f"   ⏳ Pendientes: {pendientes}")
        print(f"   🎯 Completados: {completados}")
        print(f"   🔄 Con reenvíos: {reenvios}")
        print(f"   📈 Progreso envíos: {(enviados/total)*100:.1f}%")
        print(f"   🏆 Tasa completado: {(completados/con_intentos)*100:.1f}%" if con_intentos > 0 else "   🏆 Tasa completado: 0.0%")
        
        # Estadísticas de intentos
        print(f"\n🔄 ANÁLISIS DE REENVÍOS:")
        for intentos in range(0, 3):
            count = len(self.df[self.df['intentos_envio'] == intentos])
            if count > 0:
                if intentos == 0:
                    print(f"   Sin envíos: {count}")
                elif intentos == 1:
                    print(f"   1 intento: {count}")
                else:
                    print(f"   {intentos} intentos: {count}")
        
        # Por sesión
        print(f"\n📋 POR SESIÓN:")
        for sesion in range(1, 7):
            sesion_df = self.df[self.df['sesion'] == sesion]
            if len(sesion_df) > 0:
                enviados_sesion = len(sesion_df[sesion_df['enviado'] == 1])
                completados_sesion = len(sesion_df[sesion_df['completado'] == 1])
                total_sesion = len(sesion_df)
                print(f"   Sesión {sesion}: {enviados_sesion}/{total_sesion} enviados, {completados_sesion} completados")
    
    def resetear_envios(self):
        """Resetear todos los envíos (marcar como no enviados)"""
        respuesta = input("⚠️  ¿Estás seguro de resetear TODOS los envíos? (yes/no): ")
        if respuesta.lower() == 'yes':
            self.df['enviado'] = 0
            self.df['fecha_envio'] = ''
            self.df['resultado'] = ''
            self.df['completado'] = 0
            self.df['intentos_envio'] = 0
            self.df['fecha_completado'] = ''
            self.df['ultimo_estado_botpress'] = 0
            self.save_data()
            print("🔄 Todos los envíos han sido reseteados")
        else:
            print("❌ Operación cancelada")
    
    def sincronizar_completados(self):
        """Sincronizar estado de completados con Botpress para todos los registros"""
        print("🔄 Sincronizando estado de completados con Botpress...")
        
        # Solo sincronizar registros que han tenido al menos un envío
        registros_enviados = self.df[self.df['intentos_envio'] > 0]
        total = len(registros_enviados)
        
        if total == 0:
            print("⚠️ No hay registros enviados para sincronizar")
            return
        
        print(f"📊 Sincronizando {total} registros...")
        actualizados = 0
        nuevos_completados = 0
        
        for index, row in registros_enviados.iterrows():
            numero = row['numero']
            sesion = row['sesion']
            day = row['day']
            completado_anterior = row['completado']
            
            # Actualizar estado
            if self.update_completion_status(numero, sesion, day, index):
                if completado_anterior == 0:  # Era no completado y ahora sí
                    nuevos_completados += 1
                actualizados += 1
            
            # Mostrar progreso cada 10 registros
            if (actualizados + 1) % 10 == 0:
                print(f"   📊 Procesados: {actualizados + 1}/{total}")
        
        self.save_data()
        
        print(f"\n✅ Sincronización completada:")
        print(f"   📊 Registros procesados: {total}")
        print(f"   🎯 Nuevos completados: {nuevos_completados}")
        print(f"   🔄 Total actualizados: {actualizados}")
    
    def debug_botpress_data(self):
        """Función de debug para verificar datos de Botpress"""
        print("🔍 DEBUG: Verificando datos de Botpress...")
        
        # Primero, explorar la estructura de la API
        print("\n🔍 Explorando endpoints disponibles...")
        
        # Intentar listar todas las filas de la tabla
        try:
            response = requests.get(
                f"{self.tables_base_url}/{self.progress_table_name}",
                headers=self.tables_headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ GET /rows funcionó: {len(data.get('rows', []))} filas encontradas")
                
                # Mostrar las primeras filas
                rows = data.get('rows', [])
                for i, row in enumerate(rows[:3]):  # Solo las primeras 3
                    client_num = row.get('clientNumber', 'N/A')
                    print(f"   Fila {i+1}: clientNumber = {client_num}")
                    if 'session1' in row:
                        print(f"      session1 = {row['session1']}")
                
                # Intentar buscar usuario específico
                usuarios_enviados = self.df[self.df['intentos_envio'] > 0]['numero'].unique()
                if len(usuarios_enviados) > 0:
                    numero_test = usuarios_enviados[0]
                    print(f"\n🔍 Buscando usuario {numero_test} en las filas...")
                    
                    for row in rows:
                        if str(row.get('clientNumber')) == str(numero_test):
                            print(f"   ✅ Usuario {numero_test} encontrado!")
                            print(f"   session1: {row.get('session1', 'N/A')}")
                            return row
                    
                    print(f"   ❌ Usuario {numero_test} no encontrado en las filas")
                    
            else:
                print(f"❌ GET /rows falló: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"❌ Error explorando: {e}")
        
        # Probar el método original
        print("\n🔍 Probando método original...")
        usuarios_enviados = self.df[self.df['intentos_envio'] > 0]['numero'].unique()
        
        if len(usuarios_enviados) > 0:
            numero_test = usuarios_enviados[0]
            print(f"   Probando get_user_progress para {numero_test}...")
            progress_data = self.get_user_progress(numero_test)
            
            if progress_data:
                print(f"   ✅ Datos obtenidos: {progress_data}")
            else:
                print(f"   ❌ No se pudieron obtener datos")
    
    def corregir_contadores_intentos(self):
        """Corregir contadores de intentos para registros enviados previamente"""
        print("🔧 Corrigiendo contadores de intentos para envíos previos...")
        
        # Encontrar registros que fueron enviados pero tienen intentos_envio = 0
        registros_corregir = self.df[(self.df['enviado'] == 1) & (self.df['intentos_envio'] == 0)]
        total = len(registros_corregir)
        
        if total == 0:
            print("✅ No hay registros que necesiten corrección")
            return
        
        print(f"📊 Corrigiendo {total} registros...")
        
        for index, row in registros_corregir.iterrows():
            # Marcar como 1 intento los registros que ya fueron enviados
            self.df.at[index, 'intentos_envio'] = 1
        
        self.save_data()
        
        print(f"✅ Corrección completada:")
        print(f"   📊 Registros corregidos: {total}")
        print(f"   🔄 Ahora muestran 1 intento de envío")
    
    def verificar_conexion_botpress(self):
        """Verificar la conexión con la API de Botpress Tables"""
        try:
            response = requests.get(
                f"{self.tables_base_url}",
                headers=self.tables_headers
            )
            
            if response.status_code == 200:
                print("✅ Conexión con Botpress Tables exitosa")
                tables = response.json().get('tables', [])
                print(f"   📊 Tablas disponibles: {len(tables)}")
                
                # Verificar si existe la tabla de progreso
                table_names = [table.get('name') for table in tables]
                if self.progress_table_name in table_names:
                    print(f"   ✅ Tabla de progreso encontrada: {self.progress_table_name}")
                else:
                    print(f"   ⚠️  Tabla de progreso no encontrada: {self.progress_table_name}")
                    print(f"   📋 Tablas disponibles: {', '.join(table_names)}")
                
                return True
            else:
                print(f"❌ Error de conexión: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error verificando conexión: {e}")
            return False

# Funciones de utilidad
def generar_csv_completo(numeros_telefono, archivo='control_envios.csv'):
    """Generar CSV completo con todas las combinaciones"""
    datos = []
    
    for numero in numeros_telefono:
        for sesion in range(1, 7):  # Sesiones 1-6
            for day in range(1, 6):  # Días 1-5
                datos.append({
                    'numero': str(numero),
                    'sesion': sesion,
                    'day': day,
                    'enviado': 0,
                    'fecha_envio': '',
                    'resultado': '',
                    'completado': 0,  # 0=no completado, 1=completado
                    'intentos_envio': 0,  # contador de envíos realizados
                    'fecha_completado': '',  # cuándo se completó
                    'ultimo_estado_botpress': 0  # último estado consultado en botpress
                })
    
    df = pd.DataFrame(datos)
    df.to_csv(archivo, index=False)
    print(f"✅ CSV generado: {archivo} con {len(df)} registros")

# Configuración - DEBES COMPLETAR ESTOS VALORES
BOTPRESS_TOKEN = "TU_TOKEN_PERSONAL_AQUI"  # Obtener de tu perfil en Botpress
BOT_ID = "TU_BOT_ID_AQUI"  # Obtener de la URL de tu bot

# Ejemplo de uso
if __name__ == "__main__":
    # Crear controlador con autenticación de Botpress
    bot = BotpressController('control_envios.csv')
    
    # Mostrar menú
    while True:
        print(f"\n🤖 CONTROL DE ENVÍOS BOTPRESS CON VALIDACIÓN")
        print("1. Verificar conexión con Botpress")
        print("2. Ver estadísticas")
        print("3. Procesar TODOS los pendientes (CON VALIDACIÓN)")
        print("4. Procesar sesión/día específico (CON VALIDACIÓN)")
        print("5. Procesar cantidad limitada (CON VALIDACIÓN)")
        print("6. Resetear envíos")
        print("7. Sincronizar completados con Botpress")
        print("8. Corregir contadores de intentos")
        print("9. Debug datos Botpress")
        print("10. Salir")
        
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            bot.verificar_conexion_botpress()
        
        elif opcion == "2":
            bot.mostrar_estadisticas()
        
        elif opcion == "3":
            bot.procesar_con_validacion()
        
        elif opcion == "4":
            try:
                sesion = int(input("Sesión (1-6): "))
                day = int(input("Día (1-5): "))
                bot.procesar_sesion_dia_con_validacion(sesion, day)
            except ValueError:
                print("❌ Por favor ingresa números válidos")
        
        elif opcion == "5":
            try:
                limite = int(input("Cantidad a procesar: "))
                bot.procesar_con_validacion(limite)
            except ValueError:
                print("❌ Por favor ingresa un número válido")
        
        elif opcion == "6":
            bot.resetear_envios()
        
        elif opcion == "7":
            bot.sincronizar_completados()
        
        elif opcion == "8":
            bot.corregir_contadores_intentos()
        
        elif opcion == "9":
            bot.debug_botpress_data()
        
        elif opcion == "10":
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")