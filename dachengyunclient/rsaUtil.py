import rsa
import winreg
import base64
from datetime import datetime


def newkeys():
    pubkey, privkey = rsa.newkeys(1024)
    pubkey = pubkey.save_pkcs1().decode('utf-8')
    privkey = privkey.save_pkcs1().decode('utf-8')
    return pubkey, privkey


def newMessage():
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
    username, index = winreg.QueryValueEx(key, 'username')
    privateKey, index = winreg.QueryValueEx(key, 'privateKey')
    token, index = winreg.QueryValueEx(key, 'token')
    key.Close()

    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography')
    machineGuid, index = winreg.QueryValueEx(key, 'MachineGuid')
    key.Close()

    privateKey = rsa.PrivateKey.load_pkcs1(privateKey)
    now = str(datetime.now())
    message = {
        'username': username,
        'machineGuid': machineGuid,
        'datetime': now,
        'token': int(token),
        'sign': base64.encodebytes(rsa.sign((username + '|' + machineGuid + '|' + now +
                                             '|' + token).encode('utf-8'),
                                            privateKey, 'SHA-1')).decode('utf-8')
    }
    token = str(int(token) + 1)

    key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
    winreg.SetValueEx(key, 'token', 0, winreg.REG_SZ, token)

    key.Close()
    return message
