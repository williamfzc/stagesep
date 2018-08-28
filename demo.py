import stagesep
import json


# 导入视频
stagesep_object = stagesep.load_video('res/demo_video.mp4')

# 主要用于规范视频，用于调整fps与旋转视频
# 这里的rotate_time指的是逆时针90的旋转次数，3即向逆时针旋转270度，以此类推
stagesep_object = stagesep.rebuild_video(stagesep_object, new_fps=30, rotate_time=3)

# 查看一些基本信息
print(stagesep_object.fps)

# 获取视频分析结果
# 可以直接根据这个list分析
result = stagesep.analyse_video(stagesep_object, lang='chi_sim', real_time_log=True)

# 也可以根据生成的文件进行分析
with open('output/1535442458.txt', encoding='utf-8') as f:
    for line in f:
        frame_id, time_stamp, result = line.split('|,,|')
        result = json.loads(result)
        print(result)
