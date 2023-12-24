from scanner import Lexer, Token
from tokens import TokenType, FUNC
import matplotlib.pyplot as plt
from painter import CacuSyntaxTree, CacuColor, GenerateT, Modify, singleLoopNoDelete, singleLoopDelete
from painter import doubleLoopNoDelete, doubleLoopDelete


# 表达式节点类
class ExprNode:
    def __init__(self, opcode, content=None):
        self.OpCode = opcode
        self.Content = content

# 声明全局变量
origin_x, origin_y = (0, 0)
scale_x, scale_y = (1.0, 1.0)
rot_rad = 0.0
bg_color = (0.9608, 0.9608, 0.8627)
dot_color = (1, 0.6471, 0)
delete = False
fig, ax = plt.subplots()
temp = ()
title_t = None


# 创建表达式节点
def MakeExprNode(opcode, *args):
    if opcode == TokenType.CONST_ID:
        return ExprNode(opcode, args[0])
    elif opcode == TokenType.T:
        return ExprNode(opcode, args[0])
    elif opcode == TokenType.FUNC:
        return ExprNode(opcode, (args[0], args[1]))
    else:
        return ExprNode(opcode, (args[0], args[1]))


# 打印语法树
def PrintSyntaxTree(root, indent):
    if root is None:
        return
    print("  " * indent + "OpCode: " + str(root.OpCode))
    if root.OpCode == TokenType.CONST_ID:
        print("  " * indent + "Value: " + str(root.Content))
    elif root.OpCode == TokenType.T:
        print("  " * indent + "Parameter: " + str(root.Content))
    elif root.OpCode == TokenType.FUNC:
        print("  " * indent + "Function: " + str(root.Content[0]))
        PrintSyntaxTree(root.Content[1], indent + 1)
    else:
        print("  " * indent + "Left:")
        PrintSyntaxTree(root.Content[0], indent + 1)
        print("  " * indent + "Right:")
        PrintSyntaxTree(root.Content[1], indent + 1)


token = None  # 当前记号
tokens = None  # 记号流


def FetchToken():  # 迭代取出记号
    global token
    try:
        token = next(tokens)
        if TokenType.ERROR == token.type:
            SyntaxError("词法错误")
    except StopIteration:
        print("所有翻译完毕\n")
        exit()


def MatchToken(The_Token):  # 匹配记号
    if token.type == The_Token:
        FetchToken()
        return True
    else:
        SyntaxError("语法错误")
        return False


def SyntaxError(err):  # 报错
    print(err)


## 表达式处理：Expression -> Term -> Factor -> Component -> Atom，递归下降
def Atom():
    global father_type
    if token.type == TokenType.CONST_ID or token.type == TokenType.T:
        leaf = MakeExprNode(token.type, token.lexeme)
        token_tmp = token.type
        MatchToken(token_tmp)
        return leaf
    elif token.type == TokenType.FUNC:
        father_type = token.type
        token_tmp = token.type
        token_fun = token.lexeme.lower()  # 小写
        # print(token_fun.lexeme)，大写
        MatchToken(token_tmp)
        MatchToken(TokenType.L_BRACKET)
        t = Expression()
        father_type = None
        MatchToken(TokenType.R_BRACKET)
        leaf = MakeExprNode(token_tmp, token_fun, t)
        return leaf
    elif token.type == TokenType.L_BRACKET:
        father_type = token.type
        MatchToken(TokenType.L_BRACKET)
        leaf = Expression()
        father_type = None
        MatchToken(TokenType.R_BRACKET)
        return leaf


def Component():  # 乘方，右递归实现 
    left = Atom()
    if token.type == TokenType.POWER:
        token_tmp = token.type
        MatchToken(token_tmp)
        right = Component()
        left = MakeExprNode(token_tmp, left, right)
        return left
    else:
        return left


def Factor():  # 一元正负
    if token.type == TokenType.PLUS or token.type == TokenType.MINUS:
        token_tmp = token.type
        MatchToken(token_tmp)
        if token_tmp == TokenType.MINUS:
            right = Factor()
            left = ExprNode(TokenType.CONST_ID,0)  # 一元负，左补0
            left = MakeExprNode(token_tmp, left, right)
            return left
        else:
            right = Factor()  # 一元正，消去正
            return right
    else:
        left = Component()
        return left


def Term():  # 二元乘除
    left = Factor()
    while token.type == TokenType.MUL or token.type == TokenType.DIV:
        token_tmp = token.type
        MatchToken(token_tmp)
        right = Factor()
        left = MakeExprNode(token_tmp, left, right)
    return left


father_type = None

def Expression():  # 二元加减
    left = Term()
    while token.type == TokenType.PLUS or token.type == TokenType.MINUS:
        token_tmp = token.type
        MatchToken(token_tmp)
        right = Term()
        left = MakeExprNode(token_tmp, left, right)
    if father_type != TokenType.FUNC and father_type != TokenType.L_BRACKET:  # 防止FUNC和()内部expression由于递归从而打印两遍
        PrintSyntaxTree(left, 0)  # 打印表达式语法树
    return left


