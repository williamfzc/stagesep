import os
import time


# project relative
ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'stagesep')
RESOURCE_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'res')
OUTPUT_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'output')
DEFAULT_ENCODING = 'utf-8'
EXEC_TIMESTAMP = str(int(time.time()))
RESULT_TXT = os.path.join(OUTPUT_DIR_PATH, EXEC_TIMESTAMP) + '.txt'

# for tesseract usage
TEMP_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'temp')
TEMP_PIC = os.path.join(TEMP_DIR_PATH, 'temp.png')
TEMP_VIDEO = os.path.join(TEMP_DIR_PATH, 'temp.avi')
TEMP_RESULT_NAME = os.path.join(TEMP_DIR_PATH, 'temp_result')
TEMP_RESULT_TXT = TEMP_RESULT_NAME + '.txt'

# init
DIR_LIST = (ROOT_DIR_PATH, PROJECT_DIR_PATH, RESOURCE_DIR_PATH, OUTPUT_DIR_PATH, TEMP_DIR_PATH)
for each_dir in DIR_LIST:
    os.makedirs(each_dir, exist_ok=True)
