#-----------------------------------------------------------------#
# The Penrose-Staircase-Module v1.2 for PYTHON                    #
# (c) 2022, 2024, F. Lehr  ferdinand@ferdinandlehr.de             #
# https://www.ferdinandlehr.de                                    #
# https://github.com/fl3000/Penrose-Staircase-Generator           #
#                                                                 #
# Module for calculating the n-th Penrose-Staircase.              #
#                                                                 #
# usage of this module:                                           #
#                                                                 #
#        import pstairs                                           #
#        p = pstairs.PenroseStaircase(n)                          #
#        A = p.a                                                  #
#        B = p.b                                                  #
#        C = p.c                                                  #
#        D = p.d                                                  #
#        L = p.l                                                  #
#-----------------------------------------------------------------#
from __future__ import annotations

import math


class PenroseStaircase:
    """Penrose 楼梯数学计算器

    计算第 n 个 Penrose 楼梯的参数 (a, b, c, d, l, g)。

    算法原理：
    - Penrose 楼梯是一种"不可能图形"，由四边构成循环上升的视觉错觉
    - 每个楼梯由参数 (a, b, c, d, l, g) 唯一确定
    - a, b, c, d: 四个边的台阶数
    - l: 台阶长度 (step length)
    - g: 楼梯和 (stairsum) = a + b + c + d，总是偶数

    算法来源: F. Lehr - Algorithm_Penrose-Stairs_flehr.pdf

    Attributes:
        a: A区台阶数（左上，上升）
        b: B区台阶数（右上，水平）
        c: C区台阶数（右下，下降）
        d: D区台阶数（左下，水平）
        l: 台阶长度
        g: 楼梯和
        valid: 是否为有效楼梯

    Example:
        >>> ps = PenroseStaircase(190)
        >>> print(ps.a, ps.b, ps.c, ps.d, ps.l)
        8 5 2 7 3.0
    """

    # 迭代上限常量（用于序列查找算法）
    _MAX_ITERATIONS: int = 100_000_000
    def P2(self, g: int) -> int:
        """计算给定楼梯和对应的楼梯数量

        Args:
            g: 楼梯和（stairsum，总是偶数）

        Returns:
            该楼梯和对应的 Penrose 楼梯数量
        """
        c = 0
        p = 1
        k = 2
        i = 6
        while i <= g:
            c = 0
            for j in range(p):
                c += 1
            p += k
            k = k + 1
            i += 2
        return c


    def tz(self, n: int) -> int:
        """计算前 n 个楼梯和对应的楼梯总数

        Args:
            n: 楼梯和序号上限

        Returns:
            累计楼梯数量
        """
        r = 0
        for i in range(1, n + 1):
            r += self.P2(2 * i + 4)
        return int(r)

    def NG(self, n: int) -> int:
        """计算第 n 个楼梯和的值

        公式: g = 2n + 4

        Args:
            n: 楼梯和序号

        Returns:
            楼梯和值
        """
        return n * 2 + 4

    def SNP(self, n: int) -> int:
        """计算第 n 个楼梯的楼梯和

        Stairsum of N-th Pstair

        Args:
            n: 楼梯序号

        Returns:
            对应的楼梯和
        """
        k = 1
        while self.tz(k) < n:
            k = k + 1
        return self.NG(k)

    def SBG(self, g: int) -> int:
        """计算到给定楼梯和为止有多少个楼梯和

        Stairsums Before G (含 g)

        Args:
            g: 目标楼梯和

        Returns:
            楼梯和数量
        """
        n = 1
        while self.NG(n) < g:
            n = n + 1
        return n

    def LONP(self, n: int) -> float:
        """计算第 n 个楼梯的台阶长度

        Length Of N-th Pstair

        Args:
            n: 楼梯序号

        Returns:
            台阶长度 L
        """
        g = self.SNP(n)
        rpos = self.P2(g)
        m = int((g - 4) / 2)  # d=l 出现的次数
        tpos = self.tz(self.SBG(g))
        u = m
        for j in range(m + 1):
            d = 1  # divisor
            l: float = -1  # length
            for i in range(u):
                l = g / d
                d = d + 1
                tpos -= 1
                if (tpos + 1) == n:
                    return l
            u = u - 1
        return -1  # 不应到达此处
       
    def AINC(self, p: int) -> int:
        """生成 A 区台阶数序列: 3,4,4,5,5,5,6,6,6,6,...

        A-Increment 序列生成器

        Args:
            p: 序列位置 (1-indexed)

        Returns:
            对应位置的 A 值
        """
        c = 0
        for i in range(1, self._MAX_ITERATIONS + 1):
            for k in range(1, i + 1):
                c += 1
                if c == p:
                    return i + 2
        return -1  # 不应到达此处

         
    def A_of_NP(self, n: int) -> int:
        """计算第 n 个楼梯的 A 区台阶数 (迭代算法)

        Args:
            n: 楼梯序号

        Returns:
            A 区台阶数
        """
        g = self.SNP(n)
        rpos = self.P2(g)
        tpos = self.tz(self.SBG(g) - 1) + 1
        return self.AINC(n - tpos + 1)

    def B_of_NP(self, n: int) -> int:
        """计算第 n 个楼梯的 B 区台阶数 (迭代算法)

        Args:
            n: 楼梯序号

        Returns:
            B 区台阶数
        """
        a = self.A_of_NP(n)
        g = self.SNP(n)
        return int(((g + 4) / 2) - a)

    def CINC(self, p: int) -> int:
        """生成 C 区台阶数序列: 2,2,3,2,3,4,2,3,4,5,2...

        C-Increment 序列生成器

        Args:
            p: 序列位置 (1-indexed)

        Returns:
            对应位置的 C 值
        """
        c = 0
        for i in range(1, self._MAX_ITERATIONS + 1):
            for k in range(1, i + 1):
                c += 1
                if c == p:
                    return k + 1
        return -1  # 不应到达此处

    def C_of_NP(self, n: int) -> int:
        """计算第 n 个楼梯的 C 区台阶数 (迭代算法)

        Args:
            n: 楼梯序号

        Returns:
            C 区台阶数
        """
        g = self.SNP(n)
        rpos = self.P2(g)
        tpos = self.tz(self.SBG(g) - 1) + 1
        return self.CINC(n - tpos + 1)

    def D_of_NP(self, n: int) -> int:
        """计算第 n 个楼梯的 D 区台阶数 (迭代算法)

        D = a + b - c

        Args:
            n: 楼梯序号

        Returns:
            D 区台阶数
        """
        a = self.A_of_NP(n)
        b = self.B_of_NP(n)
        c = self.C_of_NP(n)
        return a + b - c

    def DIRECT_A(self, n: int) -> int:
        """计算第 n 个楼梯的 A 区台阶数 (直接公式)

        使用数学封闭公式直接计算，无需迭代

        Args:
            n: 楼梯序号

        Returns:
            A 区台阶数
        """
        if n == 1:
            self.a = 3
        elif n > 1:
            self.a = math.floor(1/6*math.sqrt(72*n - 63 -
                (12*math.floor(6**(1/3)*(n - 1)**(1/3)
                + 1/18*6**(2/3)/(n - 1)**(1/3)) - 12)*
                math.floor(6**(1/3)*(n - 1)**(1/3) +
                1/18*6**(2/3)/(n - 1)**(1/3))*(math.floor(
                6**(1/3)*(n - 1)**(1/3) + 1/18*6**(2/3)/(n -
                1)**(1/3)) + 1)) + 1/2) + 2
        return self.a
    
    def DIRECT_B(self, n: int) -> int:
        """计算第 n 个楼梯的 B 区台阶数 (直接公式)

        Args:
            n: 楼梯序号

        Returns:
            B 区台阶数
        """
        if n == 1:
            self.b = 2
        elif n > 1:
            self.b = math.floor(6**(1/3)*(n - 1)**(1/3) + 1/18*6**(2/3)/(n -
                1)**(1/3)) + 2 - math.floor(1/6*math.sqrt(72*n - 63 -
                (12*math.floor(6**(1/3)*(n - 1)**(1/3) + 1/18*6**(2/3)/(n -
                1)**(1/3)) - 12)*math.floor(6**(1/3)*(n - 1)**(1/3) +
                1/18*6**(2/3)/(n - 1)**(1/3))*(math.floor(6**(1/3)*(n -
                1)**(1/3) + 1/18*6**(2/3)/(n - 1)**(1/3)) + 1)) + 1/2)
        return self.b

    def DIRECT_C(self, n: int) -> float:
        """计算第 n 个楼梯的 C 区台阶数 (直接公式)

        Args:
            n: 楼梯序号

        Returns:
            C 区台阶数
        """
        if n == 1:
            self.c = 2
        elif n > 1:
            self.c = n + 1 - 1/6*(math.floor(6**(1/3)*(n - 1)**(1/3) +
                1/18*6**(2/3)/(n - 1)**(1/3)) - 1)*math.floor(6**(1/3)*(n -
                1)**(1/3) + 1/18*6**(2/3)/(n - 1)**(1/3))*(math.floor(6**(
                1/3)*(n - 1)**(1/3) + 1/18*6**(2/3)/(n - 1)**(1/3)) + 1) - \
                1/2*(math.floor(1/6*math.sqrt(72*n - 63 - (12*math.floor(6**(
                1/3)*(n - 1)**(1/3) + 1/18*6**(2/3)/(n - 1)**(1/3)) - 12)*
                math.floor(6**(1/3)*(n - 1)**(1/3) + 1/18*6**(2/3)/(n -
                1)**(1/3))*(math.floor(6**(1/3)*(n - 1)**(1/3) + 1/18*6**(
                2/3)/(n - 1)**(1/3)) + 1)) + 1/2) - 1)*math.floor(1/6*
                math.sqrt(72*n - 63 - (12*math.floor(6**(1/3)*(n - 1)**(1/3)
                + 1/18*6**(2/3)/(n - 1)**(1/3)) - 12)*math.floor(6**(1/3)*(n -
                1)**(1/3) + 1/18*6**(2/3)/(n - 1)**(1/3))*(math.floor(
                6**(1/3)*(n - 1)**(1/3) + 1/18*6**(2/3)/(n - 1)**(1/3)) + 1)) + 1/2)
        return self.c

    def DIRECT_D(self, n: int) -> int | float:
        """计算第 n 个楼梯的 D 区台阶数 (直接公式)

        D = a + b - c

        Args:
            n: 楼梯序号

        Returns:
            D 区台阶数
        """
        self.a = self.DIRECT_A(n)
        self.b = self.DIRECT_B(n)
        self.c = self.DIRECT_C(n)
        return self.a + self.b - self.c

    def DIRECT_G(self, n: int) -> int:
        """计算第 n 个楼梯的楼梯和 (直接公式)

        Args:
            n: 楼梯序号

        Returns:
            楼梯和 g
        """
        if n == 1:
            self.g = 6
        elif n > 1:
            self.g = 4 + 2*math.floor(6**(1/3)*(n - 1)**(1/3) +
                1/18*6**(2/3)/(n - 1)**(1/3))
        return self.g
    
    def DIRECT_L(self, n: int) -> float:
        """计算第 n 个楼梯的台阶长度 (直接公式)

        Args:
            n: 楼梯序号

        Returns:
            台阶长度 l
        """
        return self.DIRECT_G(n) / ((self.DIRECT_A(n)/2) -
            (self.DIRECT_B(n)/2) - (self.DIRECT_C(n)/2) + (self.DIRECT_D(n)/2))

    def PStair_nth_v10(self, n: int) -> None:
        """计算第 n 个楼梯的所有参数 (v1.0 迭代算法)

        已废弃，仅保留以保持兼容性

        Args:
            n: 楼梯序号
        """
        self.a = self.A_of_NP(n)
        self.b = self.B_of_NP(n)
        self.c = self.C_of_NP(n)
        self.d = self.a + self.b - self.c
        self.g = self.SNP(n)
        self.l = self.LONP(n)
        
    def PStair_nth(self, n: int) -> None:
        """计算第 n 个楼梯的所有参数 (v1.1 直接公式)

        设置实例属性: a, b, c, d, g, l

        Args:
            n: 楼梯序号
        """
        self.a = self.DIRECT_A(n)
        self.b = self.DIRECT_B(n)
        self.c = int(self.DIRECT_C(n))
        self.d = self.a + self.b - self.c
        self.g = int(self.DIRECT_G(n))
        self.l = self.g / ((self.a/2) - (self.b/2) - (self.c/2) + (self.d/2))

    # 实例属性声明
    a: int
    b: int
    c: int | float  # DIRECT_C 返回 float，PStair_nth 中转为 int
    d: int
    g: int
    l: float
    valid: bool

    def __init__(self, n: int) -> None:
        """初始化 Penrose 楼梯计算器

        Args:
            n: 楼梯序号（必须为正整数）

        Example:
            >>> ps = PenroseStaircase(190)
            >>> ps.valid
            True
            >>> ps.a
            8
        """
        self.valid = False
        if isinstance(n, int) and n > 0:
            self.PStair_nth(n)
            self.valid = True
