"""
Flet 应用入口点

使用 Flet 框架运行 Penrose 楼梯生成器
"""
import logging

from core.config import AppConfig
from core.theme import Theme
from flet_app import run_flet_app

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main() -> int:
    """主函数"""
    # 默认配置
    config = AppConfig(
        n=190,
        theme=Theme.MINIMAL,
        scale=1.0,
    )
    
    return run_flet_app(config)


if __name__ == "__main__":
    raise SystemExit(main())
