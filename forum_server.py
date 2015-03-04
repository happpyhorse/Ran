#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os

import tornado.httpserver
import tornado.httpclient
import tornado.web
import tornado.options
from tornado.options import define, options, parse_command_line

import init_db

define('port', default=4812, help='given port', type=int)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('test_emmet.html')

    def post(self):
        pass

class NewHandler(tornado.web.RequestHandler):
    def get(self):
        print 'receive a get request - New'
        uId = self.get_argument('id')
        fName = self.get_argument('firstname')
        lName = self.get_argument('lastname')
        init_db.insert_data(uId, fName, lName)
        init_db.query_data()
        self.write('Insert into db successfully')
        pass

    def post(self):
        pass

def send(url, data):
    client = tornado.httpclient.HTTPClient()
    url = url
    body = data
    headers = {
        'Content-Type': 'application/json',
        'Connection': 'Keep-Alive',
    }
    request = tornado.httpclient.HTTPRequest(
            url,
            method = 'POST',
            body = body,
            headers = headers
            )
    response = client.fetch(request)
    return response

def main():
    parse_command_line()
    settings = {
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    }
    application = tornado.web.Application([
            (r'/', MainHandler),
            (r'/new', NewHandler),
            ], **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
