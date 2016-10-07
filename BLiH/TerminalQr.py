'''QRCode Terminal Display Helper

'''

import qrcode, platform
from Exception import CreateQrException

__all__ = [ 'create' ]

def create(content = None):
    if (content is None) or (not isinstance(content, str)):
        raise CreateQrException('Terminal display helper need a str type contents')

    qr = qrcode.QRCode(box_size = 1)
    qr.add_data(content)
    qr.make(fit = True)

    return TerminalQr(qr.make_image(), content)

class TerminalQr(object):
    BLACK = '\u2588\u2588'
    BLANK = '  '

    def __init__(self, image, content):
        self.__image   = image
        self.__data    = content
        self.__system  = platform.system()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is not None:
            raise

    def __str__(self):
        return self.__terminalQrCode()

    def __repr__(self):
        return self.__str__()

    def __terminalQrCode(self):
        canvas = ''
        # self.__image = Image.open('png.jpg')
        l = list(self.__image.getdata())

        for index in range(len(l)):
            if index is not 0 and index % (self.__image.width + 8) == 0:
                canvas += '\n'
            canvas += TerminalQr.BLANK if l[index] == 255 else TerminalQr.BLACK

        return canvas

if __name__ == '__main__':
    from Config import QrLoginUrl

    with create(QrLoginUrl('abcdefghijklmnopqrstuvwxyz012345')) as qr:
        print(qr)
