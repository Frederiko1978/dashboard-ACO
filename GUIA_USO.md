# Guía Rápida de Uso

## 🚀 Inicio Rápido (Windows)

### Primera vez:
1. Doble clic en `instalar.bat`
2. Esperar que termine la instalación
3. Descargar Excel desde SharePoint
4. Guardarlo en carpeta `data\`
5. Doble clic en `ejecutar_dashboard.bat`

### Uso posterior:
- Doble clic en `ejecutar_dashboard.bat`

## 🎯 Navegación del Dashboard

### Barra Lateral (Filtros):
- **Fecha Año/Mes**: Selecciona múltiples meses para análisis
- **Origen**: Filtra por LAMPA, TERCEROS, LEA, etc.
- **Material**: Busca SKUs específicos
- **Estado Cob(D)**: Filtra por criticidad de cobertura

### Páginas:

#### 📊 Principal
- Vista general de planificación
- Estados de cobertura por mes
- Evolutivo de inventario vs FCST
- Tabla detallada de planificación por SKU

**Uso:** Monitoreo diario, presentaciones ejecutivas

#### 🎯 Estado de Coberturas
- Análisis de SKUs críticos (< 45 días)
- Top 15 materiales con mayor/menor valor
- Distribución por origen
- Planificación detallada con código de colores

**Uso:** Identificar urgencias, planificar compras

#### 📈 Evolución Futura
- Proyección de inventario
- Predicción de estados críticos
- Análisis de tendencias

**Uso:** Planificación a mediano plazo, S&OP

#### 📉 WAPE
- Precisión del forecast
- Análisis de errores por origen
- Identificar materiales con mayor desviación
- Métricas de bias

**Uso:** Mejorar proceso de forecasting, KPI de precisión

## 💡 Tips de Uso

### Exportar Datos:
- Cada tabla tiene botón "📥 Descargar" para exportar a CSV
- Úsalo para análisis adicionales en Excel
- **PDF:** Usa el botón "📄 Guardar como PDF" en la barra lateral para exportar la vista actual con todos sus gráficos.

### Filtros Múltiples:
- Combina filtros para análisis específicos
- Ejemplo: Origen=TERCEROS + Estado=Cob<45 = SKUs críticos de terceros

### Actualizar Datos:
1. Descargar nuevo Excel desde SharePoint
2. Reemplazar archivo en `data\`
3. Presionar F5 en navegador

### Performance:
- Si es lento, reduce el rango de fechas
- Limita número de materiales seleccionados

## ❓ Preguntas Frecuentes

**P: No veo datos al iniciar**
R: Verifica que el archivo Excel esté en carpeta `data\`

**P: Me aparece un error de "columnas faltantes" al subir un archivo.**
R: El dashboard valida que el archivo Excel contenga columnas esenciales como 'Material', 'Fecha'/'Mes', 'FCST', 'Inv Kg-L', etc. Asegúrate de que tu archivo tenga estas columnas con los nombres correctos. El mensaje de error te indicará exactamente qué columnas faltan.

**P: Error al cargar Excel**
R: Asegúrate que el archivo no esté abierto en Excel

**P: Quiero filtrar por un SKU específico**
R: Usa el filtro "Material" en la barra lateral

**P: ¿Cómo comparto el dashboard?**
R: Ver sección "Opciones de Despliegue" en README.md

**P: Los gráficos no se ven bien**
R: Amplía la ventana del navegador o usa zoom 90%

## 📞 Soporte
Contacto: framirez@anasac.cl
