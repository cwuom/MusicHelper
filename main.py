"""
MusicHelper by @im-cwuom
Github: https://github.com/cwuom/MusicHelper/
"""

from __future__ import annotations

import configparser
import json
import os
import platform
import sys
import time
import traceback
from random import randint

import requests
import keyboard

from subprocess import call
import multitasking
import signal
from tqdm import tqdm

signal.signal(signal.SIGINT, multitasking.killall)

API_URL = "https://music.ghxi.com/wp-admin/admin-ajax.php"
DEBUG_MODE = True

INDEX = 1
INDEX_MAX = 0
INDEX_MIN = 1
SelectStyle = 0
music_type = "qq"
select_char = "X"

MB = 1024 ** 2

request_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 "
                  "Safari/537.36 Edg/117.0.2045.43",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://music.ghxi.com",
    "Referer": "https://music.ghxi.com/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "Connection": "keep-alive",
    "Host": "music.ghxi.com",
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 '
                  'Safari/537.36 QIHU 360SE'
}

config = configparser.ConfigParser()


def write_cfg():
    config["API"] = {
        "url": "https://music.ghxi.com/wp-admin/admin-ajax.php",
        "music_type": "qq"
    }

    config['SETTING'] = {
        "Select_Style": "0",
        "select_char": "X",
        "DEBUG": False
    }

    with open('config.ini', 'w') as f:
        config.write(f)


# ========================== download_helper ==========================
# https://zhuanlan.zhihu.com/p/369531344
# 多线程下载有问题，废弃
# def split(start: int, end: int, step: int) -> list[tuple[int, int]]:
#     # 分多块
#     parts = [(start, min(start + step, end))
#              for start in range(0, end, step)]
#     return parts
#
#
# def get_file_size(url: str, raise_error: bool = False) -> int | None:
#     response = requests.head(url)
#     file_size = response.headers.get('Content-Length')
#     if file_size is None:
#         if raise_error is True:
#             raise ValueError('该文件不支持多线程分段下载！')
#         return file_size
#     return int(file_size)
#
#
# def download(url: str, file_name: str, retry_times: int = 3, each_size=16 * MB) -> None:
#     f = open(file_name, 'wb')
#     file_size = get_file_size(url)
#
#     @retry(tries=retry_times)
#     @multitasking.task
#     def start_download(start: int, end: int) -> None:
#         _headers = headers.copy()
#         # 分段下载的核心
#         _headers['Range'] = f'bytes={start}-{end}'
#         # 发起请求并获取响应（流式）
#         response = session.get(url, headers=_headers, stream=True)
#         # 每次读取的流式响应大小
#         chunk_size = 128
#         # 暂存已获取的响应，后续循环写入
#         chunks = []
#         for chunk in response.iter_content(chunk_size=chunk_size):
#             # 暂存获取的响应
#             chunks.append(chunk)
#             # 更新进度条
#             bar.update(chunk_size)
#         f.seek(start)
#         for chunk in chunks:
#             f.write(chunk)
#         # 释放已写入的资源
#         del chunks
#
#     session = requests.Session()
#     # 分块文件如果比文件大，就取文件大小为分块大小
#     each_size = min(each_size, file_size)
#
#     # 分块
#     parts = split(0, file_size, each_size)
#     # 创建进度条
#     bar = tqdm(total=file_size, desc=f'{file_name}')
#     for part in parts:
#         start, end = part
#         start_download(start, end)
#     # 等待全部线程结束
#     multitasking.wait_for_tasks()
#     f.close()
#     bar.close()

