#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess

# Folder paths
TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')

def compile_translations():
    """Compile all translation files (*.po) to binary (*.mo) files."""
    print("Compiling translation files...")
    
    # Walk through all subdirectories in translations
    for root, dirs, files in os.walk(TRANSLATIONS_DIR):
        for file in files:
            if file.endswith('.po'):
                po_file = os.path.join(root, file)
                mo_file = os.path.join(root, 'messages.mo')
                
                try:
                    # Use pybabel directly via command line
                    cmd = ['pybabel', 'compile', '--input-file', po_file, '--output-file', mo_file]
                    print(f"Running: {' '.join(cmd)}")
                    subprocess.run(cmd, check=True)
                    print(f"Compiled: {po_file} -> {mo_file}")
                except Exception as e:
                    print(f"Error compiling {po_file}: {str(e)}")

if __name__ == '__main__':
    compile_translations()
    print("Compilation complete.") 