import stagesep


# 导入视频
ssv = stagesep.load_video('res/demo_video.mp4')

# 主要用于规范视频，用于调整fps与旋转视频
# 这里的rotate_time指的是逆时针90的旋转次数，3即向逆时针旋转270度，以此类推
ssv = stagesep.rebuild_video(ssv, new_fps=30, rotate_time=3)

# 查看一些基本信息
print(ssv.fps)

# 获取视频分析结果
# 可以直接根据这个list分析
result = stagesep.analyse_video(ssv, lang='chi_sim', real_time_log=True, feature_list=['res/feature1.jpg'])


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
