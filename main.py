"""
MusicHelper by @im-cwuom
GitHub: https://github.com/cwuom/MusicHelper/
"""

from __future__ import annotations

import configparser
import json
import os
import platform
import re
import sys
import time
import traceback
from base64 import b64decode
from msvcrt import getwch, getch
from random import randint, choice
from threading import Thread

import imageio_ffmpeg
import npyscreen
import pwinput
import pynput
import pyqrcode
import requests
import keyboard

from subprocess import call, Popen
import multitasking
import signal

from retry import retry
from tqdm import tqdm
from colorama import Fore, Back, Style
from ctypes import windll
from win32con import SW_SHOWMAXIMIZED, SHOW_FULLSCREEN, SW_MAXIMIZE
from win32gui import ShowWindow

vlc_on = False

if os.path.exists("vlc-3.0.6"):
    os.environ['PYTHON_VLC_MODULE_PATH'] = "./vlc-3.0.6"  # 不要尝试更换顺序 此项需要在import vlc之前
    import vlc

    vlc_on = True
else:
    print(Fore.YELLOW + "Warning: 未检测到vlc-3.0.6，歌曲预览功能将无法使用。")

signal.signal(signal.SIGINT, multitasking.killall)

NODE_API = "http://localhost:3000"
NODE_API_QQ = "http://localhost:3300"
API_URL = "https://music.ghxi.com/wp-admin/admin-ajax.php"
API_URL_2 = "http://music.cwuom.love:36775"
using_api_beta = True
DEBUG_MODE = True

cookies_wy = {}
INDEX = 1
INDEX_MAX = 0
INDEX_MIN = 1
SelectStyle = 0
music_source = "qq"
select_char = "->"
playing_song_name = ""
playing = False
should_wait_enter = True
flag_back = False
scrobble_flag = False
autocheck_cookies = False
download_level_netease = "hires"
download_level_qq = "flac"
disable_keyboard_flag = True
selecting = False
cookies_qq = {}

MB = 1024 ** 2

request_headers = {
    'authority': 'music.ghxi.com',
    'accept': '*/*',
    'accept-language': 'zh-CN,zh;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'origin': 'https://music.ghxi.com',
    'referer': 'https://music.ghxi.com/',
    'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
    'x-requested-with': 'XMLHttpRequest',
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

"""
standard => 标准,higher => 较高, exhigh=>极高, lossless=>无损, hires=>Hi-Res,
 jyeffect => 高清环绕声, sky => 沉浸环绕声, jymaster => 超清母带
"""
level_list = ["standard", "higher", "exhigh", "lossless", "hires", "jyeffect", "sky", "jymaster"]

config = configparser.ConfigParser()


def write_cfg():
    config["API"] = {
        "using_api_beta": True,
        "music_source": "qq",
        "api_url": "http://music.cwuom.love:36775",
        "download_level_netease": "hires",
        "download_level_qq": "flac"
    }

    config['SETTING'] = {
        "Select_Style": "0",
        "select_char": "->",
        "DEBUG": False,
        "check_netease_cookies": False
    }

    config.write(open('config.ini', 'w'))


# ========================== download_helper ==========================
# https://zhuanlan.zhihu.com/p/369531344
@retry(tries=5)
def download(url, file_name):
    file_name = file_name.replace(':', '')
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
        bar = tqdm(total=file_size, desc=f'{file_name}', position=0, ncols=100, unit='B', unit_scale=True)
        with open(file_name, mode='wb') as _f:
            # 写入分块文件
            for chunk in response.iter_content(chunk_size=chunk_size):
                _f.write(chunk)
                bar.update(chunk_size)
        # 关闭进度条
        bar.close()
    except Exception:
        makedirs("Songs")
        while True:
            # file_name = f"Songs/不和谐的文件名(请手动重命名)_{randint(100000, 999999)}.mp3"
            file_name = re.sub(r"|[\\/:*?\"<>|]+", "", file_name.strip())
            if not os.path.exists(file_name):
                break


# =========================================================

def runNodeApi(type="wy"):
    logger.info("正在检查接口是否工作...")

    try:
        API = {"wy": NODE_API, "qq": NODE_API_QQ}
        requests.get(API[type])
    except Exception:
        logger.info("正在启动API服务")
        if type == "wy":
            if os.path.exists("node/app.js"):
                cmd = """
                cd node
                node app.js
                    """
            else:
                logger.error("自动启动API服务失败，找不到`node/app.js`，请手动启动。")
        elif type == "qq":
            if os.path.exists("nodeQQ"):
                cmd = """
                 cd nodeQQ
                 npm start
                     """
            else:
                logger.error("自动启动API服务失败，找不到`nodeQQ`，请手动启动。")

        try:
            with open("start.bat", "w") as w:
                w.write(cmd)
            os.system("start /min start.bat")
            logger.info(title="OK", info="app.js - 服务启动成功")
        except Exception:
            logger.error("app.js - 启动失败")


class Player:
    def __init__(self, *args):
        if args:
            instance = vlc.Instance(*args)
            self.media = instance.media_player_new()
        else:
            self.media = vlc.MediaPlayer()

    # 设置待播放的url地址或本地文件路径，每次调用都会重新加载资源
    def set_uri(self, uri):
        self.media.set_mrl(uri)

    # 播放 成功返回0，失败返回-1
    def play(self, path=None):
        if path:
            self.set_uri(path)
            return self.media.play()
        else:
            return self.media.play()

    # 暂停
    def pause(self):
        self.media.pause()

    # 恢复
    def resume(self):
        self.media.set_pause(0)

    # 停止
    def stop(self):
        self.media.stop()

    # 释放资源
    def release(self):
        return self.media.release()

    # 是否正在播放
    def is_playing(self):
        return self.media.is_playing()

    # 已播放时间，返回毫秒值
    def get_time(self):
        return self.media.get_time()

    # 拖动指定的毫秒值处播放。成功返回0，失败返回-1 (需要注意，只有当前多媒体格式或流媒体协议支持才会生效)
    def set_time(self, ms):
        return self.media.set_time(ms)

    # 音视频总长度，返回毫秒值
    def get_length(self):
        return self.media.get_length()

    # 获取当前音量（0~100）
    def get_volume(self):
        return self.media.audio_get_volume()

    # 设置音量（0~100）
    def set_volume(self, volume):
        return self.media.audio_set_volume(volume)

    # 返回当前状态：正在播放；暂停中；其他
    def get_state(self):
        state = self.media.get_state()
        if state == vlc.State.Playing:
            return 1
        elif state == vlc.State.Paused:
            return 0
        else:
            return -1

    # 当前播放进度情况。返回0.0~1.0之间的浮点数
    def get_position(self):
        return self.media.get_position()

    # 拖动当前进度，传入0.0~1.0之间的浮点数(需要注意，只有当前多媒体格式或流媒体协议支持才会生效)
    def set_position(self, float_val):
        return self.media.set_position(float_val)

    # 获取当前文件播放速率
    def get_rate(self):
        return self.media.get_rate()

    # 设置播放速率（如：1.2，表示加速1.2倍播放）
    def set_rate(self, rate):
        return self.media.set_rate(rate)

    # 设置宽高比率（如"16:9","4:3"）
    def set_ratio(self, ratio):
        self.media.video_set_scale(0)  # 必须设置为0，否则无法修改屏幕宽高
        self.media.video_set_aspect_ratio(ratio)

    # 注册监听器
    def add_callback(self, event_type, callback):
        self.media.event_manager().event_attach(event_type, callback)

    # 移除监听器
    def remove_callback(self, event_type, callback):
        self.media.event_manager().event_detach(event_type, callback)


if vlc_on:
    player = Player()


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
        self.music_source = ""


# 自定日志输出类
class Logger:
    @staticmethod
    def get_time():
        return time.strftime('%H:%M:%S', time.localtime())

    def info(self, info, title="INFO", color=""):
        reset_print()
        print(f"{color}[{self.get_time()}] [{title}] {info}")
        reset_print()

    def error(self, info):
        reset_print()
        print(f"{Fore.RED}[ERROR - {self.get_time()}] {info}")
        reset_print()

    def debug(self, info):
        if DEBUG_MODE:
            reset_print()
            print(f"[DEBUG - {self.get_time()}] {info}")
            reset_print()


logger = Logger()


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
            "music_type": music_source,
            "search_word": search_word
        }
        req = requests.post(API_URL, data=data, headers=request_headers, cookies=_cookies)
        # logger.debug(req.text)
        return [json.loads(req.text), music_source]

    @staticmethod
    def search_c(search_word):
        if music_source == "wy":
            req = requests.get(f"{API_URL_2}/wy/search/{search_word}")
            # logger.debug(req.text)
            return [json.loads(req.text), "wy"]
        elif music_source == "qq":
            return music.search_qq(search_word)
        else:
            return None

    @staticmethod
    def search_qq(search_word):
        if music_source == "qq":
            _headers = {
                'Referer': 'https://y.qq.com',
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.60"
            }
            url = f"https://c.y.qq.com/soso/fcgi-bin/search_for_qq_cp?g_tk=5381&uin=0&format=jsonp&jsonpCallback=callback&inCharset=utf-8&outCharset=utf-8&notice=0&platform=h5&needNewCode=1&w={search_word}&zhidaqu=1&catZhida=1&t=0&flag=1&ie=utf-8&sem=1&aggr=0&perpage=35&n=20&p=1&remoteplace=txt.mqq.all&_=1512564562121"
            req = requests.get(url, headers=_headers)
            return [json.loads(req.text.replace("callback(", "")[:-1]), "qq"]
        else:
            return music.search_c(search_word) if music_source == "wy" else None

    @staticmethod
    def get_song_url(_song_id, _cookies, _music_source=""):
        """
        获取歌曲直链，返回结果不保证百分百正确。
        :param _music_source:
        :param _song_id: 歌曲id
        :param _cookies: 同上
        :return: 歌曲直链
        """
        _music_source = music_source if _music_source == "" else _music_source
        data = {
            "action": "gh_music_ajax",
            "type": "getMusicUrl",
            "music_type": _music_source,
            "music_size": "flac",
            "songid": _song_id
        }

        req = requests.post(API_URL, data=data, headers=request_headers, cookies=_cookies)
        return json.loads(req.text)

    @staticmethod
    def get_song_url_c(_song_id, level=download_level_netease):
        req = requests.get(f"{API_URL_2}/wy/get_song_url/{_song_id}/{level}")
        return json.loads(req.text)["data"][0]

    @staticmethod
    def get_song_url_q(_song_id, level=download_level_qq):
        req = requests.get(f"{API_URL_2}/qq/get_song_url/{_song_id}/{level}")
        try:
            return json.loads(req.text)["data"]
        except Exception:
            logger.error("获取flac格式文件失败，可能是此歌曲没有对应的无损格式。正在获取mp3格式文件...")
            req = requests.get(f"{API_URL_2}/qq/get_song_url/{_song_id}/128")
            return json.loads(req.text)["data"]

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

    @staticmethod
    def get_song_url_netease1(_song_id):
        req = requests.get(NODE_API + "/song/download/url?id=" + _song_id, cookies=cookies_wy).text
        logger.debug(req)
        return json.loads(req)["data"]["url"]

    @staticmethod
    def get_song_url_netease2(_song_id, _level):
        req = requests.get(NODE_API + f"/song/url/v1?id={_song_id}&level={_level}", cookies=cookies_wy).text
        logger.debug(req)
        return json.loads(req)["data"][0]["url"]


