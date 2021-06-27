import argparse
import cv2
import time
import numpy as np
from tf_pose.estimator import TfPoseEstimator
from tf_pose.networks import get_graph_path, model_wh

"""
封装并调用tf-openpose项目所提供的骨架信息识别接口
"""

class TFPOSE:
    def __init__(self):
        # 0. 参数
        self.fps_time = 0
        self.frame_count = 0
        # 1. 解析参数
        self.parseArgs()
        # 2. 输出参数
        self.printArgs()
        # 3. 生成tfpose实例
        self.w, self.h = model_wh(self.args.resize)
        self.e = TfPoseEstimator(get_graph_path(self.args.model), target_size=(self.w, self.h))

    def parseArgs(self):
        """解析参数"""
        parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
        parser.add_argument('--video', type=str, default=0,
                            help='if provided, set the video path')
        parser.add_argument('--isoutput', type=bool, default=False,
                            help='whether write to file')
        parser.add_argument('--output', type=str, default='test.avi',
                            help='if provided, set the output video path')
        parser.add_argument('--isorigin', type=bool, default=False,
                            help='whether output origin img')
        parser.add_argument('--resize', type=str, default='432x368',
                            help='if provided, resize images before they are processed. default=256x256, Recommends : 432x368 or 656x368 or 1312x736 ')
        parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                            help='if provided, resize heatmaps before they are post-processed. default=1.0')
        parser.add_argument('--model', type=str, default='mobilenet_v2_large',
                            help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
        parser.add_argument('--show-process', type=bool, default=False,
                            help='for debug purpose, if enabled, speed for inference is dropped.')
        # 命令行解析模块
        self.args = parser.parse_args()

    def printArgs(self):
        """输出参数"""
        print('获取的参数如下:')
        print('video-视频: %s' % (self.args.video))
        print('resize-重写图片大小: %s' % (self.args.resize))
        print('resize-out-ratio-重写关键点热图大小: %s' % (self.args.resize_out_ratio))
        print('show-process-是否展示过程: %s' % (self.args.show_process))
        print('model-模型: %s, 模型路径: %s' % (self.args.model, get_graph_path(self.args.model)))

    def setArgsVideo(self, video):
        """设置video参数"""
        self.args.__setattr__('video', video)

    def setArgsIsOrigin(self, isorigin):
        """设置isorigin参数"""
        self.args.__setattr__('isorigin', isorigin)

    def setArgsIsOutput(self, isoutput):
        """设置isorigin参数"""
        self.args.__setattr__('isoutput', isoutput)

    def initVideo(self):
        """
        初始化视频信息
        """
        print('读取视频')
        self.cam = cv2.VideoCapture(self.args.video)
        self.ret_val, self.image = self.cam.read()  # 获取视频第一帧图片，ret_val为bool值
        self.frame_count = 0 # 重置帧数为0，因为会换视频

        # 是否写入文件
        if self.args.isoutput :
            fps = self.cam.get(cv2.CAP_PROP_FPS)  # 视频帧率
            fourcc = cv2.VideoWriter_fourcc(*'XVID')  # 保存视频为MPEG-4编码
            frame_size = (int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self.videoWriter = cv2.VideoWriter(self.args.output, fourcc, fps, frame_size)
            print('源视频信息: 帧图片大小 %s, 帧率 %s, 视频大小 %s' % (self.image.shape, fps, frame_size))

    def getHumans(self):
        humans = self.e.inference(self.image, resize_to_default=(self.w > 0 and self.h > 0), upsample_size=self.args.resize_out_ratio)
        return humans

    def getNextFrame(self):
        """获取下一帧的图片"""
        self.ret_val, self.image = self.cam.read()
        self.frame_count += 1
        return self.ret_val

    def hasNextFrame(self):
        """是否还有下一帧"""
        return self.ret_val

    def getFrameCount(self):
        """获取帧数"""
        return self.frame_count

    def runOnce(self):
        """
        运行一次，即识别一帧，并返回此帧的cv2图片
        """
        fps_time = time.time()
        # 帧图片处理
        print('帧图片处理...')
        humans = self.getHumans()

        # 关键点绘图
        print('画图...')
        if self.args.isorigin :
            # 显示原图
            pose_img = TfPoseEstimator.draw_humans(np.array(self.image), humans, imgcopy=False)
        else:
            # 不显示原图
            emptyImage = np.zeros(self.image.shape, np.uint8)
            emptyImage[...] = 0
            pose_img = TfPoseEstimator.draw_humans(emptyImage, humans, imgcopy=False)
        # cv2.putText(pose_img, "FPS: %f" % (1.0 / (time.time() - fps_time)), (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # 判断写入文件
        if self.args.isoutput :
            self.videoWriter.write(pose_img)

        return pose_img, humans


if __name__ == '__main__':
    TFPOSE()