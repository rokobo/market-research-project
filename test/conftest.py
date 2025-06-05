from typing import Dict, Tuple
from screeninfo import get_monitors
import pytest
import subprocess
import time
import requests

# store history of failures per test class name and per index in parametrize
# (if parametrize used)
_test_failed_incremental: Dict[str, Dict[Tuple[int, ...], str]] = {}


def pytest_runtest_makereport(item, call):
    if "incremental" in item.keywords:
        # incremental marker is used
        if call.excinfo is not None:
            # the test has failed
            # retrieve the class name of the test
            cls_name = str(item.cls)
            # retrieve the index of the test
            # (if parametrize is used in combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the test function
            test_name = item.originalname or item.name
            # store in _test_failed_incremental the name of failed test
            _test_failed_incremental.setdefault(cls_name, {}).setdefault(
                parametrize_index, test_name
            )


def pytest_runtest_setup(item):
    if "incremental" in item.keywords:
        # retrieve the class name of the test
        cls_name = str(item.cls)
        # check if a previous test has failed for this class
        if cls_name in _test_failed_incremental:
            # retrieve the index of the test
            # (if parametrize is used in combination with incremental)
            parametrize_index = (
                tuple(item.callspec.indices.values())
                if hasattr(item, "callspec")
                else ()
            )
            # retrieve the name of the first test function
            # to fail for this class name and index
            test_name = _test_failed_incremental[cls_name].get(
                parametrize_index, None)
            # if name found:
            # test has failed for the combination of class name & test name
            if test_name is not None:
                pytest.skip(f"Previous test failed ({test_name})")


def get_window_position(idx, grid=(2, 2)):
    PRIMARY = next(
        (m for m in get_monitors() if m.is_primary), get_monitors()[0])
    WIDTH, HEIGHT = PRIMARY.width, PRIMARY.height
    OFFSET_X, OFFSET_Y = PRIMARY.x, PRIMARY.y

    cols, rows = grid
    cell_width = WIDTH // cols
    cell_height = HEIGHT // rows
    print(WIDTH, HEIGHT, cell_width, cell_height)

    idx -= 1  # make it 0-based
    col = idx % cols
    row = idx // cols

    x = (col * cell_width) + OFFSET_X
    y = (row * cell_height) + OFFSET_Y
    return x, y, cell_width, cell_height


def kill_port(port):
    try:
        output = subprocess.check_output(
            f"lsof -t -i:{port}", shell=True).decode().split()
        for pid in output:
            if pid:
                subprocess.run(["kill", "-9", pid], check=False)
                print(f"Killed PID {pid} on port {port}")
    except Exception:
        print(f"No process found on port {port}")


def wait_for_http_response(url, timeout=10):
    for _ in range(timeout):
        try:
            r = requests.get(url)
            if r.status_code == 200:
                return
        except requests.ConnectionError:
            pass
        time.sleep(1)
    raise RuntimeError(f"Server not responding at {url}")