def gotoxy(x, y):
    if platform.system() == "Windows":
        call(f"echo \033[{y};{x}H", shell=True)  # Windows终端下设置光标位置
    else:
        print(f"\033[{y};{x}H", end='', flush=True)  # 非Windows终端下设置光标位置


def clear():
    """
    清屏，不兼容pycharm
    """
    system = platform.system()
    if system == u'Windows':
        call("cls", shell=True)
    else:
        os.system('clear')

    gotoxy(0, 0)


def show_result(_index):
    """
    展示歌曲列表
    :param _index: 歌曲索引
    """
    if len(songs_data) == 0:
        logger.error("没有找到任何与该关键字匹配的歌曲... 按下Enter重新检索")
        return None
    index = 0

    for _song in songs_data:
        reset_print()
        index += 1
        if index == _index:
            print(
                f"{Fore.GREEN}{select_char} {Back.CYAN} {Fore.BLACK}{_song.song_name} - {_song.singer} [{_song.albumname}] {Style.RESET_ALL + ' ' * 10}")
        else:
            print(f"{_song.song_name} - {_song.singer} [{_song.albumname}]{Style.RESET_ALL + ' ' * 10}")
    reset_print()

    print(
        f"\n{Fore.LIGHTYELLOW_EX}按下Enter开始下载，空格键试听... 显示不全请全屏终端程序。{Style.RESET_ALL}")


def match_music_url(_song, level=None):
    if not using_api_beta:
        return music.get_song_url(_song.song_id, cookies)["url"]
    else:
        if level is None:
            return music.get_song_url_c(_song.song_id)["url"] if music_source == "wy" else (
                music.get_song_url_q(_song.song_id))
        else:
            return music.get_song_url_c(_song.song_id, level=level)["url"] if music_source == "wy" else (
                music.get_song_url_q(_song.song_id, level=level))


def hook_keys(x):
    """
    监听键盘事件
    :param x: 键盘event，包括按键按下松开之类的
    """

    global playing, player, playing_song_name, should_wait_enter, flag_back
    global INDEX, INDEX_MAX, INDEX_MIN

    if x.event_type == 'down' and x.name == 'left' and playing:
        player.set_time(player.get_time() - 1000)
    if x.event_type == 'down' and x.name == 'right' and playing:
        player.set_time(player.get_time() + 1000)
    if x.event_type == 'down' and x.name == 'up' and not playing:
        gotoxy(0, 0)
        if INDEX > INDEX_MIN:
            INDEX -= 1

        show_result(INDEX)
    if x.event_type == 'down' and x.name == 'down' and not playing:
        gotoxy(0, 0)
        if INDEX < INDEX_MAX:
            INDEX += 1

        show_result(INDEX)
    if x.event_type == 'down' and x.name == 'space' and vlc_on:
        if playing:
            if player.is_playing():
                player.pause()
            else:
                player.resume()
        else:
            _song = songs_data[INDEX - 1]
            logger.info(f"正在解析歌曲下载链接... 请稍等")
            music_url = match_music_url(_song, level="standard") if music_source == "wy" else match_music_url(_song)
            playing = True
            playing_song_name = _song.song_name + " - " + _song.singer
            play(music_url)

    if x.event_type == 'down' and x.name == 'esc':
        if playing:
            playing = False
            playing_song_name = ""
            player.release()
            clear()
            show_result(INDEX)
        else:
            flag_back = True
            should_wait_enter = False

    if x.event_type == 'down' and x.name == 'enter' and not playing:
        flag_back = False
        should_wait_enter = False


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


def disable_keyboard_event():
    while disable_keyboard_flag:
        getwch()


def match_music_source(music_url, _song):
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
    global should_wait_enter, disable_keyboard_flag
    clear()
    show_result(INDEX)

    while True:
        keyboard.hook(hook_keys)
        while should_wait_enter:
            time.sleep(0.1)
        should_wait_enter = True
        keyboard.unhook_all()
        if flag_back:
            break
        if not playing:
            _song = songs_data[INDEX - 1]
            logger.info(f"正在解析歌曲下载链接... 请稍等")
            music_url = match_music_url(_song)
            logger.info(title="Done", info=f"歌曲下载链接解析完成，url={music_url}")
            makedirs("Songs")
            break
        else:
            continue

    if not flag_back:
        match_music_source(music_url, _song)


def SelectStyle1():
    """
    选择风格1，采用序号来选择歌曲，不会清屏。
    """
    global song, INDEX, flag_back
    flag = False
    index = 0
    for song in songs_data:
        index += 1
        print(f"[{index}] {song.song_name} - {song.singer} [{song.albumname}]")

    while True:
        # noinspection PyBroadException
        try:
            INDEX = input("请输入歌曲序号('!b'取消): ")
            if INDEX == "!b":
                flag_back = True
                break
            else:
                INDEX = int(INDEX)
            song = songs_data[INDEX - 1]
            flag = True
            break
        except Exception:
            logger.error(f"你认真的? {INDEX}不是一个有效的序号。")
            traceback.print_exc(file=open("error.txt", "a+"))
            continue

    if flag:
        logger.info(f"正在解析歌曲下载链接... 请稍等")
        music_url = match_music_url(song)
        logger.info(title="Done", info=f"{Fore.GREEN}歌曲下载链接解析完成，url={music_url}")
        makedirs("Songs")
        flag_back = False

        match_music_source(music_url, song)


def refresh_ua():
    global request_headers
    # request_headers["User-Agent"] = choice(user_agent_list)
    headers["User-Agent"] = choice(user_agent_list)


