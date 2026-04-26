#!/usr/bin/env python3
"""
Script para actualizar todas las referencias a roles obsoletos en el código
"""

import os
import re
from pathlib import Path

def update_role_references():
    """
    Actualiza todas las referencias a roles obsoletos por los nuevos roles ACL
    """
    
    # Mapeo de roles obsoletos a nuevos roles
    role_mapping = {
        'UserRole.ADMIN': 'UserRole.ADMINISTRADOR',
        'UserRole.NOC': 'UserRole.OPERATIVO', 
        'UserRole.INFRASTRUCTURE': 'UserRole.OPERATIVO',
        'UserRole.ENGINEERING': 'UserRole.OPERATIVO',
        'UserRole.LEGAL': 'UserRole.JURIDICO',
        'UserRole.COMMERCIAL': 'UserRole.FINANCIERO'
    }
    
    # Archivos a actualizar
    files_to_update = [
        './db/seed.py',
        './auth/firebase.py', 
        './auth/router.py',
        './auth/utils.py',
        './api/access/router.py',
        './api/search/router.py',
        './api/incident/router.py'
    ]
    
    for file_path in files_to_update:
        if not os.path.exists(file_path):
            print(f"⚠️  Archivo no encontrado: {file_path}")
            continue
            
        try:
            # Leer contenido del archivo
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Aplicar reemplazos
            for old_role, new_role in role_mapping.items():
                content = content.replace(old_role, new_role)
            
            # Solo escribir si hubo cambios
            if content != original_content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ Actualizado: {file_path}")
            else:
                print(f"ℹ️  Sin cambios: {file_path}")
                
        except Exception as e:
            print(f"❌ Error procesando {file_path}: {str(e)}")

if __name__ == "__main__":
    print("🚀 Actualizando referencias a roles obsoletos...")
    update_role_references()
    print("✅ Proceso completado")