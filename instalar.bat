@echo off
echo ========================================
echo Dashboard ACO - Instalacion Rapida
echo ========================================
echo.

REM Verificar si existe Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no esta instalado o no esta en PATH
    echo Por favor instala Python 3.8 o superior desde python.org
    pause
    exit /b 1
)

echo [1/4] Creando entorno virtual...
python -m venv venv

echo [2/4] Activando entorno virtual...
call .\venv\Scripts\activate.bat

echo [3/4] Instalando dependencias...
pip install -r requirements.txt

echo [4/4] Creando carpeta de datos...
if not exist "data" mkdir data

echo.
echo ========================================
echo Instalacion completada exitosamente!
echo ========================================
echo.
echo PASOS SIGUIENTES:
echo.
echo 1. Descarga el archivo Excel desde SharePoint
echo 2. Guardalo en la carpeta: data\
echo 3. Ejecuta: ejecutar_dashboard.bat
echo.
pause