def handle_exception(exc_type, exc_value, exc_traceback):
    log_file = open("UncaughtException.txt", "a+")
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


sys.excepthook = handle_exception


def save_music(url, music_name, singer_name):
    music_name = music_name.replace(':', '')
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
                logger.info(title=music_name, info=f"{Fore.GREEN}保存成功！")
                break
        except Exception:
            traceback.print_exc(file=open("error.txt", "a+"))
            while True:
                # file_name = f"Songs/不和谐的文件名(请手动重命名)_{randint(100000, 999999)}.mp3"
                file_name = re.sub(r"|[\\/:*?\"<>|]+", "", music_name.strip())
                if not os.path.exists(file_name):
                    break
            continue


def get_netease_song_info(_id):
    name = requests.get(NODE_API + "/song/detail?ids=" + str(_id) + "&timestamp=" + get_timerstamp(),
                        cookies=cookies_wy).text
    name = json.loads(name)
    name = name["songs"][0]
    musicname = name["name"]
    singername = name["ar"]
    singername = singername[0]["name"]
    return {"musicname": musicname, "singername": singername}


def get_qq_song_info(_id):
    name = requests.get(NODE_API_QQ + "/song?songmid=" + str(_id),
                        headers=headers, cookies=cookies_qq).text
    name = json.loads(name)
    musicname = name["data"]["track_info"]["name"]
    singername = name["data"]["track_info"]["singer"]
    singername = singername[0]["name"]
    return {"musicname": musicname, "singername": singername}


def getNeteasePlaylistM1(playlist_id):
    global music_source
    playlist_id = search_plid(playlist_id)
    if playlist_id is None:
        logger.error(info="拉取歌单失败，请检查歌单URL是否包含歌单ID。")
        raise ValueError("歌单获取失败")

    playlist_url = f"{NODE_API}/playlist/track/all?id=" + playlist_id + "&timestamp=" + get_timerstamp()
    pl_data = json.loads(requests.get(playlist_url, cookies=cookies_wy).text)
    pl_data_songs = pl_data["songs"]

    pl_songs_data = []
    id_list = []
    for _song in pl_data_songs:
        _song_struct = SongStruct_Playlist()
        _song_struct.song_name = _song["name"]
        _song_struct.singer = _song["ar"]
        _song_struct.al_name = _song["al"]["name"]
        pl_songs_data.append(_song_struct)
        id_list.append(_song["id"])

    if not using_api_beta:
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
                    search_res[index] = music.search(f"{_song.song_name} {_song.singer[0]['name']}", cookies)
                    var = search_res.get(index)[0]["data"]
                    logger.info(title="Done", info=f"{Fore.GREEN}{_song.song_name} - {_song.singer[0]['name']}")
                    index += 1
                    music_source = "wy"
                    break
                except Exception:
                    traceback.print_exc(file=open("error.txt", "a+"))
                    logger.error(f"无法获取歌曲data对象，正在切换检索源并重试...  x={x}/30")
                    music_source = "qq" if music_source == "wy" else "wy"
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
                _song_struct.music_source = song_search[1]
                if (_song_name == song_pl.song_name and singer == song_pl.singer[0]['name']
                        and albumname == song_pl.al_name):
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
                _song_struct.music_source = song_search[1]
                logger.error(
                    f"无法通过当前信息命中目标歌曲，已将《{_song_struct.song_name}》命中结果设为默认（搜索排行第一名）。")
                song_data.append(_song_struct)

        makedirs("Songs")
        for _song in song_data:
            logger.info(title="GetLink", info=_song.song_name)
            for x in range(30):
                try:
                    logger.debug("song.music_source=" + _song.music_source)
                    download_url = match_music_url(_song)
                    logger.debug(download_url)
                    download_url.find("test")
                    logger.info(title="Downloading", info=_song.song_name)
                    match_music_source(download_url, _song)
                    break
                except Exception:
                    logger.error(f"获取歌曲链接失败，正在重试... x={x}/30")
                    continue

        logger.info(title="Done", info=f"{Fore.GREEN}歌单歌曲下载完成!")

    else:
        for _id in id_list:
            data = get_netease_song_info(_id)
            musicname = data["musicname"]
            singername = data["singername"]
            for x in range(3):
                try:
                    download_url = music.get_song_url_c(_id)["url"]
                    _song = SongStruct()
                    _song.song_name = musicname
                    _song.singer_name = singername
                    logger.debug(download_url)
                    download_url.find("test")
                    logger.info(title="Downloading", info=musicname)
                    match_music_source(download_url, _song)
                    break
                except Exception:
                    logger.error(f"获取歌曲链接失败，可能是该歌曲暂无版权。正在重试... x={x}/3")
                    continue


def getNeteasePlaylistM2(playlist_id):
    playlist_id = search_plid(playlist_id)
    if playlist_id is None:
        logger.error(info="拉取歌单失败，请检查歌单URL是否包含歌单ID。")
        raise ValueError("歌单获取失败")

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
        data = get_netease_song_info(_id)
        musicname = data["musicname"]
        singername = data["singername"]

        if surl is None:
            logger.error(f"亲爱的，{musicname} 暂无版权。已跳过")
        else:
            t1 = Thread(target=save_music, args=(surl, musicname, singername))
            t1.start()
            tlist.append(t1)

    for t in tlist:
        t.join()


def getQQMusicPlaylistM1(playlist_id):
    global music_source

    playlist_id = search_plid(playlist_id)
    if playlist_id is None:
        logger.error(info="拉取歌单失败，请检查歌单URL是否包含歌单ID。")
        raise ValueError("歌单获取失败")

    _playlist = NODE_API_QQ + "/songlist?id=" + playlist_id
    _playlist = json.loads(requests.get(_playlist, cookies=cookies_qq).text)

    pl_songs_data = []
    id_list = []
    for _song in _playlist["data"]["songlist"]:
        _song_struct = SongStruct_Playlist()
        _song_struct.song_name = _song["songorig"]
        _song_struct.singer = _song["singer"]
        _song_struct.al_name = _song["songname"]
        pl_songs_data.append(_song_struct)
        id_list.append(_song["songmid"])

    if not using_api_beta:
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
                    logger.info(title="Done", info=f"{Fore.GREEN}{_song.song_name} - {_song.singer[0]['name']}")
                    index += 1
                    music_source = "wy"
                    break
                except Exception:
                    traceback.print_exc(file=open("error.txt", "a+"))
                    logger.error(f"无法获取歌曲data对象，正在切换检索源并重试...  x={x}/30")
                    music_source = "wy" if music_source == "qq" else "wy"
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
                _song_struct.music_source = song_search[1]
                if (_song_name == song_pl.song_name and singer == song_pl.singer[0]['name']
                        and albumname == song_pl.al_name):
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
                _song_struct.music_source = song_search[1]
                logger.error(
                    f"无法通过当前信息命中目标歌曲，已将《{_song_struct.song_name}》命中结果设为默认（搜索排行第一名）。")
                song_data.append(_song_struct)

        makedirs("Songs")
        for _song in song_data:
            logger.info(title="GetLink", info=_song.song_name)
            for x in range(30):
                try:
                    logger.debug("song.music_source=" + _song.music_source)
                    download_url = match_music_url(_song)
                    logger.debug(download_url)
                    download_url.find("test")
                    logger.info(title="Downloading", info=_song.song_name)
                    match_music_source(download_url, _song)
                    break
                except Exception:
                    logger.error(f"获取歌曲链接失败，正在重试... x={x}/30")
                    continue

        logger.info(title="Done", info="歌单歌曲下载完成!")
    else:
        for _id in id_list:
            for x in range(3):
                try:
                    download_url = music.get_song_url_q(_id)
                    data = get_qq_song_info(_id)
                    musicname = data["musicname"]
                    singername = data["singername"]
                    _song = SongStruct()
                    _song.song_name = musicname
                    _song.singer_name = singername
                    logger.debug(download_url)
                    download_url.find("test")
                    logger.info(title="Downloading", info=musicname)
                    match_music_source(download_url, _song)
                    break
                except Exception:
                    logger.error(f"获取歌曲链接失败，可能是该歌曲暂无版权。正在重试... x={x}/3")
                    continue


