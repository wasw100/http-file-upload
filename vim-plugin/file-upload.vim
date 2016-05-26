if !(has('python') || has('python3'))
    echo "Error: Required vim compiled with +python"
    finish
endif

" vim comments start with a double quote.
" Function definition is VimL. We can mix VimL and Python in function
" definition.
function! FileUpload(arg)

" We start the python code like the next line.

python << EOF

import os.path
import sys
import threading
import time
import functools
import zlib
import mimetypes
import codecs

try:
    import urllib.request as urllib2
except:
    import urllib2

_ver = sys.version_info

is_py2 = (_ver[0] == 2)
is_py3 = (_ver[0] == 3)

is_before_py26 = (is_py2 and _ver[1]<=6)

if is_py2:
    from StringIO import StringIO
    text_type = unicode
elif is_py3:
    from io import StringIO
    text_type = str

if is_before_py26:
    from StringIO import StringIO as BytesIO
else:
    from io import BytesIO
    writer = codecs.lookup('utf-8')[3]

import vim


#for gen upload data
#from http://code.activestate.com/recipes/146306/
def encode_multipart_formdata(fields, files):
    """
        fields is a sequence of (name, value) elements for regular form fields.
        files is a sequence of (name, filename, value) elements for data to be uploaded as files
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
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
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

    
def upload(conf_key, file_path, upload_url, local_prefix, remote_prefix):
    zlib_data = zlib.compress(open(file_path, 'rb').read(), 5)
    remote_path = os.path.join(remote_prefix, file_path[len(local_prefix)+1:]) 

    fields = [('path', remote_path)]
    files = [('file', 'tmp.txt', zlib_data)]

    content_type, body = encode_multipart_formdata(fields, files)

    headers = {
        'Content-Type': content_type,
        'Content-Length': str(len(body)),
    }
    request = urllib2.Request(upload_url, body, headers)
    begin = time.time()
    body = urllib2.urlopen(request, timeout=5).read()
    use_time = (time.time() - begin) * 1000
    print('OK, {0}, {1} ms, {2}'.format(conf_key, int(use_time), body))


conf_dict = {
    'test': {
        'upload_url': 'http://{server ip}:{server port}/',
        'local_prefix': '{local path prefix}',
        'remote_prefix': '{server path prefix}',
    },
}

vim.command('w')

file_path = vim.current.buffer.name
conf_key = vim.eval('a:arg')
conf = conf_dict.get(conf_key)
if conf and file_path.startswith(conf['local_prefix']):
    upload(conf_key, file_path, conf['upload_url'], conf['local_prefix'], conf['remote_prefix'])
else:
    msg = 'Error, key-{0}, file-{1}'.format(conf_key, file_path) 
    print(msg)

EOF

" Here the python code is closed. We can continue writing VimL or python again

endfunction

command! -nargs=0 W call FileUpload('test')
