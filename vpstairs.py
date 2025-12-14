#-----------------------------------------------------------------#
# The Penrose-Staircase-Viewer v1.0 for PYTHON                    #
# (c) 2022 F. Lehr    ferdinand@ferdinandlehr.de                  #
# https://www.ferdinandlehr.de                                    #
# https://github.com/fl3000/Penrose-Staircase-Generator           #
#                                                                 #
# usage: python vpstairs.py -n <the n-th Penrose-Staircase>       #
#-----------------------------------------------------------------#

import sys
import math
import random
import os
import pstairs
from graphics import *
from PIL import Image, EpsImagePlugin

# 设置 Ghostscript 路径 (macOS 通常在 /usr/local/bin/gs 或通过 brew 安装)
# 如果没有安装 Ghostscript，可通过 `brew install ghostscript` 安装
EpsImagePlugin.gs_windows_binary = None  # 非 Windows 系统

def save_as_image(win, filename):
    """将图形窗口保存为 PNG 图片"""
    # 先保存为 PostScript 格式
    ps_filename = filename.replace('.png', '.ps')
    win.postscript(file=ps_filename, colormode='color')
    
    # 使用 PIL 转换为 PNG
    try:
        img = Image.open(ps_filename)
        img.save(filename, 'PNG')
        os.remove(ps_filename)  # 删除临时 PS 文件
        print(f"图片已保存: {filename}")
    except Exception as e:
        print(f"保存图片失败: {e}")
        print(f"PostScript 文件已保存: {ps_filename}")
        print("提示: 如需转换为 PNG，请安装 Ghostscript: brew install ghostscript")



def rotate2D(x,y,w):
    x2 = x*math.cos(math.radians(w)) - y*math.sin(math.radians(w))
    y2 = x*math.sin(math.radians(w)) + y*math.cos(math.radians(w))
    return Point(x2,y2)

def getFinalPoint(x,y):
    p2=rotate2D(x,y,30)
    return Point(p2.x*ZM+XO,p2.y*ZM*0.8+YO)

def MOVEREL(x,y):
    global xc, yc
    xc+=x
    yc+=y

def MOVETO(x,y):
    global xc, yc
    xc=x
    yc=y
    
def LINETO(x,y):
    global xc, yc, zm
    p1 = getFinalPoint(xc,-yc)
    PLIST.append(p1)
    xc=x
    yc=y
    p2=getFinalPoint(x,-y)
    PLIST.append(p2)

def LINEREL(x,y):
    global xc, yc, zm
    p1=getFinalPoint(xc,-yc)
    PLIST.append(p1)
    xc+=x
    yc+=y
    p2=getFinalPoint(xc,-yc)
    PLIST.append(p2)

def CLOSEPOLY(color):
    p = Polygon(PLIST)
    p.setFill(color)
    p.draw(win)
    PLIST.clear()

def S(l,x,y,skip_record=False,draw_diag=False):
    global STEP_COLORS, STEP_POSITIONS, CURRENT_STEP_INDEX
    PLIST.clear()
    # 台阶四个角点
    p1 = (x, y)
    p2 = (x+U*0.5*l, y+(H*l))
    p3 = (x+U*0.5*l+U*l, y+(H*l))
    p4 = (x+U*l, y)
    
    MOVETO(*p1)
    LINETO(*p2)
    LINETO(*p3)
    LINETO(*p4)
    
    # 使用预生成的颜色序列
    if not skip_record and CURRENT_STEP_INDEX < len(STEP_COLORS):
        is_red = STEP_COLORS[CURRENT_STEP_INDEX]
        step_color = color_red if is_red else color_gray
    else:
        # 对于 skip_record 的台阶，随机选色
        is_red = random.choice([0, 1])
        step_color = color_red if is_red else color_gray
    CLOSEPOLY(step_color)
    
    # 记录位置并检查是否绘制对角线（除非 skip_record）
    if not skip_record:
        # 检查是否是起点台阶
        if CURRENT_STEP_INDEX == START_STEP_INDEX:
            sp1 = getFinalPoint(p1[0], -p1[1])
            sp2 = getFinalPoint(p2[0], -p2[1])
            sp3 = getFinalPoint(p3[0], -p3[1])
            sp4 = getFinalPoint(p4[0], -p4[1])
            line_width = max(1, int(ZM / 8))
            line1 = Line(sp1, sp3)
            line1.setOutline("white")
            line1.setWidth(line_width)
            line1.draw(win)
            line2 = Line(sp2, sp4)
            line2.setOutline("white")
            line2.setWidth(line_width)
            line2.draw(win)
        
        STEP_POSITIONS.append((p1, p2, p3, p4))
        CURRENT_STEP_INDEX += 1

