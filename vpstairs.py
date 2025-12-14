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

def S(l,x,y):
    PLIST.clear()
    MOVETO(x,y)
    LINETO(x+U*0.5*l,y+(H*l))
    LINETO(x+U*0.5*l+U*l,y+(H*l))
    LINETO(x+U*l,y+0)
    # 随机选择灰色或红色
    step_color = random.choice([color_gray, color_red])
    CLOSEPOLY(step_color)

def drawStepsA(x,y,len):
    for i in range(A-1,-1,-1):
        S(len,x+((U*0.5*L)*i+(U/2)*i),y+(((H*L)-H)*i))

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
    
def drawStaircase(x,y,len):
    drawStepsA(x,y,len)

    inner_wall2(x,y)
    mid_wall2(x,y)
    drawStepsD(x,y,len)
    drawStepsB(x,y,len)
    drawStepsC(x,y,len)
    drawStairRectsD(x,y)
    drawStairRectsC(x,y)
    front_wall(x,y)
    right_wall(x,y)

color1=color_rgb(0,255,0)
color2=color_rgb(0,0,255)
color3=color_rgb(255,255,0)
# 台阶随机颜色：灰色和红色
color_gray=color_rgb(128,128,128)
color_red=color_rgb(220,60,60)
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
    YH = (A*H*L+B*H*L)*ZM
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
