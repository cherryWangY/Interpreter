from tokens import TokenType, FUNC
import math
import matplotlib.pyplot as plt

# origin_x = 0
# origin_y = 0
# scale_x = 1.5
# scale_y = 0.75
# rot_rad = 1
# 背景颜色只能在开始时设置一次
# 颜色都用元组表示
bg_color = (0.9608, 0.9608, 0.8627)
dot_color = (1, 0.6471, 0)


# 根据start， end， step 生成元组
def GenerateT(fr, to, step):
    return tuple(range(int(fr), int(to) + 1, int(step)))


# 调整rgb值为matplotlib支持的格式 0-1
def CacuColor(color):
    return tuple(c / 255.0 for c in color)


# 实现具体函数的计算
def CacuFunc(content, func):
    # content 是元组时
    if isinstance(content, tuple):
        if func == FUNC.SIN:
            sin_values = tuple(math.sin(rad) for rad in content)
            return sin_values
        elif func == FUNC.COS:
            cos_values = tuple(math.cos(rad) for rad in content)
            return cos_values
        elif func == FUNC.TAN:
            tan_values = tuple(math.tan(rad) for rad in content)
            return tan_values
        elif func == FUNC.SQRT:
            sqrt_values = tuple(math.sqrt(value) for value in content)
            return sqrt_values
        elif func == FUNC.EXP:
            exp_values = tuple(math.exp(value) for value in content)
            return exp_values
        elif func == FUNC.LN:
            ln_values = tuple(math.log(value) for value in content)
            return ln_values
    # content 不是元组时
    else:
        if func == FUNC.SIN:
            return math.sin(content)
        elif func == FUNC.COS:
            return math.cos(content)
        elif func == FUNC.TAN:
            return math.tan(content)
        elif func == FUNC.SQRT:
            return math.sqrt(content)
        elif func == FUNC.EXP:
            return math.exp(content)
        elif func == FUNC.LN:
            return math.log(content)


# 计算语法树
def CacuSyntaxTree(root, temp=None):
    # 处理const和temp外都可能存在递归调用
    if root is None:
        print('Syntax tree is empty')
    # const 直接返回值
    if root.OpCode == TokenType.CONST_ID:
        if root.Content == "PI":
            return 3.1415926
        else:
            return float(root.Content)
    # T 返回变量（元组类型）
    elif root.OpCode == TokenType.T:
        return temp
    # func 返回函数计算后的结果
    elif root.OpCode == TokenType.FUNC:
        # content1 必须是值或者元组
        content1 = CacuSyntaxTree(root.Content[1], temp)
        return CacuFunc(content1, root.Content[0])
    elif root.OpCode == TokenType.PLUS:
        # 先计算好 content0 1
        content0 = CacuSyntaxTree(root.Content[0], temp)
        content1 = CacuSyntaxTree(root.Content[1], temp)
        # 对于content不同情况需要采取不同的计算方法
        if isinstance(content0, tuple) and isinstance(content1, tuple):
            return tuple(x + y for x, y in zip(content0, content1))
        elif isinstance(content0, tuple) and isinstance(content1, tuple) is False:
            return tuple(x + content1 for x in content0)
        elif isinstance(content0, tuple) is False and isinstance(content1, tuple):
            return tuple(content0 + y for y in content1)
        else:
            return content0 + content1
    elif root.OpCode == TokenType.MINUS:
        content0 = CacuSyntaxTree(root.Content[0], temp)
        content1 = CacuSyntaxTree(root.Content[1], temp)
        if isinstance(content0, tuple) and isinstance(content1, tuple):
            return tuple(x - y for x, y in zip(content0, content1))
        elif isinstance(content0, tuple) and isinstance(content1, tuple) is False:
            return tuple(x - content1 for x in content0)
        elif isinstance(content0, tuple) is False and isinstance(content1, tuple):
            return tuple(content0 - y for y in content1)
        else:
            return content0 - content1
    elif root.OpCode == TokenType.MUL:
        content0 = CacuSyntaxTree(root.Content[0], temp)
        content1 = CacuSyntaxTree(root.Content[1], temp)
        if isinstance(content0, tuple) and isinstance(content1, tuple):
            return tuple(x * y for x, y in zip(content0, content1))
        elif isinstance(content0, tuple) and isinstance(content1, tuple) is False:
            return tuple(x * content1 for x in content0)
        elif isinstance(content0, tuple) is False and isinstance(content1, tuple):
            return tuple(content0 * y for y in content1)
        else:
            return content0 * content1
    elif root.OpCode == TokenType.DIV:
        content0 = CacuSyntaxTree(root.Content[0], temp)
        content1 = CacuSyntaxTree(root.Content[1], temp)
        if isinstance(content0, tuple) and isinstance(content1, tuple):
            return tuple(x / y for x, y in zip(content0, content1))
        elif isinstance(content0, tuple) and isinstance(content1, tuple) is False:
            return tuple(x / content1 for x in content0)
        elif isinstance(content0, tuple) is False and isinstance(content1, tuple):
            return tuple(content0 / y for y in content1)
        else:
            return content0 / content1
    elif root.OpCode == TokenType.POWER:
        content0 = CacuSyntaxTree(root.Content[0], temp)
        content1 = CacuSyntaxTree(root.Content[1], temp)
        if isinstance(content0, tuple) and isinstance(content1, tuple):
            return tuple(x ** y for x, y in zip(content0, content1))
        elif isinstance(content0, tuple) and isinstance(content1, tuple) is False:
            return tuple(x ** content1 for x in content0)
        elif isinstance(content0, tuple) is False and isinstance(content1, tuple):
            return tuple(content0 ** y for y in content1)
        else:
            return content0 ** content1


