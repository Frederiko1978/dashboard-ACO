# ✅ Checklist Pre-Deployment

Usa esta lista antes de desplegar tu Dashboard ACO en Streamlit Cloud.

## 📋 Verificación Pre-Deployment

### 1. ✅ Archivos de Configuración
- [x] `requirements.txt` existe y está actualizado
- [x] `.streamlit/config.toml` existe con configuración de tema
- [x] `.gitignore` configurado correctamente (archivos Excel ignorados)
- [x] `app.py` está en la raíz del proyecto

### 2. 🧪 Pruebas Locales
- [ ] El dashboard corre sin errores en local: `streamlit run app.py`
- [ ] Puedes cargar un archivo Excel correctamente
- [ ] Todas las páginas funcionan (Principal, Coberturas, Evolución, WAPE)
- [ ] Los gráficos se muestran correctamente
- [ ] Los filtros funcionan como esperado

### 3. 📁 Gestión de Datos
- [ ] Los archivos Excel **NO están** en el repositorio Git
- [ ] El archivo `data/DATA_GUIDE.md` explica la estructura de datos
- [ ] Sabes cómo los usuarios cargarán datos (upload o carpeta data/)

### 4. 🔐 Seguridad
- [ ] No hay credenciales hardcodeadas en el código
- [ ] No hay rutas absolutas de tu máquina en el código
- [ ] El repositorio está configurado como privado (si contiene info sensible)
- [ ] El .gitignore incluye archivos sensibles

### 5. 📦 Git & GitHub
- [ ] Git está instalado en tu sistema
- [ ] Tienes una cuenta de GitHub
- [ ] Has creado un repositorio en GitHub (o estás listo para crearlo)
- [ ] Conoces la URL de tu repositorio

### 6. 📚 Documentación
- [x] `README.md` tiene instrucciones claras
- [x] `DEPLOYMENT.md` tiene la guía de despliegue
- [x] `data/DATA_GUIDE.md` explica la estructura de datos

---

## 🚀 Pasos de Despliegue

Si completaste todos los items anteriores, sigue estos pasos:

### Opción A: Usar Script Automático (Windows)
```bash
# Ejecuta el script incluido
.\subir_a_github.bat
```

### Opción B: Manual
```bash
# 1. Inicializar Git (si no está inicializado)
git init

# 2. Hacer commit de todos los archivos
git add .
git commit -m "Preparar para deployment en Streamlit Cloud"

# 3. Conectar con GitHub
git branch -M main
git remote add origin https://github.com/TU-USUARIO/dashboard-aco.git

# 4. Subir al repositorio
git push -u origin main
```

### En Streamlit Cloud
1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Sign in con GitHub
3. Click "New app"
4. Selecciona tu repositorio y `app.py`
5. Click "Deploy!"

---

## ⚠️ Problemas Comunes

### "Git no reconocido como comando"
- **Solución:** Instala Git desde https://git-scm.com/downloads

### "Permission denied (publickey)"
- **Solución:** Configura tu SSH key o usa HTTPS en lugar de SSH

### "Requirements installation failed"
- **Solución:** Verifica que requirements.txt tenga versiones compatibles

### "Module not found"
- **Solución:** Asegúrate de que todos los imports estén en requirements.txt

---

## 📞 Necesitas Ayuda?

Si encuentras problemas:
1. Lee el archivo [DEPLOYMENT.md](DEPLOYMENT.md) completo
2. Revisa los logs en Streamlit Cloud
3. Verifica que seguiste todos los pasos del checklist

---

## 🎉 Después del Deployment

Una vez desplegado exitosamente:
- [ ] Prueba la URL pública de tu dashboard
- [ ] Sube un archivo Excel de prueba
- [ ] Comparte la URL con tu equipo
- [ ] Configura actualizaciones automáticas desde GitHub

**URL de tu Dashboard:** https://[tu-app].streamlit.app

---

**Última actualización:** Febrero 2026
