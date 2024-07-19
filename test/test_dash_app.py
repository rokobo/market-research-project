import sys
from os.path import join, dirname
from os import getenv
import time
from dotenv import load_dotenv
import chromedriver_autoinstaller
from pytest import fixture, fail, mark
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import subprocess

sys.path.append(join(dirname(dirname(__file__)), "src"))

from CONFIG import CFG

chromedriver_autoinstaller.install()
load_dotenv()

FIRST_IDS = ["collector_name", "collection_date", "establishment"]
RAW_INPUTS = ["Name", "02212020", "AAA_TESTE"]
STORED_INPUTS = ["Name", "2020-02-21", "AAA_TESTE (para Teste)"]
BASE_URL = "http://127.0.0.1:8060"
AUTHENTICATED_URL = BASE_URL.replace(
    "//", f"//{getenv("APP_USERNAME")}:{getenv("APP_PASSWORD")}@")


@fixture(scope="module")
def gunicorn_server():
    log_file = open("gunicorn.log", "w")
    command = [
        "gunicorn", "src.main:server",
        "-b", BASE_URL.split("//")[1],
        "-w", "1"]
    process = subprocess.Popen(command, stdout=log_file, stderr=log_file)

    timeout = 5
    response = "Did not send response"
    while timeout > 0:
        try:
            response = requests.get(AUTHENTICATED_URL)
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(1)
            timeout -= 1

    if timeout == 0:
        response = requests.get(AUTHENTICATED_URL)
        process.terminate()
        process.wait()
        fail(f"Gunicorn server error: {response.status_code}")

    yield process

    process.terminate()
    process.wait()
    log_file.close()
    return


def selenium_driver():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    driver.get(AUTHENTICATED_URL)
    WebDriverWait(driver, 10).until(EC.title_is("ICB"))
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.title_is("ICB"))
    driver.refresh()
    WebDriverWait(driver, 10).until(EC.title_is("ICB"))

    yield driver

    driver.quit()
    return


@fixture(scope="function")
def app_f():
    yield from selenium_driver()


@fixture(scope="class")
def app_c():
    yield from selenium_driver()


@fixture(scope="class")
def app_and_gunicorn_server(request):
    app = request.getfixturevalue('app')
    gunicorn_server = request.getfixturevalue('gunicorn_server')
    return app, gunicorn_server


def get_by_cond(driver, id, cond=By.ID, all=False):
    if all:
        return WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((cond, id)))
    return WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((cond, id)))


def scroll_to_product(driver, product, extra_delay=0.0):
    y_coord = get_by_cond(driver, f'{product}-heading', By.ID).location['y']
    driver.execute_script(
        f"document.documentElement.scrollTop = {y_coord - 60};")
    time.sleep(0.25 + extra_delay)


def test_navigation(gunicorn_server, app_f):
    scroll_command = "return document.documentElement.scrollTop;"
    app_f.set_window_size(app_f.get_window_size()["width"], 400)
    old_posY = app_f.execute_script(scroll_command)
    old_url = app_f.current_url
    for product in CFG.products:
        icon = get_by_cond(app_f, f"icon-{product}", By.ID)
        icon.click()
        time.sleep(1)
        posY = app_f.execute_script(scroll_command)
        url = app_f.current_url
        assert posY > old_posY, product
        assert url != old_url, product
        old_posY, old_url = posY, url


@mark.incremental
class TestFirstSection:
    @fixture(autouse=True)
    def setup_class(self, gunicorn_server, app_c):
        self.app = app_c
        self.elements = [get_by_cond(self.app, id, By.ID) for id in FIRST_IDS]

    def test_initial(self):
        for element in self.elements:
            assert element.get_attribute("value") == ""
            assert "wrong" in element.get_attribute("class")

    def test_interaction(self):
        for idx in range(3):
            self.elements[idx].send_keys(RAW_INPUTS[idx])
            get_by_cond(self.app, FIRST_IDS[idx], By.ID)

            for elem_idx in range(3):
                element = self.elements[elem_idx]
                if elem_idx > idx:
                    assert element.get_attribute("value") == ""
                    assert "wrong" in element.get_attribute("class")
                else:
                    assert element.get_attribute("value") != ""
                    assert "correct" in element.get_attribute("class")

    def test_load(self):
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))

        self.elements = [get_by_cond(self.app, id, By.ID) for id in FIRST_IDS]
        for element, value in zip(self.elements, STORED_INPUTS):
            assert "correct" in element.get_attribute("class")
            assert element.get_attribute("value") == value


