import win32com.server.register
import iconOverlay
import winreg
import os
import sqlite3

win32com.server.register.UnregisterClasses(iconOverlay.IconOverlayOk)
win32com.server.register.UnregisterClasses(iconOverlay.IconOverlaySync)
key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
dbPath, index = winreg.QueryValueEx(key, 'dbPath')
key.Close()

conn = sqlite3.connect(dbPath)
c = conn.cursor()
c.execute('DELETE FROM sync_folder')
c.execute('DELETE FROM sync_file')
c.execute('DELETE FROM file_sync_state')
c.close()
conn.commit()
conn.close()

winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
os.system('taskkill /f /im explorer.exe & start explorer.exe')
