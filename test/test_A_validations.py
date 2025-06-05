# conftest.py
import pytest
from pytest import fixture, mark
import subprocess
import os
import re
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
class Test001_Initial_State:
    @fixture(autouse=True)
    def setup_class(self, playwright_driver):
        self.app = playwright_driver

    def test_badges(self):
        groups = list(set(CFG.groups))
        for group in groups:
            self.app.goto(f"http://127.0.0.1:8061/{group}")
            for prd, grp in zip(CFG.products, CFG.groups):
                if grp != group:
                    continue
                badge = self.app.locator(f'#status-{prd}')
                badge.scroll_into_view_if_needed()
                badge.focus()
                expect(badge).to_have_class(re.compile("bg-danger"))

    def test_icons(self):
        groups = list(set(CFG.groups))
        for group in groups:
            self.app.goto(f"http://127.0.0.1:8061/{group}")
            for prd, grp in zip(CFG.products, CFG.groups):
                if grp != group:
                    continue
                icon = self.app.locator(f'#icon-{prd}')
                expect(icon).to_have_attribute("class", re.compile("icon-red"))

    def test_fields(self):
        groups = list(set(CFG.groups))
        for group in groups:
            self.app.goto(f"http://127.0.0.1:8061/{group}")
            for prd, grp in zip(CFG.products, CFG.groups):
                if grp != group:
                    continue

                rows = self.app.locator(f"#{prd}-rows")
                rows.scroll_into_view_if_needed()
                rows.focus()
                brands = rows.get_by_role("combobox")
                count = brands.count()
                assert count == CFG.product_fields[prd][0] * CFG.product_rows[prd], "Wrong number of brands"
                if count != 0:
                    for i in range(count):
                        brand = brands.nth(i)
                        brand.scroll_into_view_if_needed()
                        brand.focus()
                        expect(brand).to_have_class(re.compile("is-invalid"))

    def test_save_button(self):
        groups = list(set(CFG.groups))
        for group in groups:
            self.app.goto(f"http://127.0.0.1:8061/{group}")

            save_button = self.app.locator(f"#save-products-{group}")
            save_button.scroll_into_view_if_needed()
            save_button.focus()
            expect(save_button).to_have_class(re.compile("btn-danger"))

            save_container = self.app.locator(f"#save-container-{group}")
            save_container.scroll_into_view_if_needed()
            save_container.focus()
            expect(save_container).to_have_class(re.compile("unclickable"))


@mark.incremental
class Test002_No_Data:
    @fixture(autouse=True)
    def setup_class(self, playwright_driver):
        self.app = playwright_driver

    def test_badges_and_icons(self):
        groups = list(set(CFG.groups))
        for group in groups:
            self.app.goto(f"http://127.0.0.1:8061/{group}")
            for prd, grp in zip(CFG.products, CFG.groups):
                if grp != group:
                    continue

                rows = self.app.locator(f"#{prd}-rows")
                rows.scroll_into_view_if_needed()
                rows.focus()
                counter = 0
                while True:
                    deletes = rows.locator('button:has(i.bi-trash3)')
                    count = deletes.count()
                    if count == 0:
                        break

                    delete = deletes.first
                    delete.scroll_into_view_if_needed()
                    delete.focus()
                    delete.click()
                    counter += 1

                assert counter == CFG.product_rows[prd], "Wrong number of rows"

                icon = self.app.locator(f'#icon-{prd}')
                expect(icon).to_have_attribute("class", re.compile("icon-orange"))

                badge = self.app.locator(f'#status-{prd}')
                badge.scroll_into_view_if_needed()
                badge.focus()
                expect(badge).to_have_class(re.compile("bg-warning"))

            save_button = self.app.locator(f"#save-products-{group}")
            save_button.scroll_into_view_if_needed()
            save_button.focus()
            expect(save_button).to_have_class(re.compile("btn-danger"))

            save_container = self.app.locator(f"#save-container-{group}")
            save_container.scroll_into_view_if_needed()
            save_container.focus()
            expect(save_container).to_have_class(re.compile("unclickable"))


@mark.incremental
class Test003_With_Data:
    @fixture(autouse=True)
    def setup_class(self, playwright_driver):
        self.app = playwright_driver

    def test_all(self):
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
                        options = load_brands(prd)
                        brand.select_option(options[0]["value"])

                numbers = rows.get_by_role("spinbutton")
                count = numbers.count()
                assert count == (fields[1] + fields[2]) * CFG.product_rows[prd], "Wrong number of number inputs"
                skip = False
                for i in range(count):
                    if skip:
                        skip = False
                        continue

                    number = numbers.nth(i)
                    number.scroll_into_view_if_needed()
                    number.focus()
                    number.fill("10")
                    number.press("Enter")
                    expect(number).not_to_have_class(re.compile("is-invalid"))

                    if fields[2]:
                        skip = True
                        number = numbers.nth(i + 1)
                        number.scroll_into_view_if_needed()
                        number.focus()
                        number.fill("0.5")
                        number.press("Enter")
                        expect(number).not_to_have_class(re.compile("is-invalid"))

                icon = self.app.locator(f'#icon-{prd}')
                expect(icon).to_have_attribute("class", re.compile("icon-green"))

                badge = self.app.locator(f'#status-{prd}')
                badge.scroll_into_view_if_needed()
                badge.focus()
                expect(badge).to_have_class(re.compile("bg-success"))

            save_button = self.app.locator(f"#save-products-{group}")
            save_button.scroll_into_view_if_needed()
            save_button.focus()
            expect(save_button).to_have_class(re.compile("btn-danger"))

            save_container = self.app.locator(f"#save-container-{group}")
            save_container.scroll_into_view_if_needed()
            save_container.focus()
            expect(save_container).to_have_class(re.compile("unclickable"))
