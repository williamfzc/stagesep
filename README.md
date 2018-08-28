# stagesep

[![Maintainability](https://api.codeclimate.com/v1/badges/492f06dfdfc447e06470/maintainability)](https://codeclimate.com/github/williamfzc/stagesep/maintainability)

> 利用OCR，视频中的阶段检测工具

## 安装

```bash 
pip install opencv-python
```

同时需要在PC上安装tesseract，详见https://github.com/tesseract-ocr/tesseract/wiki

安装完成后在命令行中输入：

```bash
tesseract
```

如果能正常打印出内容说明已经安装成功。

## 使用

```python
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

```

## 效果

以`|,,|`为分隔符，三列分别为帧编号、对应的时间、识别到的文字。

```bash
1|,,|0.03333333333333333|,,|["Component\u79d2\u5f00"]
2|,,|0.06666666666666667|,,|["\u6ef4\u6ef4\u51fa\u884c\u79d2\u5f00", "Component\u79d2\u5f00"]
3|,,|0.1|,,|["\u6ef4\u6ef4\u51fa\u884c\u79d2\u5f00", "Component\u79d2\u5f00"]
4|,,|0.13333333333333333|,,|["Component\u79d2\u5f00"]
5|,,|0.16666666666666666|,,|["Component\u79d2\u5f00"]
6|,,|0.2|,,|["Component\u79d2\u5f00"]
7|,,|0.23333333333333334|,,|["\u6ef4\u6ef4\u51fa\u884c\u79d2\u5f00", "Component\u79d2\u5f00"]
8|,,|0.26666666666666666|,,|["\u6ef4\u6ef4\u51fa\u884c\u79d2\u5f00", "Component\u79d2\u5f00"]
9|,,|0.3|,,|["Component\u79d2\u5f00"]
```

## 关联与依赖

- [opencv](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html): 图像与视频处理
- [tesseract](https://github.com/tesseract-ocr/tesseract/wiki/Downloads): OCR

## License

MIT
