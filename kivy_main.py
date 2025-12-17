"""
Kivy 版本启动入口

用法:
    python kivy_main.py [n] [-t theme]
"""
from __future__ import annotations

import argparse
import logging
import sys

from core.config import AppConfig
from core.theme import Theme
from kivy_app import run_kivy_app


def setup_logging(debug: bool = False) -> None:
    """配置日志"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Penrose Staircase Generator (Kivy Version)",
    )
    parser.add_argument(
        "n",
        type=int,
        nargs='?',
        default=190,
        help="第n个Penrose楼梯 (默认: 190)"
    )
    parser.add_argument(
        "-t", "--theme",
        type=str,
        choices=["classic", "minimal", "professional", "artistic"],
        default="minimal",
        help="主题样式 (默认: minimal)"
    )
    parser.add_argument(
        "-s", "--scale",
        type=float,
        default=1.0,
        help="导出缩放因子 (默认: 1.0)"
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="启用调试输出"
    )
    return parser.parse_args()


def main() -> int:
    """主入口函数"""
    args = parse_args()
    setup_logging(args.debug)

    config = AppConfig(
        n=args.n,
        scale=args.scale,
        theme=Theme.get_by_name(args.theme),
        output_path=None,  # Kivy 版本不支持命令行导出
        debug=args.debug,
    )

    return run_kivy_app(config)


if __name__ == "__main__":
    sys.exit(main())
