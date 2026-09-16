@echo off
setlocal enabledelayedexpansion
REM ============================================
REM   IEEE submission build
REM   English:  pdflatex -> bibtex -> pdflatex x2
REM   Chinese:  xelatex  -> bibtex -> xelatex  x2
REM ============================================
set FAILED=0

echo [1/2] Building English manuscript (main.tex)...
pdflatex -interaction=nonstopmode main.tex >nul
if %ERRORLEVEL% neq 0 goto e1
bibtex main >nul
pdflatex -interaction=nonstopmode main.tex >nul
pdflatex -interaction=nonstopmode main.tex >nul
echo       Done.
goto zhbuild

:e1
echo [ERROR] English build failed. See main.log
set FAILED=1

:zhbuild
echo [2/2] Building Chinese manuscript (main_zh.tex)...
xelatex -interaction=nonstopmode main_zh.tex >nul
if %ERRORLEVEL% neq 0 goto e2
bibtex main_zh >nul
xelatex -interaction=nonstopmode main_zh.tex >nul
xelatex -interaction=nonstopmode main_zh.tex >nul
echo       Done.
goto cleanup

:e2
echo [ERROR] Chinese build failed. See main_zh.log
set FAILED=1

:cleanup
echo.
echo Cleaning auxiliary files...
del /q *.aux *.log *.out *.blg *.bbl *.toc *.synctex.gz 2>nul
echo.
if "!FAILED!"=="0" (
    echo ============================================
    echo   Build successful: main.pdf, main_zh.pdf
    echo ============================================
) else (
    echo ============================================
    echo   Build FAILED. Check the log files.
    echo ============================================
)
endlocal
