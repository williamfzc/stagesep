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


def load_video(video_path):
    """
    读取视频并将其转换成ssv对象

    :return:
    """
    ssv = StageSepVideo(video_path)
    logger.msg('LOAD VIDEO OK', vid=ssv)
    return ssv


def rebuild_video(old_stagesep_video, new_fps=None, rotate_time=None):
    """
    将视频重新按照指定格式打包

    :param old_stagesep_video: old ssv
    :param new_fps:
    :param rotate_time: 0为保持原状，1为逆时针旋转90度，2为逆时针180，以此类推
    :return:
    """
    size = (old_stagesep_video.width, old_stagesep_video.height)
    if rotate_time and rotate_time % 2 != 0:
        size = (size[1], size[0])
    target_fps = new_fps or old_stagesep_video.fps

    writer = cv2.VideoWriter(TEMP_VIDEO, cv2.VideoWriter_fourcc(*"WMV1"), target_fps, size)
    with ssv_video_capture(old_stagesep_video) as src:
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


def check_image_if_contain(img, feature_list):
    """
    利用match_template判定图像中是否包含特征列表中的内容

    :param img:
    :param feature_list:
    :return return_list:
    """
    result_list = []
    for each_feature in feature_list:
        res = match_template(img, each_feature)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        result_list.append([1 if max_val > 0.99 else 0, max_val])
    return result_list


def analyse_video(target_ssv, lang=None, real_time_log=None, feature_list=None):
    """
    分析视频

    :param target_ssv: ssv
    :param lang: 与tesseract对应的语言包同名，需要自行在其中配置好语言包
    :param real_time_log: 是否在运行时打印log
    :param feature_list: list，可传入特征图片路径，传入之后将对每一帧进行分析以判定特征图片是否存在其中
    :return:
    """
    feature_list = check_feature_file(feature_list)
    first_frame, last_frame = map(frame_prepare, get_first_and_last_frame(target_ssv))
    result_list = []

    with ssv_video_capture(target_ssv) as src, \
            open(RESULT_TXT, 'w+', encoding=DEFAULT_ENCODING) as result_file:
        ret, frame = src.read()
        while ret:
            if not ret:
                break
            # 当前帧参数
            cur_frame_count = src.get(cv2.CAP_PROP_POS_FRAMES)
            cur_second = src.get(cv2.CAP_PROP_POS_MSEC) / 1000
            # 帧处理
            frame = frame_prepare(frame)
            # OCR阶段
            if ocr_module:
                ocr_module.exec_ocr(frame, lang=lang)
                chi_sim_result = ocr_module.get_ocr_result()
            else:
                chi_sim_result = ''
            # 特征提取
            contained_feature_list = check_image_if_contain(frame, feature_list)
            # 与首尾帧的相似度
            first_sim, last_sim = [
                compare_ssim(each_important_frame, frame)
                for each_important_frame in (first_frame, last_frame)
            ]
            # 结果处理
            cur_result = [
                str(cur_frame_count),
                str(cur_second),
                json.dumps(chi_sim_result),
                str(first_sim),
                str(last_sim),
            ]
            if contained_feature_list:
                cur_result.append(str(contained_feature_list))
            if real_time_log:
                logger.msg('CURRENT', result=cur_result)
            result_list.append(cur_result)
            result_file.write('|,,|'.join(cur_result) + '\n')
            result_file.flush()
            ret, frame = src.read()
    return result_list
