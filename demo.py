#!/usr/bin/env python3
"""
步长驱动无主并行多Agent系统 - 演示脚本
为了保持向后兼容性，此文件调用新版本的 CLI。
"""

import subprocess
import sys

def main():
    print("=" * 60)
    print("步长驱动无主并行多Agent系统 - 演示")
    print("=" * 60)
    print()
    print("系统配置：")
    print("  - Agent数量: 2")
    print("  - 最大步数: 2")
    print("  - 模型: deepseek-chat")
    print()
    print("正在启动系统...")
    print()

    # 尝试使用新版本或旧版本
    try:
        # 使用 src 目录的新版本
        subprocess.run([
            sys.executable, "-m", "autoswarm.cli",
            "--agents", "2",
            "--max-steps", "2"
        ], cwd=".", check=True)
    except Exception as e:
        print(f"启动新版本失败: {e}")
        print("尝试使用 main.py...")
        try:
            subprocess.run([
                sys.executable, "main.py",
                "--agents", "2",
                "--max-steps", "2"
            ], cwd=".", check=True)
        except Exception as e2:
            print(f"错误: {e2}")

    print()
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
