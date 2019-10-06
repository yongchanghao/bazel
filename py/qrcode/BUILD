py_library(
    name = "QRMatrix",
    srcs = ["QRMatrix.py"],
)

py_binary(
    name = "main",
    srcs = ["main.py"],
    deps = [":QRMatrix"],
    data = [
        "//py/qrcode/pics:sample0.png",
        "//py/qrcode/pics:sample1.png",
        "//py/qrcode/pics:sample2.png",
    ],
)