## server install

- server使用sublime开发, 运行在tornadoserver下

- 在启动目录创建logs文件夹

启动:

    python tornado_app.py

- 测试能否使用

在浏览器访问:

    http://ip:port/

出现test则可以访问

- 如果使用supervisor启动

 可以像下面配置(替换成自己的路径): file-upload-server.ini

    [program:file-upload-server]
    environment=PATH="/home/ubuntu/.virtualenvs/file-upload-server/bin/"
    user=ubuntu
    command=python /var/code/file-upload-server/tornado_app.py
    autostart=true

## sublime plugin

- 复制到sublime插件文件夹

## vim 插件

- 复制upload-text.vim 到 $HOME/.vim/plugin/ 文件夹下


## 插件配置, 对应配置好就可:

- vim的配置, key是配置的一个名字, 随便起, 最下面可以设置快捷上传命令

    'test'{
        'upload_url': 'http://{server ip}:{server port}/',
        'local_prefix': '{local path prefix}',
        'remote_prefix': '{server path prefix}',
    },

- sublime的设置, 在插件Menu下设置, 可以复制Default的配置到User中修改, 重新安装插件, 配置不消失:




