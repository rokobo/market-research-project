# flake8: noqa: E501
import sys
from os.path import join, dirname
from os import getenv, listdir, remove
import time
from dotenv import load_dotenv
import chromedriver_autoinstaller
from pytest import fixture, fail, mark
import requests
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
import subprocess
import pandas as pd

sys.path.append(join(dirname(dirname(__file__)), "src"))

from CONFIG import CFG

chromedriver_autoinstaller.install()
load_dotenv()

FIRST_IDS = ["collector_name", "collection_date", "establishment"]
RAW_INPUTS = ["NameName", "02212020", "AAA_TESTE"]
STORED_INPUTS = ["NameName", "2020-02-21", "AAA_TESTE (para Teste)"]
CSV_COLUMNS = [
    'Nome', 'Data', 'Estabelecimento',
    'Produto','Marca', 'Preço', 'Quantidade']
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
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
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


def get_by_cond(driver: webdriver.Chrome, id: str, cond) -> WebElement:
    return WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((cond, id)))


def get_all_by_cond(driver: webdriver.Chrome, id: str, cond) -> list[WebElement]:
    return WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((cond, id)))


def check_in_attr(element: WebElement, attribute, substring, reverse=False):
    value = element.get_attribute(attribute)
    if value is None:
        fail(f"check attr: {substring}, {value}")
    if reverse:
        if substring in value:
            fail(f"check attr: {substring}, {value}")
    else:
        if substring not in value:
            fail(f"check attr: {substring}, {value}")
    return True


def scroll_to_product(driver, product, extra_delay=0.0):
    y_coord = get_by_cond(driver, f'{product}-heading', By.ID).location['y']
    driver.execute_script(
        f"document.documentElement.scrollTop = {y_coord - 60};")
    time.sleep(0.25 + extra_delay)


def check_logs(driver, message):
    logs = driver.get_log('browser')
    for log in logs:
        if message in log['message']:
            return True
    return False


def test_navigation(gunicorn_server, app_f):
    scroll_command = "return document.documentElement.scrollTop;"
    app_f.set_window_size(app_f.get_window_size()["width"], 400)
    old_posY = app_f.execute_script(scroll_command)
    old_url = app_f.current_url
    for product in CFG.products:
        icon: WebElement = get_by_cond(app_f, f"icon-{product}", By.ID)
        icon.click()
        time.sleep(1)
        posY = app_f.execute_script(scroll_command)
        url = app_f.current_url
        assert posY > old_posY, product
        assert url != old_url, product
        old_posY, old_url = posY, url


@mark.incremental
class Test001FirstSection:
    @fixture(autouse=True)
    def setup_class(self, gunicorn_server, app_c):
        self.app = app_c
        self.elements = [get_by_cond(self.app, id, By.ID) for id in FIRST_IDS]

    def test_initial_state(self):
        for element in self.elements:
            assert element.get_attribute("value") == ""
            assert check_in_attr(element, "class", "wrong")

    def test_interaction(self):
        for idx in range(3):
            self.elements[idx].send_keys(RAW_INPUTS[idx])
            get_by_cond(self.app, FIRST_IDS[idx], By.ID)

            for elem_idx in range(3):
                element = self.elements[elem_idx]
                if elem_idx > idx:
                    assert element.get_attribute("value") == ""
                    assert check_in_attr(element, "class", "wrong")
                else:
                    assert element.get_attribute("value") != ""
                    assert check_in_attr(element, "class", "correct")

    def test_load(self):
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))

        self.elements = [get_by_cond(self.app, id, By.ID) for id in FIRST_IDS]
        for element, value in zip(self.elements, STORED_INPUTS):
            assert check_in_attr(element, "class", "correct")
            assert element.get_attribute("value") == value