def drawStepsA(x,y,len):
    # A 区绘制 A 个台阶，但只有 A-1 个是真正的台阶（第一个是共享的起始/结束台阶）
    for i in range(A-1,-1,-1):
        S(len,x+((U*0.5*L)*i+(U/2)*i),y+(((H*L)-H)*i), skip_record=(i == 0))

def drawStepsB(x,y,len):
    for j in range(1,B,1):
        S(L,x+((U*0.5*L)*(A-1)+(U/2)*(A-1)+(L*1+U/2)*j),y+(((H*L)-H)*(A-1)-j*H))

def drawStepsC(x,y,len):
    for k in range(1,C,1):
        xx1 = ((U*0.5*L)*(A-1)+(U/2)*(A-1)+(L*1+U/2)*(B-1))
        yy1 = (((H*L)-H)*(A-1)-(B-1)*H)
        S(L,x+(xx1-L*U*0.5*k+(U/2)*k),y+(yy1-k*H*(L+1))) # z (A+B+C+D+2)]

def drawStepsD(x,y,len):
    for m in range(D-1,0,-1):
        xx1 = ((U*0.5*L)*(A-1)+(U/2)*(A-1)+(L*1+U/2)*(B-1))
        yy1 = (((H*L)-H)*(A-1)-(B-1)*H)
        xxx1 = (xx1-L*U*0.5*(C-1)+(U/2)*(C-1))
        yyy1 = (yy1-(C-1)*H*(L+1))
        S(len,x+(xxx1-L*U*m+(U/2)*m),y+(yyy1-H*m)) # z (-m+A+B+C+D+1)]

def stair_rect_D(x,y):
    PLIST.clear()
    MOVETO(x,y)
    LINETO(x+(U*L),y+0)
    LINEREL((U/2),(-H))
    LINEREL((-U*L),0)
    global color2
    CLOSEPOLY(color2)

def stair_rect_C(x,y):
    PLIST.clear()
    MOVETO(x,y)
    LINETO(x+U*L*0.5,y+H*L)
    LINEREL(U/2,-H)
    LINEREL(-U*L*0.5,-H*L)
    global color3
    CLOSEPOLY(color3)

def inner_wall2(x,y):
    PLIST.clear()
    MOVETO(x,y)
    MOVEREL(L*U+L*U*0.5+U/2,H*L-H)
    for n in range(1,A,1):
        MOVEREL(L*U*0.5,H*L)
        MOVEREL(U*0.5,-H)

    MOVEREL(-L*0.5*U,-H*L)
    for m in range(1,B-1,1):
        LINEREL(L*U,0)
        LINEREL(U*0.5,-H)

    LINEREL(L,0)
    LINEREL(U*0.5,-H)
    LINEREL(-L,0)
    LINEREL(U*WH*0.5-(B*U*0.5),-H*WH+H*B)
    LINEREL(-L*U*(B-2)+U*0.5,-H)
    global color2
    CLOSEPOLY(color2)

def front_wall(x,y):
    MOVETO(x,y)
    for i in range(1,D,1):
        LINEREL(L,0)
        LINEREL(-U*0.5,H)

    LINEREL(L,0)
    LINEREL(U*WH*0.5,-H*WH)
    LINEREL(-U*D*L,0)
    global color2
    CLOSEPOLY(color2)

