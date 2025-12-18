"""
导出服务 - 处理 PNG 和配置导出/导入

职责：
- 导出高质量 PNG 图片
- 导出/导入配置文件
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.staircase import StaircaseConfig, StaircaseModel
    from core.theme import Theme
    from core.config_io import SessionConfig

logger = logging.getLogger(__name__)


class ExportService:
    """导出服务"""
    
    def __init__(self, export_scale: float = 3.0):
        """
        初始化导出服务
        
        Args:
            export_scale: 导出缩放因子
        """
        self._export_scale = export_scale
    
    def export_png(
        self,
        config: "StaircaseConfig",
        model: "StaircaseModel",
        theme: "Theme",
        file_path: str,
    ) -> bool:
        """
        导出高质量 PNG 图片
        
        Args:
            config: 楼梯配置
            model: 楼梯模型
            theme: 主题
            file_path: 输出文件路径
            
        Returns:
            是否成功
        """
        from rendering.pillow_canvas import PillowCanvas
        from core.geometry import GeometryTransform
        from core.layout import calculate_layout_from_config
        from rendering.renderer import StaircaseRenderer
        from rendering.sequence import SequenceRenderer
        
        try:
            # 计算布局
            layout = calculate_layout_from_config(config, self._export_scale)
            
            # 创建 Pillow 画布
            canvas_width = int(layout.window_width)
            canvas_height = int(layout.window_height + 200)  # 额外空间给序列
            pillow_canvas = PillowCanvas(canvas_width, canvas_height)
            
            # 创建几何变换器
            transform = GeometryTransform(
                layout.zoom,
                layout.offset_x,
                layout.offset_y
            )
            
            # 渲染楼梯
            renderer = StaircaseRenderer(
                canvas=pillow_canvas,
                transform=transform,
                config=config,
                model=model,
                theme=theme,
            )
            renderer.render(model.start_step_index)
            
            # 渲染序列
            seq_renderer = SequenceRenderer(
                pillow_canvas,
                config,
                canvas_width,
                theme,
                x_offset=0
            )
            seq_start_y = layout.stair_height + 30
            seq_renderer.render(
                model.color_sequence,
                model.start_step_index,
                seq_start_y,
                self._export_scale,
                show_decimal=True,
            )
            
            # 保存图片
            pillow_canvas.save(file_path)
            logger.info(f"导出完成: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False
    
    def export_config(
        self,
        n: int,
        theme_name: str,
        config: "StaircaseConfig",
        model: "StaircaseModel",
        file_path: str,
    ) -> bool:
        """
        导出配置文件
        
        Args:
            n: 楼梯编号
            theme_name: 主题名称
            config: 楼梯配置
            model: 楼梯模型
            file_path: 输出文件路径
            
        Returns:
            是否成功
        """
        from core.config_io import SessionConfig, ConfigExporter
        
        try:
            session_config = SessionConfig(
                n=n,
                theme=theme_name,
                color_sequence=model.color_sequence,
                start_step_index=model.start_step_index,
                walking_order_colors=model.walking_order_colors,
                walking_order_start=model.walking_order_start,
                a=config.a,
                b=config.b,
                c=config.c,
                d=config.d,
                step_length=config.step_length,
            )
            ConfigExporter.export_to_file(session_config, file_path)
            logger.info(f"配置已导出: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"配置导出失败: {e}")
            return False
    
    def import_config(self, file_path: str) -> "SessionConfig | None":
        """
        导入配置文件
        
        Args:
            file_path: 配置文件路径
            
        Returns:
            会话配置，如果导入失败则返回 None
        """
        from core.config_io import ConfigExporter
        
        session_config = ConfigExporter.import_from_file(file_path)
        if session_config is None:
            logger.error(f"导入配置失败: {file_path}")
            return None
        
        logger.info(f"配置已导入: {file_path}")
        return session_config
