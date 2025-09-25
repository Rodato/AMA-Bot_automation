#!/usr/bin/env python3
"""
Script de monitoreo por ubicaciones para AMA Bot
Permite analizar el rendimiento de envíos y completados por location/salon
"""

import pandas as pd
import sys
from datetime import datetime, timedelta
import os

class MonitorUbicaciones:
    def __init__(self, csv_file='control_envios.csv'):
        self.csv_file = csv_file
        self.df = None
        self.load_data()
    
    def load_data(self):
        """Cargar datos del CSV de control"""
        try:
            self.df = pd.read_csv(self.csv_file, dtype={'numero': str})
            print(f"✅ CSV cargado: {len(self.df)} registros")
            
            if 'location' not in self.df.columns:
                print("❌ Error: CSV no tiene columnas de ubicación")
                print("💡 Regenera el CSV usando csvNumbersGenerator.py")
                sys.exit(1)
                
        except FileNotFoundError:
            print(f"❌ Error: No se encontró {self.csv_file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    def reporte_general_ubicaciones(self):
        """Generar reporte general por ubicaciones"""
        print("\n📊 REPORTE GENERAL POR UBICACIONES")
        print("=" * 50)
        
        # Resumen por location/location_name
        ubicaciones = self.df.groupby(['location', 'location_name']).agg({
            'numero': 'nunique',
            'enviado': 'sum',
            'completado': 'sum',
            'intentos_envio': lambda x: (x > 0).sum(),
            'usuario_excluido': 'sum'
        }).reset_index()
        
        ubicaciones.columns = ['location', 'location_name', 'usuarios', 'enviados', 
                              'completados', 'con_intentos', 'excluidos']
        
        for _, row in ubicaciones.iterrows():
            location = row['location']
            location_name = row['location_name']
            usuarios = row['usuarios']
            enviados = row['enviados']
            completados = row['completados']
            con_intentos = row['con_intentos']
            excluidos = row['excluidos']
            
            # Calcular totales para esta ubicación
            registros_total = len(self.df[
                (self.df['location'] == location) & 
                (self.df['location_name'] == location_name)
            ])
            
            tasa_envio = (enviados/registros_total)*100 if registros_total > 0 else 0
            tasa_completado = (completados/con_intentos)*100 if con_intentos > 0 else 0
            tasa_exclusion = (excluidos/usuarios)*100 if usuarios > 0 else 0
            
            print(f"\n📍 {location} - {location_name}")
            print(f"   👥 Usuarios: {usuarios}")
            print(f"   📊 Registros totales: {registros_total}")
            print(f"   📤 Enviados: {enviados} ({tasa_envio:.1f}%)")
            print(f"   ✅ Completados: {completados} ({tasa_completado:.1f}%)")
            print(f"   ❌ Excluidos: {excluidos} usuarios ({tasa_exclusion:.1f}%)")
    
    def reporte_por_salon(self):
        """Reporte detallado por salón"""
        if 'salon' not in self.df.columns:
            return
            
        print("\n🚪 REPORTE POR SALÓN")
        print("=" * 50)
        
        salones = self.df.groupby(['location', 'location_name', 'salon']).agg({
            'numero': 'nunique',
            'enviado': 'sum',
            'completado': 'sum',
            'usuario_excluido': 'sum'
        }).reset_index()
        
        for _, row in salones.iterrows():
            location = row['location']
            location_name = row['location_name'] 
            salon = row['salon']
            usuarios = row['numero']
            enviados = row['enviado']
            completados = row['completado']
            excluidos = row['usuario_excluido']
            
            registros_salon = len(self.df[
                (self.df['location'] == location) &
                (self.df['location_name'] == location_name) &
                (self.df['salon'] == salon)
            ])
            
            tasa_envio = (enviados/registros_salon)*100 if registros_salon > 0 else 0
            tasa_completado = (completados/enviados)*100 if enviados > 0 else 0
            
            print(f"\n🚪 {location} - {location_name} - Salón {salon}")
            print(f"   👥 {usuarios} usuarios")
            print(f"   📤 {enviados} enviados ({tasa_envio:.1f}%)")
            print(f"   ✅ {completados} completados ({tasa_completado:.1f}%)")
            if excluidos > 0:
                print(f"   ❌ {excluidos} excluidos")
    
    def reporte_progreso_sesiones(self):
        """Reporte de progreso por sesión y ubicación"""
        print("\n📅 PROGRESO POR SESIÓN Y UBICACIÓN")
        print("=" * 50)
        
        for sesion in range(1, 7):
            sesion_data = self.df[self.df['sesion'] == sesion]
            if len(sesion_data) == 0:
                continue
                
            print(f"\n📚 SESIÓN {sesion}")
            
            ubicacion_sesion = sesion_data.groupby(['location', 'location_name']).agg({
                'enviado': 'sum',
                'completado': 'sum',
                'numero': 'nunique'
            }).reset_index()
            
            for _, row in ubicacion_sesion.iterrows():
                location = row['location']
                location_name = row['location_name']
                enviados = row['enviado']
                completados = row['completado']
                usuarios = row['numero']
                
                registros_esperados = usuarios * 5  # 5 días por sesión
                progreso = (enviados/registros_esperados)*100 if registros_esperados > 0 else 0
                completado_rate = (completados/enviados)*100 if enviados > 0 else 0
                
                print(f"   📍 {location} - {location_name}:")
                print(f"      📤 {enviados}/{registros_esperados} enviados ({progreso:.1f}%)")
                print(f"      ✅ {completados} completados ({completado_rate:.1f}%)")
    
    def usuarios_problemáticos(self):
        """Identificar usuarios con problemas"""
        print("\n⚠️  USUARIOS PROBLEMÁTICOS")
        print("=" * 50)
        
        # Usuarios excluidos
        excluidos = self.df[self.df['usuario_excluido'] == 1].groupby(
            ['numero', 'location', 'location_name', 'salon']
        ).first().reset_index()
        
        if len(excluidos) > 0:
            print("\n❌ USUARIOS EXCLUIDOS:")
            for _, row in excluidos.iterrows():
                print(f"   📱 {row['numero']} ({row['location']} - {row['location_name']}, {row['salon']})")
        
        # Usuarios con muchos reenvíos fallidos
        problemas = self.df[self.df['reenvios_consecutivos_fallidos'] > 1].groupby(
            ['numero', 'location', 'location_name', 'salon']
        )['reenvios_consecutivos_fallidos'].max().reset_index()
        
        if len(problemas) > 0:
            print(f"\n🔄 USUARIOS CON REENVÍOS FALLIDOS:")
            for _, row in problemas.iterrows():
                print(f"   📱 {row['numero']} - {row['reenvios_consecutivos_fallidos']} fallos "
                      f"({row['location']} - {row['location_name']}, {row['salon']})")
        
        # Usuarios sin progreso en sesión 1
        sin_progreso = self.df[
            (self.df['sesion'] == 1) & 
            (self.df['intentos_envio'] > 0) & 
            (self.df['completado'] == 0)
        ].groupby(['numero', 'location', 'location_name', 'salon']).size().reset_index()
        
        if len(sin_progreso) > 0:
            print(f"\n⏳ USUARIOS SIN COMPLETAR SESIÓN 1:")
            for _, row in sin_progreso.iterrows():
                print(f"   📱 {row['numero']} ({row['location']} - {row['location_name']}, {row['salon']})")
    
    def exportar_reporte_excel(self, filename=None):
        """Exportar reporte completo a Excel"""
        if filename is None:
            fecha = datetime.now().strftime('%Y%m%d_%H%M')
            filename = f'reporte_ubicaciones_{fecha}.xlsx'
        
        print(f"\n📄 Exportando reporte a {filename}...")
        
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Hoja 1: Resumen por ubicación
            ubicaciones = self.df.groupby(['location', 'location_name']).agg({
                'numero': 'nunique',
                'enviado': 'sum',
                'completado': 'sum',
                'intentos_envio': lambda x: (x > 0).sum(),
                'usuario_excluido': 'sum'
            }).reset_index()
            ubicaciones.columns = ['Location', 'Location_Name', 'Usuarios', 'Enviados', 
                                 'Completados', 'Con_Intentos', 'Excluidos']
            ubicaciones.to_excel(writer, sheet_name='Resumen_Ubicaciones', index=False)
            
            # Hoja 2: Detalle por salón
            if 'salon' in self.df.columns:
                salones = self.df.groupby(['location', 'location_name', 'salon']).agg({
                    'numero': 'nunique',
                    'enviado': 'sum',
                    'completado': 'sum',
                    'usuario_excluido': 'sum'
                }).reset_index()
                salones.columns = ['Location', 'Location_Name', 'Salon', 'Usuarios', 
                                 'Enviados', 'Completados', 'Excluidos']
                salones.to_excel(writer, sheet_name='Detalle_Salones', index=False)
            
            # Hoja 3: Progreso por sesión
            sesiones = self.df.groupby(['location', 'location_name', 'sesion']).agg({
                'enviado': 'sum',
                'completado': 'sum',
                'numero': 'nunique'
            }).reset_index()
            sesiones.columns = ['Location', 'Location_Name', 'Sesion', 'Enviados', 
                               'Completados', 'Usuarios']
            sesiones.to_excel(writer, sheet_name='Progreso_Sesiones', index=False)
            
            # Hoja 4: Usuarios problemáticos
            problemas = self.df[
                (self.df['usuario_excluido'] == 1) | 
                (self.df['reenvios_consecutivos_fallidos'] > 1)
            ][['numero', 'location', 'location_name', 'salon', 'sesion', 'day',
               'usuario_excluido', 'reenvios_consecutivos_fallidos', 'resultado']].copy()
            
            if len(problemas) > 0:
                problemas.to_excel(writer, sheet_name='Usuarios_Problematicos', index=False)
        
        print(f"✅ Reporte exportado: {filename}")
        return filename
    
    def ejecutar_reporte_completo(self, exportar=True):
        """Ejecutar reporte completo"""
        print("🏫 MONITOR DE UBICACIONES - AMA BOT")
        print("=" * 60)
        
        self.reporte_general_ubicaciones()
        self.reporte_por_salon()
        self.reporte_progreso_sesiones()
        self.usuarios_problemáticos()
        
        if exportar:
            self.exportar_reporte_excel()

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Monitor de ubicaciones AMA Bot')
    parser.add_argument('--csv', default='control_envios.csv', help='Archivo CSV de control')
    parser.add_argument('--no-excel', action='store_true', help='No exportar a Excel')
    
    args = parser.parse_args()
    
    monitor = MonitorUbicaciones(args.csv)
    monitor.ejecutar_reporte_completo(exportar=not args.no_excel)