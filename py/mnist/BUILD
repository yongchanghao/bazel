exports_files(
    srcs = ["model.hdf5"],
)

py_binary(
    name = "server",
    srcs = ["server.py"],
    data = [
        "//py/mnist/page:index.html",
        ":model.hdf5",
    ],
)