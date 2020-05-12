import os
import winreg
import graphic
import fileSync
import time
import sqlite3
from win32comext.shell import shell, shellcon


def main():
    username = None
    syncPath = None

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
        username, index = winreg.QueryValueEx(key, 'username')
        key.Close()
    except:
        None
    if username is None:
        graphic.showLoginWin()
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
        username, index = winreg.QueryValueEx(key, 'username')
        syncPath, index = winreg.QueryValueEx(key, 'syncPath')
        key.Close()
    except:
        None
    if username is not None and syncPath is None:
        graphic.showSyncPathSetWin()

    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
        username, index = winreg.QueryValueEx(key, 'username')
        syncPath, index = winreg.QueryValueEx(key, 'syncPath')
        key.Close()
    except:
        None
    if username is not None and syncPath is not None:
        fileSync.getSyncFolder()
        while True:
            syncLoop()
            time.sleep(10)


def syncLoop():
    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
    dbPath, index = winreg.QueryValueEx(key, 'dbPath')
    syncPath, index = winreg.QueryValueEx(key, 'syncPath')
    key.Close()

    conn = sqlite3.connect(dbPath)
    c = conn.cursor()
    try:
        c.execute('INSERT INTO file_sync_state VALUES(:path, 2)',
                  {'path': os.path.basename(syncPath)})
    except:
        c.execute('UPDATE file_sync_state SET state=2 WHERE path=:path',
                  {'path': os.path.basename(syncPath)})
    c.execute('SELECT foldername FROM sync_folder')
    rs = c.fetchall()
    c.close()
    conn.commit()
    conn.close()
    shell.SHChangeNotify(shellcon.SHCNE_ATTRIBUTES,
                         shellcon.SHCNF_PATH | shellcon.SHCNF_FLUSHNOWAIT,
                         bytes(syncPath, 'gbk'), None)
    for foldername in rs:
        state, operateMap = fileSync.getSyncOperateList(foldername[0])
        if state == 'ok':
            fileSync.syncFileList(foldername[0], operateMap)
        fileSync.releaseLock(foldername[0])
    conn = sqlite3.connect(dbPath)
    c = conn.cursor()
    c.execute('UPDATE file_sync_state SET state=1 WHERE path=:path',
              {'path': os.path.basename(syncPath)})
    c.execute('SELECT foldername FROM sync_folder')
    c.close()
    conn.commit()
    conn.close()
    shell.SHChangeNotify(shellcon.SHCNE_ATTRIBUTES,
                         shellcon.SHCNF_PATH | shellcon.SHCNF_FLUSHNOWAIT,
                         bytes(syncPath, 'gbk'), None)


if __name__ == '__main__':
    main()