@mark.incremental
class TestSecondSection:
    @fixture(autouse=True)
    def setup_class(self, gunicorn_server, app_c):
        self.app = app_c

    def test_initial(self):
        products = [CFG.products[0], CFG.products[-1]]
        get_by_cond(self.app, '[id*="price-"]', By.CSS_SELECTOR, True)

        for product in products:
            section_div = get_by_cond(self.app, f"{product}-heading", By.ID)
            productElems = [section_div.find_elements_by_css_selector(
                f'[id*="{field}-{product}"]') for field in CFG.fields]
            assert len(productElems[1]) == CFG.product_rows[product], product

            for idx, elements in enumerate(productElems):
                for element in elements:
                    class_name = "wrong" if idx < 2 else "correct"
                    assert element.get_attribute("value") == ""
                    assert class_name in element.get_attribute("class")

    def test_wrong_badge(self):
        for product in CFG.products:
            scroll_to_product(self.app, product)
            badge = get_by_cond(self.app, f"status-{product}", By.ID)
            assert "danger" in badge.get_attribute("class")

    def test_interaction(self):
        for idx0, product in enumerate(CFG.products):
            scroll_to_product(self.app, product, 2 if idx0 == 0 else 0)
            prices = get_by_cond(
                self.app, f'[id*="price-{product}"]', By.CSS_SELECTOR, True)

            for idx, current_price in enumerate(prices):
                current_price.send_keys(idx0 + (idx / 10))
                for idx2, price in enumerate(prices):
                    class_name = "wrong" if idx2 > idx else "correct"
                    assert class_name in price.get_attribute("class")

    def test_correct_badge(self):
        for idx, product in enumerate(CFG.products):
            scroll_to_product(self.app, product, 2 if idx == 0 else 0)
            section = get_by_cond(self.app, f"{product}-heading", By.ID)
            badge = get_by_cond(self.app, f"status-{product}", By.ID)

            selector = [
                f'[id*="brand-{product}"]',
                f'[id*="quantity-{product}"]', f'[id*="obs-{product}"]']

            if idx < 9:
                for brd in section.find_elements_by_css_selector(selector[0]):
                    brd.send_keys(
                        brd.find_elements_by_tag_name('option')[-1].text)
            if idx < 8:
                for i, qty in enumerate(
                    section.find_elements_by_css_selector(selector[1])
                ):
                    qty.send_keys(float(f"0.{idx}{i}"))
            if idx > 8:
                for obs in section.find_elements_by_css_selector(selector[2]):
                    obs.send_keys(f"observation-{idx}")
            assert "success" in badge.get_attribute("class")

    def test_invalid_save(self):
        button = get_by_cond(self.app, "save-products", By.ID)
        assert "danger" in button.get_attribute("class")

    def test_load(self):
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))

        for idx, product in enumerate(CFG.products):
            scroll_to_product(self.app, product, 2 if idx == 0 else 0)
            section = get_by_cond(self.app, f"{product}-heading", By.ID)
            badge = get_by_cond(self.app, f"status-{product}", By.ID)

            selector = [
                f'[id*="brand-{product}"]',
                f'[id*="quantity-{product}"]', f'[id*="obs-{product}"]']

            if idx < 9:
                for brd in section.find_elements_by_css_selector(selector[0]):
                    assert brd.get_attribute("value") not in ["", None], product
            if idx < 8:
                for i, qty in enumerate(
                    section.find_elements_by_css_selector(selector[1])
                ):
                    assert float(qty.get_attribute("value")) == float(f"0.{idx}{i}"), product
            if idx > 8:
                for obs in section.find_elements_by_css_selector(selector[2]):
                    assert obs.get_attribute("value") == f"observation-{idx}", product

            assert "success" in badge.get_attribute("class"), product

# def test_deletion_second_section(gunicorn_server, app_f):
#     for product in CFG.products:
#         scroll_to_product(app_f, product)
#         elements = get_by_cond(
#             app_f, f'[id*="delete-{product}"]', By.CSS_SELECTOR, True)
#         badge = get_by_cond(app_f, f"status-{product}", By.ID)

#         assert "danger" in badge.get_attribute("class")
#         for element in elements:
#             element.click()
#         assert "warning" in badge.get_attribute("class")


# def test_load_deletion(gunicorn_server, app_f):
#     for product in CFG.products:
#         scroll_to_product(app_f, product, 0.3)
#         elements = get_by_cond(
#             app_f, f'[id*="delete-{product}"]', By.CSS_SELECTOR, True)

#         for element in elements:
#             element.click()

#         app_f.get(BASE_URL)
#         WebDriverWait(app_f, 10).until(EC.title_is("ICB"))

#         section_div = get_by_cond(app_f, f"{product}-heading", By.ID)
#         productElems = section_div.find_elements_by_css_selector(
#             f'[id*="price-{product}"]')
#         assert len(productElems) == 0, product
