"""
TODO(Schureed): Add doc
"""
import hashlib
import json
import os
import sys
import time

import markdown
from tornado import web, ioloop, options, websocket

from py.tornado.blog import backend
from py.tornado.blog import uimodules

ABS_PATH = os.path.abspath(sys.path[0])

BASE_PREFIX = ""
MAIN_PAGE = ""
POST_PAGE = ""
LOGIN_PAGE = ""
COMPOSE_PAGE = ""
COMMENT_PAGE = ""

global_backend_service = None
global_user_actions = dict()


def user_action_permitted(uid: str):
    global global_user_actions
    if uid not in global_user_actions:
        global_user_actions[uid] = []
    while len(global_user_actions[uid]) > 0 and time.time() - global_user_actions[uid][0] > 10:
        global_user_actions[uid] = global_user_actions[uid][1:]
    global_user_actions[uid].append(time.time())
    return len(global_user_actions[uid]) <= 5


def md5(raw: str):
    return hashlib.md5(raw.encode('utf8')).hexdigest()


class FileManager(object):
    @staticmethod
    def write(absl_path: str, content: str) -> str:
        filename = md5(str(time.time()))
        filepath = os.path.join(absl_path, filename)
        with open(filepath, "w") as f:
            f.write(content)
        return filepath


class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        uid = self.get_secure_cookie("uid")
        if isinstance(uid, bytes):
            uid = uid.decode('utf8')
        return uid if isinstance(uid, str) and len(uid) > 0 else None

    def get_user_info(self):
        uid = self.get_current_user()
        if uid:
            user = global_backend_service.get_user_by_uid(uid)
            return user
        return dict()

    def get_all_posts(self):
        raw_posts = global_backend_service.get_all_posts()
        for post in raw_posts:
            f = open(post["content_path"])
            post["content"] = f.read()
            f.close()

            post["like_list"] = global_backend_service.get_likes_by_pid(post["pid"])
            raw_comment_list = global_backend_service.get_comments_by_pid(post["pid"])
            for comment in raw_comment_list:
                comment['username'] = global_backend_service.get_user_by_uid(comment['uid'])['username']
                f = open(comment["content_path"])
                comment['content'] = f.read()
                f.close()
            post["comment_list"] = raw_comment_list
            post["liked"] = False
            for like in post["like_list"]:
                if like["uid"] == self.get_current_user():
                    post["liked"] = True
                    break
        raw_posts.reverse()
        return raw_posts


class MainHandler(BaseHandler):
    def get(self):
        self.render(
            template_name="main.html",
            posts=self.get_all_posts(),
            user_info=self.get_user_info(),
            server_address=options.options.server_address,
            server_port=options.options.port,
        )


class LoginHandler(BaseHandler):
    def get(self):
        logout = int(self.get_argument("logout", "0"))
        if logout:
            self.clear_cookie("uid", path="blog")
            self.redirect(MAIN_PAGE)
            return
        register = int(self.get_argument("new", default="0"))
        if register:
            username = self.get_argument("username", default="")
            self.render("register.html", username=username, user_info=self.get_user_info())
            return
        if self.get_current_user():
            self.redirect(MAIN_PAGE)
            return
        self.render("login.html", user_info=self.get_user_info())

    def post(self):
        register = int(self.get_argument("new", "0"))
        username = self.get_argument("username")
        uid = md5(username.lower())
        password = self.get_argument("password")
        if register:
            user = global_backend_service.get_user_by_uid(uid)
            if user:
                self.redirect(LOGIN_PAGE + "?new=1&username=%s" % username)
                return
            else:
                global_backend_service.execute(
                    """INSERT INTO User VALUES ('%s', '%s', '%s')""" % (uid, username, password))
        else:
            user = global_backend_service.get_user_by_uid(uid)
            if user:
                if user["password"] == password:
                    self.set_secure_cookie(
                        name="uid",
                        value=uid,
                        path="/blog",
                    )
                else:
                    self.redirect(LOGIN_PAGE)
                    return
            else:
                self.redirect(LOGIN_PAGE + "?new=1&username=%s" % username)
                return
        self.redirect(self.get_argument("next", MAIN_PAGE))


