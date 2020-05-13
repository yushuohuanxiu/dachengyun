from django.http import JsonResponse
from django.db import connection
import simplejson
import base64
import os
from dachengyun import rsaUtil, syncLockUtil
import hashlib


def querySyncFolder(request):
    result = {'state': 'ok'}
    message = simplejson.loads(request.body)
    verifyResult = rsaUtil.verifyMessage(message)
    if verifyResult != 'ok':
        result['state'] = 'error'
        result['errorInfo'] = verifyResult
        return JsonResponse(result)

    with connection.cursor() as c:
        c.execute('SELECT foldername, privilege FROM user_privilege WHERE username=:username',
                  {'username': message['username']})
        result['syncFolders'] = c.fetchall()

    return JsonResponse(result)


def queryFileInfo(request):
    result = {'state': 'ok'}
    message = simplejson.loads(request.body)
    verifyResult = rsaUtil.verifyMessage(message)
    if verifyResult != 'ok':
        result['state'] = 'error'
        result['errorInfo'] = verifyResult
        return JsonResponse(result)

    with connection.cursor() as c:
        c.execute('SELECT username FROM user_privilege WHERE username=:username AND foldername=:foldername',
                  {'username': message['username'], 'foldername': message['foldername']})
        r = c.fetchone()
    if r is None:
        result['state'] = 'error'
        result['errorInfo'] = '用户无权限'
        return JsonResponse(result)

    with connection.cursor() as c:
        c.execute('SELECT filename, md5 FROM sync_file WHERE foldername=:foldername',
                  {'foldername': message['foldername']})
        rs = c.fetchall()
        fileInfos = {}
        for fileInfo in rs:
            fileInfos[fileInfo[0]] = fileInfo[1]
        result['fileInfos'] = fileInfos
    return JsonResponse(result)


def queryFileInfoWithLock(request):
    result = {'state': 'ok'}
    message = simplejson.loads(request.body)
    verifyResult = rsaUtil.verifyMessage(message)
    if verifyResult != 'ok':
        result['state'] = 'error'
        result['errorInfo'] = verifyResult
        return JsonResponse(result)
    with connection.cursor() as c:
        c.execute('SELECT username FROM user_privilege WHERE username=:username AND foldername=:foldername',
                  {'username': message['username'], 'foldername': message['foldername']})
        r = c.fetchone()
    if r is None:
        result['state'] = 'error'
        result['errorInfo'] = '用户无权限'
        return JsonResponse(result)
    lockResult = syncLockUtil.getLock(message)
    if lockResult != 'ok':
        result['state'] = 'error'
        result['errorInfo'] = lockResult
        return JsonResponse(result)
    with connection.cursor() as c:
        c.execute('SELECT filename, md5 FROM sync_file WHERE foldername=:foldername',
                  {'foldername': message['foldername']})
        rs = c.fetchall()
        fileInfos = {}
        for fileInfo in rs:
            fileInfos[fileInfo[0]] = fileInfo[1]
        result['fileInfos'] = fileInfos
    return JsonResponse(result)


def releaseLock(request):
    result = {'state': 'ok'}
    message = simplejson.loads(request.body)

    # 签名验证
    verifyResult = rsaUtil.verifyMessage(message)
    if verifyResult != 'ok':
        result['state'] = 'error'
        result['errorInfo'] = verifyResult
        return JsonResponse(result)

    syncLockUtil.releaseLock(message)
    return JsonResponse(result)


def syncFile(request):
    result = {'state': 'ok'}
    message = simplejson.loads(request.body)
    # 签名验证
    verifyResult = rsaUtil.verifyMessage(message)
    if verifyResult != 'ok':
        result['state'] = 'error'
        result['errorInfo'] = verifyResult
        return JsonResponse(result)
    # 文件操作权限验证
    if not privilegeVerify(message):
        result['state'] = 'error'
        result['errorInfo'] = '用户无权限'
        return JsonResponse(result)
    # 文件同步锁获取
    lockResult = syncLockUtil.getLock(message)
    if lockResult != 'ok':
        result['state'] = 'error'
        result['errorInfo'] = lockResult
        return JsonResponse(result)

    folderPath = os.path.join(os.path.abspath('syncFolder'), message['foldername'])
    filePath = os.path.join(folderPath, message['filename'])

    if message['fileOperate'] == 'serverDelete':
        os.remove(filePath)
        with connection.cursor() as c:
            c.execute('DELETE FROM sync_file WHERE foldername=:foldername AND filename =:filename',
                      {'foldername': message['foldername'], 'filename': message['filename']})
    elif message['fileOperate'] == 'update' or message['fileOperate'] == 'create':
        file = open(filePath, "wb+")
        file.write(base64.decodebytes(message['fileData'].encode('utf-8')))
        file.close()
        m = hashlib.md5()  # 创建md5对象
        m.update(base64.decodebytes(message['fileData'].encode('utf-8')))  # 更新md5对象
        md5 = m.hexdigest()  # 返回md5对象
        with connection.cursor() as c:
            c.execute('SELECT filename FROM sync_file WHERE foldername=:foldername AND filename=:filename',
                      {'foldername': message['foldername'], 'filename': message['filename']})
            r = c.fetchone()
            if r is None:
                # 新建文件
                c.execute('INSERT INTO sync_file VALUES(:filename, :foldername, null, null, null, :md5)',
                          {'filename': message['filename'], 'foldername': message['foldername'],
                           'md5': md5})
            else:
                # 更新文件
                c.execute(
                    'UPDATE sync_file SET md5=:md5 WHERE foldername=:foldername AND filename=:filename',
                    {'filename': message['filename'], 'foldername': message['foldername'], 'md5': md5})
        result['fileMd5'] = md5
    elif message['fileOperate'] == 'download':
        file = open(filePath, 'rb')
        fileData = file.read()
        file.close()
        result['fileData'] = base64.encodebytes(fileData).decode('utf-8')
    return JsonResponse(result)


def privilegeVerify(message):
    with connection.cursor() as c:
        c.execute('SELECT privilege FROM user_privilege WHERE username=:username AND foldername=:foldername',
                  {'username': message['username'], 'foldername': message['foldername']})
        r = c.fetchone()
    if r is None:
        return False
    privilege = r[0]
    fileOperate = message['fileOperate']
    if fileOperate == 'serverDelete' and privilege > 0:
        return False
    if (fileOperate == 'create' or fileOperate == 'update'):
        if privilege > 2:
            return False
        with connection.cursor() as c:
            c.execute('SELECT filename FROM sync_file WHERE filename=:filename AND foldername=:foldername',
                      {'filename': message['filename'], 'foldername': message['foldername']})
            r = c.fetchone()
        if r is None and privilege > 1:
            return False
    return True
