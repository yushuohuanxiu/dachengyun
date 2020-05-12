import tkinter
import userOperate
import tkinter.filedialog
import tkinter.messagebox


def showLoginWin():
    win = tkinter.Tk()
    win.title("dachengyunClinet")
    ww = 280
    wh = 130
    win.maxsize(ww, wh)
    win.minsize(ww, wh)
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry("+%d+%d" % ((sw - ww) / 2, (sh - wh) / 2))

    usernameLabel = tkinter.Label(win, text="用户名：")
    usernameLabel.place(x=30, y=20)
    passwordLabel = tkinter.Label(win, text="密码：")
    passwordLabel.place(x=42, y=50)
    username = tkinter.Entry(win)
    username.place(x=100, y=20)
    password = tkinter.Entry(win, show="*")
    password.place(x=100, y=50)
    button = tkinter.Button(win, text="登录", command=lambda: login(username.get(), password.get(), win))
    button.place(x=0, y=100, width=280)

    win.mainloop()


def login(username, password, win):
    result = userOperate.register(username, password)
    if result != 'ok':
        tkinter.messagebox.showerror("dachengyunClinet", result)
    else:
        tkinter.messagebox.showinfo("dachengyunClinet", "操作成功")
        win.destroy()


def showSyncPathSetWin():
    win = tkinter.Tk()
    win.title("dachengyunClinet")
    ww = 360
    wh = 100
    win.maxsize(ww, wh)
    win.minsize(ww, wh)
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    win.geometry("+%d+%d" % ((sw - ww) / 2, (sh - wh) / 2))

    syncPathSetLabel = tkinter.Label(win, text="同步目录：")
    syncPathSetLabel.place(x=30, y=20)
    e = tkinter.Variable()
    syncPathSet = tkinter.Entry(win, textvariable=e)
    syncPathSet.place(x=100, y=20, width=160)
    selectButton = tkinter.Button(win, text="浏览", command=lambda: selectPath(e))
    selectButton.place(x=270, y=18, width=50, height=26)
    button = tkinter.Button(win, text="确定", command=lambda: pathSet(syncPathSet.get(), win))
    button.place(x=0, y=70, width=360)
    win.mainloop()


def selectPath(e):
    path = tkinter.filedialog.askdirectory()
    path = path.replace('/', '\\')
    if path is not None and path != '':
        e.set(path)


def pathSet(path, win):
    result = userOperate.syncPathSet(path)
    if result != 'ok':
        tkinter.messagebox.showerror("dachengyunClinet", result)
    else:
        tkinter.messagebox.showinfo("dachengyunClinet", "操作成功")
        win.destroy()
