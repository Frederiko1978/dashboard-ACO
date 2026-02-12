# 🚀 Guía de Despliegue en Streamlit Cloud

Esta guía te ayudará a publicar tu Dashboard ACO en Streamlit Community Cloud de forma gratuita.

## 📋 Requisitos Previos

1. **Cuenta de GitHub** - [Crear cuenta](https://github.com/signup) si no tienes una
2. **Git instalado** - [Descargar Git](https://git-scm.com/downloads) si no lo tienes
3. Tu proyecto debe estar en un repositorio de GitHub

## 🗂️ Paso 1: Subir el Proyecto a GitHub

### Si aún NO tienes el proyecto en GitHub:

1. **Inicializa Git en tu proyecto (si no está inicializado):**
   ```bash
   cd "c:\Users\framirez\Programacion\Dashboard ACO"
   git init
   ```

2. **Crea un repositorio en GitHub:**
   - Ve a [github.com/new](https://github.com/new)
   - Nombre sugerido: `dashboard-aco`
   - Configúralo como público o privado
   - NO inicialices con README (ya tienes uno)
   - Haz clic en "Create repository"

3. **Conecta tu proyecto local con GitHub:**
   ```bash
   git add .
   git commit -m "Initial commit - Dashboard ACO"
   git branch -M main
   git remote add origin https://github.com/TU-USUARIO/dashboard-aco.git
   git push -u origin main
   ```
   
   > **Nota:** Reemplaza `TU-USUARIO` con tu nombre de usuario de GitHub

### Si YA tienes el proyecto en GitHub:

Simplemente asegúrate de que tu código esté actualizado:
```bash
git add .
git commit -m "Preparar para deployment en Streamlit Cloud"
git push
```

## ☁️ Paso 2: Desplegar en Streamlit Cloud

1. **Ve a Streamlit Cloud:**
   - Accede a: [share.streamlit.io](https://share.streamlit.io)
   - Haz clic en "Sign up" o "Sign in"

2. **Autoriza con GitHub:**
   - Selecciona "Continue with GitHub"
   - Autoriza a Streamlit para acceder a tus repositorios

3. **Crea una nueva app:**
   - Haz clic en "New app"
   - Selecciona tu repositorio: `dashboard-aco`
   - Branch: `main` (o la rama que estés usando)
   - Main file path: `app.py`
   - App URL (opcional): Personaliza la URL si quieres

4. **Configura (si es necesario):**
   - Python version: 3.8+ (se detecta automáticamente del requirements.txt)
   - Click en "Advanced settings" si necesitas configurar algo más

5. **Deploy:**
   - Haz clic en "Deploy!"
   - Espera 2-5 minutos mientras se instalan las dependencias

## 📊 Paso 3: Cargar Datos

Tu dashboard está diseñado para cargar datos de dos formas:

### Opción A: Subir archivo manualmente (Recomendado para producción)
- Los usuarios pueden subir el archivo Excel directamente desde la interfaz
- Usa el botón "Browse files" en la barra lateral
- **Ventaja:** No necesitas incluir datos sensibles en GitHub

### Opción B: Incluir datos de ejemplo (Para pruebas)
Si quieres incluir datos de ejemplo en el repositorio:

1. Coloca un archivo de ejemplo en la carpeta `data/`
2. Asegúrate de que no contenga información sensible
3. Haz commit y push:
   ```bash
   git add data/ejemplo.xlsx
   git commit -m "Agregar datos de ejemplo"
   git push
   ```
4. Streamlit Cloud lo cargará automáticamente

## 🔧 Actualizar la Aplicación

Cada vez que hagas cambios en tu código:

```bash
git add .
git commit -m "Descripción de los cambios"
git push
```

Streamlit Cloud detectará los cambios automáticamente y redesplegará la aplicación.

## 🎨 Personalización de la URL

Tu app estará disponible en:
```
https://[tu-nombre]-dashboard-aco-[hash].streamlit.app
```

Puedes personalizar el nombre antes del despliegue en la configuración avanzada.

## ⚠️ Solución de Problemas

### Error: "Missing requirements"
- Verifica que `requirements.txt` esté en la raíz del proyecto
- Asegúrate de que todas las versiones sean compatibles

### Error al cargar el archivo
- El límite de archivos en Streamlit Cloud es de 200MB
- Optimiza tus archivos Excel si son muy grandes

### La app está lenta
- Streamlit Cloud gratuito tiene recursos limitados
- Considera optimizar el procesamiento de datos
- Usa `@st.cache_data` para cachear operaciones pesadas (ya implementado)

## 📱 Compartir tu Dashboard

Una vez desplegado, puedes compartir la URL con tu equipo:
```
https://tu-app.streamlit.app
```

## 🔐 Seguridad y Privacidad

- **Repositorio Privado:** Si tu repo es privado, solo Streamlit Cloud tendrá acceso
- **No subas datos sensibles:** Usa el .gitignore correctamente (ya configurado)
- **Secrets:** Si necesitas API keys u otra información sensible, usa [Streamlit Secrets](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

## 📚 Recursos Adicionales

- [Documentación oficial de Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [Guía de deployment](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Gestión de recursos](https://docs.streamlit.io/streamlit-community-cloud/manage-your-app)

## ✅ Checklist Final

Antes de desplegar, asegúrate de:

- [ ] Código subido a GitHub
- [ ] `requirements.txt` actualizado
- [ ] `.gitignore` configurado correctamente
- [ ] Archivos de datos sensibles NO están en el repositorio
- [ ] `app.py` está en la raíz del proyecto
- [ ] Has probado la app localmente (`streamlit run app.py`)

---

## 🆘 ¿Necesitas Ayuda?

Si tienes problemas durante el despliegue, revisa:
1. Los logs de Streamlit Cloud (disponibles en la interfaz)
2. Que todas las rutas de archivos sean relativas, no absolutas
3. Que los módulos importados existan en requirements.txt

¡Buena suerte con tu despliegue! 🎉
