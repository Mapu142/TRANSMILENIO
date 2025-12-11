import pandas as pd

# Cargar shapes.txt manteniendo la precisión
shapes = pd.read_csv('shapes.txt')
print(shapes.head())

# Verificar la precisión
print("\nPrimeras coordenadas exactas:")
print(f"shape_pt_lat: {shapes['shape_pt_lat'].iloc[0]}")
print(f"shape_pt_lon: {shapes['shape_pt_lon'].iloc[0]}")