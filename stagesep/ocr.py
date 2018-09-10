"""
tesseract在命令行运行，负责提取图片中的文字并生成文本文件
此部分设计为不与tesseract发生耦合，只通过文件通讯
"""
import subprocess
import re
import cv2
import jieba
from .config import *
from .utils import check_env

check_env()


def exec_ocr(frame, lang=None):
    """
    命令行启动tesseract

    :param frame:
    :param lang:
    :return:
    """
    cv2.imwrite(TEMP_PIC, frame)
    cmd = ['tesseract', TEMP_PIC, TEMP_RESULT_NAME]
    if lang:
        cmd = [*cmd, '-l', lang]
    need_shell = True if PLATFORM_NAME == 'Windows' else False
    return_code = subprocess.call(
        cmd,
        shell=need_shell,
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
                word_list = jieba.cut(line)
                analyse_result.extend(word_list)
    return analyse_result
