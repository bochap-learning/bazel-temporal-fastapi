load("@aspect_rules_py//py:defs.bzl", "py_test_rule")
load("@third_party_deps//:requirements.bzl", "requirement")

def pytest_runner(name, srcs, deps = [], args = [], **kwargs):
    py_test_rule(
        name = name,
        main = "//tools/runner:pytest_runner.py",
        srcs = ["//tools/runner:pytest_runner.py"] + srcs,
        args = [
            "--capture=no"
        ] + args + ["$(location :%s)" % x for x in srcs],
        deps = deps + [
            requirement("pytest")
        ],
        **kwargs
    )