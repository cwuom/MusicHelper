<h1 align="center">MusicHelper</h1>
<div align="center">

<p align="center">
    <h3>一个通过Python编写的QQ、网易云音乐无损音乐爬取工具</h3>
    <p align="center">
        <a href="https://t.me/cwuoms_group">
<img alt="JoinTelegramGroup" src="https://img.shields.io/badge/Telegram-Group-blue" />
</a>
      <p>
检索范围<br />
QQ音乐 / 网易云音乐<br />
<br />
    </p>
    <p align="center">
      <img src="logo.png" />
    </p>
  </p>
</div>

# 如何运行？
## 自行编译此项目
### Python版本选择
- 经过测试，**Python3.7.16**可以稳定运行此项目。
### 下载并运行此项目
```powershell
git clone https://github.com/cwuom/MusicHelper.git
cd MusicHelper
pip install -r .\requirements.txt

mkdir nodeQQ
mkdir node
mkdir vlc-3.0.6
cp "...\nodeQQ\*" "nodeQQ" -Recurse
cp "...\node\*" "node" -Recurse
cp "...\vlc-3.0.6\*" "vlc-3.0.6" -Recurse

python main.py
```
其中，例如"...\nodeQQ\*"、"...\node\*"、"...\vlc-3.0.6\*"需要自行去[这里](https://github.com/cwuom/MusicHelper#%E9%9F%B3%E9%A2%91%E9%A2%84%E8%A7%88%E6%89%80%E9%9C%80%E6%96%87%E4%BB%B6)下载，
```
并将"..."替换成绝对路径地址。
例如"...\nodeQQ\*"替换成 ”C:\Users\cwuom\Downloads\nodeQQ\*"
-----------------------------------------------------------
合起来命令就是
cp "C:\Users\cwuom\Downloads\nodeQQ\*" "nodeQQ" -Recurse
```
## 下载已打包版本
### 如果你懒得自己编译源码，那么可以直接前往[Releases · cwuom/MusicHelper (github.com)](https://github.com/cwuom/MusicHelper/releases)下载已打包的版本来运行。
- 此版本运行非常简单，只需要双击exe就可以了。但是不保证兼容性（Windows7可能无法运行）且只支持Windows，小白建议直接使用这个版本。
- 注意：不会第一时间放出已打包版本，意思是当源码更新时不会同步更新Releases。这意味着如果**你需要最新的特性或是遇到了Bug还是请先尝试编译源码**。


# 如何使用？
## 初始化
- 程序在打开后会自动初始化，这可能需要一定的时间。如果这个环节出错了应该是API炸了或者被风控了，过一段时间再试试
## 切换平台
### 将检索源切换为*网易云音乐*
在输入歌曲名称的地方输入
```
$#wy#
```
回车后即可变更搜索源，立刻生效。
### 将检索源切换为*QQ音乐*
在输入歌曲名称的地方输入
```
$#qq#
```
回车后即可变更搜索源，立刻生效。

## 歌单下载指令
### Warning：此功能目前正在测试，可能不稳定。掉歌是正常现象
### 网易云音乐歌单下载
#### 模式1
1. 在搜索歌曲的地方输入"$#pld-wy-1#"即可进入网易云歌单下载界面。
2. 在歌单ID输入框中输入[歌单ID(?)](https://cn.bing.com/search?q=%E7%BD%91%E6%98%93%E4%BA%91%E6%80%8E%E4%B9%88%E7%9C%8B%E6%AD%8C%E5%8D%95ID)即可下载歌单。
> 模式1无多线程，而且容易被BAN IP，当歌单歌曲数量庞大时不建议使用。
#### 模式2
1. 在搜索歌曲的地方输入"$#pld-wy-2#"即可进入网易云歌单下载界面。
2. 在歌单ID输入框中输入歌单ID
> 模式2有多线程，当歌单中的歌曲数量很多的时候也不容易被风控，但是可能需要依靠授权您的网易云账号来获得更高的音质。

### QQ音乐歌单下载
#### 模式1
1. 在搜索歌曲的地方输入"$#pld-qq-1#"即可进入网易云歌单下载界面。
2. 与网易云大差不差，可自行测试。
### 模式2
1. 在搜索歌曲的地方输入"$#pld-qq-2#"即可进入网易云歌单下载界面。
2. 掉歌非常严重，目前暂时不知道如何修复。

## 歌曲预览
如果您光看标题无法分辨所选歌曲是否为自己想要的，您可以在选歌界面（仅限select_style = 0）中按下空格来在线播放歌曲，具体操作如下
### 播放/暂停
- 空格(space)
### 播放进度切换
#### 快进1秒
- 方向键右 (->)
#### 快退1秒
- 方向键左 (<-)
### 退出歌曲预览
- ESC

# 配置文件说明
```ini
[API]
; API地址，一般无需改动
url = https://music.ghxi.com/wp-admin/admin-ajax.php
; 音乐检索平台
music_type = qq

[SETTING]
; 音乐选择模式 (0: 键盘选择; 1: 序号模式)
select_style = 0
; 命中提示字符(仅在select_style=0时有效)
select_char = X
; DEBUG模式，反馈bug请将此处设为true(会拦截全局错误)。
debug = False


```
# 授权您的音乐账号
## 登录网易云账号
1. 在搜索歌曲的地方输入"$#login-wy#"即可进入授权界面。
2. 不出意外，在终端会输出一张大大的二维码。如果二维码太大了，可以使用Ctrl+鼠标滚轮缩小至可以扫码的地步。如果出现了意外，则可以在程序运行目录找到"qrcode.jpg"并打开它再扫码进行登录。效果是一样的


# 附加组件下载
## 歌单解析API工具(只解析单曲无需下载)
### 网易云NodeAPI下载（node）
来源: https://github.com/Binaryify/NeteaseCloudMusicApi
> 这是打包好的下载地址，在终端输入*node app.js*即可直接运行(windows)

> https://wwjj.lanzouw.com/ir3NA1ake1pc
### QQ音乐NodeAPI下载（nodeQQ）
来源: https://github.com/jsososo/QQMusicApi
> 这是打包好的下载地址，在终端输入*npm start*即可直接运行(windows)

> https://wwjj.lanzouw.com/iyYaj1anz8mf

### 下载完成后和主程序放在同一目录。

## 音频预览所需文件
### vlc-3.0.6
下载地址(密码:**fhrf**)
> https://wwjj.lanzouw.com/iHlCi1ap290d

## 注意事项
- 本项目仅供学习和参考，请在72小时内删除此工具。
- 此项目**不保证能长期使用**。
- 介于项目的特殊性质，开发者在未来随时有可能会**停止更新**或**删库**
