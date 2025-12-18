"""
字体管理模块 - 统一管理中文字体注册和路径

将分散在 kivy_layout.py 和 kivy_canvas.py 中的字体处理逻辑集中管理
"""
from __future__ import annotations

import os
from functools import lru_cache


# 中文字体路径列表（按平台优先级排序）
_FONT_PATHS = [
    # Linux 中文字体
    '/usr/share/fonts/truetype/HarmonyOS_Sans_SC/HarmonyOS_Sans_SC_Regular.ttf',
    '/usr/share/fonts/truetype/HarmonyOS_Sans_SC/HarmonyOS_Sans_SC_Bold.ttf',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
    '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc',
    '/usr/share/fonts/sarasa/sarasa/SarasaGothicSC-Regular.ttf',
    '/usr/share/fonts/truetype/arphic/uming.ttc',
    '/usr/share/fonts/truetype/arphic/ukai.ttc',
    os.path.expanduser('~/.local/share/fonts/NotoSansCJKsc-Regular.otf'),
    # macOS 中文字体
    '/System/Library/Fonts/PingFang.ttc',
    '/System/Library/Fonts/STHeiti Light.ttc',
    '/System/Library/Fonts/Hiragino Sans GB.ttc',
    '/Library/Fonts/Arial Unicode.ttf',
    # Windows 中文字体
    'C:\\Windows\\Fonts\\msyh.ttc',
    'C:\\Windows\\Fonts\\simsun.ttc',
]

# 默认回退字体
_DEFAULT_FONT = 'Roboto'


@lru_cache(maxsize=1)
def get_chinese_font_path() -> str:
    """
    获取中文字体的完整路径
    
    返回第一个存在的中文字体路径，若无则返回默认字体名
    """
    for font_path in _FONT_PATHS:
        if os.path.exists(font_path):
            return font_path
    return _DEFAULT_FONT


@lru_cache(maxsize=1)
def register_chinese_font() -> str:
    """
    注册中文字体到 Kivy（延迟导入避免非 Kivy 环境报错）
    
    Returns:
        注册的字体名称，可用于 Kivy Label 的 font_name 参数
    """
    try:
        from kivy.core.text import LabelBase
    except ImportError:
        # 非 Kivy 环境，返回默认字体
        return _DEFAULT_FONT
    
    for font_path in _FONT_PATHS:
        if os.path.exists(font_path):
            try:
                LabelBase.register(name='ChineseFont', fn_regular=font_path)
                return 'ChineseFont'
            except Exception:
                continue
    
    return _DEFAULT_FONT


# 别名，便于导入
CHINESE_FONT_PATH = get_chinese_font_path()
