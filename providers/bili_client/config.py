"""Only upstream API constants; no legacy data directories or credentials."""
BILI_NAV_URL = 'https://api.bilibili.com/x/web-interface/nav'

BILI_REPLY_URL = 'https://api.bilibili.com/x/v2/reply/add'

BILI_PRIVATE_MSG_SEND_URL = 'https://api.vc.bilibili.com/web_im/v1/web_im/send_msg'

BILI_COOKIE_INFO_URL = 'https://passport.bilibili.com/x/passport-login/web/cookie/info'

BILI_COOKIE_REFRESH_URL = 'https://passport.bilibili.com/x/passport-login/web/cookie/refresh'

BILI_COOKIE_CONFIRM_URL = 'https://passport.bilibili.com/x/passport-login/web/confirm/refresh'

BILI_QR_GENERATE_URL = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'

BILI_QR_POLL_URL = 'https://passport.bilibili.com/x/passport-login/web/qrcode/poll'

BILI_DYNAMIC_TEXT_URL = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/create'

BILI_DYNAMIC_IMAGE_URL = 'https://api.bilibili.com/x/dynamic/feed/create/dyn'

BILI_UPLOAD_IMAGE_URL = 'https://api.bilibili.com/x/dynamic/feed/draw/upload_bfs'

MIXIN_KEY_ENC_TAB = [46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49, 33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40, 61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11, 36, 20, 34, 44, 52]

BILI_RSA_PUBLIC_KEY = '-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDLgd2OAkcGVtoE3ThUREbio0Eg\nUc/prcajMKXvkCKFCWhJYJcLkcM2DKKcSeFpD/j6Boy538YXnR6VhcuUJOhH2x71\nnzPjfdTcqMz7djHum0qSZA0AyCBDABUqCrfNgCiJ00Ra7GmRj+YCK1NJEuewlb40\nJNrRuoEUXpabUzGB8QIDAQAB\n-----END PUBLIC KEY-----'

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