def mid_wall2(x,y):
    MOVETO(x,y)
    MOVEREL(L*U+L*U*0.5+U/2,H*L-H)
    for n in range(1,A,1):
        LINEREL(L*U*0.5,H*L)
        LINEREL(U*0.5,-H)

    LINEREL(-L*0.5*U,-H*L)
    LINEREL(U*WH*0.5,-H*WH)
    LINEREL(-U*0.5*L*(C-1),-H*L*(C-1))
    global color3
    CLOSEPOLY(color3)

def right_wall(x,y):
    MOVETO(x,y)

    for i in range(1,D,1):
        MOVEREL(L,0)
        MOVEREL(-U*0.5,H)

    MOVEREL(L,0)
    for i in range(1,C,1):
        LINEREL(L*U*0.5,H*L)
        LINEREL(-U*0.5,H)

    LINEREL(L*U*0.5,H*L)
    for j in range(1,C,1):
        LINEREL(U*0.5,-H)

    LINEREL(U*WH*0.5,-H*WH)
    LINEREL(-U*0.5*L*C,-H*L*C)
    global color3
    CLOSEPOLY(color3)

def drawStairRectsC(x,y):
    for n in range(2,B,1):
        px = ((U*0.5*L)*(A-1)+(U/2)*(A-1)) + L*U*n + (n-1)*(U/2)
        py = (((H*L)-H)*(A-1))-H*(n-1)
        stair_rect_C(x+px,y+py)
        
def drawStairRectsD(x,y):
    for o in range(1,C-1,1):
        px = ((U*0.5*L)*(A-1)+(U/2)*(A-1)) + L*U*B + (B-1)*(U/2) - L*U
        py = (((H*L)-H)*(A-1))-H*(B-1)
        stair_rect_D(x+(px-L*U*0.5*o+(U/2)*o),y+(py-(L+1)*H*o))
    
def draw_footprint(step_index):
    """在指定台阶上绘制对角线标记"""
    global STEP_POSITIONS, START_STEP_INDEX
    START_STEP_INDEX = step_index
    if step_index < len(STEP_POSITIONS):
        p1, p2, p3, p4 = STEP_POSITIONS[step_index]
        # 转换为屏幕坐标
        sp1 = getFinalPoint(p1[0], -p1[1])
        sp2 = getFinalPoint(p2[0], -p2[1])
        sp3 = getFinalPoint(p3[0], -p3[1])
        sp4 = getFinalPoint(p4[0], -p4[1])
        
        line_width = max(1, int(ZM / 8))
        # 绘制对角线 1: p1 -> p3
        line1 = Line(sp1, sp3)
        line1.setOutline("white")
        line1.setWidth(line_width)
        line1.draw(win)
        # 绘制对角线 2: p2 -> p4
        line2 = Line(sp2, sp4)
        line2.setOutline("white")
        line2.setWidth(line_width)
        line2.draw(win)

