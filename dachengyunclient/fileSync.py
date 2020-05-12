import rsaUtil
import winreg
import requests
import json
import sqlite3
import os
import time
import base64
import hashlib
from win32comext.shell import shell, shellcon


def getSyncFolder():
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
    serverPath, index = winreg.QueryValueEx(key, 'serverPath')
    dbPath, index = winreg.QueryValueEx(key, 'dbPath')
    syncPath, index = winreg.QueryValueEx(key, 'syncPath')
    key.Close()

    message = rsaUtil.newMessage()
    response = requests.post(url=serverPath + 'sync/querySyncFolder/', data=json.dumps(message))
    result = response.json()
    if result['state'] == 'ok':
        conn = sqlite3.connect(dbPath)
        c = conn.cursor()
        for syncFolder in result['syncFolders']:
            try:
                folderPath = os.path.join(syncPath, syncFolder[0])
                if not os.path.exists(folderPath):
                    os.makedirs(folderPath)
                c.execute('INSERT INTO sync_folder VALUES (:foldername, :privilege)',
                          {'foldername': syncFolder[0], 'privilege': syncFolder[1]})
            except:
                continue
            c.close()
            conn.commit()
            conn.close()
        return 'ok'
    else:
        return result['errorInfo']


def getServerFileInfoWithLock(foldername):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
    serverPath, index = winreg.QueryValueEx(key, 'serverPath')
    key.Close()

    message = rsaUtil.newMessage()
    message['foldername'] = foldername
    response = requests.post(url=serverPath + 'sync/queryFileInfoWithLock/', data=json.dumps(message))
    result = response.json()
    if result['state'] == 'ok':
        return 'ok', result['fileInfos']
    else:
        print(result['errorInfo'])
        return result['errorInfo'], None


def releaseLock(foldername):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
    serverPath, index = winreg.QueryValueEx(key, 'serverPath')
    key.Close()
    message = rsaUtil.newMessage()
    message['foldername'] = foldername
    response = requests.post(url=serverPath + 'sync/releaseLock/', data=json.dumps(message))
    result = response.json()
    if result['state'] == 'ok':
        return 'ok'
    else:
        return result['errorInfo']


def timeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)


