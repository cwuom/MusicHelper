"""
MusicHelper by @im-cwuom
GitHub: https://github.com/cwuom/MusicHelper/
"""

from __future__ import annotations

import configparser
import json
import os
import platform
import sys
import time
import traceback
from base64 import b64decode
from random import randint, choice
from threading import Thread

import pyqrcode
import requests
import keyboard

from subprocess import call
import multitasking
import signal
from tqdm import tqdm

signal.signal(signal.SIGINT, multitasking.killall)

NODE_API = "http://localhost:3000"
NODE_API_QQ = "http://localhost:3300"
API_URL = "https://music.ghxi.com/wp-admin/admin-ajax.php"
DEBUG_MODE = True

cookies_wy = {}
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

user_agent_list = [
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) Gecko/20100101 Firefox/61.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.47"
]

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


def runNodeApi(type="wy"):
    logger.info("正在检查接口是否工作...")

    while True:
        try:
            API = {"wy": NODE_API, "qq": NODE_API_QQ}
            requests.get(API[type])
            break
        except Exception:
            logger.info("正在启动API服务")
            if type == "wy":
                cmd = """
                cd node
                node app.js
                    """
            elif type == "qq":
                cmd = """
                 cd nodeQQ
                 npm start
                     """
            with open("start.bat", "w") as w:
                w.write(cmd)

            os.system("start start.bat")
            time.sleep(3)
            pass

    logger.info(title="OK", info="app.js - 服务启动成功")


# 歌曲结构体
class SongStruct_Playlist:
    def __init__(self):
        self.song_name = ""
        self.singer = []
        self.al_name = ""


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
        self.song_url = ""
        self.music_type = ""


# 自定日志输出类
class Logger:
    def __init__(self):
        self.time_now = None

    def info(self, info, title="INFO"):
        self.time_now = time.strftime('%H:%M:%S', time.localtime())
        print(f"[{self.time_now}] [{title}] {info}")

    def error(self, info):
        self.time_now = time.strftime('%H:%M:%S', time.localtime())
        print(f"[ERROR - {self.time_now}] {info}")

    def debug(self, info):
        if DEBUG_MODE:
            self.time_now = time.strftime('%H:%M:%S', time.localtime())
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
        # logger.debug(req.text)
        return [json.loads(req.text), music_type]

    @staticmethod
    def get_song_url(_song_id, _cookies, _music_type=music_type):
        """
        获取歌曲直链，返回结果不保证百分百正确。
        :param _music_type:
        :param _song_id: 歌曲id
        :param _cookies: 同上
        :return: 歌曲直链
        """
        data = {
            "action": "gh_music_ajax",
            "type": "getMusicUrl",
            "music_type": _music_type,
            "music_size": "flac",
            "songid": _song_id
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


def calc_divisional_range(filesize, chuck=10):
    step = filesize // chuck
    arr = list(range(0, filesize, step))
    result = []
    for i in range(len(arr) - 1):
        s_pos, e_pos = arr[i], arr[i + 1] - 1
        result.append([s_pos, e_pos])
    result[-1][-1] = filesize - 1
    return result


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
            f"无法匹配{music_url}的文件类型，因为他不受支持。若你确认这是本项目的问题，请联系作者。当然，你也可以自己修改代码或是手动下载。（已将文件后缀自动匹配为mp3）")
        download(music_url, f"Songs/{_song.song_name}-{_song.singer}.mp3")


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


def refresh_ua():
    global request_headers
    request_headers["User-Agent"] = choice(user_agent_list)
    headers["User-Agent"] = choice(user_agent_list)


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


def save_music(url, music_name, singer_name):
    if url.find(".flac") != -1:
        music_name = 'Songs_nodeapi/%s-%s.flac' % (music_name, singer_name)
    elif url.find(".wav") != -1:
        music_name = 'Songs_nodeapi/%s-%s.wav' % (music_name, singer_name)
    elif url.find(".mp3") != -1:
        music_name = 'Songs_nodeapi/%s-%s.mp3' % (music_name, singer_name)
    elif url.find(".m4a") != -1:
        music_name = 'Songs_nodeapi/%s-%s.m4a' % (music_name, singer_name)
    elif url.find(".ape") != -1:
        music_name = 'Songs_nodeapi/%s-%s.ape' % (music_name, singer_name)
    else:
        logger.error(
            f"无法匹配{url}的文件类型，因为他不受支持。若你确认这是本项目的问题，请联系作者。当然，你也可以自己修改代码或是手动下载。(已自动匹配为mp3)")
        music_name = 'Songs_nodeapi/%s-%s.mp3' % (music_name, singer_name)

    for x in range(3):
        try:
            makedirs("Songs_nodeapi")
            music_response = requests.get(url, headers=headers).content
            with open(music_name, 'wb') as fp:
                fp.write(music_response)
                logger.info(title=music_name, info="保存成功！")
                break
        except Exception:
            traceback.print_exc(file=open("error.txt", "a+"))
            while True:
                music_name = f"Songs_nodeapi/不和谐的文件名(请手动重命名)_{randint(100000, 999999)}.mp3"
                if not os.path.exists(music_name):
                    break
            continue


