# -*- coding: utf-8 -*-
from django.conf import settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': '47chats',
        'USER': 'root',
        'PASSWORD': '!1ebet2@',
    }
}
settings.configure(DATABASES=DATABASES)

from django.db.models import *
class Message(Model):
    body = TextField()
    time = DateTimeField()
    user = CharField(max_length=100)
    class Meta:
    	ordering = ["-time"]
    	app_label = '47chats'
    	db_table = 'message'

from os import path as op
import tornado.web
import tornadio
import tornadio.router
import tornadio.server
from datetime import *

ROOT = op.normpath(op.dirname(__file__))

class IndexHandler(tornado.web.RequestHandler):
    """Regular HTTP handler to serve the chatroom page"""
    def get(self):
        self.render("index.html", messages=Message.objects.all()[:50])

class ChatConnection(tornadio.SocketConnection):
    # Class level variable
    participants = set()

    def on_open(self, *args, **kwargs):
        self.participants.add(self)
        for p in self.participants:
        	p.send({"user": u"Групповой чатик", "body": u"В чат вошел еще один Борис =)", "time": datetime.now().strftime('%Y-%m-%d: %H:%M:%S')})

    def on_message(self, message):
    	msg = Message(body=message["body"], time=datetime.now(), user=message["user"])
    	msg.save()
    	message["time"] = msg.time.strftime('%Y-%m-%d: %H:%M:%S')
        for p in self.participants:
            p.send(message)

    def on_close(self):
        self.participants.remove(self)
        for p in self.participants:
            p.send({"user": u"Групповой чатик", "body": u"Борис ушел", "time": datetime.now().strftime('%Y-%m-%d: %H:%M:%S')})

#use the routes classmethod to build the correct resource
ChatRouter = tornadio.get_router(ChatConnection)

#configure the Tornado application
application = tornado.web.Application(
    [(r"/", IndexHandler), ChatRouter.route()],
    enabled_protocols = ['websocket',
                         'flashsocket',
                         'xhr-multipart',
                         'xhr-polling'],
    flash_policy_port = 843,
    flash_policy_file = op.join(ROOT, 'flashpolicy.xml'),
    socket_io_port = 8001
)

if __name__ == "__main__":
	#import logging
	#logging.getLogger().setLevel(logging.DEBUG)
	application.listen(8000)
	tornadio.server.SocketServer(application)