@mark.incremental
class Test002SecondSection:
    @fixture(autouse=True)
    def setup_class(self, gunicorn_server, app_c):
        self.app = app_c

    def test_initial_state(self):
        products = [CFG.products[0], CFG.products[-1]]
        get_all_by_cond(self.app, '[id*="price-"]', By.CSS_SELECTOR)

        for product in products:
            section_div = get_by_cond(self.app, f"{product}-heading", By.ID)
            productElems = [section_div.find_elements(By.CSS_SELECTOR,
                f'[id*="{field}-{product}"]') for field in CFG.fields]
            assert len(productElems[1]) == CFG.product_rows[product], product

            for idx, elements in enumerate(productElems):
                for element in elements:
                    class_name = "wrong" if idx < 2 else "correct"
                    assert element.get_attribute("value") == ""
                    assert check_in_attr(element, "class", class_name)

    def test_red_badge(self):
        for product in CFG.products:
            scroll_to_product(self.app, product)
            badge = get_by_cond(self.app, f"status-{product}", By.ID)
            assert check_in_attr(badge, "class", "danger")

    def test_interaction(self):
        for idx0, product in enumerate(CFG.products):
            scroll_to_product(self.app, product, 2 if idx0 == 0 else 0)
            prices = get_all_by_cond(
                self.app, f'[id*="price-{product}"]', By.CSS_SELECTOR)

            for idx, current_price in enumerate(prices):
                current_price.send_keys(str(idx0 + (idx / 10)))
                for idx2, price in enumerate(prices):
                    class_name = "wrong" if idx2 > idx else "correct"
                    assert check_in_attr(price, "class", class_name)

    def test_green_badge(self):
        for idx, product in enumerate(CFG.products):
            scroll_to_product(self.app, product, 2 if idx == 0 else 0)
            section = get_by_cond(self.app, f"{product}-heading", By.ID)
            badge = get_by_cond(self.app, f"status-{product}", By.ID)

            selector = [
                f'[id*="brand-{product}"]',
                f'[id*="quantity-{product}"]', f'[id*="obs-{product}"]']

            if idx < 9:
                for brd in section.find_elements(By.CSS_SELECTOR, selector[0]):
                    brd.send_keys(
                        brd.find_elements(By.TAG_NAME, 'option')[-1].text)
            if idx < 8:
                for i, qty in enumerate(
                    section.find_elements(By.CSS_SELECTOR, selector[1])
                ):
                    qty.send_keys(f"0.{idx}{i}")
            if idx > 8:
                for obs in section.find_elements(By.CSS_SELECTOR, selector[2]):
                    obs.send_keys(f"observation-{idx}")
            assert check_in_attr(badge, "class", "success")

    def test_invalid_save(self):
        button = get_by_cond(self.app, "save-products", By.ID)
        container = get_by_cond(self.app, "save-container", By.ID)
        assert check_in_attr(button, "class", "danger")
        assert check_in_attr(container, "class", "unclickable")

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
                for brd in section.find_elements(By.CSS_SELECTOR, selector[0]):
                    assert brd.get_attribute("value") not in ["", None], product
            if idx < 8:
                for i, qty in enumerate(
                    section.find_elements(By.CSS_SELECTOR, selector[1])
                ):
                    assert float(qty.get_attribute("value")) == float(f"0.{idx}{i}"), product
            if idx > 8:
                for obs in section.find_elements(By.CSS_SELECTOR, selector[2]):
                    assert obs.get_attribute("value") == f"observation-{idx}", product

            assert check_in_attr(badge, "class", "success"), product