def getNeteasePlaylistM1(playlist_id):
    global music_type
    playlist_url = "http://localhost:3000/playlist/track/all?id=" + playlist_id
    pl_data = json.loads(requests.get(playlist_url).text)
    pl_data_songs = pl_data["songs"]

    pl_songs_data = []
    for _song in pl_data_songs:
        _song_struct = SongStruct_Playlist()
        _song_struct.song_name = _song["name"]
        _song_struct.singer = _song["ar"]
        _song_struct.al_name = _song["al"]["name"]
        pl_songs_data.append(_song_struct)

    _music = Music()
    search_res = {}

    index = 0
    for _song in pl_songs_data:
        clear()
        print("============================\n正在爬取歌单中的所有歌曲信息, 请稍等...")
        print(f"进度: {index} / {len(pl_songs_data)}\n============================\n\n")
        refresh_ua()
        for x in range(30):
            try:
                logger.info(title="Getting", info=f"{_song.song_name} - {_song.singer[0]['name']}")
                search_res[index] = _music.search(f"{_song.song_name} {_song.singer[0]['name']}", cookies)
                var = search_res.get(index)[0]["data"]
                logger.info(title="Done", info=f"{_song.song_name} - {_song.singer[0]['name']}")
                index += 1
                music_type = "wy"
                break
            except Exception:
                traceback.print_exc(file=open("error.txt", "a+"))
                logger.error(f"无法获取歌曲data对象，正在切换检索源并重试...  x={x}/30")
                if music_type == "wy":
                    music_type = "qq"
                else:
                    music_type = "wy"
                time.sleep(0.5)
                continue

    logger.debug(search_res)

    song_data = []
    for i in range(len(pl_songs_data)):
        state = False
        song_pl = pl_songs_data[i]
        song_search = search_res.get(i)
        for _song in song_search[0]["data"]:
            _song_name = _song["songname"]
            singer = _song["singer"]
            albumname = _song["albumname"]
            _song_struct = SongStruct()
            _song_struct.song_name = _song["songname"]
            _song_struct.singer = _song["singer"]
            _song_struct.albumname = _song["albumname"]
            _song_struct.album_img = _song["album_img"]
            _song_struct.song_id = _song["songid"]
            _song_struct.size128 = _song["size128"]
            _song_struct.size320 = _song["size320"]
            _song_struct.size_flac = _song["sizeflac"]
            _song_struct.music_type = song_search[1]
            if _song_name == song_pl.song_name and singer == song_pl.singer[0]['name'] and albumname == song_pl.al_name:
                song_data.append(_song_struct)
                state = True
                break

        if not state:
            _song = song_search[0]["data"][0]
            _song_struct = SongStruct()
            _song_struct.song_name = _song["songname"]
            _song_struct.singer = _song["singer"]
            _song_struct.albumname = _song["albumname"]
            _song_struct.album_img = _song["album_img"]
            _song_struct.song_id = _song["songid"]
            _song_struct.size128 = _song["size128"]
            _song_struct.size320 = _song["size320"]
            _song_struct.size_flac = _song["sizeflac"]
            _song_struct.music_type = song_search[1]
            logger.error(
                f"无法通过当前信息命中目标歌曲，已将《{_song_struct.song_name}》命中结果设为默认（搜索排行第一名）。")
            song_data.append(_song_struct)

    makedirs("Songs")
    for _song in song_data:
        logger.info(title="GetLink", info=_song.song_name)
        for x in range(30):
            try:
                logger.debug("song.music_type=" + _song.music_type)
                download_url = _music.get_song_url(_song.song_id, cookies, _song.music_type)["url"]
                logger.debug(download_url)
                download_url.find("test")
                logger.info(title="Downloading", info=_song.song_name)
                match_music_type(download_url, _song)
                break
            except Exception:
                logger.error(f"获取歌曲链接失败，正在重试... x={x}/30")
                continue

    logger.info(title="Done", info="歌单歌曲下载完成!")


