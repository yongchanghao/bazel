py_library(
    name = "lib",
    srcs = [
        "backend.py",
        "uimodules.py",
    ],
    deps = [],
)

exports_files(
    srcs = ["blog.db"],
)

py_binary(
    name = "server",
    srcs = ["server.py"],
    data = [
        ":blog.db",
        "//py/tornado/blog/static/js:md5.min.js",
        "//py/tornado/blog/static/svg:comment.svg",
        "//py/tornado/blog/static/svg:thumbsup.svg",
        "//py/tornado/blog/static/svg:thumbsup-blue.svg",
        "//py/tornado/blog/templates:compose.html",
        "//py/tornado/blog/templates:login.html",
        "//py/tornado/blog/templates:main.html",
        "//py/tornado/blog/templates:module-headbar.html",
        "//py/tornado/blog/templates:register.html",
    ],
    deps = [":lib"],
)