def getQQMusicPlaylistM2(playlist_id):
    global download_level_qq
    playlist_id = search_plid(playlist_id)
    if playlist_id is None:
        logger.error(info="拉取歌单失败，请检查歌单URL是否包含歌单ID。")
        raise ValueError("歌单获取失败")

    musicIdsList = []
    musicList = json.loads(
        requests.get(NODE_API_QQ + "/songlist?id=" + playlist_id, headers=headers, cookies=cookies_qq).text)
    for _id in musicList["data"]["songlist"]:
        logger.info(f"获取到音乐: {_id['songmid']}")
        musicIdsList.append(_id["songmid"])

    tlist = []
    failed = 0
    temp_download_level_qq = download_level_qq
    if input("您是否有QQ音乐VIP？如果没有则会为您下载mp3格式。否则可能导致所有歌曲下载失败... (回车默认为无，有请输入y)") != "y":
        download_level_qq = "128"
    else:
        if input("这里不是纯粹的指你有没有会员，如果您有会员还需自行设定cookies后才可使用，如果你配置了请直接回车... (没有请输入n)") == "n":
            download_level_qq = "128"

    temp2_download_level_qq = download_level_qq

    for _id in musicIdsList:
        never_try = True
        for x in range(2):
            try:
                surl = requests.get(
                    NODE_API_QQ + "/song/url?id=" + _id + "&type="+download_level_qq,
                    headers=headers, cookies=cookies_qq).text
                surl = json.loads(surl)
                surl = surl["data"]
                data = get_qq_song_info(_id)
                musicname = data["musicname"]
                singername = data["singername"]
                t1 = Thread(target=save_music, args=(surl, musicname, singername))
                t1.start()
                tlist.append(t1)
                download_level_qq = temp2_download_level_qq
                break
            except Exception:
                if never_try:
                    download_level_qq = "128"
                    never_try = False
                    continue
                failed += 1
                logger.error(f"{failed} 首歌曲获取失败。可能是版权或会员的问题，若都无误请重新配置您的qq音乐cookies。正在切换下载质量并重试\n歌曲URL: https://y.qq.com/n/ryqq/songDetail/{_id}")

    for t in tlist:
        t.join()

    download_level_qq = temp_download_level_qq


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
            with open("cookies_netease.txt", "w") as _f:
                _f.write(cookies_wy)
            logger.info(f"{Fore.GREEN}授权登陆成功，已成功写入网易云cookies。")
            cookies_wy = convert_cookies_to_dict(cookies_wy)
            break

        if check_res["code"] == 800:
            logger.error("登录失败，二维码已过期... 请重试")
            break


def show_phone_number(phone):
    string = phone[2:9]
    return phone.replace(string, '*******')


def loginNeteaseByPhone():
    global cookies_wy
    while True:
        phone_number = pwinput.pwinput(prompt='请输入你网易云绑定的手机号(直接输入Enter退出): ', mask='·')
        if phone_number == '':
            break
        if len(phone_number) != 11 and type(phone_number) != int:
            print("Invalid phone number, please try again.")
            continue

        if input(f"(y/*) 将发送验证码到 >{show_phone_number(phone_number)}< 确定吗? ") == "y":
            logger.info(title="Sending", info=f"正在发送验证码到 {show_phone_number(phone_number)}")
            req_send = requests.get(f"{NODE_API}/captcha/sent?phone={phone_number}&timestamp={get_timerstamp()}")
            logger.debug(req_send.text)
            while True:
                _code = input("验证码(`!b`退出)> ")
                if _code == "!b":
                    break
                req_verify = requests.get(
                    f"{NODE_API}/captcha/verify?phone={phone_number}&captcha={_code}&timestamp={get_timerstamp()}").json()
                if req_verify["code"] == 200:
                    logger.info(title="OK", info=f"{Fore.GREEN}验证成功，正在抓取cookies.")
                    break
                else:
                    logger.error("验证码校验失败，可能的原因是输入了不正确的验证码或是验证码过期，请重新输入。")

            req_login = requests.get(
                f"{NODE_API}/login/cellphone?phone={phone_number}&captcha={_code}&timestamp={get_timerstamp()}")
            logger.info(title="Done",
                        info=f"{Fore.GREEN}验证码登录成功，用户昵称: {req_login.json()['profile']['nickname']}")
            cookies_wy = req_login.json()["cookie"]
            logger.debug(cookies_wy)
            with open("cookies_netease.txt", "w") as _f:
                _f.write(cookies_wy)
            cookies_wy = convert_cookies_to_dict(cookies_wy)
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
    # print(Fore.YELLOW, end="")
    print(f"{Fore.MAGENTA}$#wy#{Style.RESET_ALL} - 将搜索源切换成网易云音乐\n"
          f"{Fore.MAGENTA}$#qq#{Style.RESET_ALL} - 将搜索源切换成QQ音乐\n"
          f"{Fore.MAGENTA}$#pld-wy-1#{Style.RESET_ALL} - 网易云歌单批量下载，所有请求经过API服务器(旧API: 不稳定，容易被封ip，但是无需会员就能下载无损，APIβ: 若服务器无故障则持续稳定，不会主动封ip)\n"
          f"{Fore.MAGENTA}$#pld-wy-2#{Style.RESET_ALL} - 网易云歌单批量下载(本地)，所有请求只经过本地，需自行解决会员问题(稳定，速度快且不容易被封，但需要登录来获取无损音频)\n"
          f"{Fore.MAGENTA}$#pld-qq-1#{Style.RESET_ALL} - QQ音乐歌单批量下载，同上(旧API: 不稳定，同上, APIβ: 稳定，同上)\n"
          f"{Fore.MAGENTA}$#pld-qq-2#{Style.RESET_ALL} - QQ音乐歌单批量下载(本地)，同上(速度快，同时会频繁掉歌)\n"
          f"{Fore.MAGENTA}$#login-wy#{Style.RESET_ALL} - 登录网易云账号，pld-wy-2下载歌单时将用自己的cookies\n"
          f"{Fore.MAGENTA}$#login-wy-p#{Style.RESET_ALL} - 通过验证码登录到网易云账号，pld-wy-2下载歌单时将用自己的cookies\n"
          f"{Fore.MAGENTA}$#check-wy#{Style.RESET_ALL} - 验证网易云登录cookies的有效性\n"
          f"{Fore.MAGENTA}$#flac2mp3#{Style.RESET_ALL} - 自动转换Songs/Songs_nodeapi里的音乐为mp3\n"
          f"{Fore.MAGENTA}$#scr-wy#{Style.RESET_ALL} - 自动刷单曲听歌量，需要先登录($#login-wy#)，如果没有生效很有可能是cookies掉了，重新登录就行了\n"
          f"{Fore.MAGENTA}$#lrc-wy#{Style.RESET_ALL} - 爬取网易云单曲歌词(包含原版歌词和中文翻译)\n"
          f"{Fore.MAGENTA}$#about#{Style.RESET_ALL} - 查看项目信息\n"
          f"{Fore.MAGENTA}$#faq#{Style.RESET_ALL} - 查看常见问题")

    reset_print()


def player_call_back(event):
    global player
    gotoxy(0, 0)
    print("正在试听所选歌曲，按下esc退出播放...")
    i = int(round(player.get_position(), 2) * 100)
    a = "#" * i
    b = "." * (100 - i)
    c = (i / 100) * 100
    print("\r[{}] {:^3.0f}%[{}{}]".format(Fore.CYAN + playing_song_name + Style.RESET_ALL, c,
                                          Fore.GREEN + a + Style.RESET_ALL, Fore.RED + b + Style.RESET_ALL), end="")
    # print("".center(50 // 2, "-"))


def play(url):
    global player
    clear()
    player = Player()
    player.add_callback(vlc.EventType.MediaPlayerTimeChanged, player_call_back)
    player.play(url)


def get_playlist_id_netease(url):
    try:
        pl_id = re.search(r'.*/playlist\?id=(\d+)', url)
        return pl_id.group(1).replace('id=', '')
    except Exception:
        return None


def get_playlist_id_qq(url):
    try:
        pl_id = re.search(r'.*playlist/(\d+)', url)
        return pl_id.group(1).replace('id=', '')
    except Exception:
        return None


def search_plid(url):
    try:
        int(url)
        return url
    except Exception:
        if "music.163.com" in url:
            return get_playlist_id_netease(url)
        elif "y.qq.com" in url:
            return get_playlist_id_qq(url)
        else:
            return None


def get_music_id_netease(url):
    # https://music.163.com/#/song?id=1
    try:
        pl_id = re.search(r'.*/song\?id=(\d+)', url)
        return pl_id.group(1).replace('id=', '')
    except Exception:
        return None


def search_mid(string):
    if "music.163.com" in string:
        return get_music_id_netease(string)
    elif "y.qq.com" in string:
        return 404
    else:
        return string


