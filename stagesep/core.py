import cv2
import json
from skimage.measure import compare_ssim
from skimage.feature import match_template
from .utils import *
from .config import *

try:
    ocr_module = __import__('.ocr')
except ModuleNotFoundError:
    ocr_module = None
    logger.msg('OCR MODULE NOT FOUND', msg='tesseract should be installed for ocr')


class AnalysisConfig(object):
    OCR_INSTALLED = bool(ocr_module)
    OCR_LANG = None
    REAL_TIME_LOG = None
    FEATURE_PIC_LIST = None


class AnalysisResult(object):
    def __init__(self):
        self.FRAME_ID = ''
        self.FRAME_TIMESTAMP = ''
        self.CONTAIN_WORD = ''
        self.SIM_WITH_FIRST_FRAME = ''
        self.SIM_WITH_LAST_FRAME = ''
        self.CONTAIN_FEATURE_LIST = []

    def to_list(self):
        return [
            json.dumps(each_arg) for each_arg in [
                self.FRAME_ID,
                self.FRAME_TIMESTAMP,
                self.CONTAIN_WORD,
                self.SIM_WITH_FIRST_FRAME,
                self.SIM_WITH_LAST_FRAME,
                self.CONTAIN_FEATURE_LIST,
            ]
        ]


class StageSepVideo(object):
    """ 视频对象 """

    def __init__(self, video_path):
        src = cv2.VideoCapture(video_path)
        self.path = video_path
        self.frame_count = src.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = src.get(cv2.CAP_PROP_FPS)
        self.width = int(src.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(src.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self.analysis_config = AnalysisConfig()

    def __repr__(self):
        return json.dumps({
            'src': repr(self.path),
            'frame_count': self.frame_count,
            'fps': self.fps,
            'size': (self.width, self.height),
        })


def load_video(video_path):
    """
    读取视频并将其转换成ssv对象

    :return:
    """
    ssv = StageSepVideo(video_path)
    logger.msg('LOAD VIDEO OK', vid=ssv)
    return ssv


def rebuild_video(old_ssv, new_fps=None, rotate_time=None):
    """
    将视频重新按照指定格式打包

    :param old_ssv: old ssv
    :param new_fps:
    :param rotate_time: 0为保持原状，1为逆时针旋转90度，2为逆时针180，以此类推
    :return:
    """
    size = (old_ssv.width, old_ssv.height)
    if rotate_time and rotate_time % 2 != 0:
        size = (size[1], size[0])
    target_fps = new_fps or old_ssv.fps

    writer = cv2.VideoWriter(TEMP_VIDEO, cv2.VideoWriter_fourcc(*"WMV1"), target_fps, size)
    with ssv_video_capture(old_ssv) as src:
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


def check_feature_file(feature_file_list):
    """
    验证feature文件是否存在及合法性

    :param feature_file_list: cv image list
    :return:
    """
    if not feature_file_list:
        return []
    if not isinstance(feature_file_list, (list, tuple)):
        raise TypeError('feature list should be iterable')
    for each_file in feature_file_list:
        if not os.path.exists(each_file):
            raise FileNotFoundError(each_file + ' not found')
    return [frame_prepare(cv2.imread(each_feature)) for each_feature in feature_file_list]


def load_cur_frame_info(cv2_src, analysis_result):
    """
    读取当前帧信息

    :param cv2_src:
    :param analysis_result:
    :return:
    """
    cur_frame_count = cv2_src.get(cv2.CAP_PROP_POS_FRAMES)
    cur_second = cv2_src.get(cv2.CAP_PROP_POS_MSEC) / 1000
    analysis_result.FRAME_ID = cur_frame_count
    analysis_result.FRAME_TIMESTAMP = cur_second


def apply_feature(target_frame, target_ssv_config, analysis_result):
    """
    利用match_template判定图像中是否包含特征列表中的内容

    :param target_frame:
    :param target_ssv_config:
    :param analysis_result:
    """
    feature_list = target_ssv_config.FEATURE_PIC_LIST
    if not feature_list:
        analysis_result.CONTAIN_FEATURE_LIST = []
        return
    result_list = []
    for each_feature in feature_list:
        res = match_template(target_frame, each_feature)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        result_list.append([1 if max_val > 0.99 else 0, max_val])
    analysis_result.CONTAIN_FEATURE_LIST = result_list


def apply_sim(target_frame, template_frame_list, analysis_result):
    """
    计算与首尾帧的相似度

    :param target_frame:
    :param template_frame_list:
    :param analysis_result:
    :return:
    """
    first_sim, last_sim, *_ = [
        compare_ssim(each_important_frame, target_frame)
        for each_important_frame in template_frame_list
    ]
    analysis_result.SIM_WITH_FIRST_FRAME = first_sim
    analysis_result.SIM_WITH_LAST_FRAME = last_sim


def apply_ocr(target_frame, analysis_config, analysis_result):
    """
    OCR

    :param target_frame:
    :param analysis_config:
    :param analysis_result:
    :return:
    """
    ocr_installed = analysis_config.OCR_INSTALLED
    ocr_lang = analysis_config.OCR_LANG
    if ocr_installed:
        ocr_module.exec_ocr(target_frame, lang=ocr_lang)
        result = ocr_module.get_ocr_result()
        analysis_result.CONTAIN_WORD = result
        return result
    analysis_result.CONTAIN_WORD = ''
    return ''


def handle_result(analysis_config, analysis_result, final_result_list, final_result_file):
    """
    结果处理

    :param analysis_config:
    :param analysis_result:
    :param final_result_list:
    :param final_result_file:
    :return:
    """
    cur_result = analysis_result.to_list()
    if analysis_config.REAL_TIME_LOG:
        logger.msg('CURRENT', result=cur_result)
    final_result_list.append(cur_result)
    final_result_file.write('|,,|'.join(cur_result) + '\n')
    final_result_file.flush()


def analyse_video(target_ssv, lang=None, real_time_log=None, feature_list=None):
    """
    分析视频

    :param target_ssv: ssv
    :param lang: 与tesseract对应的语言包同名，需要自行在其中配置好语言包
    :param real_time_log: 是否在运行时打印log
    :param feature_list: list，可传入特征图片路径，传入之后将对每一帧进行分析以判定特征图片是否存在其中
    :return:
    """
    target_ssv.analysis_config.OCR_LANG = lang or ''
    target_ssv.analysis_config.REAL_TIME_LOG = bool(real_time_log)
    target_ssv.analysis_config.FEATURE_PIC_LIST = check_feature_file(feature_list) or []

    first_frame, last_frame = map(frame_prepare, get_first_and_last_frame(target_ssv))
    result_list = []

    with ssv_video_capture(target_ssv) as src, \
        open(RESULT_TXT, 'w+', encoding=DEFAULT_ENCODING) as result_file:
        ret, frame = src.read()
        while ret:
            if not ret:
                break
            cur_analysis_result = AnalysisResult()
            # 当前帧参数
            load_cur_frame_info(src, cur_analysis_result)
            # 帧处理
            frame = frame_prepare(frame)
            # OCR阶段
            apply_ocr(frame, target_ssv.analysis_config, cur_analysis_result)
            # 特征提取
            apply_feature(frame, target_ssv.analysis_config, cur_analysis_result)
            # 与首尾帧的相似度
            apply_sim(frame, (first_frame, last_frame), cur_analysis_result)
            # 结果处理
            handle_result(target_ssv.analysis_config, cur_analysis_result, result_list, result_file)

            ret, frame = src.read()
    return result_list
