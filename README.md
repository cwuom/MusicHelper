


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

# 如何运行？⛏️

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
其中，例如"...\nodeQQ\*"、"...\node\*"、"...\vlc-3.0.6\*"需要自行去[这里](https://github.com/cwuom/MusicHelper#%E9%99%84%E5%8A%A0%E7%BB%84%E4%BB%B6%E4%B8%8B%E8%BD%BD%EF%B8%8F)下载，
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


# 如何使用？🪄
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
#### 模式2
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

## 操作打断
输错了，后悔了？这个特性可以帮你。(仅1.3.2b及以上)
### 选歌界面
#### 键盘选择模式
> 直接在选择界面按下'esc'即可
#### 序号模式
> 直接在序号输入处输入'!b'即可

### 歌单输入界面
> 直接输入`!b`

### 未分类
> 同上，直接输入`!b`

## 刷单曲播放量
- 在搜索歌曲的地方输入`$#scr-wy#`即可进入刷单曲播放界面。
- 等待API服务启动后，输入网易云单曲ID或链接进入刷播放模式。
> 注意，此功能需要配合登录使用。

## 通过单曲链接直接解析
- 在搜索歌曲的地方输入网易云单曲URL可直接进入解析详情。
- 会有两种解析模式，在程序中都有标明其作用，此处不再赘述。
> 注意，此功能需要配合登录使用。若下载黑胶VIP歌曲，本身没有会员的则是下载试听版。

## 通过单曲链接直接解析并下载双语歌词
- 在搜索歌曲的地方输入``$#lrc-wy#``
- 直接输入网易云单曲链接或单曲URL即可

# 配置文件(config.ini)说明📃
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
; 自动检测网易云登录cookies是否过期，没有node请不要开启
check_netease_cookies = False


```
# 授权您的音乐账号✅
## 登录网易云账号
### 二维码登录
1. 在搜索歌曲的地方输入"$#login-wy#"即可进入二维码登录界面。
2. 不出意外，在终端会输出一张大大的二维码。如果二维码太大了，可以使用Ctrl+鼠标滚轮缩小至可以扫码的地步。如果出现了意外，则可以在程序运行目录找到"qrcode.jpg"并打开它再扫码进行登录。效果是一样的
### 手机号登录
1. 在搜索歌曲的地方输入"$#login-wy#"即可进入手机号登录界面。
2. 及时输入正确的验证码，即可完成登录。

# 附加组件下载⬇️
## 歌单解析API工具(只解析单曲无需下载)
### 网易云NodeAPI下载（node）
来源: https://github.com/Binaryify/NeteaseCloudMusicApi
> 这是打包好的下载地址，在终端输入*node app.js*即可直接运行(windows)
```
https://wwjj.lanzouw.com/i6j4j1at9m6d  
密码:cd2v
```
### QQ音乐NodeAPI下载（nodeQQ）
来源: https://github.com/jsososo/QQMusicApi
> 这是打包好的下载地址，在终端输入*npm start*即可直接运行(windows)
```
https://wwjj.lanzouw.com/iyYaj1anz8mf
```

### 下载完成后和主程序放在同一目录。

## 音频预览所需文件
### vlc-3.0.6
下载地址(密码:**fhrf**)
```
https://wwjj.lanzouw.com/iHlCi1ap290d
```

# FAQ💭
## Q: 为什么下载出来的音频全都是试听版(30s)？
### A: 请确保你已经扫码登录了网易云，如果登录了依旧还是试听版那么请确保你有网易云的VIP。如果你有VIP依旧无法解决上述问题，那么就可以尝试重新登录（也许是cookies掉了）。
---
## Q: 初始化的时候出现 ``[ERROR - 21:00:32] HTTPSConnectionPool(host='ghxcx.lovestu.com', port=443): Max retries exceeded with url: /api/index/today_secret (Caused by ProxyError('Unable to connect to proxy', OSError(0, 'Error')))`` 之类的报错怎么办？
### A: 请关闭全局梯子或将梯子设为虚拟网卡模式(Service Mode)
## Q: 解析歌曲的时候出现``无法匹配http://mobileoc.music.tc.qq.com/的文件类型，因为他不受支持。``之类的报错怎么办？
### A: API炸了，过段时间再解析试试吧。
## Q: 一直提示 ``无法解析音乐链接，可能是其音乐链接不包含单曲ID。请检查后重试`` 怎么办？
### A: 请确认网易云API服务已经正确启动并且没有被关闭或者确认下歌单链接是否正确。正确歌单链接示例``https://music.163.com/#/playlist?id=3865036``。如果输入内容符合规范，那么大概率是歌单中的歌曲太多了，挑几首必要的创建新歌单再试试吧。
## Q: 提示``[ERR] /song/detail?ids=66285&timestamp=1696647857450 { status: 400, body: { code: -460, message: '网络太拥挤，请稍候再试！' } }``怎么办？
### 网易云API炸了，或者被风控了。过段时间重新解析一下或者直接重启路由器再试试
---
## 我有其它问题
### A： [Issues · cwuom/MusicHelper (github.com)](https://github.com/cwuom/MusicHelper/issues)

---

## 🔴注意事项
- 本项目仅供学习和参考，请在72小时内删除此工具。
- 本项目几乎没有人参与测试，有问题很正常，及时反馈后我会按情况修复。
- 此项目**不保证能长期使用**。
- 介于项目的特殊性质，开发者在未来随时有可能会**停止更新**或**删库**
