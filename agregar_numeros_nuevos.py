#!/usr/bin/env python3
"""
Script para agregar números nuevos al CSV de control manteniendo el progreso existente.
Los números nuevos empiezan desde sesión 1, día 1.
Los números existentes mantienen su progreso actual.
"""

import pandas as pd
import sys
import os
from datetime import datetime

class AgregarNumerosNuevos:
    def __init__(self, csv_control='control_envios.csv', xlsx_numeros='botNumbers_test.xlsx'):
        self.csv_control = csv_control
        self.xlsx_numeros = xlsx_numeros
        self.df_actual = None
        self.df_nuevos_usuarios = None
        
    def cargar_datos_actuales(self):
        """Cargar CSV de control actual"""
        try:
            if os.path.exists(self.csv_control):
                self.df_actual = pd.read_csv(self.csv_control, dtype={'numero': str})
                print(f"✅ CSV actual cargado: {len(self.df_actual)} registros")
                usuarios_actuales = self.df_actual['numero'].nunique()
                print(f"   👥 Usuarios actuales: {usuarios_actuales}")
            else:
                print(f"ℹ️  No existe {self.csv_control}, se creará uno nuevo")
                self.df_actual = pd.DataFrame()
        except Exception as e:
            print(f"❌ Error cargando CSV actual: {e}")
            sys.exit(1)
    
    def cargar_usuarios_xlsx(self):
        """Cargar usuarios desde XLSX"""
        try:
            if not os.path.exists(self.xlsx_numeros):
                print(f"❌ Error: No se encontró {self.xlsx_numeros}")
                sys.exit(1)
                
            self.df_nuevos_usuarios = pd.read_excel(self.xlsx_numeros)
            self.df_nuevos_usuarios['numero'] = self.df_nuevos_usuarios['numero'].astype(str)
            
            print(f"✅ XLSX cargado: {len(self.df_nuevos_usuarios)} usuarios")
            
            # Validar columnas
            required_cols = ['numero', 'location', 'location_name', 'salon']
            missing_cols = [col for col in required_cols if col not in self.df_nuevos_usuarios.columns]
            
            if missing_cols:
                print(f"❌ Columnas faltantes en XLSX: {missing_cols}")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error cargando XLSX: {e}")
            sys.exit(1)
    
    def identificar_numeros_nuevos(self):
        """Identificar qué números son nuevos"""
        if len(self.df_actual) == 0:
            # Si no hay CSV actual, todos son nuevos
            numeros_nuevos = set(self.df_nuevos_usuarios['numero'].unique())
            numeros_existentes = set()
        else:
            numeros_xlsx = set(self.df_nuevos_usuarios['numero'].unique())
            numeros_csv = set(self.df_actual['numero'].unique())
            
            numeros_nuevos = numeros_xlsx - numeros_csv
            numeros_existentes = numeros_xlsx & numeros_csv
            
            # Números que se removieron del XLSX
            numeros_removidos = numeros_csv - numeros_xlsx
        
        print(f"\n📊 ANÁLISIS DE NÚMEROS:")
        print(f"   🆕 Números nuevos: {len(numeros_nuevos)}")
        print(f"   ♻️  Números existentes: {len(numeros_existentes)}")
        
        if len(self.df_actual) > 0:
            numeros_removidos = set(self.df_actual['numero'].unique()) - set(self.df_nuevos_usuarios['numero'].unique())
            if numeros_removidos:
                print(f"   🗑️  Números removidos del XLSX: {len(numeros_removidos)}")
                for num in sorted(numeros_removidos):
                    print(f"      📱 {num}")
        
        if numeros_nuevos:
            print(f"\n🆕 NUEVOS NÚMEROS A AGREGAR:")
            for numero in sorted(numeros_nuevos):
                usuario = self.df_nuevos_usuarios[self.df_nuevos_usuarios['numero'] == numero].iloc[0]
                print(f"   📱 {numero} ({usuario['location']} - {usuario['location_name']}, {usuario['salon']})")
        
        return numeros_nuevos, numeros_existentes
    
    def generar_registros_nuevos(self, numeros_nuevos):
        """Generar registros para números nuevos (empiezan en sesión 1, día 1)"""
        registros_nuevos = []
        
        for numero in numeros_nuevos:
            # Obtener datos de ubicación del XLSX
            usuario_data = self.df_nuevos_usuarios[self.df_nuevos_usuarios['numero'] == numero].iloc[0]
            
            for sesion in range(1, 7):  # Sesiones 1-6
                for day in range(1, 6):  # Días 1-5
                    registros_nuevos.append({
                        'numero': numero,
                        'location': usuario_data['location'],
                        'location_name': usuario_data['location_name'], 
                        'salon': usuario_data['salon'],
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
        
        return pd.DataFrame(registros_nuevos)
    
    def actualizar_datos_existentes(self, numeros_existentes):
        """Actualizar datos de ubicación para números existentes (mantener progreso)"""
        if len(self.df_actual) == 0:
            return pd.DataFrame()
            
        print(f"\n🔄 Actualizando datos de ubicación para números existentes...")
        
        for numero in numeros_existentes:
            # Obtener nuevos datos de ubicación del XLSX
            usuario_data = self.df_nuevos_usuarios[self.df_nuevos_usuarios['numero'] == numero].iloc[0]
            
            # Actualizar en df_actual
            mask = self.df_actual['numero'] == numero
            self.df_actual.loc[mask, 'location'] = usuario_data['location']
            self.df_actual.loc[mask, 'location_name'] = usuario_data['location_name']
            self.df_actual.loc[mask, 'salon'] = usuario_data['salon']
            
            print(f"   ✅ {numero}: {usuario_data['location']} - {usuario_data['location_name']}, {usuario_data['salon']}")
        
        return self.df_actual
    
    def procesar_actualizacion(self):
        """Proceso principal de actualización"""
        print("🔄 AGREGAR NÚMEROS NUEVOS AL CSV DE CONTROL")
        print("=" * 60)
        
        # Cargar datos
        self.cargar_datos_actuales()
        self.cargar_usuarios_xlsx()
        
        # Identificar cambios
        numeros_nuevos, numeros_existentes = self.identificar_numeros_nuevos()
        
        if len(numeros_nuevos) == 0 and len(numeros_existentes) == len(self.df_actual['numero'].unique() if len(self.df_actual) > 0 else []):
            print("\n✅ No hay cambios que aplicar")
            return False
        
        # Confirmar con usuario
        if numeros_nuevos:
            print(f"\n⚠️  Se agregarán {len(numeros_nuevos)} números nuevos")
        if numeros_existentes:
            print(f"   Se mantendrán {len(numeros_existentes)} números existentes con su progreso")
            
        confirmar = input("\n¿Continuar con la actualización? (s/N): ").strip().lower()
        if not confirmar.startswith('s'):
            print("❌ Operación cancelada")
            return False
        
        # Procesar cambios
        df_final = pd.DataFrame()
        
        # 1. Mantener registros existentes con datos actualizados
        if len(numeros_existentes) > 0:
            df_existentes = self.actualizar_datos_existentes(numeros_existentes)
            if len(df_existentes) > 0:
                df_final = pd.concat([df_final, df_existentes], ignore_index=True)
        
        # 2. Agregar números nuevos
        if numeros_nuevos:
            print(f"\n🆕 Generando registros para {len(numeros_nuevos)} números nuevos...")
            df_nuevos = self.generar_registros_nuevos(numeros_nuevos)
            df_final = pd.concat([df_final, df_nuevos], ignore_index=True)
            print(f"   ✅ {len(df_nuevos)} registros nuevos generados")
        
        # Backup del archivo anterior
        if os.path.exists(self.csv_control):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.csv_control}.backup_{timestamp}"
            os.rename(self.csv_control, backup_file)
            print(f"\n💾 Backup creado: {backup_file}")
        
        # Guardar CSV actualizado
        df_final.to_csv(self.csv_control, index=False)
        
        print(f"\n🎉 CSV ACTUALIZADO EXITOSAMENTE!")
        print(f"   📄 Archivo: {self.csv_control}")
        print(f"   📊 Total registros: {len(df_final)}")
        print(f"   👥 Total usuarios: {df_final['numero'].nunique()}")
        
        # Resumen final
        if numeros_nuevos:
            registros_nuevos = len(numeros_nuevos) * 30  # 6 sesiones * 5 días
            print(f"   🆕 {len(numeros_nuevos)} usuarios nuevos ({registros_nuevos} registros)")
        
        if numeros_existentes:
            print(f"   ♻️  {len(numeros_existentes)} usuarios existentes (progreso mantenido)")
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Agregar números nuevos al CSV de control')
    parser.add_argument('--csv', default='control_envios.csv', help='Archivo CSV de control')
    parser.add_argument('--xlsx', default='botNumbers_test.xlsx', help='Archivo XLSX con usuarios')
    
    args = parser.parse_args()
    
    actualizador = AgregarNumerosNuevos(args.csv, args.xlsx)
    actualizador.procesar_actualizacion()

if __name__ == "__main__":
    main()