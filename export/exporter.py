"""
图像导出模块 - 负责将图形窗口保存为图片
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graphics import GraphWin


class ImageExporter:
    """
    图像导出器

    支持将graphics.py窗口保存为PNG图片
    需要安装Ghostscript才能完成转换
    """

    @staticmethod
    def save_as_png(win: GraphWin, filename: str) -> bool:
        """
        将窗口保存为PNG图片

        Args:
            win: graphics.py窗口对象
            filename: 输出文件路径（.png）

        Returns:
            是否成功保存
        """
        from PIL import Image

        # 先保存为PostScript格式
        ps_path = Path(filename).with_suffix(".ps")
        win.postscript(file=str(ps_path), colormode="color")

        try:
            # 使用PIL转换为PNG
            img = Image.open(ps_path)
            img.save(filename, "PNG")
            ps_path.unlink()  # 删除临时PS文件
            print(f"图片已保存: {filename}")
            return True
        except Exception as e:
            print(f"保存图片失败: {e}")
            print(f"PostScript 文件已保存: {ps_path}")
            print("提示: 如需转换为 PNG，请安装 Ghostscript: brew install ghostscript")
            return False

    @staticmethod
    def save_as_postscript(win: GraphWin, filename: str) -> bool:
        """
        将窗口保存为PostScript格式

        Args:
            win: graphics.py窗口对象
            filename: 输出文件路径（.ps）

        Returns:
            是否成功保存
        """
        try:
            win.postscript(file=filename, colormode="color")
            print(f"PostScript 已保存: {filename}")
            return True
        except Exception as e:
            print(f"保存失败: {e}")
            return False
