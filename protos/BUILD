load("@com_github_grpc_grpc//bazel:cc_grpc_library.bzl", "cc_grpc_library")

package(default_visibility = ["//visibility:public"])

proto_library(
    name = "test_proto",
    srcs = ["test.proto"],
)

cc_proto_library(
    name = "test_proto_cc",
    deps = [":test_proto"],
)

cc_grpc_library(
    name = "test_grpc_cc",
    srcs = ["test.proto"],
    deps = [],
)
