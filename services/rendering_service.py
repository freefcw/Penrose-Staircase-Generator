"""
楼梯渲染服务 - 协调楼梯渲染的各个阶段

职责：
- 准备渲染上下文
- 协调楼梯和序列的绘制
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

from core.render_context import RenderContext
from core.layout import LayoutInfo, calculate_layout_from_config
from core.geometry import GeometryTransform

if TYPE_CHECKING:
    from core.staircase import StaircaseConfig, StaircaseModel
    from core.theme import Theme
    from rendering.canvas import Canvas

logger = logging.getLogger(__name__)


class CanvasProvider(Protocol):
    """画布提供者协议"""
    
    def get_canvas_adapter(self, width: float, height: float) -> Canvas:
        """获取画布适配器"""
        ...
    
    def clear_drawing(self) -> None:
        """清除绘图内容"""
        ...
    
    def update_canvas(self) -> None:
        """更新画布显示"""
        ...


class RenderingService:
    """楼梯渲染服务"""
    
    def __init__(self, preview_scale_factor: float = 3.0):
        """
        初始化渲染服务
        
        Args:
            preview_scale_factor: 预览缩放因子
        """
        self._preview_scale_factor = preview_scale_factor
    
    def prepare_context(
        self,
        canvas_provider: CanvasProvider,
        config: "StaircaseConfig",
        page_width: float,
        page_height: float,
    ) -> RenderContext | None:
        """
        准备渲染上下文
        
        Args:
            canvas_provider: 画布提供者
            config: 楼梯配置
            page_width: 页面宽度
            page_height: 页面高度
            
        Returns:
            渲染上下文，如果无法创建则返回 None
        """
        canvas_provider.clear_drawing()
        
        # 计算画布尺寸
        canvas_width = page_width - 280  # 减去控制面板宽度
        canvas_height = page_height - 40  # 减去边距
        
        # 楼梯缩小 1.5 倍
        scale_factor = self._preview_scale_factor / 1.5
        
        # 计算布局
        layout = calculate_layout_from_config(config, scale_factor)
        
        # 创建画布适配器
        canvas = canvas_provider.get_canvas_adapter(canvas_width, canvas_height)
        
        # 估算序列区域高度
        total_steps = config.total_steps
        seq_rows = (total_steps // 10) + 1
        seq_height = seq_rows * 40 * scale_factor
        
        # 计算居中偏移
        total_content_height = layout.stair_height + 50 + seq_height
        center_offset_x = max(0, (canvas_width - layout.window_width) / 2)
        center_offset_y = max(50, (canvas_height - total_content_height) / 2)
        
        # 创建几何变换器
        transform = GeometryTransform(
            layout.zoom,
            layout.offset_x + center_offset_x,
            layout.offset_y + center_offset_y
        )
        
        return RenderContext(
            layout=layout,
            scale_factor=scale_factor,
            transform=transform,
            canvas=canvas,
            canvas_width=canvas_width,
            canvas_height=canvas_height,
            center_offset_x=center_offset_x,
            center_offset_y=center_offset_y,
        )
    
    def render_staircase(
        self,
        ctx: RenderContext,
        config: "StaircaseConfig",
        model: "StaircaseModel",
        theme: "Theme",
    ) -> None:
        """
        绘制楼梯
        
        Args:
            ctx: 渲染上下文
            config: 楼梯配置
            model: 楼梯模型
            theme: 主题
        """
        from rendering.renderer import StaircaseRenderer
        
        renderer = StaircaseRenderer(
            canvas=ctx.canvas,
            transform=ctx.transform,
            config=config,
            model=model,
            theme=theme,
        )
        renderer.render(model.start_step_index)
    
    def render_sequence(
        self,
        ctx: RenderContext,
        config: "StaircaseConfig",
        model: "StaircaseModel",
        theme: "Theme",
    ) -> None:
        """
        绘制颜色序列
        
        Args:
            ctx: 渲染上下文
            config: 楼梯配置
            model: 楼梯模型
            theme: 主题
        """
        from rendering.sequence import SequenceRenderer
        
        logger.info(f"开始绘制序列, 形状数量前: {len(ctx.canvas.get_shapes())}")
        
        seq_renderer = SequenceRenderer(
            ctx.canvas,
            config,
            ctx.canvas_width,
            theme,
            x_offset=0  # 居中显示
        )
        
        # 数列紧接在楼梯下方显示
        seq_start_y = ctx.canvas_height * 0.60 + 100
        # 数列缩放因子也缩小 1.5 倍
        seq_scale = ctx.scale_factor / 1.5
        
        logger.info(
            f"序列起始Y: {seq_start_y}, 颜色数量: {len(model.color_sequence)}, "
            f"画布高度: {ctx.canvas_height}"
        )
        
        seq_renderer.render(
            model.color_sequence,
            model.start_step_index,
            seq_start_y,
            seq_scale,
            show_decimal=True,
        )
        
        logger.info(f"序列绘制完成, 形状数量后: {len(ctx.canvas.get_shapes())}")
