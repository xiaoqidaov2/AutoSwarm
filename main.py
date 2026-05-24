#!/usr/bin/env python3
"""
AutoSwarm - 步长驱动无主并行多Agent系统
为了保持向后兼容性，此文件作为启动脚本。
使用新版本请运行: python -m autoswarm.cli 或 autoswarm
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from autoswarm.cli import main

if __name__ == "__main__":
    sys.exit(main())
