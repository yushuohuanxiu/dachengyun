from django.db import connection
import rsa
import base64


def verifyMessage(message):
    with connection.cursor() as c:
        c.execute('SELECT public_key, token FROM client WHERE username=:username AND machine_guid=:machineGuid',
                  {'username': message['username'], 'machineGuid': message['machineGuid']})
        r = c.fetchone()
    if r is None:
        return '终端不存在'
    if r[1] >= message['token']:
        return 'token已失效'

    with connection.cursor() as c:
        c.execute('UPDATE client SET token=:token WHERE username=:username AND machine_guid=:machineGuid',
                  {'token': message['token'], 'username': message['username'], 'machineGuid': message['machineGuid']})
    try:
        publicKey = rsa.PublicKey.load_pkcs1(r[0])
        rsa.verify((message['username'] + '|' + message['machineGuid'] + '|'
                    + message['datetime'] + '|' + str(message['token'])).encode('utf-8'),
                   base64.decodebytes(message['sign'].encode('utf-8')), publicKey)
    except:
        return '验签失败'
    return 'ok'
