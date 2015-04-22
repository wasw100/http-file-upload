# -*- coding: utf-8 -*-

import sublime
import sublime_plugin
import os.path
import sys
import threading
import time
import functools
import zlib
import urlparse
import mimetypes
import codecs
try:
    import urllib.request as urllib2
except:
    import urllib2

_ver = sys.version_info

is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)
is_before_py26 = (is_py2 and _ver[1] <= 6)

if is_py2:
    text_type = unicode
elif is_py3:
    text_type = str

if is_before_py26:
    from StringIO import StringIO as BytesIO
else:
    from io import BytesIO

writer = codecs.lookup('utf-8')[3]


class FileUploadCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message(u'开始上传 %s' % self.view.file_name())
        print(self.view.file_name())
        file_name = str(self.view.file_name())
        config_key = None

        self.settings = sublime.load_settings('FileUpload.sublime-settings')
        local_prefix = self.settings.get('local_prefix')
        if not local_prefix:
            msg = 'Setting中没有找到local_prefix, 在FileUpload->Settings设置'
            sublime.status_message(msg)
        else:
            for key in local_prefix:
                real_key = os.path.realpath(key)
                if file_name.startswith(real_key):
                    config_key = key
                    break

            if config_key is not None:
                upload_config = local_prefix[config_key]
                upload_url = upload_config['upload_url']
                upload_url = handle_url(upload_url)
                local_prefix = os.path.realpath(config_key)
                remote_prefix = upload_config['remote_prefix']
                t = UploadThread(upload_url, file_name,
                                 local_prefix, remote_prefix)
                t.start()
            else:
                msg = (u'没有匹配的配置文件, 可以ctrl+`在Console复制路径'
                       u'然后在FileUpload->Settings-User设置')
                sublime.status_message(msg)


def handle_url(url):
    """如果url的path是'', 后面加上'/'"""
    parsed = urlparse.urlparse(url)
    if not parsed.path:
        parsed = parsed._replace(path='/')
    return parsed.geturl()


def show_finish(url, remote_path, use_time):
    msg = u'上传成功, 服务器-{0}, 路径-{1}, 使用-{2}ms' \
        .format(url, remote_path, use_time)
    sublime.status_message(msg)


class UploadThread(threading.Thread):

    def __init__(self, upload_url, file_name, local_prefix, remote_prefix):
        self.upload_url = upload_url
        self.file_name = file_name

        local_prefix_len = len(local_prefix)
        if local_prefix.endswith('/'):
            local_prefix_len -= 1
        remote_path = os.path.join(remote_prefix,
                                   file_name[local_prefix_len+1:])

        self.remote_path = remote_path.replace('\\', '/')
        super(UploadThread, self).__init__()

    def run(self):
        zlib_data = zlib.compress(open(self.file_name, 'rb').read(), 5)
        files = dict(file=zlib_data)
        begin = time.time()
        try:
            fields = [('path', self.remote_path)]
            files = [('file', 'en.tmp', zlib_data)]

            content_type, body = encode_multipart_formdata(fields, files)
            headers = {
                'Content-Type': content_type,
                'Content-Length': str(len(body))
            }

            # 如果需要代理, 将下面的注释去掉
            # print self.upload_url
            # proxy = urllib2.ProxyHandler({'http': '127.0.0.1:8888'})
            # opener = urllib2.build_opener(proxy)
            # urllib2.install_opener(opener)

            request = urllib2.Request(self.upload_url, body, headers)
            print(urllib2.urlopen(request).read())

            use_time = (time.time() - begin) * 1000
            callback = functools.partial(show_finish, self.upload_url,
                                         self.remote_path, use_time)
            sublime.set_timeout(callback, 0)
        except Exception as e:
            msg = u'上传失败, 确认服务器-{0} 可以访问,\n 错误信息:{1}' \
                .format(self.upload_url, e)
            sublime.error_message(msg)
            raise e


# for gen upload data
# from http://code.activestate.com/recipes/146306/
def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    # BOUNDARY = mimetools.choose_boundary()
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = b'\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        template = 'Content-Disposition: form-data; name="{0}"; filename="{1}"'
        L.append(template.format(key, filename))
        L.append('Content-Type: %s' % get_content_type(filename))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = BytesIO()
    for line in L:
        if isinstance(line, text_type):
            writer(body).write(line)
        else:
            body.write(line)
        body.write(CRLF)

    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body.getvalue()


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