def getNeteasePlaylistM2(playlist_id):
    t = get_timerstamp()
    musicIdsList = []
    musicList = json.loads(
        requests.get(NODE_API + "/playlist/track/all?id=" + str(playlist_id), headers=headers, cookies=cookies_wy).text)
    for _id in musicList["privileges"]:
        logger.info(f"获取到音乐: {_id['id']}")
        musicIdsList.append(_id["id"])

    tlist = []
    for _id in musicIdsList:
        surl = requests.get(
            NODE_API + "/song/url/v1?id=" + str(_id) + "&level=hires" + "&timestamp=" + t,
            headers=headers, cookies=cookies_wy).text
        surl = json.loads(surl)
        surl = surl["data"][0]
        surl = surl["url"]

        name = requests.get(NODE_API + "/song/detail?ids=" + str(_id) + "&timestamp=" + t,
                            headers=headers, cookies=cookies_wy).text
        name = json.loads(name)
        name = name["songs"][0]
        musicname = name["name"]
        singername = name["ar"]
        singername = singername[0]["name"]
        if surl is None:
            logger.error(f"亲爱的，{musicname} 暂无版权。已跳过")
        else:
            t1 = Thread(target=save_music, args=(surl, musicname, singername))
            t1.start()
            tlist.append(t1)

    for t in tlist:
        t.join()


def getQQMusicPlaylistM1(playlist_id):
    global music_type
    _playlist = NODE_API_QQ + "/songlist?id=" + playlist_id
    _playlist = json.loads(requests.get(_playlist).text)

    pl_songs_data = []
    for _song in _playlist["data"]["songlist"]:
        _song_struct = SongStruct_Playlist()
        _song_struct.song_name = _song["songorig"]
        _song_struct.singer = _song["singer"]
        _song_struct.al_name = _song["songname"]
        pl_songs_data.append(_song_struct)

    search_res = {}

    index = 0
    for _song in pl_songs_data:
        clear()
        print("============================\n正在爬取歌单中的所有歌曲信息, 请稍等...")
        print(f"进度: {index} / {len(pl_songs_data)}\n============================\n\n")
        refresh_ua()
        for x in range(30):
            try:
                logger.info(title="Getting", info=f"{_song.al_name} - {_song.singer[0]['name']}")
                search_res[index] = music.search(f"{_song.al_name} {_song.singer[0]['name']}", cookies)
                var = search_res.get(index)[0]["data"]
                logger.info(title="Done", info=f"{_song.song_name} - {_song.singer[0]['name']}")
                index += 1
                music_type = "wy"
                break
            except Exception:
                traceback.print_exc(file=open("error.txt", "a+"))
                logger.error(f"无法获取歌曲data对象，正在切换检索源并重试...  x={x}/30")
                if music_type == "wy":
                    music_type = "qq"
                else:
                    music_type = "wy"
                time.sleep(0.5)
                continue

    logger.debug(search_res)

    song_data = []
    for i in range(len(pl_songs_data)):
        state = False
        song_pl = pl_songs_data[i]
        song_search = search_res.get(i)
        for _song in song_search[0]["data"]:
            _song_name = _song["songname"]
            singer = _song["singer"]
            albumname = _song["albumname"]
            _song_struct = SongStruct()
            _song_struct.song_name = _song["songname"]
            _song_struct.singer = _song["singer"]
            _song_struct.albumname = _song["albumname"]
            _song_struct.album_img = _song["album_img"]
            _song_struct.song_id = _song["songid"]
            _song_struct.size128 = _song["size128"]
            _song_struct.size320 = _song["size320"]
            _song_struct.size_flac = _song["sizeflac"]
            _song_struct.music_type = song_search[1]
            if _song_name == song_pl.song_name and singer == song_pl.singer[0]['name'] and albumname == song_pl.al_name:
                song_data.append(_song_struct)
                state = True
                break

        if not state:
            _song = song_search[0]["data"][0]
            _song_struct = SongStruct()
            _song_struct.song_name = _song["songname"]
            _song_struct.singer = _song["singer"]
            _song_struct.albumname = _song["albumname"]
            _song_struct.album_img = _song["album_img"]
            _song_struct.song_id = _song["songid"]
            _song_struct.size128 = _song["size128"]
            _song_struct.size320 = _song["size320"]
            _song_struct.size_flac = _song["sizeflac"]
            _song_struct.music_type = song_search[1]
            logger.error(
                f"无法通过当前信息命中目标歌曲，已将《{_song_struct.song_name}》命中结果设为默认（搜索排行第一名）。")
            song_data.append(_song_struct)

    makedirs("Songs")
    for _song in song_data:
        logger.info(title="GetLink", info=_song.song_name)
        for x in range(30):
            try:
                logger.debug("song.music_type=" + _song.music_type)
                download_url = music.get_song_url(_song.song_id, cookies, _song.music_type)["url"]
                logger.debug(download_url)
                download_url.find("test")
                logger.info(title="Downloading", info=_song.song_name)
                match_music_type(download_url, _song)
                break
            except Exception:
                logger.error(f"获取歌曲链接失败，正在重试... x={x}/30")
                continue

    logger.info(title="Done", info="歌单歌曲下载完成!")