## 显示语句处理
def Hint(statment_type, op):  # 提示进入退出
    if 0 == op:
        print("enter in %s" % statment_type)
    else:
        print("exit from %s" % statment_type)


def OriginStatment():  # 坐标平移
    # 声明全局变量
    global origin_x, origin_y
    Hint("OriginStatment", 0)
    MatchToken(TokenType.ORIGIN)
    MatchToken(TokenType.IS)
    MatchToken(TokenType.L_BRACKET)
    x = Expression()
    # 计算origin_x的值
    origin_x = CacuSyntaxTree(x)
    MatchToken(TokenType.COMMA)
    y = Expression()
    # 计算origin_y的值
    origin_y = CacuSyntaxTree(y)
    MatchToken(TokenType.R_BRACKET)
    Hint("OriginStatment", 1)


def ScaleStatment():  # 比例设置
    # 声明全局变量
    global scale_x, scale_y
    Hint("ScaleStatment", 0)
    MatchToken(TokenType.SCALE)
    MatchToken(TokenType.IS)
    MatchToken(TokenType.L_BRACKET)
    x = Expression()
    MatchToken(TokenType.COMMA)
    y = Expression()
    # 计算scale
    scale_x = CacuSyntaxTree(x)
    scale_y = CacuSyntaxTree(y)
    MatchToken(TokenType.R_BRACKET)
    Hint("ScaleStatment", 1)


def RotStatment():  # 角度旋转
    # 声明全局变量
    global rot_rad
    Hint("RotStatment", 0)
    MatchToken(TokenType.ROT)
    MatchToken(TokenType.IS)
    angle = Expression()
    # 计算rot_rad的值
    rot_rad = CacuSyntaxTree(angle)
    Hint("RotStatment", 1)


## 创新点
def TitleStatment():  # 用户添加标题
    # 声明全局变量
    global title_t
    Hint("TitleStatment", 0)
    MatchToken(TokenType.TITLE)
    MatchToken(TokenType.IS)
    MatchToken(TokenType.QUOTE)
    title = Expression()
    # 直接获取title
    title_t = title.Content
    MatchToken(TokenType.QUOTE)
    Hint("TitleStatment", 1)


def BgcolourStatment():  # 用户规定背景色
    # 声明全局变量
    global bg_color
    Hint("BgcolourStatment", 0)
    MatchToken(TokenType.BGCOLOUR)
    MatchToken(TokenType.IS)
    MatchToken(TokenType.L_BRACKET)
    r = Expression()
    MatchToken(TokenType.COMMA)
    g = Expression()
    MatchToken(TokenType.COMMA)
    b = Expression()
    MatchToken(TokenType.R_BRACKET)
    Hint("BgcolourStatment", 1)

    # 计算bg_color并将其调整成适合matplotlib的格式
    bg_color = (CacuSyntaxTree(r), CacuSyntaxTree(g), CacuSyntaxTree(b))
    bg_color = CacuColor(bg_color)
    fig.set_facecolor(bg_color)


def FgcolourStatment():  # 用户规定前景色
    # 声明全局变量
    global dot_color
    Hint("FgcolourStatment", 0)
    MatchToken(TokenType.FGCOLOUR)
    MatchToken(TokenType.IS)
    MatchToken(TokenType.L_BRACKET)
    r = Expression()
    MatchToken(TokenType.COMMA)
    g = Expression()
    MatchToken(TokenType.COMMA)
    b = Expression()
    MatchToken(TokenType.R_BRACKET)
    Hint("FgcolourStatment", 1)
    # 计算dot_color并将其调整成适合matplotlib的格式
    dot_color = (CacuSyntaxTree(r), CacuSyntaxTree(g), CacuSyntaxTree(b))
    dot_color = CacuColor(dot_color)


def ClearStatment():  # 用户清除图形，动画效果
    # 声明全局变量
    global delete
    Hint("ClearStatment", 0)
    MatchToken(TokenType.CLEAR)
    f = token.lexeme  # 得到True/False
    # 直接进行字符串比较获得delete的值
    if f == 'TRUE':
        print(f)
        delete = True
    elif f == 'FALSE':
        delete = False
    MatchToken(TokenType.CONST_ID)
    Hint("ClearStatment", 1)


