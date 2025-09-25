import pandas as pd
import requests
import time
from datetime import datetime
import sys

class BotpressController:
    def __init__(self, csv_file='control_envios.csv'):
        self.csv_file = csv_file
        self.url = "https://webhook.botpress.cloud/2d63c736-0910-47a8-b06a-c82c12372106"
        self.headers = {
            "x-bp-secret": "73c380fc550ad6b061d4d8ec3547731eprod",
            "Content-Type": "application/json"
        }
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Cargar datos del CSV"""
        try:
            self.df = pd.read_csv(self.csv_file)
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
    
    def enviar_mensaje(self, numero, sesion, day):
        """Enviar mensaje individual"""
        data = {
            "clientNumber": int(numero),
            "session": int(sesion),
            "day": int(day)
        }
        
        try:
            response = requests.post(self.url, headers=self.headers, json=data)
            return response.status_code == 200, response.status_code, response.text
        except Exception as e:
            return False, 0, str(e)
    
    def procesar_pendientes(self, limite=None):
        """Procesar todos los envíos pendientes"""
        pendientes = self.df[self.df['enviado'] == 0]
        
        if len(pendientes) == 0:
            print("✅ No hay envíos pendientes")
            return
        
        if limite:
            pendientes = pendientes.head(limite)
            print(f"📤 Procesando {len(pendientes)} envíos (límite aplicado)")
        else:
            print(f"📤 Procesando {len(pendientes)} envíos pendientes")
        
        exitosos = 0
        fallidos = 0
        
        for index, row in pendientes.iterrows():
            numero = row['numero']
            sesion = row['sesion'] 
            day = row['day']
            
            print(f"📞 Enviando: {numero} - Sesión {sesion}, Día {day}")
            
            exito, status_code, respuesta = self.enviar_mensaje(numero, sesion, day)
            
            # Actualizar registro
            self.df.loc[index, 'enviado'] = 1 if exito else 0
            self.df.loc[index, 'fecha_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.df.loc[index, 'resultado'] = f"Status: {status_code}"
            
            if exito:
                print(f"   ✅ Enviado exitosamente")
                exitosos += 1
            else:
                print(f"   ❌ Error: {status_code} - {respuesta}")
                fallidos += 1
            
            # Pausa entre envíos
            time.sleep(3)
        
        # Guardar cambios
        self.save_data()
        
        print(f"\n📊 Resumen:")
        print(f"   ✅ Exitosos: {exitosos}")
        print(f"   ❌ Fallidos: {fallidos}")
    
    def procesar_sesion_dia(self, sesion, day):
        """Procesar una sesión y día específicos"""
        filtro = (self.df['sesion'] == sesion) & (self.df['day'] == day) & (self.df['enviado'] == 0)
        registros = self.df[filtro]
        
        if len(registros) == 0:
            print(f"✅ No hay pendientes para Sesión {sesion}, Día {day}")
            return
        
        print(f"📤 Procesando Sesión {sesion}, Día {day}: {len(registros)} números")
        
        for index, row in registros.iterrows():
            numero = row['numero']
            print(f"📞 Enviando a: {numero}")
            
            exito, status_code, respuesta = self.enviar_mensaje(numero, sesion, day)
            
            self.df.loc[index, 'enviado'] = 1 if exito else 0
            self.df.loc[index, 'fecha_envio'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.df.loc[index, 'resultado'] = f"Status: {status_code}"
            
            if exito:
                print(f"   ✅ Enviado")
            else:
                print(f"   ❌ Error: {status_code}")
            
            time.sleep(4)
        
        self.save_data()
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas del CSV"""
        total = len(self.df)
        enviados = len(self.df[self.df['enviado'] == 1])
        pendientes = total - enviados
        
        print(f"\n📊 ESTADÍSTICAS:")
        print(f"   Total registros: {total}")
        print(f"   ✅ Enviados: {enviados}")
        print(f"   ⏳ Pendientes: {pendientes}")
        print(f"   📈 Progreso: {(enviados/total)*100:.1f}%")
        
        # Por sesión
        print(f"\n📋 POR SESIÓN:")
        for sesion in range(1, 7):
            sesion_df = self.df[self.df['sesion'] == sesion]
            if len(sesion_df) > 0:
                enviados_sesion = len(sesion_df[sesion_df['enviado'] == 1])
                total_sesion = len(sesion_df)
                print(f"   Sesión {sesion}: {enviados_sesion}/{total_sesion} enviados")
    
    def resetear_envios(self):
        """Resetear todos los envíos (marcar como no enviados)"""
        respuesta = input("⚠️  ¿Estás seguro de resetear TODOS los envíos? (yes/no): ")
        if respuesta.lower() == 'yes':
            self.df['enviado'] = 0
            self.df['fecha_envio'] = ''
            self.df['resultado'] = ''
            self.save_data()
            print("🔄 Todos los envíos han sido reseteados")
        else:
            print("❌ Operación cancelada")

# Funciones de utilidad
def generar_csv_completo(numeros_telefono, archivo='control_envios.csv'):
    """Generar CSV completo con todas las combinaciones"""
    datos = []
    
    for numero in numeros_telefono:
        for sesion in range(1, 7):  # Sesiones 1-6
            for day in range(1, 6):  # Días 1-5
                datos.append({
                    'numero': numero,
                    'sesion': sesion,
                    'day': day,
                    'enviado': 0,
                    'fecha_envio': '',
                    'resultado': ''
                })
    
    df = pd.DataFrame(datos)
    df.to_csv(archivo, index=False)
    print(f"✅ CSV generado: {archivo} con {len(df)} registros")

# Ejemplo de uso
if __name__ == "__main__":
    # Crear controlador
    bot = BotpressController('control_envios.csv')
    
    # Mostrar menú
    while True:
        print(f"\n🤖 CONTROL DE ENVÍOS BOTPRESS")
        print("1. Ver estadísticas")
        print("2. Procesar TODOS los pendientes")
        print("3. Procesar sesión/día específico")
        print("4. Procesar cantidad limitada")
        print("5. Resetear envíos")
        print("6. Salir")
        
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            bot.mostrar_estadisticas()
        
        elif opcion == "2":
            bot.procesar_pendientes()
        
        elif opcion == "3":
            try:
                sesion = int(input("Sesión (1-6): "))
                day = int(input("Día (1-5): "))
                bot.procesar_sesion_dia(sesion, day)
            except ValueError:
                print("❌ Por favor ingresa números válidos")
        
        elif opcion == "4":
            try:
                limite = int(input("Cantidad a procesar: "))
                bot.procesar_pendientes(limite)
            except ValueError:
                print("❌ Por favor ingresa un número válido")
        
        elif opcion == "5":
            bot.resetear_envios()
        
        elif opcion == "6":
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción no válida")