def get_songs_netease_m1(_song_id):
    level = input("音质选择: (1) 标准 (2) 较高 (3) 极高 "
                  "(4) 无损 (5) Hi-Res (6) 高清环绕声 "
                  "(7) 沉浸环绕声 (8) 超清母带\n(默认5 - Hi-Res) 请输入序号> ")

    try:
        level = level_list[int(level) - 1]
    except Exception:
        logger.info("将使用默认音质进行解析。")
        level = level_list[4]

    url = music.get_song_url_netease2(_song_id, level)

    data = get_netease_song_info(_song_id)
    musicname = data["musicname"]
    singername = data["singername"]

    logger.info(title="Downloading", info="正在下载 {} - {}".format(musicname, singername))
    save_music(url, musicname, singername)


def get_songs_netease_m2(_song_id):
    url = music.get_song_url_netease1(_song_id)
    data = get_netease_song_info(_song_id)
    musicname = data["musicname"]
    singername = data["singername"]

    logger.info(title="Downloading", info="正在下载 {} - {}".format(musicname, singername))
    save_music(url, musicname, singername)


def wait_esc_scrobble():
    global scrobble_flag
    keyboard.wait("esc")
    scrobble_flag = True


def scrobble_netease(_song_id):
    global scrobble_flag

    data = get_netease_song_info(_song_id)
    song_detail = requests.get(NODE_API + f"/song/detail?ids={_song_id}", cookies=cookies_wy, headers=headers)
    dt = json.loads(song_detail.text)
    dt = dt["songs"]
    dt = dt[0]["dt"]
    dt = str(dt)[0:3]
    logger.info(f"歌曲时间(s)->{dt}")
    musicname = data["musicname"]
    singername = data["singername"]

    print("歌曲名称:", musicname)
    print("歌手:", singername)
    input("若无误，按下回车开始刷歌曲播放... 按下esc随时停止。")

    num = 0
    Thread(target=wait_esc_scrobble, args=()).start()
    while not scrobble_flag:
        num += 1
        req = requests.get(f"{NODE_API}/scrobble?id={_song_id}&time={dt}&timestamp={get_timerstamp()}",
                           cookies=cookies_wy).text
        logger.info(title=f"requests{num}", info=req)

    scrobble_flag = False


def get_lyric_netease(_song_id):
    makedirs("lyric")
    req_lrc = requests.get(f"{NODE_API}/lyric?id={_song_id}")

    data = get_netease_song_info(_song_id)
    musicname = data["musicname"]
    singername = data["singername"]
    lyric = req_lrc.json()["lrc"]["lyric"]
    lyric_zh = req_lrc.json()["tlyric"]["lyric"]
    with open(f"lyric/{musicname}-{singername}_lrc.txt", "w", encoding='utf-8') as _f:
        _f.write(lyric)
        _f.close()
    with open(f"lyric/{musicname}-{singername}_zh.txt", "w", encoding='utf-8') as _f:
        _f.write(lyric_zh)
        _f.close()

    logger.info(title="Done", info=f"歌词已保存至lyric文件夹")


def check_netease_cookies():
    runNodeApi()
    check_req = requests.get(f"{NODE_API}/daily_signin", cookies=cookies_wy)
    if check_req.json()["code"] == 200:
        logger.info(title="Success", info=F"{Fore.GREEN}网易云cookies验证成功！")
    else:
        logger.info(title="Warning", info="您的网易云cookies已过期，请尝试重新登录以获取最新cookies。",
                    color=Fore.YELLOW)


def reset_print():
    print(Style.RESET_ALL, end="")


def read_cfg():
    global using_api_beta, download_level_netease, download_level_qq, API_URL_2, music_source, DEBUG_MODE, SelectStyle, select_char, autocheck_cookies, config
    if not os.path.exists("config.ini"):
        write_cfg()
        logger.info(f"{Fore.YELLOW}配置文件不存在，已自动创建。")
    try:
        config.read("config.ini")
        using_api_beta = config.getboolean("API", "using_api_beta")
        API_URL_2 = config["API"]["api_url"]
        music_source = config["API"]["music_source"]
        download_level_netease = config["API"]["download_level_netease"]
        download_level_qq = config["API"]["download_level_qq"]
        # DEBUG_MODE = config["SETTING"]["debug"]
        DEBUG_MODE = config.getboolean("SETTING", "debug")
        SelectStyle = int(config["SETTING"]["select_style"])
        select_char = config["SETTING"]["select_char"]
        # autocheck_cookies = bool(config["SETTING"]["check_netease_cookies"])
        autocheck_cookies = config.getboolean("SETTING", "check_netease_cookies")
    except Exception:
        logger.error("配置文件读取错误，已自动重置配置文件。")
        write_cfg()
        read_cfg()


def findAllFile(_base):
    for root, ds, fs in os.walk(_base):
        for _f in fs:
            yield _f


def flac2mp3(_base):
    makedirs("convert_mp3")
    for file_name in findAllFile(_base):
        compress = """{} -i "{}/{}" "convert_mp3/{}.mp3" -y""".format(imageio_ffmpeg.get_ffmpeg_exe(), _base, file_name,
                                                                      file_name.split('.')[0])
        Popen(compress, shell=True)

    logger.info(f"{Fore.GREEN}已将{_base}目录下的音乐文件转换为mp3格式。")


def analyse_song_data(_search_result):
    _n = 0
    for _song in _search_result["data"]:
        if _n >= 35:
            break
        _song_struct = SongStruct()
        _song_struct.song_name = _song["songname"]
        _song_struct.singer = _song["singer"]
        _song_struct.albumname = _song["albumname"]
        _song_struct.album_img = _song["album_img"]
        _song_struct.song_id = _song["songid"]
        _song_struct.size128 = _song["size128"]
        _song_struct.size320 = _song["size320"]
        _song_struct.size_flac = _song["sizeflac"]
        _n += 1
        yield _song_struct


def load_qq_song_struct(_song):
    _song_struct = SongStruct()
    _song_struct.song_name = _song["songname"]
    _song_struct.singer = _song["singer"][0]["name"]
    _song_struct.albumname = _song["albumname"]
    _song_struct.album_img = None
    _song_struct.song_id = _song["songmid"]
    _song_struct.size128 = None
    _song_struct.size320 = None
    _song_struct.size_flac = None
    return _song_struct


def load_wy_song_struct(_song):
    _song_struct = SongStruct()
    _song_struct.song_name = _song["name"]
    _song_struct.singer = _song["artists"][0]["name"]
    _song_struct.albumname = _song["album"]["name"]
    _song_struct.album_img = _song["album"]["artist"]["img1v1Url"]
    _song_struct.song_id = _song["id"]
    _song_struct.size128 = None
    _song_struct.size320 = None
    _song_struct.size_flac = None
    return _song_struct


def analyse_song_data_c(_search_result):
    _n = 0
    if music_source == "qq":
        for _song in search_result["data"]["song"]["list"]:
            if _n >= 35:
                break
            _n += 1
            yield load_qq_song_struct(_song)
    else:
        for _song in search_result["result"]["songs"]:
            if _n >= 35:
                break
            _n += 1
            yield load_wy_song_struct(_song)


def output_logo():
    print(Fore.LIGHTCYAN_EX + f"""
------------------------------------------------------------------------------------------------------------

 /$$      /$$                     /$$           /$$   /$$           /$$                              
| $$$    /$$$                    |__/          | $$  | $$          | $$                              
| $$$$  /$$$$ /$$   /$$  /$$$$$$$ /$$  /$$$$$$$| $$  | $$  /$$$$$$ | $$  /$$$$$$   /$$$$$$   /$$$$$$ 
| $$ $$/$$ $$| $$  | $$ /$$_____/| $$ /$$_____/| $$$$$$$$ /$$__  $$| $$ /$$__  $$ /$$__  $$ /$$__  $$
| $$  $$$| $$| $$  | $$|  $$$$$$ | $$| $$      | $$__  $$| $$$$$$$$| $$| $$  \ $$| $$$$$$$$| $$  \__/
| $$\  $ | $$| $$  | $$ \____  $$| $$| $$      | $$  | $$| $$_____/| $$| $$  | $$| $$_____/| $$      
| $$ \/  | $$|  $$$$$$/ /$$$$$$$/| $$|  $$$$$$$| $$  | $$|  $$$$$$$| $$| $$$$$$$/|  $$$$$$$| $$      
|__/     |__/ \______/ |_______/ |__/ \_______/|__/  |__/ \_______/|__/| $$____/  \_______/|__/      
                                                                       | $$                          
                                                                       | $$                    {Fore.BLUE}@im-cwuom   {Fore.LIGHTCYAN_EX}   
                                                                       |__/                    
------------------------------------------------------------------------------------------------------------""" + Style.RESET_ALL)


