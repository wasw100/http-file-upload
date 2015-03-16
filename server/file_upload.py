# -*- coding: utf-8 -*-

import zlib, os.path
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, request

app = Flask(__name__)
app.debug = False

#log to file
app.logger.setLevel(logging.INFO)
log_path = os.path.join(os.path.dirname(__file__), 'logs/web.log')
handler = RotatingFileHandler(log_path, maxBytes=10*1024*1024, backupCount=1)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
app.logger.addHandler(handler)


@app.before_request
def before_request():
    #可以做一些权限限制, 比如限制IP
    if not request.headers.getlist('X-Forwarded-For'):
        ip = request.remote_addr
    else:
        ip = request.headers.getlist('X-Forwarded-For')[0]
    if ip not in ['可以上传文件的ip']:
        return 'no permission - %s' % ip


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    ''' if method is GET, can return, but you should upload zlib file
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
        <input type=file name=file><br>
        <input name=path><br>
        <input type=submit value=Upload>
    </form>
    '''
    if request.method == 'POST':
        file_ = request.files['file']
        path = request.form['path']
        app.logger.debug('upload-%s' % path)
        app.logger.info('upload-%s' % path)
        app.logger.error('upload-%s' % path)
        if file_ and path:
            zlib_data = file_.stream.read()
            data = zlib.decompress(zlib_data)
            with open(path, 'wb') as f:
                f.write(data)
            return 'OK, save-%s' % path
        else:
            return 'Error, path-%s' % path

    return 'test'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9877)
