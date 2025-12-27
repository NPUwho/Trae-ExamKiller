@echo off
chcp 65001 >nul
echo ============================================
echo    ExamKiller - 大学考试复习辅助平台
echo    启动脚本
echo ============================================
echo.

REM 激活虚拟环境
echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.11+
    pause
    exit /b 1
)

REM 安装依赖
echo [2/3] 安装依赖...
pip install -q -r requirements.txt
if errorlevel 1 (
    echo 警告: 依赖安装遇到问题，继续尝试启动...
)

REM 启动后端服务
echo [3/3] 启动后端服务...
echo.
echo 后端服务将在 http://localhost:8000 启动
echo 按 Ctrl+C 停止服务
echo.
echo 启动中...

cd /d "%~dp0"
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

pause