class ComposeHandler(BaseHandler):
    @web.authenticated
    def get(self):
        user = global_backend_service.get_user_by_uid(self.get_current_user())
        if user["username"].lower() == "schureed":
            self.render("compose.html")
        else:
            self.set_status(404, "Page Not Found")

    @web.authenticated
    def post(self):
        user = global_backend_service.get_user_by_uid(self.get_current_user())
        if not user["username"].lower() == "schureed":
            self.set_status(404, "Page Not Found")
            return
        title = self.get_argument("title")
        content = self.get_argument("content")
        timestamp = int(time.time() * 1000)

        filepath = os.path.abspath(os.path.join(ABS_PATH, "posts"))
        filepath = FileManager.write(filepath, content)
        global_backend_service.execute(
            """INSERT INTO Post VALUES (null, '%s', '%s', %d)""" % (title, filepath, timestamp))
        self.get_all_posts()
        self.redirect(MAIN_PAGE)


class PostActionHandler(websocket.WebSocketHandler, BaseHandler):
    def on_message(self, message):
        data = json.loads(message)
        if not self.get_current_user():
            self.write_message("")
            return
        user = self.get_user_info()
        if not user_action_permitted(user["uid"]):
            print("Dropped uid %s" % user["uid"], flush=True)
            return
        pid = int(data["pid"])
        if data["action"] == "like":
            global_backend_service.execute(
                """INSERT INTO Like VALUES (null, '%s', %d, %d)""" % (user["uid"], pid, int(time.time() * 1000)))
        elif data["action"] == "unlike":
            print("""DELETE FROM Like WHERE uid = '%s' AND pid = %d""" % (user["uid"], pid), flush=True)
            global_backend_service.execute(
                """DELETE FROM Like WHERE uid = '%s' AND pid = %d""" % (user["uid"], pid))


class ViewPostHandler(BaseHandler):
    def get(self):
        pid = self.get_argument("pid")
        post_record = global_backend_service.get_post_by_pid(pid)
        self.render(
            template_name="post.html",
        )


class CommentHandler(BaseHandler):
    @web.authenticated
    def post(self):
        content = self.get_argument("content")
        pid = int(self.get_argument("pid"))
        user = self.get_user_info()
        content = markdown.markdown(content)
        filepath = os.path.abspath(os.path.join(ABS_PATH, "comments"))
        filepath = FileManager.write(filepath, content)
        global_backend_service.execute(
            """INSERT INTO Comment VALUES (null, %d, '%s', '%s', %d)""" % (
                pid, user["uid"], filepath, int(time.time() * 1000)))
        self.redirect(MAIN_PAGE)


if __name__ == "__main__":
    options.define("cookie_secret", "blog", str)
    options.define("port", 8888, int)
    options.define("base_prefix", "/blog", str)
    options.define("debug", True, bool)
    options.define("db_path", "/Users/Schureed/projects/bazel/py/tornado/blog/blog.sqlite", str)
    options.define("server_address", "localhost", str)

    options.parse_command_line()

    global_backend_service = backend.BackendService(options.options.db_path)
    BASE_PREFIX = options.options.base_prefix

    MAIN_PAGE = BASE_PREFIX + ""
    POST_PAGE = BASE_PREFIX + "/post"
    LOGIN_PAGE = BASE_PREFIX + "/login"
    COMMENT_PAGE = BASE_PREFIX + "/comment"
    COMPOSE_PAGE = BASE_PREFIX + "/compose"
    POST_ACTION_HANDLER = BASE_PREFIX + "/paws"

    app = web.Application([
        (MAIN_PAGE, MainHandler),
        (POST_PAGE, ViewPostHandler),
        (LOGIN_PAGE, LoginHandler),
        (COMMENT_PAGE, CommentHandler),
        (COMPOSE_PAGE, ComposeHandler),
        (POST_ACTION_HANDLER, PostActionHandler),
    ], **{
        "login_url": BASE_PREFIX + "/login",
        "cookie_secret": options.options.cookie_secret,
        "debug": options.options.debug,
        "template_path": os.path.join(ABS_PATH, "templates"),
        'static_path': os.path.join(ABS_PATH, "static"),
        "ui_modules": uimodules,
    })

    port = options.options.port
    while True:
        try:
            app.listen(port)
            sys.stdout.write("Server is listening %d" % port)
            sys.stdout.flush()
            break
        except Exception:
            sys.stdout.write("Port %d is not available, try %d" % (port, port + 1))
            sys.stdout.flush()
            port += 1
    ioloop.IOLoop.instance().start()
