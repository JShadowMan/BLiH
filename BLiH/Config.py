'''BiliBili Helper Config Information

'''
from . import Exceptions

# encoding
ENCODING = 'UTF-8'

INIT_COOKIES_START = 'https://passport.bilibili.com/login'
GET_OAUTH_KEY      = 'https://passport.bilibili.com/qrcode/getLoginUrl'

QR_LOGIN_URL   = 'https://account.bilibili.com/qrcode/login?oauthKey=%s'
LOGIN_INFO_URL = 'https://passport.bilibili.com/qrcode/getLoginInfo'

# Expiration time is 3 minutes. To be safe, on that basis minus 5 seconds
QR_EXPIRED_TIME = 3 * 60 - 5

# Detection frequency of login status
DETECT_LOGIN_STATUS_INTERVAL = 2

# Number of retries, HTTP
RE_HTTP_REQUEST_COUNT = 3

# Number of retries
RE_LOGIN_COUNT = 3

CAPTCHA_URL   = 'https://passport.bilibili.com/captcha'

VIDEO_URL = 'http://www.bilibili.com/video/av%s/'
LIVE_URL  = 'http://live.bilibili.com/%s'

# Get Sign Info
''' http://live.bilibili.com/sign/GetSignInfo

    Request:
        type: GET

    Response:
        type: JSON
'''
GET_SIGN_INFO = 'http://live.bilibili.com/sign/GetSignInfo'

# Sign Daily
''' Sign Daily

    Request:

    Response:
        JSON

'''
LIVE_SIGN_DAILY = 'http://live.bilibili.com/sign/doSign'

# Main: Get User Information API
GET_USER_INFO = 'http://interface.bilibili.com/nav.js'

# Live: Get User Information API
''' Get Live-User Information API

    Request:
        type: GET
        data:
            q -> (Date.now() * Math.ceil(Math.random() * 100000)).toString(16)
        dataType: JSON
    Response:
        JSON: {
            code: String,
            msg: String,
            data: {
            uname: String,
            face: URL[String],
            gold: Number,
            silver: Number,
            user_intimacy: Number,
            user_level: Number,
            user_level_rank: Number,
            user_next_intimacy: Number,
            user_next_level: Number,
            vip: [1: true, 0: false]
            }
        }
'''
GET_USER_LIVE_INFO = 'http://live.bilibili.com/User/getUserInfo'

# Unread messages Count
''' Unread messages Count

    Request:
        type: GET ? POST
        data:
            type -> "jsonp"
            captcha -> captcha_key (?)
            callback -> "callback"
            ts: (unix time strap)
    Response:
        type: "JSONP"
'''
UNREAD_MESSAGE_COUNT = 'http://message.bilibili.com/api/notify/query.notify.count.do'

# Get Live Room Admin List
''' Get Admin List

    Request:
        type: GET
        data:
            roomid -> ROOM ID

    Response:
        type: JSON

'''
LIVE_GET_ADMIN_LIST = 'http://live.bilibili.com/liveact/ajaxGetAdminList'

# Get Master Info
''' Get Master Info

    Request:
        type: GET
        data:
            roomid -> ROOM ID

    Response:
        type: JSON
'''
GET_OWN_MASTER_INFO = 'http://live.bilibili.com/live/getMasterInfo'

# Get My Wear Medal
''' ajaxGetMyWearMedal

    Request:
        type: GET

    Response:
        type: JSON
'''
GET_MY_WEAR_MEDAL = 'http://live.bilibili.com/i/ajaxGetMyWearMedal'


# Get My Medal List
''' ajaxGetMyMedalList

    Request:
        type: GET

    Response:
        type: JSON
'''
GET_MY_MEDAL_LIST = 'http://live.bilibili.com/i/ajaxGetMyMedalList'

# Wear Fans Medal
''' ajaxWearFansMedal

    Request:
        type: POST
    data:
        medal_id -> medalId

    Response:
        type: JSON
'''
WEAR_FANS_MEDAL = 'http://live.bilibili.com/i/ajaxWearFansMedal'

