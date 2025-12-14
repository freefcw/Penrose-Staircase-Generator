"""
Penrose Staircase Generator - 命令行接口

用法:
    python -m cli <n> [-s <scale>] [-o <output.png>]
    penrose-stair <n> [-s <scale>] [-o <output.png>]

参数:
    n          第n个Penrose楼梯
    -s, --scale    缩放因子 (默认: 1)
    -o, --output   输出PNG文件路径 (可选)
"""
from __future__ import annotations

import argparse
import sys

from graphics import GraphWin, GraphicsError

import pstairs
from core.colors import ColorPalette, ColorSequence
from core.geometry import GeometryTransform
from core.staircase import StaircaseConfig, StaircaseModel
from export.exporter import ImageExporter
from rendering.canvas import GraphicsCanvas
from rendering.renderer import StaircaseRenderer
from rendering.sequence import SequenceRenderer


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Penrose Staircase Generator - 彭罗斯楼梯生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("n", type=int, help="第n个Penrose楼梯")
    parser.add_argument("-s", "--scale", type=int, default=1, help="缩放因子 (默认: 1)")
    parser.add_argument("-o", "--output", type=str, help="输出PNG文件路径")
    parser.add_argument(
        "-t", "--theme",
        type=str,
        choices=["classic", "minimal", "professional", "artistic"],
        default="minimal",
        help="主题样式: classic(经典), minimal(简约,默认), professional(专业), artistic(艺术)"
    )
    return parser.parse_args()


def calculate_window_dimensions(
    config: StaircaseConfig, scale: float
) -> tuple[float, float, float, float, float]:
    """
    计算窗口尺寸和偏移量

    Returns:
        (window_width, window_height, zoom, offset_x, offset_y)
    """
    A, B, C, D, L = config.a, config.b, config.c, config.d, config.step_length
    H = GeometryTransform.UNIT_HEIGHT

    # 缩放因子
    zoom = 11 / ((A + B + C + D + L - 4) * 0.1) * scale

    # 窗口尺寸
    window_width = (A * L + B * L) * zoom
    stair_height = (A * H * L + B * H * L) * zoom

    # 序列显示区域高度（减少空白）
    total_steps = config.total_steps
    seq_rows = (total_steps // 6) + 1
    seq_height = seq_rows * (30 * scale) + 5 * scale

    window_height = stair_height + seq_height

    # 偏移量
    offset_x = 10 * scale
    offset_y = (A * L * H * 0.5) * zoom

    return window_width, window_height, zoom, offset_x, offset_y


def main() -> int:
    """主入口函数"""
    args = parse_args()

    # 计算楼梯参数
    try:
        ps = pstairs.PenroseStaircase(args.n)
    except Exception as e:
        print(f"错误: 无法计算第 {args.n} 个Penrose楼梯: {e}")
        return 1

    # 设置主题
    ColorPalette.set_theme(args.theme)

    # 创建配置
    config = StaircaseConfig(ps.a, ps.b, ps.c, ps.d, ps.l)
    scale = args.scale

    # 计算窗口尺寸
    window_width, window_height, zoom, offset_x, offset_y = calculate_window_dimensions(
        config, scale
    )

    print(
        f"The Penrose-Staircase Nr. {args.n} is: "
        f"{config.a} {config.b} {config.c} {config.d} ({config.step_length}) "
        f"缩放: {scale}x"
    )

    # 创建窗口
    win = GraphWin("Penrose-Staircase Generator v2.0", window_width, window_height)

    # 创建几何变换器
    transform = GeometryTransform(zoom, offset_x, offset_y)

    # 创建画布
    canvas = GraphicsCanvas(win)

    # 创建模型
    model = StaircaseModel(config)

    # 生成颜色序列
    color_gen = ColorSequence(config.total_steps)
    model.color_sequence = color_gen.generate()
    model.start_step_index = color_gen.start_index

    # 调试日志
    print(f"[DEBUG] 总台阶数: {config.total_steps} "
          f"(A={config.a-1}, D={config.d-1}, B={config.b-1}, C={config.c-1})")
    print(f"[DEBUG] 起点索引(绘制顺序): {model.start_step_index}")
    print(f"[DEBUG] 颜色序列(绘制顺序): {[1 if c else 0 for c in model.color_sequence]}")

    # 渲染楼梯
    renderer = StaircaseRenderer(canvas, transform, config, model)
    renderer.render(model.start_step_index)

    # 经典主题显示标题
    if args.theme == "classic":
        from core.geometry import Point
        title = f"n={args.n} ratio: {config.a} {config.b} {config.c} {config.d} ({config.step_length})"
        canvas.draw_text(
            Point(window_width / 2, 5 * scale),
            title,
            min(10 * scale, 36),
            ColorPalette.TEXT_BLACK,
            face="courier",
        )

    # 渲染颜色序列
    stair_height = (config.a * GeometryTransform.UNIT_HEIGHT * config.step_length +
                    config.b * GeometryTransform.UNIT_HEIGHT * config.step_length) * zoom
    seq_renderer = SequenceRenderer(canvas, config, window_width)
    seq_renderer.render(
        model.color_sequence,
        model.start_step_index,
        stair_height - 30 * scale,
        scale,
        show_decimal=True,
    )

    # 保存图片（如果指定了输出路径）
    if args.output:
        ImageExporter.save_as_png(win, args.output)

    # 等待用户点击关闭
    try:
        win.getMouse()
    except GraphicsError:
        pass

    win.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