def getSyncOperateList(foldername):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
    dbPath, index = winreg.QueryValueEx(key, 'dbPath')
    syncPath, index = winreg.QueryValueEx(key, 'syncPath')
    username, index = winreg.QueryValueEx(key, 'username')
    key.Close()

    # 得到数据库文件列表
    dbFileMap = {}
    conn = sqlite3.connect(dbPath)
    c = conn.cursor()
    c.execute('SELECT filename, size, create_time, update_time, md5 FROM sync_file WHERE foldername=:foldername',
              {'foldername': foldername})
    rs = c.fetchall()
    c.close()
    conn.close()
    for fileInfo in rs:
        dbFileMap[fileInfo[0]] = fileInfo[1], fileInfo[2], fileInfo[3], fileInfo[4]
    # 得到硬盘文件列表
    diskFileMap = {}
    folderPath = os.path.join(syncPath, foldername)
    for filename in os.listdir(folderPath):
        # 过滤offic临时文件
        if (filename.startswith('~$')):
            continue
        filePath = os.path.join(folderPath, filename)
        if os.path.isdir(filePath):
            continue
        diskFileMap[filename] = os.path.getsize(filePath), \
                                timeStampToTime(os.path.getctime(filePath)), \
                                timeStampToTime(os.path.getmtime(filePath))
    # 得到服务器文件列表
    state, serverFileMap = getServerFileInfoWithLock(foldername)
    if state != 'ok':
        return state, None
    # 得到本地文件需要向服务器同步列表
    diskOperateMap = {}
    for filename in diskFileMap:
        dbFileInfo = dbFileMap.get(filename)
        if dbFileInfo is None:
            diskOperateMap[filename] = 'create'
        elif dbFileInfo[0] != diskFileMap[filename][0] or dbFileInfo[1] != \
                diskFileMap[filename][1] or dbFileInfo[2] != \
                diskFileMap[filename][2]:
            diskOperateMap[filename] = 'update'
    for filename in dbFileMap:
        diskFileInfo = diskFileMap.get(filename)
        if diskFileInfo is None:
            diskOperateMap[filename] = 'serverDelete'
    # 得到服务器文件需要向本地同步列表
    serverOperateMap = {}
    for filename in serverFileMap:
        dbFileInfo = dbFileMap.get(filename)
        if dbFileInfo is None or (dbFileInfo[3] != serverFileMap[filename]):
            serverOperateMap[filename] = 'download'
    for filename in dbFileMap:
        if serverFileMap.get(filename) is None:
            serverOperateMap[filename] = 'diskDelete'
    # 用户操作权限处理
    conn = sqlite3.connect(dbPath)
    c = conn.cursor()
    c.execute('SELECT privilege FROM sync_folder WHERE foldername=:foldername',
              {'foldername': foldername})
    r = c.fetchone()
    c.close()
    conn.close()
    privilege = int(r[0])
    for filename in list(diskOperateMap.keys()):
        if diskOperateMap[filename] == 'create' and privilege > 1:
            del diskOperateMap[filename]
            if serverOperateMap.get(filename) is None:
                serverOperateMap[filename] = 'diskDelete'
        elif diskOperateMap[filename] == 'update' and serverFileMap.get(filename) \
                is not None and privilege > 2:
            del diskOperateMap[filename]
            if serverOperateMap.get(filename) is None:
                serverOperateMap[filename] = 'download'
        elif diskOperateMap[filename] == 'serverDelete' and serverFileMap.get(filename) \
                is not None and privilege > 0:
            del diskOperateMap[filename]
            if serverOperateMap.get(filename) is None:
                serverOperateMap[filename] = 'download'

    # 冲突处理
    operateMap = {}
    for filename in diskOperateMap:
        serverOperate = serverOperateMap.get(filename)
        if serverOperate is None:
            operateMap[filename] = diskOperateMap[filename]
        elif diskOperateMap[filename] == 'create' or diskOperateMap[filename] == 'update':
            operateMap[filename] = serverOperate
            del serverOperateMap[filename]
            filePath = os.path.join(folderPath, filename)
            os.rename(filePath, filePath + '.conflict.' + username)
        elif diskOperateMap[filename] == 'serverDelete':
            operateMap[filename] = serverOperate
            del serverOperateMap[filename]
    for filename in serverOperateMap:
        operateMap[filename] = serverOperateMap[filename]
    return 'ok', operateMap


