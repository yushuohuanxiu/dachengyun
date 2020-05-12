import requests
import winreg
import json
import os
import rsaUtil


def register(username, password):
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
    serverPath, index = winreg.QueryValueEx(key, 'serverPath')
    key.Close()
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'SOFTWARE\Microsoft\Cryptography')
    machineGuid, index = winreg.QueryValueEx(key, 'MachineGuid')
    key.Close()
    publicKey, privateKey = rsaUtil.newkeys()
    data = {
        'username': username,
        'password': password,
        'machineGuid': machineGuid,
        'publicKey': publicKey
    }
    response = requests.post(url=serverPath + 'user/register/', data=json.dumps(data))
    result = response.json()
    if result['state'] == 'ok':
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
        winreg.SetValueEx(key, 'username', 0, winreg.REG_SZ, username)
        winreg.SetValueEx(key, 'privateKey', 0, winreg.REG_SZ, privateKey)
        winreg.SetValueEx(key, 'token', 0, winreg.REG_SZ, str(1))
        return 'ok'
    else:
        return result['errorInfo']


def syncPathSet(syncPath):
    if os.path.isdir(syncPath) and not os.listdir(syncPath):
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
        winreg.SetValueEx(key, 'syncPath', 0, winreg.REG_SZ, syncPath)
        key.Close()
        return 'ok'
    return '请选择一个空文件夹作为同步目录'
