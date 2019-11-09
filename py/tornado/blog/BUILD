py_library(
    name = "lib",
    srcs = ["backend.py", "uimodules.py"],
    deps = [],
)

py_binary(
    name = "server",
    srcs = ["server.py"],
    deps = [":lib"],
    data = [
        "//py/tornado/blog/templates:compose.html",
        "//py/tornado/blog/templates:login.html",
        "//py/tornado/blog/templates:main.html",
        "//py/tornado/blog/templates:module-headbar.html",
        "//py/tornado/blog/templates:register.html",
    ]
)