from win32comext.shell import shell, shellcon

shell.SHChangeNotify(shellcon.SHCNE_UPDATEDIR,
                     shellcon.SHCNF_PATH | shellcon.SHCNF_FLUSHNOWAIT,
                     bytes(r'D:\dachengyun', 'utf-8'), None)
