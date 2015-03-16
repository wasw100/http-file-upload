# -*- coding: utf-8 -*-

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from file_upload import app

http_server = HTTPServer(WSGIContainer(app))
http_server.listen(9877)
IOLoop.instance().start()