def draw_sequence(start_y, scale_factor=1, show_decimal=False):
    """在图形下方绘制颜色序列，每行6个，带边框
    
    Args:
        start_y: 起始Y坐标
        scale_factor: 缩放因子
        show_decimal: 是否在每行下方显示十进制转换值（前3位和后3位）
    """
    global STEP_COLORS, START_STEP_INDEX, XH
    
    total_steps = len(STEP_COLORS)
    if total_steps == 0:
        return
    
    # 绘制顺序: A区(A-1个) → D区(D-1个) → B区(B-1个) → C区(C-1个)
    # 行走顺序: D区 → C区 → B区 → A区
    # 需要重新映射
    a_count = A - 1  # 8
    d_count = D - 1  # 8
    b_count = B - 1  # 4
    c_count = C - 1  # 4
    
    # 绘制顺序索引范围:
    # A区: 0 ~ a_count-1 (0-7)
    # D区: a_count ~ a_count+d_count-1 (8-15)
    # B区: a_count+d_count ~ a_count+d_count+b_count-1 (16-19)
    # C区: a_count+d_count+b_count ~ 末尾 (20-23)
    
    # 按行走顺序重排: D → C → B → A
    walking_order = []
    # D区 (绘制索引 a_count ~ a_count+d_count-1)
    walking_order.extend(STEP_COLORS[a_count:a_count+d_count])
    # C区 (绘制索引 a_count+d_count+b_count ~ 末尾) - 需要反转
    walking_order.extend(list(reversed(STEP_COLORS[a_count+d_count+b_count:])))
    # B区 (绘制索引 a_count+d_count ~ a_count+d_count+b_count-1) - 需要反转
    walking_order.extend(list(reversed(STEP_COLORS[a_count+d_count:a_count+d_count+b_count])))
    # A区 (绘制索引 0 ~ a_count-1)
    walking_order.extend(STEP_COLORS[0:a_count])
    
    # 计算起点在行走顺序中的位置
    # START_STEP_INDEX 是绘制顺序中的索引，需要转换
    # 注意：B区和C区在构建walking_order时被反转了，所以索引也需要反转
    if START_STEP_INDEX < a_count:
        # 在A区 → 行走顺序中A在最后
        walking_start = d_count + c_count + b_count + START_STEP_INDEX
    elif START_STEP_INDEX < a_count + d_count:
        # 在D区 → 行走顺序中D在最前
        walking_start = START_STEP_INDEX - a_count
    elif START_STEP_INDEX < a_count + d_count + b_count:
        # 在B区 → 行走顺序中B在C后面，且B区被反转
        position_in_b = START_STEP_INDEX - a_count - d_count
        walking_start = d_count + c_count + (b_count - 1 - position_in_b)
    else:
        # 在C区 → 行走顺序中C在D后面，且C区被反转
        position_in_c = START_STEP_INDEX - a_count - d_count - b_count
        walking_start = d_count + (c_count - 1 - position_in_c)
    
    # 从起点开始重排序列，完整循环一周
    if walking_start >= 0 and walking_start < total_steps:
        ordered = walking_order[walking_start:] + walking_order[:walking_start]
    else:
        ordered = walking_order[:]
    
    # 调试日志
    print(f"[DEBUG] 行走顺序颜色: {walking_order}")
    print(f"[DEBUG] 起点索引(行走顺序): {walking_start}")
    print(f"[DEBUG] 从起点开始的序列: {ordered}")
    
    box_size = 20 * scale_factor
    margin = 5 * scale_factor
    cols = 6
    start_x = (XH - (cols * (box_size + margin))) / 2
    
    # 计算行高：如果显示十进制，每行需要额外高度
    row_height = box_size + margin
    if show_decimal:
        row_height = box_size + margin + 15 * scale_factor  # 额外空间给十进制数字
    
    # 显示台阶数量提示
    hint = Text(Point(XH/2, start_y - 15 * scale_factor), f"台阶序列 (共{total_steps}级, 从★开始)")
    hint.setSize(min(12 * scale_factor, 30))
    hint.setTextColor("black")
    hint.draw(win)
    
    num_rows = (len(ordered) + cols - 1) // cols
    
    for i, color_val in enumerate(ordered):
        row = i // cols
        col = i % cols
        x = start_x + col * (box_size + margin)
        y = start_y + row * row_height
        
        # 绘制边框
        rect = Rectangle(Point(x, y), Point(x + box_size, y + box_size))
        rect.setOutline("black")
        rect.setWidth(max(1, scale_factor))
        if color_val == 1:
            rect.setFill(color_rgb(220, 60, 60))  # 红色
        else:
            rect.setFill(color_rgb(128, 128, 128))  # 灰色
        rect.draw(win)
        
        # 绘制数字
        text = Text(Point(x + box_size/2, y + box_size/2), str(color_val))
        text.setSize(min(int(12 * scale_factor), 36))
        text.setTextColor("white")
        text.draw(win)
    
    # 绘制十进制转换值
    if show_decimal:
        for row in range(num_rows):
            row_start_idx = row * cols
            row_end_idx = min(row_start_idx + cols, len(ordered))
            row_data = ordered[row_start_idx:row_end_idx]
            
            if len(row_data) >= 6:
                # 前3位转十进制
                first_3 = row_data[0:3]
                first_decimal = first_3[0] * 4 + first_3[1] * 2 + first_3[2] * 1
                
                # 后3位转十进制
                last_3 = row_data[3:6]
                last_decimal = last_3[0] * 4 + last_3[1] * 2 + last_3[2] * 1
                
                # 十进制数字的Y位置（在方块下方）
                decimal_y = start_y + row * row_height + box_size + 2 * scale_factor
                decimal_box_height = 12 * scale_factor
                
                # 前3个方块的边框（宽度覆盖3个方块）
                first_box_x1 = start_x
                first_box_x2 = start_x + 3 * (box_size + margin) - margin
                first_center_x = (first_box_x1 + first_box_x2) / 2
                
                # 绘制前3位的边框
                rect1 = Rectangle(Point(first_box_x1, decimal_y), Point(first_box_x2, decimal_y + decimal_box_height))
                rect1.setOutline("black")
                rect1.setFill("white")
                rect1.draw(win)
                
                # 绘制前3位的数字
                text1 = Text(Point(first_center_x, decimal_y + decimal_box_height/2), str(first_decimal))
                text1.setSize(min(int(10 * scale_factor), 24))
                text1.setTextColor("black")
                text1.draw(win)
                
                # 后3个方块的边框
                last_box_x1 = start_x + 3 * (box_size + margin)
                last_box_x2 = start_x + 6 * (box_size + margin) - margin
                last_center_x = (last_box_x1 + last_box_x2) / 2
                
                # 绘制后3位的边框
                rect2 = Rectangle(Point(last_box_x1, decimal_y), Point(last_box_x2, decimal_y + decimal_box_height))
                rect2.setOutline("black")
                rect2.setFill("white")
                rect2.draw(win)
                
                # 绘制后3位的数字
                text2 = Text(Point(last_center_x, decimal_y + decimal_box_height/2), str(last_decimal))
                text2.setSize(min(int(10 * scale_factor), 24))
                text2.setTextColor("black")
                text2.draw(win)

