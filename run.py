import subprocess
import sys
from pathlib import Path


def main():
    project_root = Path(__file__).parent
    app_path = project_root / "app" / "main.py"
    env_file = project_root / ".env"

    if not app_path.exists():
        print(f"错误: 找不到应用入口文件 {app_path}")
        sys.exit(1)

    if not env_file.exists():
        print(f"警告: 未找到环境配置文件 {env_file}")

    print("正在启动服务...")
    print("访问地址: http://localhost:8000")
    print("API文档: http://localhost:8000/docs")
    print("-" * 40)

    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload",
    ]

    try:
        subprocess.run(cmd, cwd=str(project_root))
    except KeyboardInterrupt:
        print("\n服务已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
