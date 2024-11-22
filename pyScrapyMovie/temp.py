import os
import re
from aTools import utils
from pathlib import Path
from avScrapyer.meta_utils import playwright_brower

def play():
    dir = Path(r'F:\已归档\【図鑑】10mu-秘藏')
    dir_list = utils.myOsFile.getListdir(dir)
    for item in dir_list:
        if item.name != '归档' and item.name != '已下架':
            print('目录', item.name)
            # 找到视频文件 然后移动位置
            file_list = utils.myOsFile.getListfile(item)
            # print('文件列表:', file_list)
            for item_f in file_list:
                video_suffix_list = ['.mp4', '.wmv', '.avi', '.mkv', '.ts', '.flv', '.mpeg']
                if item_f.suffix in video_suffix_list:
                    print('视频文件：', item_f.name)
                    old_path = item_f

                    filename = ''
                    pattern = r'番号：.*?(?=_女优)'
                    match = re.search(pattern, item_f.stem)
                    if match:
                        result = match.group()
                        filename = '10mu-' + result + item_f.suffix
                    else:
                        print("未找到匹配内容")
                        continue
                    new_path = dir / filename.replace('番号：', '')
                    print(old_path, new_path)
                    os.rename(old_path, new_path)


def query_has_image():
    dir = Path(r'F:\已归档\媒体库\【女体図鑑】\10mu-秘藏')
    dir_list = utils.myOsFile.getListdir(dir)
    for item in dir_list:
        file_list =  utils.myOsFile.getListfile(item)
        for item_f in file_list:
            flag = False
            if item_f.suffix in ['.png', '.jpg']:
                flag = True
        if not flag:
            print('当前没有海报', item.name )


def query_video():
    dir = Path(r'E:\AV媒体库【E】\再更 - hucows')
    dir_list = utils.myOsFile.getListdir(dir)
    for item in dir_list:
        file_list = utils.myOsFile.getListfile(item)
        for item_f in file_list:
            image_list = [ '.png', '.jpg', '.jpeg']
            other = [ '.ini','.nfo',]
            video_list = ['.mp4', '.wmv','.mkv']

            suffix_arr = video_list
            if item_f.suffix in suffix_arr:
                print('当前视频', item, item_f.name)

                new_path = dir / item_f.name
                os.rename(item_f, new_path)


if __name__ == "__main__":
    a = playwright_brower('https://www.baidu.com')
    print(a)
    # query_has_image()
    # query_video()