import pandas as pd
import numpy as np

file_path = r'data\Master  ACOL FEB-2026 V2.xlsx'

# Leer sin header para inspeccionar
df_raw = pd.read_excel(file_path, header=None, nrows=30)

print('=== BUSCAR FILA DE ENCABEZADOS ===')
for i in range(min(20, len(df_raw))):
    row_vals = df_raw.iloc[i].values
    non_null = [v for v in row_vals if pd.notna(v) and str(v).strip() != '']
    
    if len(non_null) > 0:
        sample = non_null[:8] if len(non_null) <= 8 else non_null[:5] + ['...']
        print(f'Fila {i}: {len(non_null)} valores -> {sample}')
    else:
        print(f'Fila {i}: VACIA')

print('\n=== BUSCANDO "Código" o "Material" ===')
for i in range(min(20, len(df_raw))):
    row_vals = [str(v).lower() for v in df_raw.iloc[i].values if pd.notna(v)]
    if any('código' in v or 'codigo' in v or 'material' in v for v in row_vals):
        print(f'Fila {i}: Posible header -> {df_raw.iloc[i].values[:10]}')