def drawStaircase(x,y,step_len):
    """绘制楼梯，先生成完整颜色序列，再按序列绘制台阶"""
    global STEP_COLORS, STEP_POSITIONS, START_STEP_INDEX, CURRENT_STEP_INDEX
    STEP_POSITIONS = []
    CURRENT_STEP_INDEX = 0
    
    # 先计算总台阶数
    total_steps = A + B + C + D - 4
    
    # 生成完整的颜色序列
    STEP_COLORS = [random.choice([0, 1]) for _ in range(total_steps)]
    
    # 随机选择起点
    START_STEP_INDEX = random.randint(0, total_steps - 1)
    
    # 调试日志
    print(f"[DEBUG] 总台阶数: {total_steps} (A={A-1}, D={D-1}, B={B-1}, C={C-1})")
    print(f"[DEBUG] 起点索引(绘制顺序): {START_STEP_INDEX}")
    print(f"[DEBUG] 颜色序列(绘制顺序): {STEP_COLORS}")
    
    drawStepsA(x,y,step_len)

    inner_wall2(x,y)
    mid_wall2(x,y)
    drawStepsD(x,y,step_len)
    drawStepsB(x,y,step_len)
    drawStepsC(x,y,step_len)
    drawStairRectsD(x,y)
    drawStairRectsC(x,y)
    front_wall(x,y)
    right_wall(x,y)
    
    # 绘制 ABCD 区域标签
    draw_zone_labels()
    
    return START_STEP_INDEX

def draw_zone_labels():
    """在四个区域绘制 A、B、C、D 标签"""
    global win, XH, YH, ZM
    
    font_size = max(16, int(ZM / 1.5))
    
    # 使用窗口相对位置，更简单可靠
    # A区: 左上角
    label_a = Text(Point(80, 40), "A")
    label_a.setSize(font_size)
    label_a.setTextColor("black")
    label_a.setStyle("bold")
    label_a.draw(win)
    
    # B区: 右上角
    label_b = Text(Point(XH - 80, 80), "B")
    label_b.setSize(font_size)
    label_b.setTextColor("black")
    label_b.setStyle("bold")
    label_b.draw(win)
    
    # C区: 右下角
    label_c = Text(Point(XH - 80, YH / 2), "C")
    label_c.setSize(font_size)
    label_c.setTextColor("black")
    label_c.setStyle("bold")
    label_c.draw(win)
    
    # D区: 左下角
    label_d = Text(Point(100, YH / 2 - 50), "D")
    label_d.setSize(font_size)
    label_d.setTextColor("black")
    label_d.setStyle("bold")
    label_d.draw(win)

