@echo off
echo ========================================
echo Iniciando Dashboard ACO...
echo ========================================
echo.

REM Activar entorno virtual
if exist "venv\Scripts\activate.bat" (
    call .\venv\Scripts\activate.bat
) else (
    echo ERROR: Entorno virtual no encontrado
    echo Por favor ejecuta primero: instalar.bat
    pause
    exit /b 1
)

REM Verificar si existe archivo de datos
if not exist "data\*.xlsx" if not exist "data\*.xls" (
    echo.
    echo ADVERTENCIA: No se encontro un archivo Excel en la carpeta 'data'.
    echo.
    echo Puedes cargar el archivo directamente desde la interfaz del dashboard
    echo o guardarlo en la carpeta 'data' y recargar la pagina.
    echo.
    timeout /t 5
)

REM Iniciar Streamlit
echo Abriendo dashboard en navegador...
echo.
echo Si el navegador no se abre automaticamente, por favor ve a: http://localhost:8501
echo Para detener el dashboard, presiona Ctrl+C
echo.
python -m streamlit run app.py --server.headless false

pause
