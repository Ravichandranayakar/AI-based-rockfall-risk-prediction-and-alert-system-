@echo off
echo 🐳 AI Rockfall Prediction System - Docker Build
echo ================================================
echo.

echo 🏗️  Building Docker image...
docker build -t ai-rockfall-system .

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Build successful!
    echo.
    echo 🚀 Starting container...
    docker run -d -p 5000:5000 --name ai-rockfall-app ai-rockfall-system
    
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo 🎉 SUCCESS! Your AI Rockfall System is now running!
        echo.
        echo 🌐 Access your application at: http://localhost:5000
        echo.
        echo 📊 Useful commands:
        echo    docker logs ai-rockfall-app       (View logs)
        echo    docker stop ai-rockfall-app       (Stop container)
        echo    docker start ai-rockfall-app      (Start container)
        echo.
        echo 🎯 Ready for SIH 2025 demonstrations!
    ) else (
        echo ❌ Failed to start container
    )
) else (
    echo ❌ Build failed
)

pause