color1=color_rgb(0,255,0)
color2=color_rgb(0,0,255)
color3=color_rgb(255,255,0)
# 台阶随机颜色：灰色和红色
color_gray=color_rgb(128,128,128)
color_red=color_rgb(220,60,60)
# 记录每个台阶的颜色序列 (0=灰色, 1=红色) 和位置
STEP_COLORS = []
STEP_POSITIONS = []
START_STEP_INDEX = -1
CURRENT_STEP_INDEX = 0
XC=0
YC=0
U = 1
H = 0.866025404
#-------- RATIO ---------
ps = 0
A=0
B=0
C=0
D=0
L = 0
#------------------------
WH = 0
ZM = 0
PLIST=[]
XH = 0
YH = 0
XO = 0 #final x-offset
YO = 0 #final y-offset

win = 0

def main():
    #print ('Number of arguments:', len(sys.argv), 'arguments.')
    #print ('Argument List:', str(sys.argv))
    #print ('Argument 1:', str(sys.argv[1]))
    global YH
    global PS
    
    
    
    try:
        PS = pstairs.PenroseStaircase(int(sys.argv[1])) # calc the nth-PStair
    except IndexError:
        print ("Error: You did not specify n.")
        print ("usage: python vpstairs.py -n <the n-th Penrose-Staircase>")
        sys.exit(1)
    
    # 检查是否有 -s 缩放参数
    scale_factor = 1
    if "-s" in sys.argv:
        try:
            idx = sys.argv.index("-s")
            scale_factor = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            scale_factor = 1
    
    global A,B,C,D,L,WH,ZM,PLIST,XH,YH,XO,YO,win
    A=PS.a
    B=PS.b
    C=PS.c
    D=PS.d
    L = PS.l
    WH = D*2
    ZM = 11/((A+B+C+D+L-4)*0.1) * scale_factor  # 应用缩放因子
    PLIST=[]
    XH = (A*L+B*L)*ZM
    stair_height = (A*H*L+B*H*L)*ZM
    # 计算数列需要的额外高度 (台阶数量 / 6 行 * 每行高度)
    total_steps = A + B + C + D - 4  # 大约的台阶数
    seq_rows = (total_steps // 6) + 1
    seq_height = seq_rows * (40 * scale_factor) + 30 * scale_factor  # 增加行高以适应十进制显示
    YH = stair_height + seq_height
    XO = 10 * scale_factor  # 缩放偏移量
    YO = (A*L*H*0.5)*ZM  # final y-offset
    print("The Penrose-Staircase Nr.", int(sys.argv[1]), " is: ", A, B, C, D, "(", L, ")", f"缩放: {scale_factor}x")
    win = GraphWin("Penrose-Staircase Generator v1.0", XH,YH)
    drawStaircase(0,0,L)
    str = "n=",int(sys.argv[1]),"ratio:", A, B, C, D, "(",L,")"
    message = Text(Point(XH/2, 5 * scale_factor), str)
    message.setFace("courier")
    message.setSize(min(10 * scale_factor, 36))  # 字体大小最大36
    message.draw(win)
    
    # 绘制颜色序列（启用十进制转换显示）
    draw_sequence(stair_height + 10 * scale_factor, scale_factor, show_decimal=True)

    # 检查是否有 -o 参数指定输出文件
    output_file = None
    if "-o" in sys.argv:
        try:
            idx = sys.argv.index("-o")
            output_file = sys.argv[idx + 1]
        except (IndexError, ValueError):
            print("用法: python vpstairs.py <n> [-o <输出文件.png>]")
    
    if output_file:
        # 保存图片
        save_as_image(win, output_file)
    
    try:
        win.getMouse() # Pause to view result
    except GraphicsError:
        pass
    
    win.close()    # Close window when done

if __name__ == "__main__":
    main()