def download(url: str, file_name: str):
    for x in range(3):
        # noinspection PyBroadException
        try:
            # 发起 head 请求，即只会获取响应头部信息
            head = requests.head(url, headers=headers)
            # 文件大小，以 B 为单位
            file_size = head.headers.get('Content-Length')
            if file_size is not None:
                file_size = int(file_size)
            response = requests.get(url, headers=headers, stream=True)
            # 一块文件的大小
            chunk_size = 1024
            bar = tqdm(total=file_size, desc=f'{file_name}')
            with open(file_name, mode='wb') as f:
                # 写入分块文件
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    bar.update(chunk_size)
            # 关闭进度条
            bar.close()
            break
        except Exception:
            while True:
                file_name = f"Songs/不和谐的文件名(请手动重命名)_{randint(100000, 999999)}.mp3"
                if not os.path.exists(file_name):
                    break
            continue


# =========================================================

# 歌曲结构体
class SongStruct:
    def __init__(self):
        self.song_name = ""
        self.singer = ""
        self.albumname = ""
        self.album_img = ""
        self.song_id = ""
        self.size128 = 1
        self.size320 = 1
        self.size_flac = 1


# 自定日志输出类
class Logger:
    def __init__(self):
        self.time_now = time.strftime('%H:%M:%S', time.localtime())

    def info(self, info, title="INFO"):
        print(f"[{self.time_now}] [{title}] {info}")

    def error(self, info):
        print(f"[ERROR - {self.time_now}] {info}")

    def debug(self, info):
        if DEBUG_MODE:
            print(f"[DEBUG - {self.time_now}] {info}")


# 音乐检索/破解类
class Music:
    @staticmethod
    def search(search_word, _cookies):
        """
        通过关键字搜索歌曲，支持模糊搜索。
        :param search_word: 检索关键字
        :param _cookies: 传入get_cookies中获取的cookies，用于API验证。
        :return: 返回检索结果列表
        """
        data = {
            "action": "gh_music_ajax",
            "type": "search",
            "music_type": music_type,
            "search_word": search_word
        }
        req = requests.post(API_URL, data=data, headers=request_headers, cookies=_cookies)
        return json.loads(req.text)

    @staticmethod
    def get_song_url(song_id, _cookies):
        """
        获取歌曲直链，返回结果不保证百分百正确。
        :param song_id: 歌曲id
        :param _cookies: 同上
        :return: 歌曲直链
        """
        data = {
            "action": "gh_music_ajax",
            "type": "getMusicUrl",
            "music_type": music_type,
            "music_size": "flac",
            "songid": song_id
        }

        req = requests.post(API_URL, data=data, headers=request_headers, cookies=_cookies)
        return json.loads(req.text)

    @staticmethod
    def get_code():
        """
        :return: 获取每日code，用于爬取cookies并验证API
        """
        req = requests.get("https://ghxcx.lovestu.com/api/index/today_secret")
        return json.loads(req.text)["data"]

    @staticmethod
    def get_cookies(_code):
        """
        :param _code: 传入get_code中返回的code
        :return: dict(cookies)
        """
        data = {
            "action": "gh_music_ajax",
            "type": "postAuth",
            "code": _code
        }

        req = requests.post(API_URL, data=data, headers=request_headers)
        return req.cookies.get_dict()


def clear():
    """
    清屏，不兼容pycharm
    """
    system = platform.system()
    if system == u'Windows':
        call("cls", shell=True)
    else:
        os.system('clear')


def show_result(_index):
    """
    展示歌曲列表
    :param _index: 歌曲索引
    """
    index = 0
    for _song in songs_data:
        index += 1
        if index == _index:
            print(f"[{select_char}] {_song.song_name} - {_song.singer} [{_song.albumname}]")
        else:
            print(f"[ ] {_song.song_name} - {_song.singer} [{_song.albumname}]")

    print("\n按下回车开始下载... 显示不全请全屏终端程序。")
    print(
        f"index: {_index}, "
        f"当前选择《{songs_data[_index - 1].song_name} - {songs_data[_index - 1].singer}"
        f" [{songs_data[_index - 1].albumname}]》")


