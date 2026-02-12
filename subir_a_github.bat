@echo off
REM Script para subir el proyecto a GitHub
echo.
echo ========================================
echo   Preparando el proyecto para GitHub
echo ========================================
echo.

REM Verificar si Git está instalado
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git no está instalado en tu sistema.
    echo Por favor, descarga e instala Git desde: https://git-scm.com/downloads
    echo.
    pause
    exit /b 1
)

echo [OK] Git detectado correctamente.
echo.

REM Verificar si ya hay un repositorio Git
if exist .git (
    echo [INFO] Ya existe un repositorio Git en este directorio.
    echo.
    set /p respuesta="¿Deseas hacer commit y push de los cambios? (S/N): "
    if /i "%respuesta%"=="S" (
        goto :commit_push
    ) else (
        echo Operación cancelada.
        pause
        exit /b 0
    )
) else (
    echo [INFO] Inicializando nuevo repositorio Git...
    git init
    echo.
)

REM Pedir URL del repositorio remoto
echo.
echo Antes de continuar, crea un nuevo repositorio en GitHub:
echo   1. Ve a: https://github.com/new
echo   2. Nombre sugerido: dashboard-aco
echo   3. NO inicialices con README (ya tienes uno)
echo   4. Copia la URL del repositorio (ej: https://github.com/usuario/dashboard-aco.git)
echo.
set /p repo_url="Ingresa la URL de tu repositorio de GitHub: "

if "%repo_url%"=="" (
    echo [ERROR] No se proporcionó una URL válida.
    pause
    exit /b 1
)

:commit_push
REM Agregar archivos al stage
echo.
echo [INFO] Agregando archivos al repositorio...
git add .

REM Hacer commit
set /p commit_msg="Ingresa un mensaje para el commit (Enter para usar mensaje por defecto): "
if "%commit_msg%"=="" (
    set commit_msg=Preparar proyecto para deployment en Streamlit Cloud
)

git commit -m "%commit_msg%"
echo.

REM Configurar rama main si es nuevo repositorio
if not exist .git\refs\heads\main (
    echo [INFO] Configurando rama principal...
    git branch -M main
)

REM Agregar remoto si es necesario
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    if not "%repo_url%"=="" (
        echo [INFO] Configurando repositorio remoto...
        git remote add origin %repo_url%
    )
)

REM Push al repositorio
echo.
echo [INFO] Subiendo archivos a GitHub...
git push -u origin main

if errorlevel 1 (
    echo.
    echo [ERROR] Hubo un problema al subir los archivos.
    echo Posibles causas:
    echo   - La URL del repositorio es incorrecta
    echo   - No tienes permisos para el repositorio
    echo   - Necesitas autenticarte con GitHub
    echo.
    echo Intenta ejecutar manualmente:
    echo   git push -u origin main
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ¡Éxito! Proyecto subido a GitHub
echo ========================================
echo.
echo Próximos pasos:
echo   1. Ve a: https://share.streamlit.io
echo   2. Inicia sesión con tu cuenta de GitHub
echo   3. Crea una nueva app y selecciona tu repositorio
echo   4. Selecciona app.py como archivo principal
echo   5. ¡Deploy!
echo.
echo Más detalles en DEPLOYMENT.md
echo.
pause