def show_full_windows():
    user32 = windll.user32
    user32.SetProcessDPIAware()

    hWnd = user32.GetForegroundWindow()
    ShowWindow(hWnd, SW_MAXIMIZE)
    ShowWindow(hWnd, SHOW_FULLSCREEN)
    ShowWindow(hWnd, SW_SHOWMAXIMIZED)


# ---------------------------Menu---------------------------
class MultiLine(npyscreen.MultiLine):
    def __init__(self, screen, values=None, value=None,
                 slow_scroll=False, scroll_exit=False,
                 return_exit=False, select_exit=False,
                 exit_right=False,
                 widgets_inherit_color=False,
                 always_show_cursor=False,
                 allow_filtering=True,
                 **keywords):
        super().__init__(screen, values, value, slow_scroll, scroll_exit,
                         return_exit, select_exit, exit_right, widgets_inherit_color, always_show_cursor,
                         allow_filtering, **keywords)
        self.cursor_line_temp = None

    def h_cursor_line_up(self, ch):
        super().h_cursor_line_up(ch)
        self.h_select(ch)

    def h_cursor_line_down(self, ch):
        super().h_cursor_line_down(ch)
        self.h_select(ch)

    def handle_mouse_event(self, mouse_event):
        ctr = pynput.mouse.Controller()
        ctr.release(pynput.mouse.Button.left)
        ctr.release(pynput.mouse.Button.right)
        mouse_id, rel_x, rel_y, z, bstate = self.interpret_mouse_event(mouse_event)
        self.cursor_line = rel_y // self._contained_widget_height + self.start_display_at
        if self.cursor_line < 0:
            if self.scroll_exit:
                self.cursor_line = 0
                self.h_exit_up(None)
            else:
                self.cursor_line = 0

        self.h_select(None)
        # if self.cursor_line == self.cursor_line_temp:
        #     time.sleep(0.3)
        #     keyboard.write("f")
        # else:
        #     self.cursor_line_temp = self.cursor_line
        self.display()


class SelectOne(npyscreen.SelectOne):
    def h_cursor_line_up(self, ch):
        super().h_cursor_line_up(ch)
        self.h_select(ch)

    def h_cursor_line_down(self, ch):
        super().h_cursor_line_down(ch)
        self.h_select(ch)


class ActionForm(npyscreen.ActionForm):
    def use_mouse_event(self, mouse_event):
        ctr = pynput.mouse.Controller()
        ctr.release(pynput.mouse.Button.left)
        ctr.release(pynput.mouse.Button.right)
        wg = self.find_mouse_handler(mouse_event)
        if wg:
            self.set_editing(wg)
            if hasattr(wg, 'handle_mouse_event'):
                wg.handle_mouse_event(mouse_event)
            keyboard.press_and_release("Space")
            keyboard.press_and_release("Enter")


class ConfigForm(ActionForm):
    def __init__(self, name=None, parentApp=None, framed=None, _help=None, color='FORMDEFAULT',
                 widget_list=None, cycle_widgets=False, *args, **keywords):
        super().__init__(name, parentApp, framed, _help, color, widget_list, cycle_widgets, args, keywords)

        self.config_list = None
        config.read("config.ini")
        self.music_type_index = 0
        self.select_style_index = 0
        self.download_level_qq_index = 0
        self.download_level_netease_index = 0
        self.download_level_netease_index = 0
        self.api_url_index = 0
        self.music_type_index = 0
        self.select_char_index = 0
        # API
        self.using_api_beta = config["API"]["using_api_beta"]
        self.music_type = config["API"]["music_source"]
        self.music_type_select_list = ["qq", "wy"]
        self.music_type_length = len(self.music_type_select_list)
        self.api_url = config["API"]["api_url"]
        self.api_url_select_list = ["http://music.cwuom.love:36775",
                                    "http://musicv2.cwuom.love:41464", "http://musicv3.cwuom.love:44757"]
        self.api_url_length = len(self.api_url_select_list)
        self.download_level_netease = config["API"]["download_level_netease"]
        self.download_level_netease_select_list = ["standard", "higher", "exhigh",
                                                   "lossless", "hires",
                                                   "jyeffect", "sky", "jymaster"]
        self.download_level_netease_length = len(self.download_level_netease_select_list)
        self.download_level_qq = config["API"]["download_level_qq"]
        self.download_level_qq_select_list = ["128", "320", "m4a", "flac", "ape"]
        self.download_level_qq_length = len(self.download_level_qq_select_list)
        # SETTING
        self.select_style = config["SETTING"]["select_style"]
        self.select_style_select_list = ["0", "1"]
        self.select_style_length = len(self.select_style_select_list)
        self.select_char = config["SETTING"]["select_char"]
        self.select_char_select_list = ["->", ">"]
        self.select_char_length = len(self.select_char_select_list)
        self.debug = config.getboolean("SETTING", "debug")
        self.check_netease_cookies = config.getboolean("SETTING", "check_netease_cookies")
        self.config_val = [f"using_api_beta = {self.using_api_beta}", f"music_source = {self.music_type}",
                           f"api_url = {self.api_url}", f"download_level_netease = {self.download_level_netease}",
                           f"download_level_qq = {self.download_level_qq}", f"select_style = {self.select_style}",
                           f"select_char = {self.select_char}", f"debug = {self.debug}",
                           f"check_netease_cookies = {self.check_netease_cookies}"]
        self.config_list = self.add(SelectOne, max_height=15, value=[0, ], name="Config List",
                                    values=self.config_val, scroll_exit=True)

        self.add(npyscreen.TitleFixedText,
                 name=f"You can press 'up' or 'down' to select config you want.",
                 editable=False)
        self.add(npyscreen.TitleFixedText, name=f"Press 'q' or 'e' to change the config, press 'r' to reset all.",
                 editable=False)
        self.add(npyscreen.TitleFixedText,
                 name=f"To apply all setting, please click the 'OK' button. Otherwise press the 'Cancel' button",
                 editable=False)

    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers.update({
            ord("q"): self.on_q,
            ord("e"): self.on_e,
            ord("r"): self.reset_config,
        })

    def create(self):
        self.name = "Edit config.ini"

    def change_config(self, add=False):
        val = self.config_list.value[0]
        if val == 0:
            self.using_api_beta = not self.using_api_beta
            self.config_val[val] = f"using_api_beta = {self.using_api_beta}"
            self.config_list.values = self.config_val
        if val == 1:
            self.music_type_index = self.music_type_index - 1 if not add else self.music_type_index + 1
            self.music_type = self.music_type_select_list[self.music_type_index % self.music_type_length]
            self.config_val[
                val] = f"music_source = {self.music_type}"
            self.config_list.values = self.config_val
        if val == 2:
            self.api_url_index = self.api_url_index - 1 if not add else self.api_url_index + 1
            self.api_url = self.api_url_select_list[self.api_url_index % self.api_url_length]
            self.config_val[val] = f"api_url = {self.api_url}"
            self.config_list.values = self.config_val
        if val == 3:
            self.download_level_netease_index = self.download_level_netease_index - 1 if not add else self.download_level_netease_index + 1
            self.download_level_netease = self.download_level_netease_select_list[
                self.download_level_netease_index % self.download_level_netease_length]
            self.config_val[val] = (f"download_level_netease = "
                                    f"{self.download_level_netease}")
            self.config_list.values = self.config_val
        if val == 4:
            self.download_level_qq_index = self.download_level_qq_index - 1 if not add else self.download_level_qq_index + 1
            self.download_level_qq = self.download_level_qq_select_list[
                self.download_level_qq_index % self.download_level_qq_length]
            self.config_val[val] = (f"download_level_qq = "
                                    f"{self.download_level_qq}")
            self.config_list.values = self.config_val
        if val == 5:
            self.select_style_index = self.select_style_index - 1 if not add else self.select_style_index + 1
            self.select_style = self.select_style_select_list[self.select_style_index % self.select_style_length]
            self.config_val[
                val] = f"select_style = {self.select_style}"
            self.config_list.values = self.config_val
        if val == 6:
            self.select_char_index = self.select_char_index - 1 if not add else self.select_char_index + 1
            self.select_char = self.select_char_select_list[self.select_char_index % self.select_char_length]
            self.config_val[
                val] = f"select_char = {self.select_char}"
            self.config_list.values = self.config_val
        if val == 7:
            self.debug = not self.debug
            self.config_val[val] = f"debug = {self.debug}"
            self.config_list.values = self.config_val
        if val == 8:
            self.check_netease_cookies = not self.check_netease_cookies
            self.config_val[val] = f"check_netease_cookies = {self.check_netease_cookies}"
            self.config_list.values = self.config_val

    def reset_config(self, *args, **keywords):
        self.config_val = ['using_api_beta = True', 'music_source = qq', 'api_url = http://music.cwuom.love:36775',
                           'download_level_netease = hires', 'download_level_qq = flac',
                           'select_style = 0', 'select_char = ->',
                           'debug = False', 'check_netease_cookies = False']

        self.using_api_beta = True
        self.music_type = "qq"
        self.api_url = "http://music.cwuom.love:36775"
        self.download_level_netease = "hires"
        self.download_level_qq = "flac"
        self.select_style = "0"
        self.select_char = "->"
        self.debug = False
        self.check_netease_cookies = False
        self.config_list.values = self.config_val

        self.music_type_index = 0
        self.select_style_index = 0
        self.download_level_qq_index = 0
        self.download_level_netease_index = 0
        self.download_level_netease_index = 0
        self.api_url_index = 0
        self.music_type_index = 0
        self.select_char_index = 0

    def on_q(self, *args, **keywords):
        self.change_config()

    def on_e(self, *args, **keywords):
        self.change_config(add=True)

    def on_ok(self, *args, **keywords):
        config["API"] = {
            "using_api_beta": self.using_api_beta,
            "music_source": self.music_type,
            "api_url": self.api_url,
            "download_level_netease": self.download_level_netease,
            "download_level_qq": self.download_level_qq
        }

        config['SETTING'] = {
            "Select_Style": self.select_style,
            "select_char": self.select_char,
            "DEBUG": self.debug,
            "check_netease_cookies": self.check_netease_cookies
        }

        os.remove('config.ini')
        config_file = open('config.ini', 'w')
        config.write(config_file)
        config_file.close()
        logger.info("配置文件设置成功，重启程序后应用。")
        self.parentApp.switchForm("MAIN")

    def on_cancel(self, *args, **keywords):
        self.parentApp.switchForm("MAIN")


