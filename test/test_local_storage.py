# conftest.py
import pytest
from pytest import fixture, mark
import subprocess
import time
import requests
import os
import re
import sys
from os.path import join, dirname
from playwright.sync_api import sync_playwright, expect


sys.path.append(join(dirname(dirname(__file__)), "src"))

from tools import load_brands
from CONFIG import CFG


def kill_port(port):
    try:
        output = subprocess.check_output(
            f"lsof -t -i:{port}", shell=True).decode().split()
        for pid in output:
            if pid:
                subprocess.run(["kill", "-9", pid], check=False)
                print(f"Killed PID {pid} on port {port}")
    except Exception as _:
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


@fixture(scope="session")
def gunicorn_server():
    cmd = [
        "gunicorn", "src.main:server",
        "-b", "127.0.0.1:8061",
        "-w", "4"
    ]
    kill_port(8061)
    proc = subprocess.Popen(cmd)
    try:
        yield
    finally:
        proc.terminate()
        proc.wait()


MONITOR_SIZE = (3840, 2160)
MONITOR_GRID = (2, 2)

def get_window_position(idx):
    cols, rows = MONITOR_GRID
    cell_width = MONITOR_SIZE[0] // cols
    cell_height = MONITOR_SIZE[1] // rows

    idx -= 1  # make it 0-based
    col = idx % cols
    row = idx // cols

    x = col * cell_width
    y = row * cell_height

    return x, y

@pytest.fixture(scope="class")
def playwright_driver(gunicorn_server, request):
    subprocess.run(["playwright", "install", "chromium"], check=True)
    app_url = "http://127.0.0.1:8061"
    index = request.cls.__name__.split('_')[0][4:]

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            geolocation={"latitude": -22.9, "longitude": -47.1},
            permissions=["geolocation"],
            viewport={
                "width": MONITOR_SIZE[0] / MONITOR_GRID[0],
                "height": MONITOR_SIZE[1] / MONITOR_GRID[1]},
            http_credentials={
                "username": os.environ.get("APP_USERNAME"),
                "password": os.environ.get("APP_PASSWORD")
            }
        )
        page = context.new_page()
        x, y = get_window_position(int(index))
        page.evaluate(f"window.moveTo({x}, {y})")
        page.goto(app_url)
        expect(page).to_have_title("ICB")

        yield page

        browser.close()


@mark.incremental
class Test004_Brands:
    @fixture(autouse=True)
    def setup_class(self, playwright_driver):
        self.app = playwright_driver

    def test_options(self):
        groups = list(set(CFG.groups))
        for group in groups:
            self.app.goto(f"http://127.0.0.1:8061/{group}")
            for prd, grp in zip(CFG.products, CFG.groups):
                if grp != group:
                    continue

                rows = self.app.locator(f"#{prd}-rows")
                rows.scroll_into_view_if_needed()
                rows.focus()
                fields = CFG.product_fields[prd]

                brands = rows.get_by_role("combobox")
                count = brands.count()
                assert count == fields[0] * CFG.product_rows[prd], "Wrong number of brands"
                if count != 0:
                    for i in range(count):
                        brand = brands.nth(i)
                        brand.scroll_into_view_if_needed()
                        brand.focus()
                        expected_options = [i["label"] for i in load_brands(prd)]
                        actual_options = brand.get_by_role("option")
                        actual_options_count = actual_options.count()
                        assert actual_options_count == len(expected_options), \
                            f"Expected {len(expected_options)} options, got {actual_options_count}"
                        for j in range(actual_options_count):
                            option = actual_options.nth(j)
                            option_text = option.text_content().strip()
                            assert option_text in expected_options, \
                                f"Option '{option_text}' not in expected options {expected_options}"
