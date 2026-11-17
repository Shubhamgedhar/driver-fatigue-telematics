@echo off
echo ============================================================
echo   Compiling FastGeometry.cpp to FastGeometry.dll via GCC
echo ============================================================
g++ -O3 -shared -fPIC -o ../FastGeometry.dll src/FastGeometry.cpp -I include/
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] FastGeometry.dll compiled successfully in project root!
) else (
    echo [ERROR] Compilation failed.
)
