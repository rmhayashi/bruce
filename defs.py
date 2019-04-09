from classes import *

def req(variavel):
    return request.form.get(variavel)

def md5(variavel):
    return hashlib.md5(variavel.encode('utf-8')).hexdigest()