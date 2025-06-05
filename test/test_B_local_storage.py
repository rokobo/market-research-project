# conftest.py
import pytest
from pytest import fixture, mark
import subprocess
import os
import sys
from os.path import join, dirname
from playwright.sync_api import sync_playwright, expect
from conftest import get_window_position, kill_port


sys.path.append(join(dirname(dirname(__file__)), "src"))

from tools import load_brands
from CONFIG import CFG


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


@pytest.fixture(scope="class")
def playwright_driver(gunicorn_server, request):
    subprocess.run(["playwright", "install", "chromium"], check=True)
    app_url = "http://127.0.0.1:8061"
    index = request.cls.__name__.split('_')[0][4:]
    POS_X, POS_Y, WIDTH, HEIGHT = get_window_position(int(index))
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False, args=[
                f"--window-position={POS_X},{POS_Y}",
            ]
        )
        context = browser.new_context(
            geolocation={"latitude": -22.9, "longitude": -47.1},
            permissions=["geolocation"],
            viewport={
                "width": WIDTH,
                "height": HEIGHT},
            http_credentials={
                "username": os.environ.get("APP_USERNAME"),
                "password": os.environ.get("APP_PASSWORD")
            }
        )
        page = context.new_page()
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
