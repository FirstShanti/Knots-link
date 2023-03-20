import re
import hashlib
import random
import string
import base64
import datetime
from dateutil import parser

from flask_restful import reqparse
# from Crypto.Cipher import AES
# from Crypto.Util.Padding import unpad


def fromisoformat(s):
    d = parser.parse(s)
    return d


def randomString(choises=[string.ascii_letters, string.digits, string.punctuation], length=64):
    return ''.join(random.SystemRandom().choice(''.join(choises)) for _ in range(length))


# def decryptString(content, k, i):
#     enc = base64.b64decode(content)
#     cipher = AES.new(k.encode('utf-8'), AES.MODE_CBC, i.encode('utf-8'))
#     return unpad(cipher.decrypt(enc), 16)



def args_to_parser(validator, params, location):
    parser = reqparse.RequestParser(bundle_errors=True)
    parser.args.clear()
    for field, valid_param in validator[params].items():
        parser.add_argument(field, **valid_param, location=location)
    return parser


def encrypt_string(string):
    return hashlib.sha3_256(string.encode()).hexdigest()


def slugify(s):
    pattern = r'[^\w+]'
    return re.sub(pattern, '-', s)