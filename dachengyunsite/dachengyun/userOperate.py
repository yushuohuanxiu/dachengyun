from django.http import JsonResponse
from django.db import connection
import simplejson


def register(request):
    result = {'state': 'ok'}
    message = simplejson.loads(request.body)

    with connection.cursor() as c:
        c.execute('SELECT username FROM user WHERE username=:username AND password=:password',
                  {'username': message['username'], 'password': message['password']})
        r = c.fetchone()
    if r is None or message['password'] == '':
        result['state'] = 'error'
        result['errorInfo'] = '用户名或密码错误'
        return JsonResponse(result)
    with connection.cursor() as c:
        c.execute('SELECT username FROM client WHERE username=:username AND machine_guid=:machineGuid',
                  {'username': message['username'], 'machineGuid': message['machineGuid']})
        r = c.fetchone()
    if r is not None:
        result['state'] = 'error'
        result['errorInfo'] = '终端已存在'
        return JsonResponse(result)
    with connection.cursor() as c:
        c.execute('INSERT INTO client VALUES (:username, :machineGuid, :publicKey, 0)',
                  {'username': message['username'], 'machineGuid': message['machineGuid']
                      , 'publicKey': message['publicKey']})
        c.execute('UPDATE user SET password=:password WHERE username=:username',
                  {'username': message['username'], 'password': ''})
    return JsonResponse(result)
