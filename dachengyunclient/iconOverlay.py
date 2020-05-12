import os
import winreg
import sqlite3
import winerror
import win32con
from win32comext.shell import shell, shellcon


class IconOverlayOk:
    """
    图标覆盖组件
    windows shell下的IShellIconOverlayIdentifier接口用于实现图标覆盖功能
    用python实现功能需要以下步骤
    1. 使用pywin32，编写python class实现windows com组件
    2. 将组件注册到windows系统
    3. 在注册表中添加图标覆盖组件的项
    4. 重启explorer.exe

    当windows文件资源管理器浏览文件时
    1. explorer会为每一个当前要显示的文件调用IShellIconOverlayIdentifier的IsMemberOf方法判断是否需要对文件做处理
    2. 如果IsMemberOf返回winerror.S_OK，系统会继续调用GetOverlayInfo方法获取要叠加的图标文件
    3. 操作系统负责将GetOverlayInfo返回的图标叠加到文件原有图标上

    _reg_remove_keys_: 卸载组件时，需要同时删除的注册表项

    """
    _reg_clsid_ = '{EA258179-A91D-45F9-A237-FC92A5290423}'
    _reg_progid_ = 'SUN.PythonPackagesOverlayHandlerOK'
    _reg_desc_ = 'Icon Overlay Handler to indicate Python packages'
    _public_methods_ = ['GetOverlayInfo', 'GetPriority', 'IsMemberOf']
    _com_interfaces_ = [shell.IID_IShellIconOverlayIdentifier]
    _reg_remove_keys_ = [(
        r'Software\Microsoft\Windows\CurrentVersion\Explorer\ShellIconOverlayIdentifiers\     PyPackageOverlay1',
        win32con.HKEY_LOCAL_MACHINE)]

    def GetOverlayInfo(self):
        """
        获取要叠加的图标文件位置
        从注册表获取图标文件路径iconPath
        :return:
        """
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
        iconPath, index = winreg.QueryValueEx(key, 'iconPath')
        key.Close()
        return os.path.join(iconPath, 'Ok.ico'), 0, shellcon.ISIOI_ICONFILE

    def GetPriority(self):
        return 1

    def IsMemberOf(self, fname, attributes):
        """
        判断是否对文件进行图标覆盖

        从注册表读取同步文件夹路径syncPath、sqlite数据库文件路径dbPath
        如果当前是syncPath下的文件，则到db查询文件同步状态
        根据文件同步状态判断是否需要图标覆盖
        :param fname:
        :param attributes:
        :return:
        """
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
        syncPath, index = winreg.QueryValueEx(key, 'syncPath')
        dbPath, index = winreg.QueryValueEx(key, 'dbPath')
        key.Close()
        if fname.startswith(syncPath):
            filePath = fname[len(os.path.dirname(syncPath)):]
            conn = sqlite3.connect(dbPath)
            c = conn.cursor()
            c.execute('SELECT state FROM file_sync_state WHERE path=:filePath', {'filePath': filePath})
            r = c.fetchone()
            c.close()
            conn.close()
            if r is not None and r[0] == 1:
                return winerror.S_OK
        return winerror.E_FAIL


class IconOverlaySync:
    _reg_clsid_ = '{EA258179-A92D-45F9-A237-FC92A5290423}'
    _reg_progid_ = 'SUN.PythonPackagesOverlayHandlerSync'
    _reg_desc_ = 'Icon Overlay Handler to indicate Python packages'
    _public_methods_ = ['GetOverlayInfo', 'GetPriority', 'IsMemberOf']
    _com_interfaces_ = [shell.IID_IShellIconOverlayIdentifier]
    _reg_remove_keys_ = [(
        r'Software\Microsoft\Windows\CurrentVersion\Explorer\ShellIconOverlayIdentifiers\     PyPackageOverlay2',
        win32con.HKEY_LOCAL_MACHINE)]

    def GetOverlayInfo(self):
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
        iconPath, index = winreg.QueryValueEx(key, 'iconPath')
        key.Close()
        return os.path.join(iconPath, 'Sync.ico'), 0, shellcon.ISIOI_ICONFILE

    def GetPriority(self):
        return 2

    def IsMemberOf(self, fname, attributes):

        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r'Software\Dachengyun')
        syncPath, index = winreg.QueryValueEx(key, 'syncPath')
        dbPath, index = winreg.QueryValueEx(key, 'dbPath')
        key.Close()
        if fname.startswith(syncPath):
            filePath = fname[len(os.path.dirname(syncPath)):]
            conn = sqlite3.connect(dbPath)
            c = conn.cursor()
            c.execute('SELECT state FROM file_sync_state WHERE path=:filePath',
                      {'filePath': filePath})
            r = c.fetchone()
            c.close()
            conn.close()
            if r is not None and r[0] == 2:
                return winerror.S_OK
        return winerror.E_FAIL
