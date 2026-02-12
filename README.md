# Dashboard ACO - Abastecimiento S&OP Ejecutivo

Dashboard interactivo para análisis de planificación y cobertura de inventario, replicando la funcionalidad del reporte Power BI de S&OP.

## 🎯 Características

### Páginas del Dashboard

1. **📊 Vista Principal**
   - Tabla resumen de materiales
   - Material por estados de cobertura (< 45, < 90, > 90 días)
   - Evolutivo de cobertura con despachos, FCST e inventario
   - Planificación detallada por SKU

2. **🎯 Estado de Coberturas**
   - Análisis filtrado por estado de cobertura
   - Evolución del inventario
   - Distribución por origen (LAMPA, TERCEROS, LEA)
   - Top 15 de mayor y menor valor
   - Planificación por SKU con formato condicional

3. **📈 Evolución Futura**
   - Proyección de estados de cobertura
   - Tendencias futuras de inventario
   - Análisis predictivo de SKUs críticos

4. **📉 WAPE (Kg-L)**
   - Análisis de precisión del forecast
   - WAPE por origen
   - Top 15 materiales con mayor/menor error
   - Evolución mensual del WAPE
   - Métricas de bias (sobre/sub forecast)

### Filtros Disponibles
- Fecha Año/Mes (selección múltiple)
- Origen (Todas, LAMPA, TERCEROS, LEA, LAMPA (M))
- Material (búsqueda de SKUs)
- Estado Cob(D) (< 45, < 90, > 90 días)

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.8 o superior
- Archivo Excel desde SharePoint

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd "c:\Users\framirez\Programacion\Dashboard ACO"
   ```

2. **Crear entorno virtual (recomendado)**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate
   ```

3. **Instalar dependencias**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configurar datos**
   - Crear carpeta `data` en el directorio raíz (se crea automáticamente)
   - Descargar el archivo Excel desde SharePoint:
     ```
     https://grupoanasac-my.sharepoint.com/:x:/r/personal/framirez_anasac_cl/Documents/2026/SUBG%20PLANIFICACION/PLANIFICACION%20REGIONAL/ACO/Master%20%20ACOL%20FEB-2026%20V2.xlsx
     ```
   - Guardarlo en: `c:\Users\framirez\Programacion\Dashboard ACO\data\`

5. **Ejecutar el dashboard**
   ```powershell
   streamlit run app.py
   ```

6. **Abrir en navegador**
   - Se abrirá automáticamente en: `http://localhost:8501`

## 📂 Estructura del Proyecto

```
Dashboard ACO/
│
├── app.py                          # Aplicación principal
├── requirements.txt                # Dependencias Python
├── README.md                       # Este archivo
│
├── data/                          # Carpeta para archivos Excel (no en Git)
│   └── Master_ACOL_FEB-2026.xlsx
│
├── pages/                         # Módulos de páginas
│   ├── __init__.py
│   ├── page_principal.py          # Página principal
│   ├── page_estado_coberturas.py  # Estado de coberturas
│   ├── page_evolucion_futura.py   # Evolución futura
│   └── page_wape.py               # Análisis WAPE
│
└── utils/                         # Utilidades y funciones
    ├── __init__.py
    ├── data_loader.py             # Carga y procesamiento de datos
    └── calculations.py            # Cálculos y métricas
```

## 🌐 Despliegue en la Nube

### 🚀 Streamlit Cloud (Recomendado) ⭐

Este dashboard está **listo para desplegarse en Streamlit Community Cloud** de forma gratuita.

**📖 Guía Completa:** Ver [DEPLOYMENT.md](DEPLOYMENT.md) para instrucciones paso a paso.

