from tornado import web


class NavBar(web.UIModule):
    def render(self, user_info, title="Blog"):
        nav_items = [
            {'href': "/blog", 'text': "Blog"},
            {'href': "/mnist", 'text': "MNIST Demo"},
        ]
        return self.render_string(
            path="module-headbar.html",
            title=title,
            nav_items=nav_items,
            user_info=user_info,
        )
