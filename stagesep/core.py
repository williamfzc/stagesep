import cv2
import subprocess
import re
import json
import contextlib
import numpy as np
from skimage.measure import compare_ssim
from .config import *


@contextlib.contextmanager
def ssv_video_capture(ssv):
    video_cap = cv2.VideoCapture(ssv.path)
    yield video_cap
    video_cap.release()


class StageSepVideo(object):
    """ 视频对象 """

    def __init__(self, video_path):
        src = cv2.VideoCapture(video_path)
        self.path = video_path
        self.frame_count = src.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = src.get(cv2.CAP_PROP_FPS)
        self.width = int(src.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(src.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def __repr__(self):
        return json.dumps({
            'src': repr(self.path),
            'frame_count': self.frame_count,
            'fps': self.fps,
            'size': (self.width, self.height),
        })


def get_first_and_last_frame(target_ssv):
    """ 获取视频的首尾帧 """
    with ssv_video_capture(target_ssv) as video_cap:
        _, first_frame = video_cap.read()
        video_cap.set(1, target_ssv.frame_count - 1)
        _, last_frame = video_cap.read()
    return first_frame, last_frame


def load_video(video_path):
    """
    读取视频并将其转换成ssv对象

    :return:
    """
    ssv = StageSepVideo(video_path)
    logger.msg('LOAD VIDEO OK', vid=ssv)
    return ssv


def rotate_pic(old_pic, rotate_time):
    """ 帧旋转 """
    new_pic = np.rot90(old_pic, rotate_time)
    return new_pic


def rebuild_video(old_stagesep_video, new_fps=None, rotate_time=None):
    """
    将视频重新按照指定格式打包

    :param old_stagesep_video: old ssv
    :param new_fps:
    :param rotate_time: 0为保持原状，1为逆时针旋转90度，2为逆时针180，以此类推
    :return:
    """
    if rotate_time % 2 == 0:
        size = (old_stagesep_video.width, old_stagesep_video.height)
    else:
        size = (old_stagesep_video.height, old_stagesep_video.width)
    target_fps = new_fps or old_stagesep_video.fps
    writer = cv2.VideoWriter(TEMP_VIDEO, cv2.VideoWriter_fourcc(*"WMV1"), target_fps, size)

    src = cv2.VideoCapture(old_stagesep_video.path)
    success, frame = src.read()
    while success:
        if rotate_time:
            frame = rotate_pic(frame, rotate_time)
        writer.write(frame)
        success, frame = src.read()

    writer.release()
    new_ssv = StageSepVideo(TEMP_VIDEO)
    logger.msg('REBUILD OK', new_vid=new_ssv)
    return new_ssv


def get_stage():
    """
    TODO 从视频中提取阶段

    :return:
    """
    raise NotImplementedError('todo')


def check_env():
    """
    环境检测，如tesseract是否安装

    :return:
    """
    tesseract_return_code = subprocess.call('tesseract --version')
    if tesseract_return_code:
        raise ImportError('tesseract installed?')


def frame_prepare(old_frame):
    # 处理图片
    gray_frame = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    blur_gray_frame = cv2.medianBlur(gray_frame, 3)
    return blur_gray_frame


def analyse_video(target_stagesep_video, lang=None, real_time_log=None):
    """
    分析视频

    :param target_stagesep_video:
    :param lang:
    :param real_time_log:
    :return:
    """
    first_frame, last_frame = get_first_and_last_frame(target_stagesep_video)
    first_frame, last_frame = frame_prepare(first_frame), frame_prepare(last_frame)
    ret = True
    cur_frame_count = 0
    result_list = []

    with ssv_video_capture(target_stagesep_video) as src, \
            open(RESULT_TXT, 'w+', encoding=DEFAULT_ENCODING) as result_file:
        while ret:
            ret, frame = src.read()
            if not ret:
                break
            # 当前帧参数
            cur_frame_count += 1
            cur_second = src.get(cv2.CAP_PROP_POS_MSEC) / 1000
            # 帧处理
            frame = frame_prepare(frame)
            # OCR阶段
            cv2.imwrite(TEMP_PIC, frame)
            exec_ocr(lang=lang)
            chi_sim_result = get_ocr_result()
            # 与首尾帧的相似度
            first_sim = compare_ssim(first_frame, frame)
            last_sim = compare_ssim(last_frame, frame)
            # 结果处理
            cur_result = (
                str(cur_frame_count),
                str(cur_second),
                json.dumps(chi_sim_result),
                str(first_sim),
                str(last_sim),
            )
            if real_time_log:
                logger.msg('CURRENT', result=cur_result)
            result_list.append(cur_result)
            result_file.write('|,,|'.join(cur_result) + '\n')
            result_file.flush()
    return result_list


def exec_ocr(lang=None):
    """
    命令行启动tesseract

    :param lang:
    :return:
    """
    cmd = ['tesseract', TEMP_PIC, TEMP_RESULT_NAME]
    if lang:
        cmd = [*cmd, '-l', lang]
    return_code = subprocess.call(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if return_code:
        raise RuntimeError('tesseract error: {}'.format(return_code))


def get_ocr_result():
    """
    获取OCR分析结果

    :return:
    """
    analyse_result = []
    with open(TEMP_RESULT_TXT, encoding=DEFAULT_ENCODING) as result_file:
        for line in result_file:
            # filter
            line = re.sub('\W', '', line).replace('\n', '').replace('\r', '')
            if line:
                analyse_result.append(line)
    return analyse_result
