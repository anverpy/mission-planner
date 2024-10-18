import os
import sys

# Obtiene la ruta al directorio padre del directorio actual (tests)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Añade el directorio padre al PYTHONPATH
sys.path.insert(0, parent_dir)
