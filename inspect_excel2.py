import pandas as pd

file_path = r'data\Master  ACOL FEB-2026 V2.xlsx'

# Leer con header en fila 0
df = pd.read_excel(file_path, header=0)

print('=== INFORMACIÓN GENERAL ===')
print(f'Shape: {df.shape}')
print(f'Columnas: {len(df.columns)}')
print('')

print('=== PRIMERAS 3 COLUMNAS (10 filas) ===')
print(df.iloc[:10, :3])
print('')

print('=== VALORES ÚNICOS EN CÓDIGO MATERIAL ===')
print(df['Código Material'].dropna().unique())
print('')

print('=== VALORES ÚNICOS EN DESCRIPCIÓN MATERIAL ===')
print(df['Descripción Material'].dropna().unique())
print('')

print('=== PRIMERA FILA CON CÓDIGO NO NULO ===')  
non_null_rows = df[df['Código Material'].notna()]
if not non_null_rows.empty:
    print(non_null_rows.iloc[0])
else:
    print('No hay filas con Código Material')
print('')

print('=== VERIFICAR SI HAY DATOS REALES ===')
print(f'Filas con Código Material: {df["Código Material"].notna().sum()}')
print(f'Filas con Descripción: {df["Descripción Material"].notna().sum()}')
print(f'Total valores no-cero en Enero 2026: {(df["Enero 2026"] != 0).sum() if "Enero 2026" in df.columns else "N/A"}')
