load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:git.bzl", "git_repository")

http_archive(
    name = "com_google_protobuf",
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

http_archive(
    name = "upb",
    strip_prefix = "upb-9effcbcb27f0a665f9f345030188c0b291e32482",
    url = "https://github.com/protocolbuffers/upb/archive/9effcbcb27f0a665f9f345030188c0b291e32482.tar.gz",
)

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")

http_archive(
    name = "build_bazel_rules_swift",
    urls = [
        "https://github.com/bazelbuild/rules_swift/releases/download/0.11.1/rules_swift.0.11.1.tar.gz",
    ],
)

load(
    "@build_bazel_rules_swift//swift:repositories.bzl",
    "swift_rules_dependencies",
)

swift_rules_dependencies()

load(
    "@build_bazel_apple_support//lib:repositories.bzl",
    "apple_support_dependencies",
)

apple_support_dependencies()

load("@com_github_grpc_grpc//bazel:grpc_deps.bzl", "grpc_deps")
load("@com_google_protobuf//:protobuf_deps.bzl", "protobuf_deps")
load("@upb//bazel:workspace_deps.bzl", "upb_deps")

upb_deps()

protobuf_deps()

grpc_deps()
