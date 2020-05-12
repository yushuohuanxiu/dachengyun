import threading
from datetime import datetime
from django.db import connection


def getLock(message):
    username = message['username']
    machineGuid = message['machineGuid']
    foldername = message['foldername']
    lock = threading.Lock()
    lock.acquire()
    with connection.cursor() as c:
        c.execute('SELECT username, machine_guid, lock_time FROM sync_lock WHERE foldername=:foldername',
                  {'foldername': foldername})
        r = c.fetchone()
        if r is None:
            # 成功获得同步锁
            c.execute('INSERT INTO sync_lock VALUES (:foldername, :username, :machineGuid, :now)',
                      {'foldername': foldername, 'username': username, 'machineGuid': machineGuid
                          , 'now': datetime.now()})
        elif r[0] == username and r[1] == machineGuid:
            # 成功获得同步锁
            c.execute('UPDATE sync_lock SET lock_time=:now WHERE foldername=:foldername',
                      {'foldername': foldername, 'now': datetime.now()})
        elif (datetime.now() - datetime.fromisoformat(r[2])).total_seconds() > 300:
            # 前一个用户5分钟没有请求，取消其同步锁
            c.execute(
                'UPDATE sync_lock SET username=:username, machine_guid = :machineGuid, lock_time=:now WHERE foldername=:foldername',
                {'foldername': foldername, 'username': username, 'machineGuid': machineGuid
                    , 'now': datetime.now()})
        else:
            lock.release()
            return '同步锁被占用，获取失败'
    connection.commit()
    lock.release()
    return 'ok'


def releaseLock(message):
    username = message['username']
    machineGuid = message['machineGuid']
    foldername = message['foldername']
    with connection.cursor() as c:
        c.execute(
            'DELETE FROM sync_lock WHERE foldername=:foldername AND '
            'username=:username AND machine_guid=:machineGuid',
            {'foldername': foldername, 'username': username, 'machineGuid': machineGuid})
    return 'ok'
