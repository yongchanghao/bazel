load("@com_github_grpc_grpc//bazel:cc_grpc_library.bzl", "cc_grpc_library")

package(default_visibility = ["//visibility:public"])

proto_library(
    name = "message_proto",
    srcs = ["message.proto"],
)

cc_grpc_library(
    name = "message_proto_cc",
    srcs = ["message.proto"],
    deps = [],
)
