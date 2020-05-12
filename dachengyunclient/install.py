import os
import winreg
import win32api
import win32con
from win32com.server import register
import iconOverlay

key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
winreg.SetValueEx(key, 'path', 0, winreg.REG_SZ, os.getcwd())
winreg.SetValueEx(key, 'dbPath', 0, winreg.REG_SZ, os.path.join(os.getcwd(), 'data.db'))
winreg.SetValueEx(key, 'iconPath', 0, winreg.REG_SZ, os.path.join(os.getcwd(), 'icon'))
winreg.SetValueEx(key, 'serverPath', 0, winreg.REG_SZ, r'http://39.106.114.247:8000/')
winreg.SetValueEx(key, 'fileMaxSize', 0, winreg.REG_SZ, '104857600')
winreg.FlushKey(key)
key.Close()

register.UseCommandLine(iconOverlay.IconOverlayOk)
win32api.RegSetValue(win32api.RegCreateKey(iconOverlay.IconOverlayOk._reg_remove_keys_[0][1],
                                           iconOverlay.IconOverlayOk._reg_remove_keys_[0][0]),
                     None, win32con.REG_SZ,
                     iconOverlay.IconOverlayOk._reg_clsid_)

register.UseCommandLine(iconOverlay.IconOverlaySync)
win32api.RegSetValue(win32api.RegCreateKey(iconOverlay.IconOverlaySync._reg_remove_keys_[0][1],
                                           iconOverlay.IconOverlaySync._reg_remove_keys_[0][0]),
                     None, win32con.REG_SZ,
                     iconOverlay.IconOverlaySync._reg_clsid_)

os.system('taskkill /f /im explorer.exe & start explorer.exe')
