import stagesep


# design

# begin
# 导入视频
stagesep_object = stagesep.load_video('res/demo_video.mp4')

# operation
# 主要用于规范视频，例如在30上下波动，则可以用此方法规范视频的fps
# 但不适合大幅度修改，例如60改为30，会导致后面时间对不上
stagesep_object = stagesep.rebuild_video(stagesep_object, 60)
print(stagesep_object.fps)

# get result
# 获取视频分析结果
stagesep.analyse_video(stagesep_object)
