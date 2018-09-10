import contextlib
import cv2
import subprocess
import numpy as np


@contextlib.contextmanager
def ssv_video_capture(ssv):
    """ 打开视频的上下文控制 """
    video_cap = cv2.VideoCapture(ssv.path)
    yield video_cap
    video_cap.release()


def get_first_and_last_frame(target_ssv):
    """ 获取视频的首尾帧 """
    with ssv_video_capture(target_ssv) as video_cap:
        _, first_frame = video_cap.read()
        video_cap.set(1, target_ssv.frame_count - 1)
        _, last_frame = video_cap.read()
    return first_frame, last_frame


def rotate_pic(old_pic, rotate_time):
    """ 帧旋转 """
    new_pic = np.rot90(old_pic, rotate_time)
    return new_pic


def check_env():
    """
    环境检测，如tesseract是否安装

    :return:
    """
    ocr_return_code = subprocess.call(
        ['tesseract', '--version']
    )
    if ocr_return_code:
        raise ImportError('tesseract installed?')


def frame_prepare(old_frame):
    # 处理图片
    gray_frame = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
    blur_gray_frame = cv2.medianBlur(gray_frame, 3)
    return blur_gray_frame


__all__ = [
    'ssv_video_capture',
    'get_first_and_last_frame',
    'rotate_pic',
    'frame_prepare',
    'check_env',
]
