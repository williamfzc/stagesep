from setuptools import setup, find_packages


setup(
    name='stagesep',
    version='0.1.0',
    description='detect stages in video',
    author='williamfzc',
    author_email='fengzc@vip.qq.com',
    url='https://github.com/williamfzc/stagesep',
    packages=find_packages(),
    install_requires=[
        'opencv-python',
        'structlog',
        'numpy',
        'scikit-image',
        'matplotlib',
        'jieba',
    ]
)