def getQQMusicPlaylistM2(playlist_id):
    musicIdsList = []
    musicList = json.loads(
        requests.get(NODE_API_QQ + "/songlist?id=" + playlist_id, headers=headers).text)
    for _id in musicList["data"]["songlist"]:
        logger.info(f"获取到音乐: {_id['songmid']}")
        musicIdsList.append(_id["songmid"])

    tlist = []
    for _id in musicIdsList:
        surl = requests.get(
            NODE_API_QQ + "/song/url?id=" + _id,
            headers=headers).text
        surl = json.loads(surl)
        surl = surl["data"]
        surl = surl["data"]

        name = requests.get(NODE_API_QQ + "/song?songmid=" + str(_id),
                            headers=headers).text
        name = json.loads(name)
        musicname = name["data"]["track_info"]["name"]
        singername = name["data"]["track_info"]["singer"]
        singername = singername[0]["name"]
        # print("[get!] url =", surl)
        t1 = Thread(target=save_music, args=(surl, musicname, singername))
        t1.start()
        tlist.append(t1)

    for t in tlist:
        t.join()


def decode_base64(base64_data):
    with open('./qrcode.jpg', 'wb') as file:
        img = b64decode(base64_data)
        file.write(img)


def get_timerstamp():
    t = time.time()
    return str(int(round(t * 1000)))


def loginNetease():
    global cookies_wy
    t = get_timerstamp()
    key = json.loads(requests.get(NODE_API + f"/login/qr/key?timerstamp={t}").text)["data"]["unikey"]
    logger.info(title="key", info=key)
    qr_img = json.loads(
        requests.get(f"{NODE_API}/login/qr/create?key={key}&qrimg=true&timerstamp={t}").text)
    qr_img_base64 = qr_img["data"]["qrimg"]
    qr_img_base64 = qr_img_base64.replace("data:image/png;base64,", "")
    qr_img_url = qr_img["data"]["qrurl"]
    decode_base64(qr_img_base64)
    url = pyqrcode.create(qr_img_url)
    text = url.terminal(quiet_zone=1, module_color='red', background='white')
    print(text)

    while True:
        t = get_timerstamp()
        check_url = f"{NODE_API}/login/qr/check?key={key}&timerstamp={t}"
        time.sleep(3)
        check_res = json.loads(requests.get(check_url).text)
        if check_res["code"] == 803:
            cookies_wy = check_res["cookie"]
            with open("cookies_netease.txt", "w") as f:
                f.write(cookies_wy)
            logger.info("授权登陆成功，已成功写入网易云cookies。")
            cookies_wy = convert_cookies_to_dict(cookies_wy)
            break

        if check_res["code"] == 800:
            logger.error("登录失败，二维码已过期... 请重试")
            break


def convert_cookies_to_dict(_cookies):
    cookies_d = {}
    for line in _cookies.split(';'):
        try:
            key, value = line.split('=', 1)
            cookies_d[key] = value
        except Exception:
            pass

    return cookies_d