**Resumen rápido:**
1. Sube el código a GitHub (usa el script `subir_a_github.bat`)
2. Ve a [share.streamlit.io](https://share.streamlit.io) y conecta tu repositorio
3. Selecciona `app.py` como archivo principal
4. ¡Deploy! (toma 2-5 minutos)

**Ventajas:**
- ✅ 100% gratuito para proyectos privados
- ✅ URL pública personalizable
- ✅ Actualización automática desde GitHub
- ✅ Sin necesidad de servidor propio

**Costo:** Gratis

### Opción 2: Power BI Embed
**Ventajas:** Se mantiene en el ecosistema actual de la organización
**Pasos:**
1. Exportar visualizaciones de Streamlit como imágenes
2. Usar Power BI para crear el dashboard final
3. Publicar en Power BI Service

**Costo:** Depende de las licencias de Power BI existentes

### Opción 3: Azure Web Apps
**Ventajas:** Integración con Azure, control total, seguridad empresarial
**Pasos:**
1. Crear Azure Web App
2. Configurar deployment desde GitHub o local
3. Configurar variables de entorno
4. Acceso mediante URL de Azure

**Costo:** Desde $13/mes (Basic tier)

### Opción 4: Docker + Servidor Interno
**Ventajas:** Control total, datos internos, sin costos cloud
**Pasos:**
1. Crear Dockerfile (proporcionado abajo)
2. Build de imagen Docker
3. Deploy en servidor interno de la organización
4. Configurar reverse proxy (nginx) para acceso

**Costo:** Solo infraestructura interna

### Opción 5: SharePoint + HTML Estático
**Ventajas:** Usa infraestructura existente
**Limitaciones:** Interactividad limitada, requiere regeneración manual
**Pasos:**
1. Exportar dashboard como HTML estático
2. Subir a SharePoint
3. Embedar en página de SharePoint

**Costo:** Gratis (usa SharePoint existente)

## 🐳 Dockerfile (para despliegue Docker)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

**Comandos Docker:**
```powershell
# Build
docker build -t dashboard-aco .

# Run
docker run -p 8501:8501 -v ${PWD}/data:/app/data dashboard-aco
```

## 🔒 Seguridad y Acceso

### Para despliegue interno:
1. Implementar autenticación (AD, LDAP)
2. Usar HTTPS con certificados
3. Configurar firewall para acceso solo desde red interna

### Para Streamlit Cloud:
1. Usar repositorio privado de GitHub
2. Configurar secrets en Streamlit Cloud
3. Implementar autenticación con `streamlit-authenticator`

## 📊 Actualización de Datos

### Método Manual:
1. Descargar archivo Excel actualizado desde SharePoint
2. Reemplazar archivo en carpeta `data/`
3. Recargar página del dashboard (F5)

### Método Automático (Futuro):
- Configurar acceso a SharePoint API
- Actualización programada mediante cron job
- Notificaciones de actualización

## 🎨 Personalización

### Colores de Estado:
- Rojo (#EF5350): Cob < 45 días (Crítico)
- Amarillo (#FFA726): Cob < 90 días (Precaución)
- Verde (#66BB6A): Cob > 90 días (Saludable)

### Logotipo:
- Agregar logo de ANASAC en carpeta `assets/`
- Modificar `app.py` para incluir imagen

## 📞 Soporte

Para dudas o mejoras:
- Contacto: framirez@anasac.cl
- Repositorio: [GitHub interno]

## 📝 Notas Importantes

1. **Formato del Excel:**
   - El dashboard espera columnas específicas (Material, FCST, Inv Kg-L, etc.)
   - Si el formato cambia, actualizar `data_loader.py`

2. **Performance:**
   - Para datasets grandes (>50k filas), considerar paginación
   - Implementar caché para queries frecuentes

3. **Actualización de Dependencias:**
   ```powershell
   pip install --upgrade -r requirements.txt
   ```

## 🚀 Recomendación de Despliegue para ANASAC

**Mejor opción:** Streamlit Cloud (corto plazo) + Azure Web Apps (largo plazo)

**Razones:**
1. Rápido de implementar (< 1 día)
2. Sin costos iniciales con Streamlit Cloud
3. Fácil migración a Azure cuando se requiera
4. Mantiene datos en SharePoint (fuente única de verdad)
5. Permite compartir con toda la organización mediante URL

**Siguiente paso:** 
1. Testear localmente
2. Subir a GitHub privado de ANASAC
3. Deploy en Streamlit Cloud para pruebas
4. Evaluar migración a Azure según necesidades
