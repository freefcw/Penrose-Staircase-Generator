#!/usr/bin/env python3
"""
Penrose Staircase 打包脚本

支持 macOS、Android、Web 多平台打包。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tomllib
from pathlib import Path


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 打包配置
BUILD_CONFIG = {
    "org": "com.penrose",
    "project": "Penrose Staircase",
    "product": "Penrose",
}


def get_version() -> str:
    """从 pyproject.toml 读取版本号"""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    return data["project"]["version"]


def run_command(cmd: list[str], verbose: bool = False) -> bool:
    """运行命令并返回是否成功"""
    print(f">>> {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=not verbose,
            text=True,
        )
        if result.returncode != 0:
            if not verbose and result.stderr:
                print(f"错误: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"命令执行失败: {e}")
        return False


def build_macos(verbose: bool = False) -> bool:
    """打包 macOS 应用"""
    print("\n🍎 打包 macOS 应用...")
    version = get_version()
    
    cmd = [
        "flet", "build", "macos",
        "--org", BUILD_CONFIG["org"],
        "--project", BUILD_CONFIG["project"],
        "--product", BUILD_CONFIG["product"],
        "--build-version", version,
    ]
    
    return run_command(cmd, verbose)


def build_android(verbose: bool = False) -> bool:
    """打包 Android APK"""
    print("\n🤖 打包 Android APK...")
    version = get_version()
    
    cmd = [
        "flet", "build", "apk",
        "--org", BUILD_CONFIG["org"],
        "--project", BUILD_CONFIG["project"],
        "--product", BUILD_CONFIG["product"],
        "--build-version", version,
    ]
    
    return run_command(cmd, verbose)


def build_web(verbose: bool = False) -> bool:
    """打包 Web 应用"""
    print("\n🌐 打包 Web 应用...")
    
    cmd = [
        "flet", "build", "web",
        "--project", BUILD_CONFIG["project"],
    ]
    
    return run_command(cmd, verbose)


def clean_build() -> None:
    """清理构建目录"""
    print("🧹 清理构建目录...")
    build_dir = PROJECT_ROOT / "build"
    if build_dir.exists():
        import shutil
        shutil.rmtree(build_dir)
        print("已删除 build/ 目录")
    else:
        print("build/ 目录不存在，跳过清理")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Penrose Staircase 打包工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scripts/build.py --platform macos     # 打包 macOS
  python scripts/build.py --platform android   # 打包 Android APK
  python scripts/build.py --platform web       # 打包 Web
  python scripts/build.py --platform all       # 全平台打包
  python scripts/build.py --clean              # 清理后打包
        """,
    )
    
    parser.add_argument(
        "--platform", "-p",
        choices=["macos", "android", "web", "all"],
        default="macos",
        help="目标平台 (默认: macos)",
    )
    
    parser.add_argument(
        "--clean", "-c",
        action="store_true",
        help="构建前清理 build 目录",
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细输出",
    )
    
    args = parser.parse_args()
    
    # 打印版本信息
    version = get_version()
    print(f"📦 Penrose Staircase v{version}")
    print(f"   目标平台: {args.platform}")
    
    # 清理
    if args.clean:
        clean_build()
    
    # 打包
    success = True
    
    if args.platform == "macos" or args.platform == "all":
        success &= build_macos(args.verbose)
    
    if args.platform == "android" or args.platform == "all":
        success &= build_android(args.verbose)
    
    if args.platform == "web" or args.platform == "all":
        success &= build_web(args.verbose)
    
    # 结果
    if success:
        print("\n✅ 打包完成!")
        return 0
    else:
        print("\n❌ 打包失败!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
