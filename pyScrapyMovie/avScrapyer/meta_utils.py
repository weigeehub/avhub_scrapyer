import requests
import re
from termcolor import cprint
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from selenium import webdriver
from termcolor import colored
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

from pyScrapyMovie.avScrapyer.meta_data import headers, max_retries

def get_api_json(url, retries=10):
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, verify=False)
            cprint(f'-> 状态码: {response.status_code}')
            if response.status_code == 404:
                cprint(f"-> 请求出错：404", 'yellow')
                return None
            if response.status_code == 200:
                return response.json()
            response.raise_for_status()
        except RequestException as e:
            cprint(f"请求出错: {e}, 正在重试...", 'yellow')
    cprint(f"经过 {retries} 次重试后仍无法获取数据", 'red')
    return None


def parse_json(series, json):
    obj = {
        'poster': json['MovieThumb'],
        'title': json['Title'],
        'actor': json['Actor'].replace(',', '、'),
        'carno': json['MovieID'],
        'series': json['Series'],
        'date': json['Release'].replace('-', '.')
    }
    filename = obj['series'] + '.' + obj['date'] + '_番号：' + obj['carno'] + '女优：' + obj['actor']
    if obj['series'] == '人妻マンコ図鑑':
        num = obj['title'].replace(obj['series'], '').strip().split(' ')[0].strip()
        filename = f'n{num}_{filename}'
    obj['filename'] = filename
    return obj


# 请求网页
def get_page_data(url, retries=10):
    for _ in range(retries):
        try:
            response = requests.get(url, headers=headers, verify=False)
            print(response.status_code)
            print(response.history)
            if response.history:
                # 获取原始请求状态码
                if response.history[0].status_code != 200:
                    print('网页进行了重定向，应该是没有找到数据')
                    return None

            if response.status_code == 200:
                # 检测页面的编码
                pcharset = 'UTF-8'
                match = re.search(r'<meta http-equiv="Content-Type" content="text/html; charset=(.*)">', response.text)
                if match:
                    charset = match.group(1)
                    pcharset = charset
                    cprint(f'-> 爬取到编码: {charset}', 'blue')
                else:
                    cprint(f'-> 未找到编码信息', 'red')

                page_content = response.content
                try:
                    page_content = response.content.decode(pcharset).encode('utf-8')
                except:
                    cprint(f'-> 尝试编码解析失败{pcharset} - UTF-8', 'red')
                return page_content
            else:
                return None
            response.raise_for_status()
        except RequestException as e:
            cprint(f"-> 请求出错: {e}, 正在重试...", 'yellow')

    cprint(f"-> 经过 {retries} 次重试后仍无法获取数据", 'red')
    return None


def get_carib_details(content):
    soup = BeautifulSoup(content, 'html.parser')
    title = soup.find('div', class_="heading").find('h1').text.strip()

    actorList = soup.find('span', class_='spec-content').findAll('span', itemprop="name")

    releaseDom = soup.find('span', itemprop="datePublished")
    release = ''
    website = 'https://www.caribbeancom.com'
    if releaseDom:
        release = releaseDom.text.strip().replace('/', '.')

    name_list = []
    for name in actorList:
        name_list.append(name.text.strip())

    actor = '、'.join(name_list)
    return (title, release, actor)


# 下载图片
def down_image(image_url, local_path, referer_url=''):
    cprint(f'---> 图片地址{image_url}', 'blue')
    max_retries = 10
    for retry_count in range(max_retries):
        headers = {
            "Referer": referer_url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(image_url, headers=headers)
        cprint(f'---> 下载图片的状态码：{response.status_code}', 'yellow')
        if response.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(response.content)
            cprint(f'---> 海报下载成功', 'green')
            return True
        else:
            retry_count += 1
            cprint(f"---> HTTP错误: {response.status_code}，正在进行第 {retry_count + 1} 次重试，等待3秒...", 'red')
    cprint(f'---> 达到最大重试次数，文件下载失败', 'red')
    return False


class EdgeDrive:
    def __init__(self):
        self.driver = None

    def open(self):
        edge_options = webdriver.EdgeOptions()

        edge_options.add_argument("--headless")
        prefs = {"profile.managed_default_content_settings.images": 2}
        edge_options.add_experimental_option("prefs", prefs)
        # 启用优化设置，这将阻止图片加载
        # edge_options.add_experimental_option('useAutomationExtension', False)

        driver = webdriver.Edge(options=edge_options)
        # 设置网页不加载图片
        driver.execute_cdp_cmd("Page.setDownloadBehavior", {
            "behavior": "deny",
            "download_path": ""
        })

        self.driver = driver
        return driver

    def close(self):
        if self.driver:
            self.driver.close()
        else:
            print('没有初始化edge drive')

class PlaywrightBrower():
    def __init__(self):
        self.browser = ''
        self.page = ''
        self.launch()

    def launch(self):
        with sync_playwright() as p:
            self.browser = p.chromium.launch(
                headless=False,  # 设置为无头模式，即浏览器在后台运行，不显示界面
                args=[
                    '--blink-settings=imagesEnabled=false'  # 设置不加载图片的参数
                ]
            )
            self.page = self.browser.new_page()

    def goto(self, url):
        self.page.once("domcontentloaded", lambda: print("页面DOM加载完成"))
        self.page.goto(url)
        page_source = self.page.content()
        return page_source

    def close(self):
        self.browser.close()


def playwright_brower(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # 设置为无头模式，即浏览器在后台运行，不显示界面
            args=[
                '--blink-settings=imagesEnabled=false'  # 设置不加载图片的参数
            ]
        )
        page = browser.new_page()
        page.once("domcontentloaded", lambda: print("页面DOM加载完成"))
        page.goto(url)
        page_source = page.content()
        return page_source

