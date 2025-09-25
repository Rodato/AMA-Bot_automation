#!/usr/bin/env python3
"""
Script optimizado para ejecutar en GitHub Actions
Versión automatizada del AMA Bot Controller
"""
import pandas as pd
import requests
import time
import json
from datetime import datetime
import sys
import os

class AMABotGitHubRunner:
    def __init__(self, csv_file='control_envios.csv'):
        self.csv_file = csv_file
        
        # Configuración para webhook (envíos) - desde variables de entorno
        self.webhook_url = os.getenv('WEBHOOK_URL', 'https://webhook.botpress.cloud/2d63c736-0910-47a8-b06a-c82c12372106')
        self.webhook_headers = {
            "x-bp-secret": os.getenv('WEBHOOK_SECRET', '73c380fc550ad6b061d4d8ec3547731eprod'),
            "Content-Type": "application/json"
        }
        
        # Configuración para Tables API (consultas) - desde variables de entorno
        self.botpress_token = os.getenv('BOTPRESS_TOKEN', 'bp_pat_t3Qzk5mKulbKTudzrZHEJ2Rjqkb6z9f6qrw9')
        self.bot_id = os.getenv('BOT_ID', 'f70c360d-ed8d-402f-9cd2-488d9f1d358c')
        self.tables_base_url = "https://api.botpress.cloud/v1/tables"
        self.progress_table_name = os.getenv('PROGRESS_TABLE_NAME', 'DataJsonProgressTable')
        self.tables_headers = {
            "Authorization": f"Bearer {self.botpress_token}",
            "x-bot-id": self.bot_id,
            "Content-Type": "application/json"
        }
        
        self.df = None
        self.botpress_data = {}
        
    def log(self, message):
        """Log con timestamp"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")
        
    def load_data(self):
        """Cargar datos del CSV de control"""
        try:
            if not os.path.exists(self.csv_file):
                self.log(f"❌ Archivo {self.csv_file} no existe")
                return False
                
            self.df = pd.read_csv(self.csv_file, dtype={'numero': str})
            
            # Agregar nuevas columnas si no existen (compatibilidad con CSVs antiguos)
            required_columns = {
                'reenvios_consecutivos_fallidos': 0,  # Contador de reenvíos fallidos seguidos
                'usuario_excluido': 0  # 1 = excluido permanentemente, 0 = activo
            }
            
            for col, default_value in required_columns.items():
                if col not in self.df.columns:
                    self.df[col] = default_value
                    self.log(f"➕ Columna agregada: {col}")
            
            self.log(f"✅ CSV cargado: {len(self.df)} registros")
            return True
        except Exception as e:
            self.log(f"❌ Error cargando CSV: {e}")
            return False
    
    def save_data(self):
        """Guardar cambios en el CSV"""
        try:
            self.df.to_csv(self.csv_file, index=False)
            self.log("💾 CSV guardado correctamente")
            return True
        except Exception as e:
            self.log(f"❌ Error guardando CSV: {e}")
            return False
    
    def refresh_botpress_data(self):
        """Obtener datos frescos de Botpress"""
        self.log("🔄 Consultando datos de Botpress...")
        
        try:
            response = requests.post(
                f"{self.tables_base_url}/{self.progress_table_name}/rows/find",
                headers=self.tables_headers,
                json={"limit": 1000},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'rows' in data and isinstance(data['rows'], list):
                    rows = data['rows']
                    self.log(f"✅ Datos Botpress: {len(rows)} usuarios")
                    
                    # Crear diccionario para acceso rápido
                    self.botpress_data = {}
                    for row in rows:
                        client_num = str(row.get('clientNumber', ''))
                        self.botpress_data[client_num] = row
                    
                    # Sincronizar con CSV local
                    self.sync_with_botpress_data()
                    return True
                else:
                    self.log("⚠️ No se encontraron datos en respuesta Botpress")
                    return False
            else:
                self.log(f"❌ Error API Botpress: {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"❌ Error consultando Botpress: {e}")
            return False
    
    def sync_with_botpress_data(self):
        """Sincronizar estado del CSV con datos de Botpress"""
        self.log("🔄 Sincronizando con datos de Botpress...")
        
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
                    
                    # Actualizar estado
                    self.df.at[index, 'ultimo_estado_botpress'] = int(day_status) if day_status.isdigit() else 0
                    
                    # Si completó y no estaba marcado
                    if day_status == '2' and row['completado'] == 0:
                        self.df.at[index, 'completado'] = 1
                        self.df.at[index, 'fecha_completado'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        nuevos_completados += 1
                        self.log(f"   ✅ Completado: {numero} S{sesion}D{day}")
                    
                    actualizados += 1
        
        self.log(f"   🔄 Sincronizados: {actualizados}, ✅ Completados: {nuevos_completados}")
    
    def can_send_message(self, numero, sesion, day, csv_row):
        """Verificar si se puede enviar mensaje"""
        
        # Verificar si usuario está excluido permanentemente
        if csv_row['usuario_excluido'] == 1:
            return False, "Usuario excluido permanentemente"
        
        # Verificar límite de intentos por día
        if csv_row['intentos_envio'] >= 2:
            return False, f"Límite intentos diarios ({csv_row['intentos_envio']}/2)"
        
        # Si ya completó, no reenviar
        if csv_row['completado'] == 1:
            return False, "Ya completado"
        
        # Sesión 1, Día 1 siempre se permite (primer contacto)
        if sesion == 1 and day == 1:
            return True, "Inicio campaña"
        
        # Verificar prerrequisitos en Botpress
        numero_str = str(numero)
        if numero_str not in self.botpress_data:
            return False, "Usuario no en Botpress"
        
        botpress_row = self.botpress_data[numero_str]
        session1_data = botpress_row.get('session1', {})
        
        if not isinstance(session1_data, dict):
            return False, "Datos sesión inválidos"
        
        # Para días posteriores en sesión 1
        if sesion == 1 and day > 1:
            # Si es un reenvío del mismo día (no completado)
            current_day_status = str(session1_data.get(str(day), '0'))
            if current_day_status == '1':  # Enviado pero no completado
                return True, f"Reenvío día {day} (intento {csv_row['intentos_envio']+1}/2)"
            
            # Si es un día nuevo, verificar prerrequisito
            prev_day_status = str(session1_data.get(str(day - 1), '0'))
            if prev_day_status == '2':
                return True, f"Día {day-1} completado"
            else:
                return False, f"Día {day-1} no completado ({prev_day_status})"
        
        # Sesiones posteriores (futuro)
        if sesion > 1:
            return False, "Sesiones >1 pendientes"
        
        return True, "Condiciones OK"
    
    def manejar_reenvios_fallidos(self):
        """Manejar lógica de reenvíos consecutivos fallidos"""
        self.log("🔄 Verificando reenvíos consecutivos fallidos...")
        
        usuarios_excluidos = 0
        
        # Procesar por usuario
        for numero in self.df['numero'].unique():
            registros_usuario = self.df[self.df['numero'] == numero].sort_values(['sesion', 'day'])
            
            reenvios_consecutivos = 0
            usuario_debe_excluirse = False
            
            for index, registro in registros_usuario.iterrows():
                # Solo procesar registros que han sido enviados
                if registro['intentos_envio'] == 0:
                    continue
                
                # Si completó este día, resetear contador
                if registro['completado'] == 1:
                    reenvios_consecutivos = 0
                    self.df.at[index, 'reenvios_consecutivos_fallidos'] = 0
                
                # Si es un segundo intento (reenvío) y no completó
                elif registro['intentos_envio'] == 2 and registro['completado'] == 0:
                    reenvios_consecutivos += 1
                    self.df.at[index, 'reenvios_consecutivos_fallidos'] = reenvios_consecutivos
                    
                    # Si llegó a 2 reenvíos fallidos consecutivos
                    if reenvios_consecutivos >= 2:
                        usuario_debe_excluirse = True
                        self.log(f"   🚫 Usuario {numero} excluido tras 2 reenvíos fallidos")
                        break
            
            # Excluir usuario si corresponde
            if usuario_debe_excluirse:
                self.df.loc[self.df['numero'] == numero, 'usuario_excluido'] = 1
                usuarios_excluidos += 1
        
        if usuarios_excluidos > 0:
            self.log(f"   🚫 {usuarios_excluidos} usuarios excluidos permanentemente")
        else:
            self.log(f"   ✅ No hay usuarios para excluir")
    
    def enviar_mensaje(self, numero, sesion, day):
        """Enviar mensaje via webhook"""
        data = {
            "clientNumber": int(numero),
            "session": int(sesion),
            "day": int(day)
        }
        
        try:
            response = requests.post(
                self.webhook_url, 
                headers=self.webhook_headers, 
                json=data,
                timeout=15
            )
            return response.status_code == 200, response.status_code, response.text
        except Exception as e:
            return False, 0, str(e)
    
    def procesar_envios_automatico(self):
        """Procesar envíos en modo automático (GitHub Actions)"""
        self.log("🚀 INICIANDO PROCESAMIENTO AUTOMÁTICO")
        self.log("=" * 60)
        
        # 1. Cargar datos
        if not self.load_data():
            self.log("❌ Error cargando datos. Terminando.")
            return False
        
        # 2. Actualizar desde Botpress
        if not self.refresh_botpress_data():
            self.log("⚠️ No se pudieron actualizar datos de Botpress")
            # Continuar sin datos de Botpress
        
        # 3. Filtrar registros pendientes (incluir reenvíos, excluir usuarios eliminados)
        condicion_pendientes = (
            (self.df['usuario_excluido'] == 0) &  # No excluidos
            (
                (self.df['enviado'] == 0) |  # Nunca enviados
                (
                    (self.df['enviado'] == 1) &  # Ya enviados pero...
                    (self.df['completado'] == 0) &  # No completados y...
                    (self.df['intentos_envio'] < 2)  # Con menos de 2 intentos por día
                )
            )
        )
        pendientes = self.df[condicion_pendientes]
        
        if len(pendientes) == 0:
            self.log("✅ No hay envíos pendientes (incluidos reenvíos)")
            return True
        
        self.log(f"📤 Procesando {len(pendientes)} registros pendientes (incluidos reenvíos)...")
        
        exitosos = 0
        fallidos = 0
        omitidos = 0
        enviados_detalle = []
        
        # 4. Procesar cada registro
        for index, row in pendientes.iterrows():
            numero = row['numero']
            sesion = row['sesion']
            day = row['day']
            
            self.log(f"📞 Evaluando: {numero} S{sesion}D{day}")
            
            # Verificar si se puede enviar
            can_send, reason = self.can_send_message(numero, sesion, day, row)
            
            if not can_send:
                self.log(f"   ⏭️ Omitido: {reason}")
                self.df.at[index, 'resultado'] = f"Omitido: {reason}"
                omitidos += 1
                continue
            
            self.log(f"   ✅ Validado: {reason}")
            
            # Incrementar intentos
            self.df.at[index, 'intentos_envio'] = self.df.at[index, 'intentos_envio'] + 1
            
            # Enviar mensaje
            exito, status_code, respuesta = self.enviar_mensaje(numero, sesion, day)
            
            # Actualizar registro
            self.df.at[index, 'enviado'] = 1 if exito else 0
            self.df.at[index, 'fecha_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.df.at[index, 'resultado'] = f"Status: {status_code} (Intento {self.df.at[index, 'intentos_envio']})"
            
            if exito:
                self.log(f"   ✅ Enviado exitosamente")
                exitosos += 1
                enviados_detalle.append({
                    'numero': numero,
                    'sesion': sesion,
                    'day': day,
                    'intento': self.df.at[index, 'intentos_envio']
                })
            else:
                self.log(f"   ❌ Error: {status_code}")
                fallidos += 1
            
            # Pausa entre envíos
            time.sleep(2)
        
        # 5. Guardar cambios
        if not self.save_data():
            self.log("❌ Error guardando datos")
            return False
        
        # 6. Actualizar datos post-envío y manejar reenvíos consecutivos
        self.log("🔄 Actualizando progreso post-envío...")
        self.refresh_botpress_data()
        
        # 7. Verificar reenvíos consecutivos fallidos y excluir usuarios
        self.manejar_reenvios_fallidos()
        
        self.save_data()
        
        # 7. Reporte final
        self.log("📊 RESUMEN DE ENVÍOS:")
        self.log(f"   ✅ Exitosos: {exitosos}")
        self.log(f"   ❌ Fallidos: {fallidos}")
        self.log(f"   ⏭️ Omitidos: {omitidos}")
        self.log(f"   📋 Total: {exitosos + fallidos + omitidos}")
        
        if enviados_detalle:
            self.log("📋 ENVÍOS EXITOSOS:")
            for envio in enviados_detalle:
                self.log(f"   📞 {envio['numero']} → S{envio['sesion']}D{envio['day']}")
        
        self.log("=" * 60)
        self.log("✅ PROCESAMIENTO COMPLETADO")
        
        return True

def main():
    """Función principal para GitHub Actions"""
    runner = AMABotGitHubRunner('control_envios.csv')
    
    try:
        success = runner.procesar_envios_automatico()
        if success:
            print("🎉 Ejecución exitosa")
            sys.exit(0)
        else:
            print("❌ Ejecución falló")
            sys.exit(1)
    except Exception as e:
        print(f"💥 Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()