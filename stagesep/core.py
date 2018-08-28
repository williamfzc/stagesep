import cv2
import subprocess
import re
import json
from .config import *


class StageSepVideo(object):
    def __init__(self, video_path):
        src = cv2.VideoCapture(video_path)
        self.src = src
        self.frame_count = src.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = src.get(cv2.CAP_PROP_FPS)
        self.width = int(src.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(src.get(cv2.CAP_PROP_FRAME_HEIGHT))


def load_video(video_path):
    """
    Load video file into stagesep

    :return:
    """
    return StageSepVideo(video_path)


def rebuild_video(old_stagesep_video, new_fps):
    """
    Rebuild this video, change the size or fps ...

    :return:
    """
    size = (old_stagesep_video.width, old_stagesep_video.height)
    writer = cv2.VideoWriter(TEMP_VIDEO, cv2.VideoWriter_fourcc(*"WMV1"), new_fps, size)

    src = old_stagesep_video.src
    success, frame = src.read()
    while success:
        writer.write(frame)
        success, frame = src.read()

    return StageSepVideo(TEMP_VIDEO)


def get_stage():
    """
    get stages from video, using OCR

    :return:
    """
    print('get stage')


def check_env():
    tesseract_return_code = subprocess.call('tesseract --version', stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if tesseract_return_code:
        raise ImportError('tesseract installed?')


def analyse_video(target_stagesep_video):
    src = target_stagesep_video.src
    ret = True
    cur_frame_count = 0
    result_list = []

    with open(EXEC_TIMESTAMP + '.txt', 'w+', encoding=DEFAULT_ENCODING) as result_file:
        while ret:
            ret, frame = src.read()
            if not ret:
                break
            # 当前帧参数
            cur_frame_count += 1
            cur_second = src.get(cv2.CAP_PROP_POS_MSEC) / 1000
            # 处理图片
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur_gray_frame = cv2.medianBlur(gray_frame, 3)
            # OCR阶段
            cv2.imwrite(TEMP_PIC, blur_gray_frame)
            exec_tesseract(lang='chi_sim')
            chi_sim_result = get_tesseract_result()
            # 结果处理
            cur_result = (str(cur_frame_count), str(cur_second), json.dumps(chi_sim_result))
            result_list.append(cur_result)
            result_file.write('|,,|'.join(cur_result) + '\n')
            result_file.flush()
    return result_list


def exec_tesseract(lang=None):
    """
    exec tesseract to analyse picture

    :param lang:
    :return:
    """
    cmd = ['tesseract', TEMP_PIC, TEMP_RESULT_NAME]
    if lang:
        cmd = [*cmd, '-l', lang]
    return_code = subprocess.call(
        cmd,
        shell=True,
        stdout=subprocess.PIPE
    )
    if return_code:
        raise RuntimeError('tesseract error: %s', return_code)


def get_tesseract_result():
    """
    get tesseract analysis result from txt, and return list

    :return:
    """
    analyse_result = []
    with open(TEMP_RESULT_TXT, encoding=DEFAULT_ENCODING) as result_file:
        for line in result_file:
            line = re.sub('\W', '', line).replace('\n', '').replace('\r', '')
            if line:
                analyse_result.append(line)
    return analyse_result