class MenuForm(ActionForm):
    def __init__(self, name=None, parentApp=None, framed=None, help=None, color='FORMDEFAULT',
                 widget_list=None, cycle_widgets=False, *args, **keywords):
        super().__init__(name, parentApp, framed, help, color, widget_list, cycle_widgets, args, keywords)
        menu_list = ["1. Switch the search source to NetEase music",
                     "2. Switch the search source to QQ music",
                     "3. NetEase playlist batch download [server]",
                     "4. NetEase playlist batch download [local]",
                     "5. QQ music playlist batch download [server]",
                     "6. QQ music playlist batch download [local]",
                     "7. Login NetEase account [qrcode]",
                     "8. Login NetEase account [verification-code]",
                     "9. Verify NetEase cookies",
                     "a. MP3s Converter",
                     "b. Scrobble [netease][need-login]",
                     "c. Netease lyrics downloader",
                     "d. Reset config.ini",
                     "e. Edit config.ini", ]
        self.command = self.add(MultiLine, max_height=15, value=[0, ], name="Command List",
                                values=menu_list, scroll_exit=True)

        self.add(npyscreen.TitleFixedText,
                 name=f"You can press 'up' or 'down' to select command you want.",
                 editable=False)
        self.add(npyscreen.TitleFixedText, name=f"Press 'q' to quit, 'f' to confirm it.",
                 editable=False)

    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers.update({
            ord("q"): self.on_cancel,
            ord("f"): self.on_ok,
            # ----------------------
            ord("1"): self.on_a,
            ord("2"): self.on_b,
            ord("3"): self.on_c,
            ord("4"): self.on_d,
            ord("5"): self.on_e,
            ord("6"): self.on_f,
            ord("7"): self.on_g,
            ord("8"): self.on_h,
            ord("9"): self.on_i,
            ord("a"): self.on_j,
            ord("b"): self.on_k,
            ord("c"): self.on_l,
            ord("d"): self.on_m,
            ord("e"): self.on_n,
            # ---------------------
        })

    def create(self):
        self.name = "MusicHelper-Menu"

    def beforeEditing(self):
        pass

    @staticmethod
    def set_command(name):
        global song_name
        song_name = name

    def on_a(self, *args, **keywords):
        self.set_command("$#wy#")
        self.parentApp.switchForm(None)

    def on_b(self, *args, **keywords):
        self.set_command("$#qq#")
        self.parentApp.switchForm(None)

    def on_c(self, *args, **keywords):
        self.set_command("$#pld-wy-1#")
        self.parentApp.switchForm(None)

    def on_d(self, *args, **keywords):
        self.set_command("$#pld-wy-2#")
        self.parentApp.switchForm(None)

    def on_e(self, *args, **keywords):
        self.set_command("$#pld-qq-1#")
        self.parentApp.switchForm(None)

    def on_f(self, *args, **keywords):
        self.set_command("$#pld-qq-2#")
        self.parentApp.switchForm(None)

    def on_g(self, *args, **keywords):
        self.set_command("$#login-wy#")
        self.parentApp.switchForm(None)

    def on_h(self, *args, **keywords):
        self.set_command("$#login-wy-p#")
        self.parentApp.switchForm(None)

    def on_i(self, *args, **keywords):
        self.set_command("$#check-wy#")
        self.parentApp.switchForm(None)

    def on_j(self, *args, **keywords):
        self.set_command("$#flac2mp3#")
        self.parentApp.switchForm(None)

    def on_k(self, *args, **keywords):
        self.set_command("$#scr-wy#")
        self.parentApp.switchForm(None)

    def on_l(self, *args, **keywords):
        self.set_command("$#lrc-wy#")
        self.parentApp.switchForm(None)

    def on_m(self, *args, **keywords):
        write_cfg()
        logger.info("配置文件重置成功，重启程序后应用。")
        self.parentApp.switchForm(None)

    def on_n(self, *args, **keywords):
        self.parentApp.switchForm('CONFIG')

    def on_ok(self, *args, **keywords):
        val = self.command.value
        if type(val) != int:
            val = 0
        def_list = [self.on_a, self.on_b, self.on_c,
                    self.on_d, self.on_e, self.on_f,
                    self.on_g, self.on_h, self.on_i,
                    self.on_j, self.on_k, self.on_l,
                    self.on_m]

        if val <= 12:
            def_list[val]()
        if val == 13:
            self.parentApp.switchForm('CONFIG')
        else:
            self.parentApp.switchForm(None)

    def on_cancel(self, *args, **keywords):
        self.parentApp.switchForm(None)


class MenuApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", MenuForm, name="Menu", color="IMPORTANT")
        self.addForm("CONFIG", ConfigForm, name="Edit config.ini", color="WARNING")

    def reset(self):
        self.__init__()