def syncFileList(foldername, operateMap):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
    serverPath, index = winreg.QueryValueEx(key, 'serverPath')
    syncPath, index = winreg.QueryValueEx(key, 'syncPath')
    dbPath, index = winreg.QueryValueEx(key, 'dbPath')
    fileMaxSize, index = winreg.QueryValueEx(key, 'fileMaxSize')
    key.Close()
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography')
    key.Close()

    folderPath = os.path.join(syncPath, foldername)

    folderSyncPath = folderPath[len(os.path.dirname(syncPath)):]
    conn = sqlite3.connect(dbPath)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO file_sync_state VALUES(:path, 2)',
                  {'path': folderSyncPath})
    except:
        c.execute('UPDATE file_sync_state SET state=2 WHERE path=:path',
                  {'path': folderSyncPath})
    c.close()
    conn.commit()
    conn.close()
    shell.SHChangeNotify(shellcon.SHCNE_ATTRIBUTES,
                         shellcon.SHCNF_PATH | shellcon.SHCNF_FLUSHNOWAIT,
                         bytes(folderPath, 'gbk'), None)

    for filename in operateMap:
        fileOperate = operateMap[filename]
        filePath = os.path.join(folderPath, filename)
        fileSyncPath = filePath[len(os.path.dirname(syncPath)):]

        conn = sqlite3.connect(dbPath)
        c = conn.cursor()
        try:
            c.execute('INSERT INTO file_sync_state VALUES(:path, 2)',
                      {'path': fileSyncPath})
        except:
            c.execute('UPDATE file_sync_state SET state=2 WHERE path=:path',
                      {'path': fileSyncPath})
        c.close()
        conn.commit()
        conn.close()
        shell.SHChangeNotify(shellcon.SHCNE_ATTRIBUTES,
                             shellcon.SHCNF_PATH | shellcon.SHCNF_FLUSHNOWAIT,
                             bytes(filePath, 'gbk'), None)
        try:
            if fileOperate == 'diskDelete':
                if os.path.exists(filePath):
                    os.remove(filePath)
                conn = sqlite3.connect(dbPath)
                c = conn.cursor()
                c.execute('DELETE FROM sync_file WHERE filename=:filename AND foldername=:foldername',
                          {'filename': filename, 'foldername': foldername})
                c.execute('DELETE FROM file_sync_state WHERE path=:path',
                          {'path': fileSyncPath})
                c.close()
                conn.commit()
                conn.close()
            else:
                message = rsaUtil.newMessage()
                message['foldername'] = foldername
                message['filename'] = filename
                message['fileOperate'] = fileOperate
                if fileOperate == 'update' or fileOperate == 'create':
                    size = os.path.getsize(filePath)
                    if size > int(fileMaxSize):
                        conn = sqlite3.connect(dbPath)
                        c = conn.cursor()
                        c.execute('DELETE FROM file_sync_state WHERE path=:path',
                                  {'path': fileSyncPath})
                        c.close()
                        conn.commit()
                        conn.close()
                        shell.SHChangeNotify(shellcon.SHCNE_ATTRIBUTES,
                                             shellcon.SHCNF_PATH | shellcon.SHCNF_FLUSHNOWAIT,
                                             bytes(filePath, 'gbk'), None)
                        continue

                    file = open(filePath, 'rb')
                    fileData = file.read()
                    file.close()
                    size = os.path.getsize(filePath)
                    ctime = timeStampToTime(os.path.getctime(filePath))
                    mtime = timeStampToTime(os.path.getmtime(filePath))
                    message['fileData'] = base64.encodebytes(fileData).decode('utf-8')
                response = requests.post(url=serverPath + 'sync/syncFile/', data=json.dumps(message))
                result = response.json()
                if result['state'] == 'ok':
                    if fileOperate == 'serverDelete':
                        conn = sqlite3.connect(dbPath)
                        c = conn.cursor()
                        c.execute('DELETE FROM sync_file WHERE filename=:filename AND foldername=:foldername',
                                  {'filename': filename, 'foldername': foldername})
                        c.execute('DELETE FROM file_sync_state WHERE path=:path',
                                  {'path': fileSyncPath})
                        c.close()
                        conn.commit()
                        conn.close()
                    elif fileOperate == 'download':
                        file = open(filePath, "wb+")
                        file.write(base64.decodebytes(result['fileData'].encode('utf-8')))
                        file.close()
                        m = hashlib.md5()  # 创建md5对象
                        m.update(base64.decodebytes(result['fileData'].encode('utf-8')))  # 更新md5对象
                        md5 = m.hexdigest()  # 返回md5对象
                        size = os.path.getsize(filePath)
                        ctime = timeStampToTime(os.path.getctime(filePath))
                        mtime = timeStampToTime(os.path.getmtime(filePath))

                        conn = sqlite3.connect(dbPath)
                        c = conn.cursor()
                        c.execute('SELECT filename FROM sync_file WHERE foldername=:foldername AND filename=:filename',
                                  {'foldername': foldername, 'filename': filename})
                        r = c.fetchone()
                        if r is None:
                            # 新建文件
                            c.execute(
                                'INSERT INTO sync_file VALUES(:filename, :foldername, :size, :ctime, :mtime, :md5)',
                                {'filename': filename, 'foldername': foldername, 'size': size,
                                 'md5': md5, 'ctime': ctime, 'mtime': mtime})
                        else:
                            # 更新文件
                            c.execute(
                                'UPDATE sync_file SET size=:size, create_time=:ctime, update_time=:mtime, md5=:md5 WHERE foldername=:foldername AND filename=:filename',
                                {'filename': filename, 'foldername': foldername, 'size': size,
                                 'md5': md5, 'ctime': ctime, 'mtime': mtime})
                        c.execute('UPDATE file_sync_state SET state=1 WHERE path=:path',
                                  {'path': fileSyncPath})
                        c.close()
                        conn.commit()
                        conn.close()
                    elif fileOperate == 'update' or fileOperate == 'create':
                        md5 = result['fileMd5']
                        conn = sqlite3.connect(dbPath)
                        c = conn.cursor()
                        c.execute('SELECT filename FROM sync_file WHERE foldername=:foldername AND filename=:filename',
                                  {'foldername': foldername, 'filename': filename})
                        r = c.fetchone()
                        if r is None:
                            # 新建文件
                            c.execute(
                                'INSERT INTO sync_file VALUES(:filename, :foldername, :size, :ctime, :mtime, :md5)',
                                {'filename': filename, 'foldername': foldername, 'size': size,
                                 'md5': md5, 'ctime': ctime, 'mtime': mtime})
                        else:
                            # 更新文件
                            c.execute(
                                'UPDATE sync_file SET size=:size, create_time=:ctime, update_time=:mtime, md5=:md5 WHERE foldername=:foldername AND filename=:filename',
                                {'filename': filename, 'foldername': foldername, 'size': size,
                                 'md5': md5, 'ctime': ctime, 'mtime': mtime})
                        c.execute('UPDATE file_sync_state SET state=1 WHERE path=:path',
                                  {'path': fileSyncPath})
                        c.close()
                        conn.commit()
                        conn.close()
                else:
                    conn = sqlite3.connect(dbPath)
                    c = conn.cursor()
                    c.execute('DELETE FROM file_sync_state WHERE path=:path',
                              {'path': fileSyncPath})
                    c.close()
                    conn.commit()
                    conn.close()

        except:
            conn = sqlite3.connect(dbPath)
            c = conn.cursor()
            c.execute('DELETE FROM file_sync_state WHERE path=:path',
                      {'path': fileSyncPath})
            c.close()
            conn.commit()
            conn.close()
        shell.SHChangeNotify(shellcon.SHCNE_ATTRIBUTES,
                             shellcon.SHCNF_PATH | shellcon.SHCNF_FLUSHNOWAIT,
                             bytes(filePath, 'gbk'), None)
    conn = sqlite3.connect(dbPath)
    c = conn.cursor()
    c.execute('UPDATE file_sync_state SET state=1 WHERE path=:path',
              {'path': folderSyncPath})
    c.close()
    conn.commit()
    conn.close()
    shell.SHChangeNotify(shellcon.SHCNE_ATTRIBUTES,
                         shellcon.SHCNF_PATH | shellcon.SHCNF_FLUSHNOWAIT,
                         bytes(folderPath, 'gbk'), None)


def releaseLock(foldername):

    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
    serverPath, index = winreg.QueryValueEx(key, 'serverPath')
    username, index = winreg.QueryValueEx(key, 'username')
    key.Close()
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography')
    machineGuid, index = winreg.QueryValueEx(key, 'MachineGuid')
    key.Close()

    message = rsaUtil.newMessage()
    message['username'] = username
    message['foldername'] = foldername
    message['machineGuid'] = machineGuid
    requests.post(url=serverPath + 'sync/releaseLock/', data=json.dumps(message))