def hook_keys(x):
    """
    监听键盘事件
    :param x: 键盘event，包括按键按下松开之类的
    """
    global INDEX, INDEX_MAX, INDEX_MIN

    if x.event_type == 'down' and x.name == 'left':
        pass
    if x.event_type == 'down' and x.name == 'right':
        pass
    if x.event_type == 'down' and x.name == 'up':
        clear()
        if INDEX > INDEX_MIN:
            INDEX -= 1

        show_result(INDEX)
    if x.event_type == 'down' and x.name == 'down':
        clear()
        if INDEX < INDEX_MAX:
            INDEX += 1

        show_result(INDEX)


def makedirs(folder):
    """
   创建文件夹，创建前先判断文件夹是否存在
   :param folder: 文件夹名称
   :return:
    """
    if not os.path.exists(folder):
        os.makedirs(folder)


def match_music_type(music_url, _song):
    """
    判断音乐文件后缀类型
    :param music_url: 音乐直链
    :param _song: 歌曲结构体对象
    """
    if music_url.find(".flac") != -1:
        download(music_url, f"Songs/{_song.song_name}-{_song.singer}.flac")
    elif music_url.find(".wav") != -1:
        download(music_url, f"Songs/{_song.song_name}-{_song.singer}.wav")
    elif music_url.find(".mp3") != -1:
        download(music_url, f"Songs/{_song.song_name}-{_song.singer}.mp3")
    else:
        logger.error(
            f"无法匹配{music_url}的文件类型，因为他不受支持。若你确认这是本项目的问题，请联系作者。当然，你也可以自己修改代码或是手动下载。")


def SelectStyle0():
    """
    选择风格0，用上下键选择歌曲，会导致清屏。
    """
    index = 0
    for _song in songs_data:
        index += 1
        if index == INDEX:
            print(f"[{select_char}] {_song.song_name} - {_song.singer} [{_song.albumname}]")
        else:
            print(f"[ ] {_song.song_name} - {_song.singer} [{_song.albumname}]")

    keyboard.hook(hook_keys)
    keyboard.wait("Enter")
    keyboard.unhook_all()
    _song = songs_data[INDEX - 1]
    logger.info("正在解析歌曲下载链接... 请稍等")
    music_url = music.get_song_url(_song.song_id, cookies)["url"]
    logger.info(title="Done", info=f"歌曲下载链接解析完成，url={music_url}")
    makedirs("Songs")

    match_music_type(music_url, _song)


def SelectStyle1():
    """
    选择风格1，采用序号来选择歌曲，不会清屏。
    """
    global song, INDEX
    index = 0
    for song in songs_data:
        index += 1
        print(f"[{index}] {song.song_name} - {song.singer} [{song.albumname}]")

    while True:
        # noinspection PyBroadException
        try:
            INDEX = int(input("请输入歌曲序号: "))
            song = songs_data[INDEX - 1]
            break
        except Exception:
            logger.error(f"你认真的? {INDEX}不是一个有效的序号。")
            traceback.print_exc(file=open("error.txt", "a+"))
            continue

    logger.info("正在解析歌曲下载链接... 请稍等")
    music_url = music.get_song_url(song.song_id, cookies)["url"]
    logger.info(title="Done", info=f"歌曲下载链接解析完成，url={music_url}")
    makedirs("Songs")

    match_music_type(music_url, song)


log_file = open("UncaughtException.txt", "a+")


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    print("程序在运行时发生致命错误，请查看日志文件<UncaughtException.txt>中的报错信息并报告给作者。")
    print("程序将在10s后退出。 报错详情如下：")
    for line in traceback.format_exception(exc_type, exc_value, exc_traceback):
        log_file.write(line)
        print(line, end="")

    log_file.close()
    time.sleep(10)


if DEBUG_MODE:
    sys.excepthook = handle_exception

