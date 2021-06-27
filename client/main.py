import numpy as np
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
import cv2
from PIL import ImageTk, Image
from client import TFPOSE
from client import POSTRECOGNIZE

from tf_pose import common
from tf_pose.common import CocoPart
from tf_pose.tensblur.smoother import Smoother

class GUI:
    def __init__(self, root):
        self.root = root
        self.filename = ''
        self.is_stop = True # 是否暂停
        self.is_first_run = True # 是否第一次测试该视频
        self.is_origin = IntVar() # 是否显示原图
        self.is_outpose = IntVar() # 是否输出步态时序图
        self.is_savefile = IntVar()  # 是否保存结果到文件
        self.outpose_count = 0
        self.outpose_img = None # 步态时序图
        # 1. 设置布局
        self.setLayout()
        # 2. 初始化检测类
        self.runner = TFPOSE()
        # 循环显示
        self.root.mainloop()


    def setLayout(self):
        """
        设置布局
        """
        # 根节点设置
        self.root.title('基于姿态识别的身份认证系统')
        self.root.geometry('1080x681+200+50')

        # 第一列
        # 画布标签
        label_canva = Label(self.root, text='处理后视频流', font="20")
        label_canva.pack()
        label_canva.place(x=50, y=20)
        # 画布，显示处理后的视频
        self.canva = Canvas(self.root, width=400, height=400, bg='gray')
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

        # 第二列
        # 节点信息标签
        label_text = Label(self.root, text='输出信息', font="20")
        label_text.pack()
        label_text.place(x=480, y=20)
        # 显示节点信息
        self.scroll_text = ScrolledText(self.root, width=40, height=34)
        self.scroll_text.pack()
        self.scroll_text.place(x=480, y=50)
        # 运行按钮
        self.btn_run = Button(self.root, width=40, text="识别视频", command=self.run)
        self.btn_run.pack()
        self.btn_run.place(x=480, y=518)
        # 停止按钮
        self.btn_stop = Button(self.root, width=40, text="暂停识别", command=self.stop)
        self.btn_stop.pack()
        self.btn_stop.place(x=480, y=568)

        # 第三列
        ## 需要使用self.is_outpose.get()获取值
        # 复选框-是否显示原图
        self.checkbtn_origin = Checkbutton(root, text="输出原图", variable=self.is_origin, command=self.initRunnerIsOrigin)
        self.checkbtn_origin.pack()
        self.checkbtn_origin.place(x=800, y=50)
        # 复选框-是否输出步态时序
        self.checkbtn_outpose = Checkbutton(root, text="保存步态时序图", variable=self.is_outpose)
        self.checkbtn_outpose.pack()
        self.checkbtn_outpose.place(x=800, y=80)
        # 复选框-是否输出步态时序
        self.checkbtn_savefile = Checkbutton(root, text="保存结果到文件(在初次检测视频时选择)", variable=self.is_savefile)
        self.checkbtn_savefile.pack()
        self.checkbtn_savefile.place(x=800, y=110)

    def initRunnerVideo(self):
        # 设置视频路径
        self.runner.setArgsVideo(self.filename)
        # 设置是否保存结果到文件
        self.runner.setArgsIsOutput(self.is_savefile.get())
        # 初始化视频
        self.runner.initVideo()

    def initRunnerIsOrigin(self):
        # 设置是否输出原图
        self.runner.setArgsIsOrigin(self.is_origin.get())

    def initRunnerIsOrigin(self):
        # 设置是否输出原图
        self.runner.setArgsIsOrigin(self.is_origin.get())

    def run(self):
        if self.filename == '':
            messagebox.showerror("错 误", "请先选择视频文件")
            return
        if self.is_first_run:
            self.initRunnerVideo()
        # 开始运算
        self.is_stop = False
        self.is_first_run = False
        frame_count_outpose = 0
        frame_count = 0
        while self.runner.hasNextFrame() and self.is_stop!=True:
            # 获取一帧图片，并转换成Image格式
            ans, humans = self.runner.runOnce()
            self.cv2_img = ans
            self.image = self.cv2Image(ans)
            # 保存5帧的humans
            flg = self.saveHumans(frame_count, humans)
            frame_count += 1
            # 姿态识别
            if flg == True :
                infos = POSTRECOGNIZE(self.humans_5).run()
                self.drawInfoPose(infos)
            # 是否保存步态图（无背景），需要分离人物，并且要隔几帧存
            if self.is_outpose.get() :
                self.savePose(frame_count_outpose, humans)
                frame_count_outpose += 1
            else:
                frame_count_outpose = 0
            # 在图上绘制
            self.drawCanvas(self.image)
            # 显示信息
            self.drawInfo(len(humans))
            # 获取下一帧
            self.runner.getNextFrame()

    def saveHumans(self, frame_count, humans):
        """保存图片"""
        fps = 5
        flg = frame_count % fps
        # 构造数组
        if flg == 0:
            self.humans_5 = []
        # 追加
        self.humans_5.append(humans)
        # 返回是否可以姿态识别
        if flg == fps-1 :
            return True
        else:
            return False

    def savePose(self, frame_count, humans):
        """保存图片，传入humans进行人物分离，默认无背景"""
        fps = 10
        flg = frame_count % fps
        # 跳过几帧
        if flg % 2 == 1:
            return
        # 确保当前全局有数组存放序列图
        if flg == 0:
            self.outpose_img = []
        # 分离人物
        for index,human in enumerate(humans):
            if flg == 0:
                self.outpose_img.append(self.drawHuman(human))
            else:
                if index >= len(self.outpose_img):
                    break
                self.outpose_img[index] = np.concatenate((self.outpose_img[index], self.drawHuman(human)), axis=1)
            # 保存骨架信息到文件
            outpose_path = './pose/' + str(frame_count) + '-pose-people' + str(index) + '.txt'
            np.savetxt(outpose_path, [human], delimiter=" ", fmt='%s')
        # 保存文件
        if flg == fps-2 :
            for index,value in enumerate(self.outpose_img):
                outpose_path = './img/' + str(self.outpose_count) + '-pose-people' + str(index) + '.png'
                cv2.imwrite(outpose_path, value)
            self.outpose_count += 1

    def drawHuman(self, human):
        npimg = np.zeros(self.cv2_img.shape, np.uint8)
        npimg[...] = 0
        image_h, image_w = npimg.shape[:2]
        centers = {}
        # 画图
        for i in range(common.CocoPart.Background.value):  # 共18个关键点
            if i not in human.body_parts.keys():
                continue
            body_part = human.body_parts[i]
            # 由于网络运算出来为0~1的值，需要等比放大
            center = (int(body_part.x * image_w + 0.5), int(body_part.y * image_h + 0.5))
            centers[i] = center
            cv2.circle(npimg, center, 3, common.CocoColors[i], thickness=3, lineType=8, shift=0)

        # 画线
        for pair_order, pair in enumerate(common.CocoPairsRender):
            if pair[0] not in human.body_parts.keys() or pair[1] not in human.body_parts.keys():
                continue
            cv2.line(npimg, centers[pair[0]], centers[pair[1]], common.CocoColors[pair_order], 3)

        return npimg

    def stop(self):
        self.is_stop = True
        # 绘制最后一帧
        self.drawCanvas(self.image)

    def openFile(self):
        """打开文件"""
        self.is_first_run = True
        self.filename = filedialog.askopenfilename()
        self.msg_file['text'] = self.filename

    def cv2Image(self, img_cv_in, layout='fit'):
        """将cv2的图片格式转换未Image格式"""
        canvawidth = int(self.canva.winfo_reqwidth())
        canvaheight = int(self.canva.winfo_reqheight())
        # 获取宽高
        h, w = img_cv_in.shape[0], img_cv_in.shape[1]
        # 设置输出格式
        if (layout == "fill"):
            imgCV = cv2.resize(img_cv_in, (canvawidth, canvaheight), interpolation=cv2.INTER_AREA)
        elif (layout == "fit"):
            if (float(w / h) > float(canvawidth / canvaheight)):
                imgCV = cv2.resize(img_cv_in, (canvawidth, int(canvawidth * h / w)), interpolation=cv2.INTER_AREA)
            else:
                imgCV = cv2.resize(img_cv_in, (int(canvaheight * w / h), canvaheight), interpolation=cv2.INTER_AREA)
        else:
            imgCV = img_cv_in
        # 转换
        imgCV2 = cv2.cvtColor(imgCV, cv2.COLOR_BGR2RGBA)  # 转换颜色从BGR到RGBA
        img_Image = Image.fromarray(imgCV2)  # 将图像转换成Image对象
        imgTK = ImageTk.PhotoImage(image=img_Image)  # 将image对象转换为imageTK对象
        return imgTK
        # canva.create_image(0,0,anchor = NW, image = imgTK)

    def flush(self):
        self.root.update_idletasks()  # 最重要的更新是靠这两句来实现
        self.root.update()

    def drawCanvas(self, image):
        """显示视频"""
        self.canva.create_image(0, 0, anchor=NW, image=image)
        # self.flush()

    def drawInfo(self, humans_len):
        """显示信息"""
        # self.scroll_text.delete(1.0, "end")
        info = """帧数:""" + str(self.runner.getFrameCount()) + """ 人数:""" + str(humans_len) + """\n"""
        self.scroll_text.insert('insert', info)
        self.flush()

    def drawInfoPose(self, infos):
        """显示信息"""
        self.scroll_text.insert('insert', '姿态识别结果:\n')
        for info in infos :
            self.scroll_text.insert('insert', info + '\n')
        self.scroll_text.insert('insert', '\n')
        self.flush()


if __name__ == '__main__':
    root = Tk()
    # 1. 初始化界面
    GUI(root)