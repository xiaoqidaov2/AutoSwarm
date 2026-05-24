#!/usr/bin/env python3
"""
步长驱动无主并行多Agent系统 - 演示脚本
"""

import time
import sys
import os

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

    os.system("python main.py --agents 2 --max-steps 2")

    print()
    print("=" * 60)
    print("演示完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
