# Penrose Staircase 打包入口
# 使用方法: make build-macos / make build-android / make build-web

.PHONY: build-macos build-android build-web build-all clean icon dev test help

# === 打包命令 ===

build-macos:  ## 打包 macOS 应用
	uv run python scripts/build.py --platform macos --verbose

build-android:  ## 打包 Android APK
	uv run python scripts/build.py --platform android --verbose

build-web:  ## 打包 Web 应用
	uv run python scripts/build.py --platform web --verbose

build-all:  ## 全平台打包
	uv run python scripts/build.py --platform all --verbose

# === 辅助命令 ===

clean:  ## 清理构建目录
	rm -rf build/
	@echo "✅ build/ 目录已清理"

icon:  ## 生成应用图标
	uv run python scripts/generate_icon.py

# === 开发命令 ===

dev:  ## 启动开发服务器
	uv run python -m flet_app

test:  ## 运行测试
	uv run pytest -v

lint:  ## 代码检查
	uv run basedpyright

# === 帮助 ===

help:  ## 显示帮助信息
	@echo "Penrose Staircase 打包工具"
	@echo ""
	@echo "用法: make <target>"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'
