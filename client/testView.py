import numpy as np
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import cv2
from PIL import ImageTk, Image

"""
仅用来测试客户端布局
"""

class GUI:
    def __init__(self, root):
        self.root = root
        self.filename = ''
        self.is_stop = True
        self.is_first_run = True
        # 1. 设置布局
        self.setLayout()
        # 循环显示
        self.root.mainloop()


    def setLayout(self):
        """
        设置布局
        """
        self.root.title('基于姿态识别的身份认证系统')
        self.root.geometry('1080x681+200+50')
        # 画布标签
        label_canva = Label(self.root, text='处理后视频流', font="20")
        label_canva.pack()
        label_canva.place(x=50, y=20)
        # 画布，显示处理后的视频
        self.canva = Canvas(self.root, width=400, height=400, bg='gray')
        # self.canva = Canvas(self.root, width=246, height=448, bg='gray')
        self.canva.pack()
        self.canva.place(x=50, y=50)
        # 选择文件按钮
        self.btn_select_file = Button(self.root, text="选择视频文件", command=self.openFile)
        self.btn_select_file.pack()
        self.btn_select_file.place(x=50, y=518)
        # 文件信息
        self.msg_file = Message(self.root, highlightthickness=1, highlightbackground='black', width=200, text="当前未选择文件")
        self.msg_file.pack()
        self.msg_file.place(x=50, y=568)
        # 节点信息标签
        label_text = Label(self.root, text='输出信息', font="20")
        label_text.pack()
        label_text.place(x=480, y=20)
        # 显示节点信息
        self.text = Text(self.root, width=40, height=34)
        self.text = ScrolledText(self.root, width=40, height=34)
        self.text.pack()
        self.text.place(x=480, y=50)
        str = '''If there is anyone out there who still doubts that America is a place where all things are possible, who still wonders if the dream of our founders is alive in our time, who still questions the power of our democracy, tonight is your answerIt’s the answer told by lines that stretched around schools and churches in numbers this nation has never seen, by people who waited three hours and four hours, many for the first time in their lives, because they believed that this time must be different, that their voices could be that difference.'''
        self.text.insert('insert', str)
        # 运行按钮
        self.btn_run = Button(self.root, width=40, text="识别视频", command=self.run)
        self.btn_run.pack()
        self.btn_run.place(x=480, y=518)
        # 停止按钮
        self.btn_stop = Button(self.root, width=40, text="暂停识别", command=self.stop)
        self.btn_stop.pack()
        self.btn_stop.place(x=480, y=568)
        # 复选框
        self.is_origin = IntVar()
        self.checkbtn_origin = Checkbutton(root, text="输出原图", variable=self.is_origin)
        self.checkbtn_origin.pack()
        self.checkbtn_origin.place(x=800, y=50)
        self.var = IntVar()
        c = Checkbutton(root, text="保存步态时序图", variable=self.var, command=self.run)
        c.pack()
        c.place(x=800, y=80)

    def run(self):
        print(self.var.get())

    def stop(self):
        self.is_stop = True
        # 绘制最后一帧
        self.drawCanvas(self.image)


    def openFile(self):
        pass



if __name__ == '__main__':
    root = Tk()
    # 1. 初始化界面
    GUI(root)