if __name__ == '__main__':
    show_full_windows()
    clear()
    # 读取配置文件
    read_cfg()
    output_logo()
    makedirs("Songs")
    makedirs("Songs_nodeapi")

    if using_api_beta:
        # print("".center(100, "-"))
        print(
            f"\n{Fore.YELLOW}Warning: 当前音乐接口为β版，可能会出现不稳定现象。若部分功能出现问题请将using_api_beta改为False。\n"
            f"当然，如果你乐意参与测试，可以忽略此警告。这是我们自己搭建的接口，因为用的人少理论上也许比旧的API更加稳定。{Style.RESET_ALL}\n")
        # print("".center(100, "-"), "\n")
    else:
        print("\n")

    refresh_ua()
    logger.info(title="Starting", info="正在初始化程序，这可能需要一些时间来获取数据。")
    music = Music()
    cookies = {}
    if os.path.exists("cookies_qq.txt"):
        try:
            f = open("cookies_qq.txt", "r")
            cookies_qq = convert_cookies_to_dict(f.read())
            f.close()
        except Exception:
            logger.error("解析QQ音乐cookies失败，格式错误。")

        logger.info(f"{Fore.GREEN}解析QQ音乐cookies成功。{Style.RESET_ALL}若无法正确下载歌曲请重新配置cookies。")

    if os.path.exists("cookies_netease.txt"):
        f = open("cookies_netease.txt", "r")
        cookies_wy = convert_cookies_to_dict(f.read())
        f.close()
        if autocheck_cookies:
            logger.info("解析网易云cookies成功，正在验证cookies有效性...")
            check_netease_cookies()
        else:
            logger.info(f"{Fore.GREEN}解析网易云cookies成功。{Style.RESET_ALL}使用$#check-wy#来验证cookies有效性。")
    else:
        logger.info("未检测到网易云cookies，部分解析功能将以受限模式运行。使用'$#login-wy#'来授权。")

    logger.info(f"当前平台: {Fore.RED}{music_source}{Style.RESET_ALL}, 可在歌曲输入框使用'$#help#'查看帮助。")

    if not using_api_beta:
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

    print("".center(25, "="))
    output_help_list()
    print("".center(25, "="))

    while True:
        selecting = False
        song_name = input("请输入要下载的歌曲名称或歌曲url(特殊指令格式为'$#[command]#', $#help#可查看特殊指令)\n> ")
        if song_name == "":
            menuApp = MenuApp()
            menuApp.run(fork=False)
        INDEX = 1
        if song_name == "$#help#":
            output_help_list()
        if song_name == "$#wy#":
            music_source = "wy"
            config.set('API', 'music_source', 'wy')
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            logger.info(f"{Fore.GREEN}成功将检索源切换为{Fore.RED}网易云音乐{Style.RESET_ALL}。")
        if song_name == "$#qq#":
            music_source = "qq"
            config.set('API', 'music_source', 'qq')
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            logger.info(f"{Fore.GREEN}成功将检索源切换为{Fore.YELLOW}QQ音乐{Style.RESET_ALL}。")
        if song_name == "$#about#":
            print("作者: @im-cwuom | 仅供学习交流使用，请在72小时内删除本程序。")

        if song_name == "$#pld-wy-1#":
            runNodeApi()
            temp_music_source = music
            try:
                playlist = input("(MODE1)(Netease) [输入'!b'返回]\n歌单ID&歌单url> ")
                if playlist == "!b":
                    continue
                getNeteasePlaylistM1(playlist)
            except Exception:
                logger.error("错误的，无法解析的歌单ID。请检查(还有一种可能是node服务没有启动或出现了问题)")
                traceback.print_exc(file=open("error.txt", "a+"))
            music_source = temp_music_source

        if song_name == "$#pld-wy-2#":
            runNodeApi()
            temp_music_source = music
            try:
                playlist = input("(MODE2)(Netease) [输入'!b'返回]\n歌单ID&歌单url> ")
                if playlist == "!b":
                    continue
                getNeteasePlaylistM2(playlist)
            except Exception:
                logger.error("错误的，无法解析的歌单ID。请检查")
                traceback.print_exc(file=open("error.txt", "a+"))

            music_source = temp_music_source

        if song_name == "$#pld-qq-1#":
            runNodeApi(type="qq")
            temp_music_source = music
            try:
                playlist = input("(MODE1)(QQ) [输入'!b'返回]\n歌单ID&歌单url> ")
                if playlist == "!b":
                    continue
                getQQMusicPlaylistM1(playlist)
            except Exception:
                logger.error("错误的，无法解析的歌单ID。请检查")
                traceback.print_exc(file=open("error.txt", "a+"))

            music_source = temp_music_source

        if song_name == "$#pld-qq-2#":
            runNodeApi(type="qq")
            temp_music_source = music
            try:
                playlist = input("(MODE2)(QQ) [输入'!b'返回]\n歌单ID&歌单url> ")
                if playlist == "!b":
                    continue
                getQQMusicPlaylistM2(playlist)
            except Exception:
                logger.error("错误的，无法解析的歌单ID。请检查")
                traceback.print_exc(file=open("error.txt", "a+"))

            music_source = temp_music_source

        if song_name == "$#login-wy#":
            runNodeApi()
            try:
                loginNetease()
            except Exception:
                traceback.print_exc(file=open("error.txt", "a+"))
                logger.error("登录失败，在登录时遇到了错误，请检查网络连接或是API服务是否被关闭。")

        if song_name == "$#check-wy#":
            check_netease_cookies()

        if song_name == "$#login-wy-p#":
            runNodeApi()
            try:
                loginNeteaseByPhone()
            except Exception:
                traceback.print_exc(file=open("error.txt", "a+"))
                logger.error("登录失败，在登录时遇到了错误，请检查网络连接或是API服务是否被关闭。")

        if song_name == "$#scr-wy#":
            runNodeApi()
            try:
                song_id = input("歌曲ID&URL(`!b`退出)> ")
                if song_id == "!b":
                    continue
                song_id = search_mid(song_id)
                scrobble_netease(song_id)
            except Exception:
                logger.error("出错了，请检查网络连接或是API服务是否被关闭并确保输入内容是合法的。")
                continue

        if song_name == "$#lrc-wy#":
            runNodeApi()
            try:
                song_id = input("歌曲ID&URL(`!b`退出)> ")
                if song_id == "!b":
                    continue
                song_id = search_mid(song_id)
                get_lyric_netease(song_id)
            except Exception:
                logger.error("出错了，请检查网络连接或是API服务是否被关闭并确保输入内容是合法的。")
                continue

        if song_name == "$#flac2mp3#":
            base = input("输入需要转换的文件所在的文件夹名称/路径(`!b`退出)\n(回车默认Songs)> ")
            if base == "!b":
                continue
            base = "Songs" if base == "" else base
            if not os.path.exists(base):
                continue
            if base != "Songs":
                if base != "Songs_nodeapi":
                    if input("您输入的文件夹名称不是`Songs`或`Songs_nodeapi`，是否继续？(y/*)> ") != "y":
                        continue

            flac2mp3(base)

        if song_name == "$#faq#":
            print("https://github.com/cwuom/MusicHelper/#faq")
            selecting = True

        try:
            if song_name[0] + song_name[1] == "$#" and song_name[-1] == "#":
                continue
        except Exception:
            continue
        res = search_mid(song_name)
        if res != song_name:
            if res == 404:
                logger.error("对不起，暂不支持解析QQ音乐单曲。")
                continue

            mode = input(
                "解析模式选择 \n(1) 获取客户端歌曲下载url (接口获取的是歌曲试听 url, 但存在部分歌曲在非 VIP 账号上可以下载无损音质而不能试听无损音质, 使用此接口可使非 VIP 账号获取这些歌曲的无损音频)\n"
                "(2) 获取音乐url (默认，音质可选)\n(`!b`退出) (1/2)> ")

            if mode == "!b":
                continue
            try:
                runNodeApi()
                if mode == "1":
                    get_songs_netease_m2(res)
                elif mode == "2":
                    get_songs_netease_m1(res)
                else:
                    logger.info("将使用默认解析模式...")
                    get_songs_netease_m1(res)
            except Exception:
                logger.error("无法解析音乐链接，可能是其音乐链接不包含单曲ID。请检查后重试")
                traceback.print_exc(file=open("error.txt", "a+"))
                pass

            continue
        else:
            if "https://" in res:
                logger.error("不受支持的音乐链接，仅限网易云音乐单曲链接。")
                continue
        try:
            if not using_api_beta:
                search_result = music.search(song_name, _cookies=cookies)[0]
                songs_data = [d for d in analyse_song_data(search_result)]
            else:
                search_result = music.search_c(song_name)[0]
                songs_data = [d for d in analyse_song_data_c(search_result)]

        except Exception:
            logger.error("无法解析音乐数据，API服务器可能出现了故障，请稍后重试。")
            traceback.print_exc(file=open("error.txt", "a+"))
            continue

        clear()
        INDEX_MAX = len(songs_data)
        logger.info(title="Done", info="歌曲列表加载完成。使用上下键选择歌曲，回车下载。")
        try:
            if SelectStyle == 0:
                disable_keyboard_flag = True
                disable_thread = Thread(target=disable_keyboard_event)
                disable_thread.start()
                SelectStyle0()
            elif SelectStyle == 1:
                SelectStyle1()

            if not flag_back:
                logger.info(title="Done", info=f"{Fore.GREEN}歌曲下载完成...")
            else:
                clear()
                logger.info(title="-", info=f"{Fore.RED}用户取消操作...")
        except Exception as e:
            if len(songs_data) != 0:
                logger.error(
                    "在选择/下载歌曲时发生了错误，请检查网络连接。若持续出现此错误，则有可能是对方的API服务器出现了故障或是反爬手段增强了。请关注最新动态")
                logger.error(e)
                traceback.print_exc(file=open("error.txt", "a+"))

        disable_keyboard_flag = False
        print("为了防止误触，双击任意键继续...")
        getch()