def ForStatment():  #（单/双层嵌套）for-draw制图
    # 声明全局变量
    global temp, title_t, ax
    # 打印此时的全局变量信息，起调试作用
    print(origin_x, origin_y, scale_x, scale_y, rot_rad, dot_color, delete)
    Hint("ForStatment", 0)
    MatchToken(TokenType.FOR)
    MatchToken(TokenType.T)
    MatchToken(TokenType.FROM)
    start = Expression()
    MatchToken(TokenType.TO)
    end = Expression()
    MatchToken(TokenType.STEP)
    step = Expression()

    # 计算start，end，step后生成temp对应的元组
    temp = GenerateT(CacuSyntaxTree(start), CacuSyntaxTree(end), CacuSyntaxTree(step))

    MatchToken(TokenType.DRAW)
    MatchToken(TokenType.L_BRACKET)
    x = Expression()
    # 计算得到需要的x坐标（元组）
    x_data = CacuSyntaxTree(x, temp)
    # 如果x是常量，需要将其转化成对应temp长度的元组
    if not isinstance(x_data, tuple):
        x_data = (x_data,) * len(temp)
    MatchToken(TokenType.COMMA)
    y = Expression()
    # 计算得到需要的y坐标（元组）
    y_data = CacuSyntaxTree(y, temp)
    # 如果y是常量，需要将其转化成对应temp长度的元组
    if not isinstance(y_data, tuple):
        y_data = (y_data,) * len(temp)

    MatchToken(TokenType.R_BRACKET)

    # 绘图之前设置title，因为每次ax.clr后都会清空题目
    if title_t is not None:
        plt.title(title_t)
    if token.type == TokenType.SEMICO:
        # 分号表示该循环是单层的
        print('single loop')
        # print(x_data)
        # print(y_data)
        # 绘图前需要根据全局变量调整坐标
        x_data, y_data = Modify(x_data, y_data, origin_x, origin_y, scale_x, scale_y, rot_rad)
        # print(x_data)
        # print(y_data)
        # 根据是否delete选择不同的绘图函数
        if delete:
            print('delete')
            ax.cla()
            plt.title(title_t)
            singleLoopDelete(ax, list(x_data), list(y_data), dot_color, title_t)
        else:
            singleLoopNoDelete(ax, list(x_data), list(y_data), dot_color)
    elif token.type == TokenType.COLON:  # Doublefor处理
        print('double loop')
        # 冒号表示双重循环
        MatchToken(TokenType.COLON)
        MatchToken(TokenType.FOR)
        MatchToken(TokenType.T)
        MatchToken(TokenType.FROM)
        start = Expression()
        MatchToken(TokenType.TO)
        end = Expression()
        MatchToken(TokenType.STEP)
        step = Expression()

        # 获得第二层循环中的temp，此时以及不会再用到第一层中的temp，所以可以直接覆盖
        temp = GenerateT(CacuSyntaxTree(start), CacuSyntaxTree(end), CacuSyntaxTree(step))

        MatchToken(TokenType.DRAW)
        MatchToken(TokenType.L_BRACKET)
        x = Expression()
        x_data2 = CacuSyntaxTree(x, temp)
        if not isinstance(x_data2, tuple):
            x_data2 = (x_data2,) * len(temp)
        MatchToken(TokenType.COMMA)
        y = Expression()
        y_data2 = CacuSyntaxTree(y, temp)
        if not isinstance(y_data2, tuple):
            y_data2 = (y_data2,) * len(temp)
        MatchToken(TokenType.R_BRACKET)

        # 修改绘图数据
        x_data2, y_data2 = Modify(x_data2, y_data2, origin_x, origin_y, scale_x, scale_y, rot_rad)
        # 根据是否delete选择不同的绘图函数
        if delete:
            print('delete')
            ax.cla()
            plt.title(title_t)
            doubleLoopDelete(ax, list(x_data), list(y_data), list(x_data2), list(y_data2), dot_color, title_t)
        else:
            doubleLoopNoDelete(ax, list(x_data), list(y_data), list(x_data2), list(y_data2), dot_color)

    Hint("ForStatment", 1)


## 主程序：main -> Parser -> Program -> Statment                
def Statment():  # 判断语句类型
    if token.type == TokenType.ORIGIN:
        OriginStatment()
    elif token.type == TokenType.SCALE:
        ScaleStatment()
    elif token.type == TokenType.ROT:
        RotStatment()
    elif token.type == TokenType.TITLE:
        TitleStatment()
    elif token.type == TokenType.BGCOLOUR:
        BgcolourStatment()
    elif token.type == TokenType.FGCOLOUR:
        FgcolourStatment()
    elif token.type == TokenType.CLEAR:
        ClearStatment()
    elif token.type == TokenType.FOR:
        ForStatment()
    elif token.type == TokenType.SEMICO:  # 词法分析的一个小bug，以;分隔句子，如果注释末尾无; 则会把下一句也吞掉。所以给注释末尾加; 分号不会被吞掉，用来标识注释语句
        SyntaxError("注释语句")
    else:
        SyntaxError("错误语句")


def Program():
    i = 0

    while TokenType.NONTOKEN != token.type:
        Statment()
        if MatchToken(TokenType.SEMICO):  # 用分号来分句
            i += 1
            print("第%d句翻译完毕\n" % i)
        else:
            exit()

    # 展示绘图结果
    plt.show()


def Parser(file_path): 
    global tokens
    try:
        with open(file_path, 'r', encoding='utf-8') as file:  # utf-8：正确处理中文注释
            content = file.read()  # 读文件
        lexer = Lexer()
        tokenList = lexer.lex(content)  # 从词法分析器得到记号流
        tokens = iter(tokenList)  # 列表转迭代器
        FetchToken()
        Program()
    except FileNotFoundError:
        print("打开源文件有误\n")
    finally:
        file.close()  # 关闭文件


if __name__ == "__main__":
    Parser("2.txt")
