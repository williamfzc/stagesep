# stagesep

> detect stages in video with OCR 

## Usage

```python
import stagesep


# 导入视频
stagesep_object = stagesep.load_video('res/demo_video.mp4')

# 主要用于规范视频，例如在30上下波动，则可以用此方法规范视频的fps
# 但不适合大幅度修改，例如60改为30，会导致后面时间对不上
stagesep_object = stagesep.rebuild_video(stagesep_object, 60)

# 查看一些基本信息
print(stagesep_object.fps)

# 获取视频分析结果
stagesep.analyse_video(stagesep_object)
```

## Dependence

- [opencv](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html): image processing
- [tesseract](https://github.com/tesseract-ocr/tesseract/wiki/Downloads): get specific words from image

## License

MIT