@mark.incremental
class Test003SaveProducts:
    @fixture(autouse=True)
    def setup_class(self, gunicorn_server, app_c):
        self.app = app_c

    def fill_first_section(self):
        elements = [get_by_cond(self.app, id, By.ID) for id in FIRST_IDS]
        for idx in range(3):
            elements[idx].send_keys(RAW_INPUTS[idx])

    def perform_save(self):
        button = get_by_cond(self.app, "save-products", By.ID)
        button.click()
        alert = WebDriverWait(self.app, 5).until(EC.alert_is_present())
        message = alert.text
        alert.accept()
        button = get_by_cond(self.app, "close-send-confirmation", By.ID)
        return message

    def find_save_file(self):
        file_path = None
        path = join(CFG.home, "data")
        for file in listdir(path):
            if (STORED_INPUTS[0] in file) and (STORED_INPUTS[1] in file):
                file_path = join(path, file)
                break
        return file_path

    def test_valid_save(self):
        self.fill_first_section()

        for idx, product in enumerate(CFG.products):
            scroll_to_product(self.app, product)
            section = get_by_cond(self.app, f"{product}-heading", By.ID)

            selector = [
                f'[id*="brand-{product}"]', f'[id*="price-{product}"]',
                f'[id*="quantity-{product}"]', f'[id*="obs-{product}"]']

            if idx < 9:
                for brd in section.find_elements(By.CSS_SELECTOR, selector[0]):
                    brd.send_keys(
                        brd.find_elements(By.TAG_NAME, 'option')[-1].text)
            for idx2, prc in enumerate(section.find_elements(By.CSS_SELECTOR, selector[1])):
                prc.send_keys(str(idx + (idx2 / 10)))
            if idx < 8:
                for i, qty in enumerate(
                    section.find_elements(By.CSS_SELECTOR, selector[2])
                ):
                    qty.send_keys(f"0.{idx}{i}")
            for obs in section.find_elements(By.CSS_SELECTOR, selector[3]):
                obs.send_keys(f"observation-{idx}")

        path = join(CFG.home, "data")
        for file in listdir(path):
            if (STORED_INPUTS[0] in file) and (STORED_INPUTS[1] in file):
                remove(join(path, file))

        button = get_by_cond(self.app, "save-products", By.ID)
        container = get_by_cond(self.app, "save-container", By.ID)
        assert check_in_attr(button, "class", "success")
        assert check_in_attr(container, "class", "unclickable", True)

    def test_full_save(self):
        message = self.perform_save()
        for line in message.splitlines():
            if "poucos itens" not in line:
                continue
            assert int(line.split(":")[-1].strip()) == 0, line
            break
        file_path = self.find_save_file()
        assert file_path is not None
        dataframe = pd.read_csv(file_path)

        assert len(dataframe) == 33, dataframe
        assert list(dataframe.Nome.unique()) == [STORED_INPUTS[0]], dataframe
        assert list(dataframe.Data.unique()) == [STORED_INPUTS[1]], dataframe
        assert list(dataframe.Estabelecimento.unique()) == [RAW_INPUTS[2]], dataframe
        assert list(dataframe.columns) == CSV_COLUMNS, dataframe.columns
        assert dataframe.Produto.value_counts().to_dict() == CFG.product_rows, dataframe
        assert float(dataframe.Preço.sum()) == 156.6, dataframe
        assert float(dataframe.Quantidade.sum()) == 15.85, dataframe
        assert float(dataframe.Preço.min()) == 0.0, dataframe
        assert float(dataframe.Preço.max()) == 12.0, dataframe
        assert float(dataframe.Quantidade.min()) == 0.0, dataframe
        assert float(dataframe.Quantidade.max()) == 1.0, dataframe
        remove(file_path)

    def test_animation(self):
        button = get_by_cond(self.app, "close-send-confirmation", By.ID)
        assert not check_logs(self.app, "Began confetti")
        button.click()

        assert WebDriverWait(self.app, 10).until(
            lambda d: check_logs(d, "Began confetti")
        ), self.app.get_log('browser')

    def test_cleared_contents(self):
        elements = [get_by_cond(self.app, id, By.ID) for id in FIRST_IDS]

        for element in elements:
            assert element.get_attribute("value") == ""
            assert check_in_attr(element, "class", "wrong")

        for product in CFG.products:
            section_div = get_by_cond(self.app, f"{product}-heading", By.ID)
            productElems = [section_div.find_elements(By.CSS_SELECTOR,
                f'[id*="{field}-{product}"]') for field in CFG.fields]
            assert len(productElems[1]) == CFG.product_rows[product], product

            for idx, elements in enumerate(productElems):
                for element in elements:
                    class_name = "wrong" if idx < 2 else "correct"
                    assert element.get_attribute("value") == ""
                    assert check_in_attr(element, "class", class_name)

    def test_yellow_badge(self):
        scroll_to_product(self.app, CFG.products[0], 2)
        self.fill_first_section()

        for product in CFG.products:
            scroll_to_product(self.app, product)
            elements = get_all_by_cond(self.app, f'[id*="delete-{product}"]', By.CSS_SELECTOR)
            badge = get_by_cond(self.app, f"status-{product}", By.ID)

            for element in elements:
                element.click()
            assert check_in_attr(badge, "class", "warning")

    def test_load_deletion(self):
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))

        for product in CFG.products:
            scroll_to_product(self.app, product)

            section_div = get_by_cond(self.app, f"{product}-heading", By.ID)
            productElems = section_div.find_elements(By.CSS_SELECTOR,
                f'[id*="price-{product}"]')
            assert len(productElems) == 0, product

    def test_empty_save(self):
        message = self.perform_save()
        for line in message.splitlines():
            if "poucos itens" not in line:
                continue
            assert int(line.split(":")[-1].strip()) == len(CFG.products), line
            break
        file_path = self.find_save_file()
        assert file_path is not None
        dataframe = pd.read_csv(file_path)
        assert dataframe.empty, dataframe
        assert list(dataframe.columns) == CSV_COLUMNS, dataframe.columns
        remove(file_path)