def output_help_list():
    print("平台切换指令\n"
          "$#wy# - 将搜索源切换成网易云音乐\n"
          "$#qq# - 将搜索源切换成QQ音乐\n\n其他指令\n"
          "$#pld-wy-1# - 使用歌单批量下载，模式1(不稳定，非常容易被ban，但是无需会员就能下载无损)\n"
          "$#pld-wy-2# - 使用歌单批量下载，模式2(稳定，速度快且不容易被ban，需要登录来获取更好的音质)\n"
          "$#pld-qq-1# - 使用歌单批量下载，模式1(不稳定，同上)\n"
          "$#pld-qq-2# - 使用歌单批量下载，模式2(速度快，同时会频繁掉歌)\n"
          "$#login-wy# - 登录网易云账号，pld-wy-2下载歌单时将用自己的cookies\n"
          "$#about# - 查看项目信息\n"
          "$#faq# - 查看常见问题")


if __name__ == '__main__':
    refresh_ua()
    logger = Logger()
    logger.info(title="Starting", info="正在初始化程序，这可能需要一些时间来获取数据。")
    music = Music()
    cookies = {}
    if os.path.exists("cookies_netease.txt"):
        f = open("cookies_netease.txt", "r")
        cookies_wy = convert_cookies_to_dict(f.read())
        f.close()
        logger.info("解析网易云cookies成功，已自动登录。")
    else:
        logger.info("未检测到网易云cookies，歌单解析($#pld-wy-2#)将以受限模式运行。使用'$#login-wy#'来授权。")

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

        print("===============================")
        output_help_list()
        print("===============================\n")
    except Exception as e:
        logger.error(
            "在初始化程序时发生了错误，请检查网络连接。若持续出现此错误，则有可能是对方的API服务器出现了故障或是反爬手段增强了。请关注最新动态")
        logger.error(e)
        traceback.print_exc(file=open("error.txt", "a+"))

    while True:
        song_name = input("请输入要下载的歌曲名称(特殊指令格式为'$#[command]#', $#help#可查看特殊指令)\n> ")
        if song_name == "$#help#":
            output_help_list()
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

        if song_name == "$#pld-wy-1#":
            runNodeApi()
            temp_music_type = music
            try:
                playlist = input("(MODE1) 歌单ID> ")
                getNeteasePlaylistM1(playlist)
            except Exception:
                logger.error("错误的，无法解析的歌单ID。请检查(还有一种可能是node服务没有启动或出现了问题)")
                traceback.print_exc(file=open("error.txt", "a+"))
            music_type = temp_music_type

        if song_name == "$#pld-wy-2#":
            runNodeApi()
            temp_music_type = music
            try:
                playlist = input("(MODE2) 歌单ID> ")
                getNeteasePlaylistM2(playlist)
            except Exception:
                logger.error("错误的，无法解析的歌单ID。请检查")
                traceback.print_exc(file=open("error.txt", "a+"))

            music_type = temp_music_type

        if song_name == "$#pld-qq-1#":
            runNodeApi(type="qq")
            temp_music_type = music
            try:
                playlist = input("(MODE1)(QQ) 歌单ID> ")
                getQQMusicPlaylistM1(playlist)
            except Exception:
                logger.error("错误的，无法解析的歌单ID。请检查")
                traceback.print_exc(file=open("error.txt", "a+"))

            music_type = temp_music_type

        if song_name == "$#pld-qq-2#":
            runNodeApi(type="qq")
            temp_music_type = music
            try:
                playlist = input("(MODE2)(QQ) 歌单ID> ")
                getQQMusicPlaylistM2(playlist)
            except Exception:
                logger.error("错误的，无法解析的歌单ID。请检查")
                traceback.print_exc(file=open("error.txt", "a+"))

            music_type = temp_music_type

        if song_name == "$#login-wy#":
            runNodeApi()
            try:
                loginNetease()
            except Exception:
                logger.error("登录失败，在登录时遇到了错误，请检查网络连接或是API服务是否被关闭。")

        if song_name == "$#faq#":
            print("Q: 为什么下载的音乐有问题/无法搜索音乐/频繁报错/无法下载?\nA: "
                  "本项目使用的是别人的API，可能是对方的API服务器反爬手段增强了或是对本程序做出了一些限制。又或是API服务器目前正出现故障，请关注最新动态或是过个几小时/一天再去使用。")

        try:
            if song_name[0] + song_name[1] == "$#" and song_name[-1] == "#":
                continue
        except Exception:
            continue

        search_result = music.search(song_name, _cookies=cookies)[0]
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
            traceback.print_exc(file=open("error.txt", "a+"))
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
