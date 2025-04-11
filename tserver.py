from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
import tornado.web

def tornado_server(app, port=5000):
    wsgi_app = tornado.wsgi.WSGIContainer(app)
    server = tornado.httpserver.HTTPServer(wsgi_app)
    server.listen(port, address="0.0.0.0")
    print("Tornado API listening on port ", port)
    tornado.ioloop.IOLoop.current().start()