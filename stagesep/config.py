import os


# project relative
ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'stagesep')
RESOURCE_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'res')
OUTPUT_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'output')

# for tesseract usage
TEMP_DIR_PATH = os.path.join(ROOT_DIR_PATH, 'temp')
TEMP_PIC = os.path.join(TEMP_DIR_PATH, 'temp.png')
TEMP_RESULT = os.path.join(TEMP_DIR_PATH, 'temp_result')

# init
DIR_LIST = (ROOT_DIR_PATH, PROJECT_DIR_PATH, RESOURCE_DIR_PATH, OUTPUT_DIR_PATH, TEMP_DIR_PATH)
for each_dir in DIR_LIST:
    os.makedirs(each_dir, exist_ok=True)


__all__ = [*DIR_LIST, TEMP_PIC, TEMP_RESULT]
