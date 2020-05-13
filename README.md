# dachengyun
大成云是一个同步盘应用，包括客户端和服务器端应用，前后端都基于python和sqlite开发，提供多用户多终端之间的文件同步支持，服务器端提供完善的权限管理界面可以控制用户的同步权限与终端数量
| 项目        | 说明   |
| ------------- | ------------- |
| dachengyunclient| 客户端应用 |
| dachengyunsite | 服务器端应用 |
| dachengyunfrontapp| 服务器端web界面工程 |

### dachengyunclient-客户端应用
##### install.py
应用初始化脚本，将应用路径、服务器端应用访问地址、同步文件最大限制等信息初始化到windows注册表。<br/>
然后将iconOverlay组件注册到windows shell实现同步目录下的文件同步状态图标叠加显示功能（类似于坚果云和oneDriver的同步文件状态图标更改）。
最后重启explorer.exe进程，用于使刚刚注册的iconOverlay组件生效。
##### uninstall.py
应用卸载脚本，卸载iconOverlay组件，删除注册表项，删除数据库数据，最后重启explorer.exe进程。
##### run.py
应用启动脚本，初次运行会有图形界面提供用户登录（终端注册）与同步目录设置，用户、同步文件夹、权限需要提前在服务器端管理界面添加。
用户密码只在首次用户登录时有效，成功登录后密码即失效，用户无法在另一终端再次登录（用户首次登陆时验证密码，密码验证通过后使用rsa密钥代替用户密码进行以后的身份认证和安全保护，密码在登陆成功后即失效），以此限制同一用户终端数量，用户如需使用多终端，需要在服务器端管理界面重新生成密码，为生成一个密码可注册一个新终端，注册多个终端要多次重复操作。
应用启动后，会以10秒间隔重复做文件同步操作（可以修改代码更改轮询间隔）。
##### fileSync.py
文件同步脚本，主要用来支持文件同步功能。
getSyncFolder方法在应用启动时执行一次，用于访问服务器端应用，获取用户的同步文件夹与权限列表。
getSyncOperateList方法分析同步文件夹下的文件状态，先分析此次同步开始与上次同步完成之间服务器端的文件更改与本地文件更改，然后将服务器端文件更改与本地文件更改合并得到此次文件同步需要进行的文件操作列表，中间还有用户同步权限判断与处理。
syncFileList遍历上一步得到的文件操作列表，然后依次与服务器通信进行文件同步操作，同步过程中同时进行文件iconOverlay图标覆盖的状态更改。
