# 📊 Guía de Datos para el Dashboard ACO

## 🎯 Cómo Cargar Datos en el Dashboard

Este dashboard puede cargar datos de **dos formas**:

### Opción 1: Subir archivo manualmente (Recomendado) ✅
- Usa el botón **"Browse files"** en la barra lateral izquierda
- Selecciona tu archivo Excel (`Master ACOL *.xlsx`)
- El dashboard cargará y procesará los datos automáticamente

### Opción 2: Archivo local en la carpeta `data/`
- Coloca tu archivo Excel en la carpeta `data/`
- El dashboard lo detectará automáticamente al iniciar

---

## 📋 Estructura de Datos Requerida

El archivo Excel debe contener las siguientes columnas:

### Columnas Obligatorias:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `FECHA AÑO/MES` | Fecha en formato YYYY-MM o similar | `2026-02` |
| `MATERIAL` | Código SKU del material | `ACO12345` |
| `MATERIAL-DESC` | Descripción del material | `HERBICIDA XYZ 5L` |
| `ORIGEN` | Origen del material | `LAMPA`, `TERCEROS`, `LEA` |
| `ESTADO COB(D)` | Estado de cobertura en días | `< 45`, `< 90`, `>= 90` |
| `$VALOR INV` | Valor del inventario | `150000` |
| `COBERTURA(D)` | Días de cobertura | `65` |

### Columnas de Despachos (históricas):
- `DES 4M`, `DES 3M`, `DES 2M`, `DES 1M`
- Representan despachos de meses anteriores

### Columnas de Forecast (futuras):
- `FCST 0M`, `FCST 1M`, `FCST 2M`, `FCST 3M`, `FCST 4M`, etc.
- Representan el pronóstico de demanda

### Columnas de Inventario (futuras):
- `INV 0M`, `INV 1M`, `INV 2M`, `INV 3M`, `INV 4M`, etc.
- Representan el inventario proyectado

### Columnas para WAPE (análisis de precisión):
- `WAPE(Kg-L)` - Weighted Absolute Percentage Error
- Columnas de Real vs Forecast para comparación

---

## 🚫 No Incluir Datos Sensibles en el Repositorio

**IMPORTANTE:** Por seguridad, NO subas archivos Excel con datos reales al repositorio Git.

El archivo `.gitignore` ya está configurado para ignorar:
```
data/*.xlsx
data/*.xls
data/*.csv
```

---

## 🧪 Para Desarrollo/Pruebas

Si necesitas crear un archivo de ejemplo para pruebas:

1. **Crea un archivo Excel** con la estructura correcta
2. **Usa datos ficticios o anonimizados**
3. **Guárdalo en la carpeta `data/`** con nombre descriptivo
4. El dashboard lo cargará automáticamente

### Ejemplo de Datos Mínimos:

```csv
FECHA AÑO/MES,MATERIAL,MATERIAL-DESC,ORIGEN,ESTADO COB(D),$VALOR INV,COBERTURA(D),DES 1M,FCST 0M,INV 0M
2026-02,MAT001,Producto A,LAMPA,< 45,100000,30,500,600,300
2026-02,MAT002,Producto B,TERCEROS,< 90,200000,60,800,850,400
2026-02,MAT003,Producto C,LEA,>= 90,150000,120,400,420,500
```

---

## 🔧 Validación de Datos

El dashboard incluye **validación automática** de columnas:
- Si faltan columnas requeridas, mostrará un error claro
- Indicará qué columnas o grupos de columnas están faltando
- Mostrará las columnas detectadas para ayudar en la depuración

---

## 📤 Para Despliegue en Streamlit Cloud

Cuando despliegues en Streamlit Cloud:

1. **NO incluyas el archivo Excel** en el repositorio
2. Los usuarios deberán **subir su archivo** usando la interfaz
3. Esto mantiene los datos seguros y fuera del control de versiones

Si absolutamente necesitas un archivo de ejemplo en producción:
- Usa datos completamente ficticios
- Anonimiza toda la información
- Asegúrate de que no contenga información confidencial

---

## ✅ Checklist de Preparación de Datos

Antes de cargar tu archivo, verifica:

- [ ] El archivo es formato Excel (.xlsx o .xls)
- [ ] Contiene todas las columnas requeridas
- [ ] Los nombres de columnas coinciden exactamente
- [ ] Las fechas están en formato correcto
- [ ] Los datos están limpios (sin filas vacías al inicio)
- [ ] El archivo pesa menos de 200MB

---

## 🆘 Solución de Problemas

### Error: "Faltan columnas requeridas"
- Revisa que los nombres de columnas coincidan exactamente
- Verifica que no haya espacios extra o tildes incorrectas
- Usa el expandible "Ver columnas detectadas" para diagnóstico

### El dashboard carga pero no muestra datos
- Verifica que haya datos en las filas (no solo encabezados)
- Revisa que los formatos de fecha sean consistentes
- Asegúrate de que los valores numéricos sean números, no texto

### Archivo muy grande
- Filtra solo los datos necesarios antes de cargar
- Considera comprimir el Excel
- Verifica que no haya hojas ocultas con datos innecesarios

---

## 📁 Estructura de la Carpeta `data/`

```
data/
├── README.md                    # Este archivo
└── [tus archivos .xlsx aquí]   # Ignorados por Git
```

Los archivos Excel que coloques aquí serán ignorados por Git automáticamente.

---

**¿Necesitas ayuda?** Revisa el formato de tus columnas o contacta al administrador del sistema.
