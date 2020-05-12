from django.db import connection
from django.http import JsonResponse
import os
import shutil
import simplejson
import random
import string


def queryUserList(request):
    result = []
    ip = request.META['REMOTE_ADDR']
    if ip != '127.0.0.1':
        return JsonResponse(result, safe=False)
    with connection.cursor() as c:
        c.execute('SELECT username, password FROM user')
        r = c.fetchall()
    for user in r:
        with connection.cursor() as c:
            c.execute('SELECT COUNT(username) FROM client WHERE username=:username', {'username': user[0]})
            r1 = c.fetchone()
        result.append({'username': user[0], 'clientCount': r1[0], 'password': user[1]})
    return JsonResponse(result, safe=False)


def querySyncFolderList(request):
    result = []
    ip = request.META['REMOTE_ADDR']
    if ip != '127.0.0.1':
        return JsonResponse(result, safe=False)
    with connection.cursor() as c:
        c.execute('SELECT foldername FROM sync_folder')
        r = c.fetchall()
    for foldername in r:
        with connection.cursor() as c:
            c.execute('SELECT COUNT(username) FROM user_privilege WHERE foldername=:foldername',
                      {'foldername': foldername[0]})
            r1 = c.fetchone()
        result.append({'foldername': foldername[0], 'userCount': r1[0]})
    return JsonResponse(result, safe=False)


def queryPrivilegeList(request):
    result = []
    ip = request.META['REMOTE_ADDR']
    if ip != '127.0.0.1':
        return JsonResponse(result, safe=False)
    with connection.cursor() as c:
        c.execute('SELECT username, foldername, privilege FROM user_privilege')
        r = c.fetchall()
    for privilege in r:
        result.append({'username': privilege[0], 'foldername': privilege[1], 'privilege': privilege[2]})
    return JsonResponse(result, safe=False)


def userAdd(request):
    ip = request.META['REMOTE_ADDR']
    if ip != '127.0.0.1':
        return JsonResponse('请使用远程桌面登录服务器进行操作', safe=False)
    username = simplejson.loads(request.body)['username']
    try:
        with connection.cursor() as c:
            c.execute('INSERT INTO user VALUES (:username, :password)', {'username': username, 'password': generate_password()})
    except:
        return JsonResponse('用户已存在', safe=False)
    return JsonResponse('ok', safe=False)

def userPasswordRefresh(request):
    ip = request.META['REMOTE_ADDR']
    if ip != '127.0.0.1':
        return JsonResponse('请使用远程桌面登录服务器进行操作', safe=False)
    username = simplejson.loads(request.body)['username']
    try:
        with connection.cursor() as c:
            c.execute('UPDATE user SET password=:password WHERE username=:username',
                      {'username': username, 'password': generate_password()})
    except:
        return JsonResponse('用户不存在', safe=False)
    return JsonResponse('ok', safe=False)


def syncFolderAdd(request):
    ip = request.META['REMOTE_ADDR']
    if ip != '127.0.0.1':
        return JsonResponse('请使用远程桌面登录服务器进行操作', safe=False)
    foldername = simplejson.loads(request.body)['foldername']
    try:
        with connection.cursor() as c:
            c.execute('INSERT INTO sync_folder VALUES (:foldername)', {'foldername': foldername})
        folderPath = os.path.join(os.path.abspath('syncFolder'), foldername)
        if not os.path.exists(folderPath):
            os.makedirs(folderPath)
    except:
        return JsonResponse('文件夹已存在', safe=False)
    return JsonResponse('ok', safe=False)


def userPrivilegeAdd(request):
    ip = request.META['REMOTE_ADDR']
    if ip != '127.0.0.1':
        return JsonResponse('请使用远程桌面登录服务器进行操作', safe=False)
    username = simplejson.loads(request.body)['username']
    foldername = simplejson.loads(request.body)['foldername']
    privilege = simplejson.loads(request.body)['privilege']

    with connection.cursor() as c:
        c.execute('SELECT username FROM user WHERE username=:username', {'username': username})
        r = c.fetchone()
    if r is None:
        return JsonResponse('用户不存在', safe=False)

    with connection.cursor() as c:
        c.execute('SELECT foldername FROM sync_folder WHERE foldername=:foldername', {'foldername': foldername})
        r = c.fetchone()
    if r is None:
        return JsonResponse('同步文件夹不存在', safe=False)

    try:
        with connection.cursor() as c:
            c.execute('INSERT INTO user_privilege VALUES (:username, :foldername, :privilege)'
                      , {'username': username, 'foldername': foldername, 'privilege': privilege})
    except:
        return JsonResponse('用户权限已存在', safe=False)
    return JsonResponse('ok', safe=False)


def userDel(request):
    ip = request.META['REMOTE_ADDR']
    if ip != '127.0.0.1':
        return JsonResponse('请使用远程桌面登录服务器进行操作', safe=False)
    username = simplejson.loads(request.body)['username']
    with connection.cursor() as c:
        c.execute('DELETE FROM user WHERE username=:username', {'username': username})
        c.execute('DELETE FROM client WHERE username=:username', {'username': username})
        c.execute('DELETE FROM sync_lock WHERE username=:username', {'username': username})
        c.execute('DELETE FROM user_privilege WHERE username=:username', {'username': username})
    return JsonResponse('ok', safe=False)


def syncFolerDel(request):
    ip = request.META['REMOTE_ADDR']
    if ip != '127.0.0.1':
        return JsonResponse('请使用远程桌面登录服务器进行操作', safe=False)
    foldername = simplejson.loads(request.body)['foldername']
    with connection.cursor() as c:
        c.execute('DELETE FROM sync_folder WHERE foldername=:foldername', {'foldername': foldername})
        c.execute('DELETE FROM sync_file WHERE foldername=:foldername', {'foldername': foldername})
        c.execute('DELETE FROM sync_lock WHERE foldername=:foldername', {'foldername': foldername})
        c.execute('DELETE FROM user_privilege WHERE foldername=:foldername', {'foldername': foldername})

    folderPath = os.path.join(os.path.abspath('syncFolder'), foldername)
    if os.path.exists(folderPath):
        shutil.rmtree(folderPath, ignore_errors=True)
    return JsonResponse('ok', safe=False)


def userPrivilegeDel(request):
    ip = request.META['REMOTE_ADDR']
    if ip != '127.0.0.1':
        return JsonResponse('请使用远程桌面登录服务器进行操作', safe=False)
    requestJson = simplejson.loads(request.body)
    with connection.cursor() as c:
        c.execute('DELETE FROM sync_lock WHERE username=:username AND foldername=:foldername',
                  {'username': requestJson['username'], 'foldername': requestJson['foldername']})
        c.execute('DELETE FROM user_privilege WHERE username=:username AND foldername=:foldername',
                  {'username': requestJson['username'], 'foldername': requestJson['foldername']})
    return JsonResponse('ok', safe=False)

def generate_password(len=16):
    '''生成n个长度为len的随机序列码'''
    random.seed()
    chars = string.ascii_letters + string.digits
    return ''.join([random.choice(chars) for _ in range(len)])