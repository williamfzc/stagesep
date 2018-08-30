# stagesep

[![Maintainability](https://api.codeclimate.com/v1/badges/492f06dfdfc447e06470/maintainability)](https://codeclimate.com/github/williamfzc/stagesep/maintainability)

> 利用OCR与图像识别，检测出视频中的阶段

## 安装

```bash
pip install -r requirements.txt
```

同时需要在PC上安装tesseract，详见https://github.com/tesseract-ocr/tesseract/wiki

安装完成后在命令行中输入：

```bash
tesseract
```

如果能正常打印出内容说明已经安装成功。另外中文视频需要从[这里](https://github.com/tesseract-ocr/langdata)下载语言包。

## 使用

方法的详细参数详见docstring

```python
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
```

在处理之后可以自由对这些数据进行分析，得到结论：

```python
# analysis
import json

# 也可以根据生成的文件进行分析
with open('output/sample_code.txt', encoding='utf-8') as f:
    for line in f:
        frame_id, time_stamp, result, first_sim, last_sim, match_template = line.split('|,,|')
        result = json.loads(result)
        match_template = json.loads(match_template)
        print(match_template)

```

## 数据

以`|,,|`为分隔符，分别为帧编号、对应的时间、识别到的文字、与首帧的相似度、与末帧的相似度、是否存在特征图片

```bash
1|,,|0.03333333333333333|,,|["Component\u79d2\u5f00"]|,,|1.0|,,|0.8744666747566574|,,|[[0, 0.27060889074688604]]
2|,,|0.06666666666666667|,,|["\u6ef4\u6ef4\u51fa\u884c\u79d2\u5f00", "Component\u79d2\u5f00"]|,,|0.9945336759012924|,,|0.8732500535811166|,,|[[0, 0.2702154980448374]]
3|,,|0.1|,,|["\u6ef4\u6ef4\u51fa\u884c\u79d2\u5f00", "Component\u79d2\u5f00"]|,,|0.9906519049687903|,,|0.8724468661392125|,,|[[0, 0.27054042596336]]
4|,,|0.13333333333333333|,,|["Component\u79d2\u5f00"]|,,|0.988436570914413|,,|0.8721808443349266|,,|[[0, 0.2707208582528737]]
5|,,|0.16666666666666666|,,|["Component\u79d2\u5f00"]|,,|0.9871368443037327|,,|0.8719868653399506|,,|[[0, 0.27088961169977555]]
6|,,|0.2|,,|["Component\u79d2\u5f00"]|,,|0.9859772325311379|,,|0.8717396593736755|,,|[[0, 0.271510313888945]]
7|,,|0.23333333333333334|,,|["\u6ef4\u6ef4\u51fa\u884c\u79d2\u5f00", "Component\u79d2\u5f00"]|,,|0.9853347906343617|,,|0.8714577411208654|,,|[[0, 0.272172863024542]]
8|,,|0.26666666666666666|,,|["\u6ef4\u6ef4\u51fa\u884c\u79d2\u5f00", "Component\u79d2\u5f00"]|,,|0.9851302157674813|,,|0.8715705722879807|,,|[[0, 0.27234378435162576]]
9|,,|0.3|,,|["Component\u79d2\u5f00"]|,,|0.9837414105243203|,,|0.8715590796786445|,,|[[0, 0.273214648246217]]
10|,,|0.3333333333333333|,,|["Component\u79d2\u5f00"]|,,|0.9838234965397075|,,|0.8716437205735402|,,|[[0, 0.27276039086080933]]
```

## 相似度变化

统一使用SSIM进行相似度匹配。

### 与视频首帧尾帧的相似度变化趋势

相似度变化趋势是规律的，基本符合应用加载流程。

![](pic/similarity.png)

### 文字识别出来的词数变化趋势

就目前来看，词数趋势难以反映问题。

![](pic/word_count.png)

## 特征提取

- opencv与skimage均提供了match_template方法供使用。
- 算法：Fast Normalized Cross-Correlation
- 详见[这里](http://scikit-image.org/docs/dev/auto_examples/features_detection/plot_template.html)

![](pic/match_template.png)

## TODO

- []jieba分词对OCR结果进一步分析
    - OCR得到的结果通常是不规则的句子
    - 使用分词后数据会变得更规范
- []从相似度变化趋势中提取阶段
    - 就目前情况来看，当前帧与首尾帧的相似度变化趋势是有规律的
- [x]关键点过滤
    - 假设我们需要在某段视频中找出会出现某个物体的部分帧
    - 传入该物体的特征图片（如果需要的是一个按钮，那么就是这个按钮的截图
    - 启动分析，结果中将会多出一列bool说明该帧中是否出现了该物体

## 关联与依赖

- [opencv](https://opencv-python-tutroals.readthedocs.io/en/latest/py_tutorials/py_tutorials.html): 图像与视频处理
- [tesseract](https://github.com/tesseract-ocr/tesseract/wiki/Downloads): OCR
- [skimage](https://github.com/scikit-image/scikit-image): 图片相似度

## License

MIT
