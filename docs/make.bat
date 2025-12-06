@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=source
set BUILDDIR=build

REM Check for the 'clean' command
if "%1" == "clean" (
    echo Cleaning up '_autogen' directories in %SOURCEDIR%...

    REM Iterate through all subdirectories under source/ and delete '_autogen' directories
    set found=0
    for /d /r %SOURCEDIR% %%i in (_autogen) do (
        rmdir /s /q %%i
        set found=1
    )

    REM Print a message if no _autogen directories were found
    if "%found%" == "0" (
        REM No _autogen directories found, suppress output
        REM echo No '_autogen' directories found in %SOURCEDIR%.
    )

    echo Cleanup complete.
    popd
    exit /b 0
)

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.https://www.sphinx-doc.org/
	exit /b 1
)

if "%1" == "" goto help

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS% %O%

:end
popd
