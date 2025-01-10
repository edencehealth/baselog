#!/usr/bin/env python3
"""configuration for tests in this package"""
# pylint: disable=too-few-public-methods

import os

import pytest


@pytest.fixture(scope="function")
def temp_envvars():
    """fixture which saves envvars and then restores them after a test runs"""
    saved_env = os.environ.copy()
    yield lambda: None
    os.environ = saved_env


@pytest.fixture
def tmp_log_dir(tmp_path):
    """
    fixture which presents a correctly-formatted envfile covering all options in the
    config
    """
    yield tmp_path
    _ = [
        os.unlink(os.path.join(tmp_path, f))
        for f in os.listdir(tmp_path)
        if (f.endswith(".log") and os.path.isfile(os.path.join(tmp_path, f)))
    ]
    if len(os.listdir(tmp_path)) < 1:
        os.rmdir(tmp_path)


@pytest.fixture
def tmp_run_files(tmp_path):
    """
    returns a coule temp files, which are needed to run the an external test program
    """
    paths = [tmp_path / filename for filename in ("test_prog.py", "stderr.log")]
    yield paths
    for file in paths:
        if os.path.exists(file):
            os.unlink(file)
    if len(os.listdir(tmp_path)) < 1:
        os.rmdir(tmp_path)
