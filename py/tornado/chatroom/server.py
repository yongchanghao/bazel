"""
WebSocker Handler
"""

import json
import os
from hashlib import md5 as _md5
from time import time_ns

from tornado import websocket, web, ioloop

global_room_rid_mapping = dict()
global_user_uid_mapping = dict()
global_handler_session_mapping = dict()


def md5(namespace: str, name: str):
    return _md5((_md5(namespace.encode("utf8")).hexdigest() + name).encode('utf8')).hexdigest()


class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        if self.get_cookie("user") not in global_user_uid_mapping.keys():
            self.clear_cookie("user")
            return None
        return self.get_cookie("user")


class User:
    def __init__(self, username: str, uid: str):
        self.username = username
        self.uid = uid
        global_user_uid_mapping[uid] = username


class Message(dict):
    def __init__(self, sender_uid: str, content: str):
        super(Message, self).__init__()
        self["timestamp"] = time_ns()
        self["username"] = global_user_uid_mapping[sender_uid]
        self["content"] = content


class Session:
    def __init__(self, uid: str, rid: str, handler: websocket.WebSocketHandler):
        self.uid = uid
        self.rid = rid
        self.handler = handler
        global_handler_session_mapping[handler] = self


class Room:
    def __init__(self, name: str):
        self.rid = md5("room", name)
        self.name = name
        self.online_sessions = []
        self.message_list = []
        self.users_online_range = dict()
        global_room_rid_mapping[self.rid] = self

    def user_join(self, uid: str, handler: websocket.WebSocketHandler):
        self.online_sessions.append(Session(rid=self.rid, uid=uid, handler=handler))

    def user_leave(self, uid: str, handler: websocket.WebSocketHandler, online_range: tuple):
        self.online_sessions.remove(global_handler_session_mapping[handler])
        if uid not in self.users_online_range.keys():
            self.users_online_range[uid] = []
        self.users_online_range[uid].append(online_range)
        del global_handler_session_mapping[handler]
        del handler

    def get_user_message(self, uid: str):
        valid_messages = []
        if uid not in self.users_online_range.keys():
            return valid_messages
        for message in self.message_list:
            for online_range in self.users_online_range[uid]:
                if online_range[0] < message['timestamp'] < online_range[1]:
                    valid_messages.append(message)
        return valid_messages

    def add_message(self, messsage: Message):
        self.message_list.append(messsage)
        for sess in self.online_sessions:
            sess.handler.write_message(messsage)


class MainHandler(BaseHandler):
    @web.authenticated
    def get(self):
        self.render("room_list.html",
                    rooms=global_room_rid_mapping.values(),
                    username=global_user_uid_mapping[self.current_user])


class MessageHandler(websocket.WebSocketHandler, BaseHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        self.start_timestamp = time_ns()
        rid = self.get_argument("rid")
        uid = self.get_current_user()
        room = global_room_rid_mapping[rid]
        messages = room.get_user_message(uid)
        for message in messages:
            self.write_message(message)
        room.user_join(uid=uid, handler=self)

    def on_close(self):
        rid = self.get_argument("rid")
        uid = self.get_current_user()
        room = global_room_rid_mapping[rid]
        online_range = (self.start_timestamp, time_ns())
        room.user_leave(uid=uid, handler=self, online_range=online_range)

    def on_message(self, message):
        if not self.get_current_user():
            self.close(code=1011, reason="Please Login")
            return
        message = Message(self.get_current_user(), json.loads(message))
        rid = self.get_argument("rid")
        room = global_room_rid_mapping[rid]
        room.add_message(message)


class LoginHandler(BaseHandler):
    def get(self):
        logout = len(self.get_arguments("logout"))
        if self.get_current_user():
            if logout:
                self.clear_cookie("user")
            self.redirect("/")
            return
        self.render("login.html")

    def post(self):
        username = self.get_argument("name").lower()
        uid = md5("user", username)
        # Register a new user if username is not exist
        if uid not in global_user_uid_mapping.keys():
            User(username, uid)
        self.set_cookie("user", uid)
        self.redirect("/")


class InRoomHandler(BaseHandler):
    @web.authenticated
    def get(self):
        rid = self.get_argument("rid")
        self.render("room.html", rid=rid, name=global_room_rid_mapping[rid].name)


class ManagementHandler(BaseHandler):
    @web.authenticated
    def get(self):
        op = self.get_argument("operation")
        arg = self.get_argument("argument")
        if op == "add":
            Room(arg)
        elif op == "del":
            del global_room_rid_mapping[arg]
        self.redirect("/")


web.Application(
    [(r"/login", LoginHandler),
     (r"/ws", MessageHandler),
     (r"/", MainHandler),
     (r"/room", InRoomHandler),
     (r"/manage", ManagementHandler)],
    template_path=os.path.join("py/tornado/chatroom", "templates"),
    login_url="/login",
).listen(8848)

if __name__ == "__main__":
    Room("Default Room")
    ioloop.IOLoop.instance().start()
