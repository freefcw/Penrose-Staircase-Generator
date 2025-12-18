"""
生成 Penrose Staircase 应用图标
"""
from PIL import Image, ImageDraw
import math

def create_icon(size: int = 1024) -> Image.Image:
    """创建应用图标"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 背景渐变（深紫到蓝色）
    for y in range(size):
        r = int(60 + (40 - 60) * y / size)
        g = int(20 + (80 - 20) * y / size)  
        b = int(120 + (180 - 120) * y / size)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # 圆角遮罩
    corner_radius = size // 5
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(0, 0), (size-1, size-1)], 
        radius=corner_radius, 
        fill=255
    )
    img.putalpha(mask)
    
    # 绘制 Penrose 楼梯（简化版）
    center_x = size // 2
    center_y = size // 2
    
    # 楼梯颜色
    colors = [
        (200, 180, 230, 255),  # 淡紫色
        (180, 200, 240, 255),  # 淡蓝色
        (160, 220, 220, 255),  # 青色
        (220, 200, 180, 255),  # 米色
    ]
    
    # 绘制四段楼梯
    step_size = size // 8
    
    # 楼梯段定义（简化的等距视角）
    segments = [
        # 上方楼梯（向右上）
        [(center_x - step_size*2, center_y - step_size),
         (center_x, center_y - step_size*2),
         (center_x + step_size, center_y - step_size*1.5),
         (center_x - step_size, center_y - step_size*0.5)],
        # 右边楼梯（向右下）
        [(center_x + step_size, center_y - step_size*1.5),
         (center_x + step_size*2, center_y),
         (center_x + step_size*1.5, center_y + step_size),
         (center_x + step_size*0.5, center_y - step_size*0.5)],
        # 下方楼梯（向左下）
        [(center_x + step_size*1.5, center_y + step_size),
         (center_x, center_y + step_size*2),
         (center_x - step_size, center_y + step_size*1.5),
         (center_x + step_size*0.5, center_y + step_size*0.5)],
        # 左边楼梯（向左上）
        [(center_x - step_size, center_y + step_size*1.5),
         (center_x - step_size*2, center_y),
         (center_x - step_size*1.5, center_y - step_size),
         (center_x - step_size*0.5, center_y + step_size*0.5)],
    ]
    
    # 绘制每段楼梯（作为多边形）
    for i, seg in enumerate(segments):
        pts = [(int(p[0]), int(p[1])) for p in seg]
        draw.polygon(pts, fill=colors[i], outline=(80, 60, 100, 255))
    
    # 中心绘制一个小的 Penrose 三角
    tri_size = step_size * 0.8
    tri_points = [
        (center_x, center_y - tri_size * 0.6),
        (center_x + tri_size * 0.5, center_y + tri_size * 0.3),
        (center_x - tri_size * 0.5, center_y + tri_size * 0.3),
    ]
    draw.polygon([(int(p[0]), int(p[1])) for p in tri_points], 
                 fill=(255, 255, 255, 200), 
                 outline=(100, 80, 140, 255))
    
    return img


def main():
    # 生成 1024x1024 PNG
    icon = create_icon(1024)
    icon.save('assets/icon.png')
    print("图标已生成: assets/icon.png")
    
    # 生成 512x512 版本
    icon_512 = icon.resize((512, 512), Image.Resampling.LANCZOS)
    icon_512.save('assets/icon-512.png')
    print("图标已生成: assets/icon-512.png")


if __name__ == "__main__":
    main()
