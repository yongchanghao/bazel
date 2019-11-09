"""
TODO(Schureed): Add doc
"""
import sqlite3


class Post(dict):
    def __init__(self, raw: tuple):
        assert len(raw) == 4
        self["pid"] = raw[0]
        self["title"] = raw[1]
        self["content_path"] = raw[2]
        self["time"] = raw[3]


class Comment(dict):
    def __init__(self, raw: tuple):
        assert len(raw) == 5
        self["cid"] = raw[0]
        self["pid"] = raw[1]
        self["uid"] = raw[2]
        self["content_path"] = raw[3]
        self["time"] = raw[4]


class User(dict):
    def __init__(self, raw: tuple):
        assert len(raw) == 3
        self["uid"] = raw[0]
        self["username"] = raw[1]
        self["password"] = raw[2]


class Like(dict):
    def __init__(self, raw: tuple):
        assert len(raw) == 4
        self["lid"] = raw[0]
        self["uid"] = raw[1]
        self["pid"] = raw[2]
        self["time"] = raw[3]


global_all_kinds = dict()
global_all_kinds["user"] = User
global_all_kinds["comment"] = Comment
global_all_kinds["post"] = Post
global_all_kinds["like"] = Like


class BackendService(object):
    def __init__(self, db_path: str):
        self.connect = sqlite3.connect(db_path)
        self.cursor = self.connect.cursor()

    def execute(self, sql: str):
        result = self.cursor.execute(sql).fetchall()
        self.connect.commit()
        return result

    def query(self, kind: str, cond: str = ""):
        assert kind in global_all_kinds

        if len(cond):
            sql = """SELECT * FROM %s WHERE %s""" % ("%s", cond)
        else:
            sql = """SELECT * FROM %s""" % "%s"

        Tp = global_all_kinds[kind.lower()]
        table_name = kind[0].upper() + kind[1:].lower()
        raw_list = self.execute(sql % table_name)
        processed_list = []
        for item in raw_list:
            processed_list.append(Tp(item))
        return processed_list

    def get_all_users(self):
        return self.query("user")

    def get_user_by_uid(self, uid: str):
        user = self.query("user", "uid = '%s'" % uid)
        return user[0] if len(user) else None

    def get_all_posts(self):
        return self.query("post")

    def get_post_by_pid(self, pid: int):
        return self.query("post", "pid = %d" % pid)[0]

    def get_all_comments(self):
        return self.query("comment")

    def get_comments_by_pid(self, pid: int):
        return self.query("comment", "pid = %d" % pid)

    def get_comments_by_uid(self, uid: str):
        return self.query("comment", "pid = '%s'" % uid)

    def get_likes_by_pid(self, pid: str):
        return self.query("like", "pid = '%s'" % pid)

    def __del__(self):
        self.connect.commit()
        self.connect.close()