# test CacuSyntaxTree
# root = MakeExprNode(TokenType.FUNC, FUNC.SQRT,
#                     MakeExprNode(TokenType.PLUS,
#                                  MakeExprNode(TokenType.CONST_ID, 15),
#                                  MakeExprNode(TokenType.T))
#                     )
# print(CacuSyntaxTree(root))


# 根据绘图语言中设置的参数调整x，y的坐标
def Modify(x_data: tuple, y_data: tuple, origin_x, origin_y, scale_x, scale_y, rot_rad):
    x_origin = tuple(x + origin_x for x in x_data)
    y_origin = tuple(y + origin_y for y in y_data)
    x_scale = tuple(x * scale_x for x in x_origin)
    y_scale = tuple(y * scale_y for y in y_origin)
    x_rot = tuple(x * math.cos(rot_rad) + y * math.sin(rot_rad) for x, y in zip(x_scale, y_scale))
    y_rot = tuple(y * math.cos(rot_rad) - x * math.sin(rot_rad) for x, y in zip(x_scale, y_scale))
    return x_rot, y_rot


# main
'''
fig, ax = plt.subplots()
draw ...
plt.show()
'''


# 画出所有点后暂停给定的时间
def drawNodes(ax, x_data, y_data, pause_time, color):
    # 使用 plt.scatter() 绘制点
    plt.scatter(x_data, y_data, color=color, marker='o')

    # 暂停给定时间
    plt.pause(pause_time)


# 设置坐标轴范围并隐藏坐标轴
def setAx(x_min, x_max, y_min, y_max, ax):
    # 反转y轴方向
    ax.invert_yaxis()

    # 设置坐标轴范围，保证不会缩小原先的坐标轴范围
    # 使得非delete的情况下能展示出所有的绘图结果
    xmin, xmax, ymin, ymax = plt.axis()
    if xmin < x_min:
        x_min = xmin
    if xmax > x_max:
        x_max = xmax
    if ymin < y_min:
        y_min = ymin
    if ymax > y_max:
        y_max = ymax
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_max, y_min)

    # 隐藏坐标轴
    # ax.axis('off')


# 不删除的单循环绘图
def singleLoopNoDelete(ax, x_data, y_data, color):
    # 获得X，Y轴的范围
    x_max = max(x_data) + 2
    x_min = min(x_data) - 2
    y_max = max(y_data) + 2
    y_min = min(y_data) - 2

    # 设置坐标轴
    setAx(x_min, x_max, y_min, y_max, ax)

    # 使用 plt.scatter() 绘制点
    plt.scatter(x_data, y_data, color=color, marker='o')
    # 暂停观看效果
    plt.pause(2)


