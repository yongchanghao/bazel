py_library(
    name = "lib",
    srcs = ["backend.py", "uimodules.py"],
    deps = [],
)

py_binary(
    name = "server",
    srcs = ["server.py"],
    deps = [":lib"],
)