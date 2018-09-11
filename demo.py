import stagesep

# 导入视频
ssv = stagesep.load_video('res/demo_video.mp4')

# 主要用于规范视频，用于调整fps与旋转视频
# 这里的rotate_time指的是逆时针90的旋转次数，3即向逆时针旋转270度，以此类推
# 正常的速度类测试应该用 fps>60 的视频以保证足够精确
ssv = stagesep.rebuild_video(ssv, new_fps=30, rotate_time=3)

# 查看一些基本信息
print(ssv.fps)

# 可以不需要使用OCR启动分析
result1 = stagesep.analyse_video(
    ssv,
    no_ocr=True,
    real_time_log=True,
)

# 完整版本
# 可以直接根据这个list分析
result = stagesep.analyse_video(
    ssv,

    # 对应tesseract的语言包
    lang='chi_sim',

    # 是否输入分析实时log
    real_time_log=True,

    # 特征图片
    feature_list=['res/feature1.jpg'],
)

# analysis
import json

# 也可以根据生成的文件进行分析
with open('output/sample_data.txt', encoding='utf-8') as f:
    for line in f:
        frame_id, time_stamp, result, first_sim, last_sim, match_template = line.split('|,,|')
        result = json.loads(result)
        match_template = json.loads(match_template)[0]
        if match_template[0]:
            print(time_stamp, result, match_template[1])
