import hashlib
import base64

def md5Hash(data):
    return hashlib.md5(str(data).encode('utf-8')).hexdigest().lower()


def isBase64(data):
    return data.startswith('base64://', 0, len('base64://'))


def base64Encode(data):
    return 'base64://' + base64.b64encode(data).decode('utf-8')


def base64Decode(data):
    if (isBase64(data)):
        data = data[len('base64://'):]

    return base64.b64decode(bytes(data, 'utf-8'))


def getExceptionMessage(e):
    if hasattr(e, 'message'):
        return e.message
    return str(e)