if __name__ == '__main__':
    logger = Logger()
    logger.info(title="Starting", info="正在初始化程序，这可能需要一些时间来获取数据。")
    music = Music()
    cookies = {}

    # 读取配置文件
    if not os.path.exists("config.ini"):
        write_cfg()
        logger.info("配置文件不存在，已自动创建。")
    config.read("config.ini")
    API_URL = config["API"]["url"]
    music_type = config["API"]["music_type"]
    DEBUG_MODE = bool(config["SETTING"]["debug"])
    SelectStyle = int(config["SETTING"]["select_style"])
    select_char = config["SETTING"]["select_char"]

    logger.info(f"当前平台: {music_type}, 可在歌曲输入框使用'$#help#'查看帮助。")

    try:  # 破解反爬
        code = music.get_code()
        logger.info(title="OK", info=f"获取code成功, code={code}。正在抓取cookies....")
        cookies = music.get_cookies(code)
        logger.info(title="Done", info=f"获取cookies成功。cookies={cookies}，初始化完成。")

    except Exception as e:
        logger.error(
            "在初始化程序时发生了错误，请检查网络连接。若持续出现此错误，则有可能是对方的API服务器出现了故障或是反爬手段增强了。请关注最新动态")
        logger.error(e)
        traceback.print_exc(file=open("error.txt", "a+"))

    while True:
        song_name = input("请输入要下载的歌曲名称(特殊指令格式为'$#[command]#', $#help#可查看特殊指令)\n> ")
        if song_name == "$#help#":
            print("平台切换指令\n"
                  "$#wy# - 将搜索源切换成网易云音乐\n"
                  "$#qq# - 将搜索源切换成QQ音乐\n"
                  "$#about# - 查看项目信息\n"
                  "$#faq# - 查看常见问题")
        if song_name == "$#wy#":
            music_type = "wy"
            config.set('API', 'music_type', 'wy')
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            logger.info("成功将检索源切换为网易云云音乐。")
        if song_name == "$#qq#":
            music_type = "qq"
            config.set('API', 'music_type', 'qq')
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            logger.info("成功将检索源切换为QQ音乐。")
        if song_name == "$#about#":
            print("作者: @im-cwuom | 仅供学习交流使用，请在72小时内删除本程序。")

        if song_name == "$#faq#":
            print("Q: 为什么下载的音乐有问题/无法搜索音乐/频繁报错/无法下载?\nA: "
                  "本项目使用的是别人的API，可能是对方的API服务器反爬手段增强了或是对本程序做出了一些限制。又或是API服务器目前正出现故障，请关注最新动态或是过个几小时/一天再去使用。")

        if song_name[0] + song_name[1] == "$#" and song_name[-1] == "#":
            continue

        search_result = music.search(song_name, _cookies=cookies)
        songs_data = []
        # noinspection PyBroadException
        try:
            for song in search_result["data"]:
                song_struct = SongStruct()
                song_struct.song_name = song["songname"]
                song_struct.singer = song["singer"]
                song_struct.albumname = song["albumname"]
                song_struct.album_img = song["album_img"]
                song_struct.song_id = song["songid"]
                song_struct.size128 = song["size128"]
                song_struct.size320 = song["size320"]
                song_struct.size_flac = song["sizeflac"]
                songs_data.append(song_struct)
        except Exception:
            logger.error(songs_data)
            logger.error("无法解析音乐数据，API服务器可能出现了故障，请稍后重试。")
            continue

        INDEX_MAX = len(songs_data)

        logger.info(title="Done", info="歌曲列表加载完成。使用上下键选择歌曲，回车下载。")
        try:
            if SelectStyle == 0:
                SelectStyle0()
            elif SelectStyle == 1:
                SelectStyle1()
            else:
                SelectStyle0()

            logger.info(title="Done", info="歌曲下载完成...")
        except Exception as e:
            logger.error(
                "在选择/下载歌曲时发生了错误，请检查网络连接。若持续出现此错误，则有可能是对方的API服务器出现了故障或是反爬手段增强了。请关注最新动态")
            logger.error(e)
            traceback.print_exc(file=open("error.txt", "a+"))

        print("为了防止误触，请输入'!c'继续.... Ctrl+C退出")
        while True:
            if input() == "!c":
                break