# Cancel Wear
''' ajaxCancelWear

    Request:
        type: GET

    Response:
        type: JSON
'''
CANCEL_WEAR_MEDAL = 'http://live.bilibili.com/i/ajaxCancelWear'

# Get My Wear Title
''' ajaxGetMyWearTitle

    Request:
        type: GET

    Response:
        type: JSON
'''
GET_MY_WEAR_TITLE = 'http://live.bilibili.com/i/ajaxGetMyWearTitle'

# Get My Title List
''' ajaxGetMyTitleList

    Request:
        type: POST

    Response:
        type: JSON
'''
GET_MY_TITLE_LIST = 'http://live.bilibili.com/i/ajaxGetMyTitleList'

# Cancel Wear Title
''' ajaxCancelWearTitle

    Request:
        type: POST

    Response:
        type: JSON
'''
CANCEL_WEAR_TITLE = 'http://live.bilibili.com/i/ajaxCancelWearTitle'

# Shield user
''' shield_user

    Request:
        type: POST
        data:
            roomid -> room id
            uid    -> user id
            type: 1

    Response:
        type: JSON
'''
ADMIN_SHIELD_USER = 'http://live.bilibili.com/liveact/shield_user'

# DM report
''' dmreport

    Request:
        type: POST
        data:
            roomid -> room id
            uid    -> user id
            msg:   -> user message
            reason -> reason

    Response:
        type: JSON
'''
USER_DM_REPORT = 'http://live.bilibili.com/liveact/dmreport'

# Get Other Master Info
''' /user/getMasterInfo

    Request:
        type: POST
        data:
            uid -> user id

    Response:
        type: JSON
'''
GET_OTHER_MASTER_INFO = 'http://live.bilibili.com/user/getMasterInfo'

# Attention Master
''' /liveact/attention

    Request:
        type: POST
        data:
            uid -> master uid
            type: 1

    Response:
        type: JSON
'''
ATTENTION_MASTER_ROOM = 'http://live.bilibili.com/liveact/attention'

# Get Current Treasure
''' /FreeSilver/getCurrentTask

    Request:
        type: GET

    Response:
        type: JSON

'''
GET_CURRENT_TREASURE = 'http://live.bilibili.com/FreeSilver/getCurrentTask'

# Get Award
''' /FreeSilver/getAward

    Request:
        type: GET
        data:
            time_start -> start time
            time_end -> end time
            captcha -> GET_CAPTCHA

    Response:
        JSON
'''
GET_CURRENT_AWARD = 'http://live.bilibili.com/FreeSilver/getAward'

# return apiDomain + '/freeSilver/getCaptcha?ts=' + Date.now();
GET_CAPTCHA = 'http://live.bilibili.com/freeSilver/getCaptcha?ts='

# Get Room Info
''' /live/getInfo

    Request:
        type: GET
        data:
            roomid -> room id

    Response:
        type: JSON
'''
GET_ROOM_INFO = 'http://live.bilibili.com/live/getInfo'

# Live Room Online Heart, 5min
''' /User/userOnlineHeart

    Request:
        type: POST

    Response:
        type: JSON
'''
USER_ONLIVE_HEART = 'http://live.bilibili.com/User/userOnlineHeart'

def QrLoginUrl(oAuthKey = None):
    if oAuthKey is None:
        raise Exceptions.ConfigException('oAuthKey parameter must be specified')
    else:
        if len(oAuthKey) != 32:
            raise Exceptions.ConfigException('oAuthKey format error, length is not 32')
        return QR_LOGIN_URL % oAuthKey

def videoUrl(av = None):
    if av is None:
        raise Exceptions.ConfigException('avCode parameter must be specified')
    if not isinstance(av, int):
        raise Exceptions.ConfigException('avCode must be int type')
    return VIDEO_URL % av