# 删除效果的单循环绘图
def singleLoopDelete(ax, x_data, y_data, color, title=None):
    # 获得X，Y轴的范围
    x_max = max(x_data) + 2
    x_min = min(x_data) - 2
    y_max = max(y_data) + 2
    y_min = min(y_data) - 2

    # 设置坐标轴
    setAx(x_min, x_max, y_min, y_max, ax)

    # 使用 plt.scatter() 绘制点
    plt.scatter(x_data, y_data, color=color, marker='o')

    plt.pause(2)
    pause_time = 3.0 / len(x_data)
    length = len(x_data)

    for i in range(length):
        # 准备好当前帧需要绘制的点，即少画一个点
        x_data.pop()
        y_data.pop()
        # 绘制当前帧
        drawNodes(ax, x_data, y_data, pause_time, color)
        # 清空当前帧
        ax.cla()
        # 设置题目
        plt.title(title)
        # 设置坐标轴
        setAx(x_min, x_max, y_min, y_max, ax)


# 无delete的双重循环绘图
def doubleLoopNoDelete(ax, x_move, y_move, x_data, y_data, color):
    # 获得X，Y轴的范围
    x_max = max(x_data) + max(x_move) + 2
    x_min = min(x_data) - min(x_move) - 2
    y_max = max(y_data) + max(y_move) + 2
    y_min = min(y_data) + min(y_move) - 2

    setAx(x_min, x_max, y_min, y_max, ax)

    pause_time = 3.0 / len(x_move)
    length = len(x_move)

    # 双重循环绘图即每次都将初始x，y坐标移动一定偏移量
    for i in range(length):
        x_draw = [x + x_move[i] for x in x_data]
        y_draw = [y + y_move[i] for y in y_data]
        drawNodes(ax, x_draw, y_draw, pause_time, color)

    plt.pause(2)


# delete效果的双重循环绘图
def doubleLoopDelete(ax, x_move, y_move, x_data, y_data, color, title=None):
    # 获得X，Y轴的范围
    x_max = max(x_data) + max(x_move) + 2
    x_min = min(x_data) - min(x_move) - 2
    y_max = max(y_data) + max(y_move) + 2
    y_min = min(y_data) + min(y_move) - 2

    setAx(x_min, x_max, y_min, y_max, ax)
    length = len(x_move)

    x_all = []
    y_all = []

    # 获得要绘制的所有点
    for i in range(length):
        x_draw = [x + x_move[i] for x in x_data]
        y_draw = [y + y_move[i] for y in y_data]
        x_all.extend(x_draw)
        y_all.extend(y_draw)

    # 绘制所有点
    plt.scatter(x_all, y_all, color=color, marker='o')

    plt.pause(2)
    pause_time = 3.0 / len(x_all)
    length = len(x_all)

    # 每次弹出一个点
    for i in range(length):
        x_all.pop()
        y_all.pop()
        drawNodes(ax, x_all, y_all, pause_time, color)
        ax.cla()
        plt.title(title)
        setAx(x_min, x_max, y_min, y_max, ax)


# 测试painter功能
def test():
    # 正式使用的时候需要将元组转化成列表
    x = []
    y = []
    x2 = []
    y2 = []
    fig, ax = plt.subplots()
    # 设置背景颜色
    fig.set_facecolor(bg_color)
    for i in range(100):
        x.append(i)
        y.append(i)
    for i in range(5):
        x2.append(i * 10)
        y2.append((5 - i) * 10)
    singleLoopNoDelete(ax, x, y, dot_color)
    singleLoopDelete(ax, x, y, dot_color)
    for i in range(100):
        x.append(i)
        y.append(i)
    # doubleLoopNoDelete(ax, x2, y2, x, y, color)
    doubleLoopDelete(ax, x2, y2, x, y, dot_color)
    for i in range(100):
        x.append(i)
        y.append(i)

    singleLoopNoDelete(ax, x, y, dot_color)
    plt.show()


if __name__ == "__main__":
    test()
