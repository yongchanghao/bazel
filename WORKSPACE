load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

http_archive(
    name = "com_google_protobuf",
    sha256 = "33cba8b89be6c81b1461f1c438424f7a1aa4e31998dbe9ed6f8319583daac8c7",
    strip_prefix = "protobuf-3.10.0",
    urls = ["https://github.com/google/protobuf/archive/v3.10.0.zip"],
)

http_archive(
    name = "com_github_grpc_grpc",
    strip_prefix = "grpc-fe494ff4104b6f6a78117ab2da71d29c93053267",
    urls = [
        "https://github.com/grpc/grpc/archive/fe494ff4104b6f6a78117ab2da71d29c93053267.tar.gz",
    ],
)

load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")

protobuf_deps()
