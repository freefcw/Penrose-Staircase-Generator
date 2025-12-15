"""
Penrose Staircase Generator - 命令行接口

用法:
    python -m cli <n> [-s <scale>] [-o <output.png>] [-t <theme>]
    penrose-stair <n> [-s <scale>] [-o <output.png>] [-t <theme>]

参数:
    n              第n个Penrose楼梯
    -s, --scale    缩放因子 (默认: 1)
    -o, --output   输出PNG文件路径 (可选)
    -t, --theme    主题样式 (默认: minimal)
    -d, --debug    启用调试输出
"""
from __future__ import annotations

import argparse
import logging
import sys

from app import PenroseApp
from core.config import AppConfig
from core.theme import Theme


def setup_logging(debug: bool) -> None:
    """配置日志"""
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
    )


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Penrose Staircase Generator - 彭罗斯楼梯生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("n", type=int, help="第n个Penrose楼梯")
    parser.add_argument(
        "-s", "--scale",
        type=int,
        default=1,
        help="缩放因子 (默认: 1)"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="输出PNG文件路径"
    )
    parser.add_argument(
        "-t", "--theme",
        type=str,
        choices=["classic", "minimal", "professional", "artistic"],
        default="minimal",
        help="主题样式: classic(经典), minimal(简约,默认), professional(专业), artistic(艺术)"
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

    # 配置日志
    setup_logging(args.debug)

    # 创建配置
    config = AppConfig(
        n=args.n,
        scale=args.scale,
        theme=Theme.get_by_name(args.theme),
        output_path=args.output,
        debug=args.debug,
    )

    # 运行应用
    app = PenroseApp(config)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())

