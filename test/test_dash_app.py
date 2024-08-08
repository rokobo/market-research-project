# flake8: noqa: E501
import sys
from os.path import join, dirname
from os import getenv, listdir, remove
import time
from typing import Optional
from dotenv import load_dotenv
import chromedriver_autoinstaller
from pytest import fixture, fail, mark
import requests
from datetime import datetime
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, TimeoutException
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


@fixture(scope="class")
def selenium_driver(request):
    # Start Gunicorn server
    BASE_URL = f"http://127.0.0.1:806{int(request.cls.__name__[4:7])}"
    AUTHENTICATED_URL = BASE_URL.replace(
        "//", f"//{getenv('APP_USERNAME')}:{getenv('APP_PASSWORD')}@")

    log_file = open("gunicorn.log", "w")
    command = [
        "gunicorn", "src.main:server",
        "-b", BASE_URL.split("//")[1],
        "-w", "1"]
    process = subprocess.Popen(command, stdout=log_file, stderr=log_file)

    # Wait for the server to start
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

    # Set up Selenium driver
    options = webdriver.ChromeOptions()
    options.set_capability("goog:loggingPrefs", {"browser": "ALL"})
    driver = webdriver.Chrome(options=options)

    # Access the app
    driver.get(AUTHENTICATED_URL)
    WebDriverWait(driver, 10).until(EC.title_is("ICB"))
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.title_is("ICB"))
    for _ in range(5):
        try:
            driver.refresh()
            WebDriverWait(driver, 10).until(EC.title_is("ICB"))
            wait_substring(driver, "online-badge", By.ID, "LINE", wait=2)
            break
        except:
            time.sleep(1)
    else:
        fail("Failed to start server, ONLINE badge not present")

    yield driver

    # Tear down
    driver.quit()
    process.terminate()
    process.wait()
    log_file.close()


def get_by_cond(driver: webdriver.Chrome, id: str, cond) -> WebElement:
    return WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((cond, id)))


def get_all_by_cond(driver: webdriver.Chrome, id: str, cond) -> list[WebElement]:
    return WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((cond, id)))


def wait_substring(
    driver: webdriver.Chrome, id: str, cond, substring: str, wait=10,
    attr=None, value=False
) -> WebElement:
    if attr is not None:
        WebDriverWait(driver, wait).until(
            EC.text_to_be_present_in_element_attribute(
                (cond, id), attr, substring))
    elif value:
        WebDriverWait(driver, wait).until(
            EC.text_to_be_present_in_element_value((cond, id), substring))
    else:
        WebDriverWait(driver, wait).until(
            EC.text_to_be_present_in_element((cond, id), substring))
    return get_by_cond(driver, id, cond)


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


def scroll_to_coordinate(driver, coordinate, extra_delay=0.0):
    driver.execute_script(
        f"document.documentElement.scrollTop = {coordinate - 60};")
    time.sleep(0.25 + extra_delay)


def scroll_to_product(driver, product, extra_delay=0.0):
    y_coord = get_by_cond(driver, f'{product}-heading', By.ID).location['y']
    scroll_to_coordinate(driver, y_coord, extra_delay)


def element_in_viewport(driver, element):
    top = driver.execute_script("return window.scrollY")
    bottom = top + driver.execute_script("return window.innerHeight")
    element_top = element.location['y']
    return top < element_top < bottom


def check_logs(driver, message):
    logs = driver.get_log('browser')
    for log in logs:
        if message in log['message']:
            return True
    return False


def wait_interactable(driver: webdriver.Chrome, element: WebElement, wait=2):
    for _ in range(3):
        try:
            WebDriverWait(driver, wait).until(EC.element_to_be_clickable(element))
            WebDriverWait(driver, wait).until(EC.visibility_of(element))
            assert element_in_viewport(driver, element)
            return
        except Exception:
            scroll_to_coordinate(driver, element.location['y'], 0.25)
    msg = "wait_interactable failed: "
    top = driver.execute_script("return window.scrollY")
    bottom = top + driver.execute_script("return window.innerHeight")
    msg += f"{element.location['y']}, [{top}, {bottom}]"
    fail(msg)


def send_click(driver: webdriver.Chrome, element: WebElement):
    wait_interactable(driver, element)
    element.click()


def send_input(driver: webdriver.Chrome, element: WebElement, keys: str):
    for _ in range(3):
        wait_interactable(driver, element)
        element.send_keys(keys)
        if element.get_attribute("value"):
            break


def fill_first_section(driver, date=False):
    elements = [get_by_cond(driver, id, By.ID) for id in FIRST_IDS]
    for idx, element in enumerate(elements):
        input_val = datetime.now().strftime('%m%d%Y') if ((idx == 1) and date) else RAW_INPUTS[idx]
        stored_val = datetime.now().strftime('%Y-%m-%d') if ((idx == 1) and date) else STORED_INPUTS[idx]
        try:
            wait_interactable(driver, element)
            if idx != 2:
                element.clear()
            send_input(driver, element, input_val)
            assert wait_substring(driver, FIRST_IDS[idx], By.ID, stored_val, value=True, wait=2)
        except TimeoutException:
            pass


def perform_save(driver: webdriver.Chrome) -> str:
    for file in listdir(CFG.data_obs):
        remove(join(CFG.data_obs, file))
    for file in listdir(CFG.data):
        remove(join(CFG.data, file))
    button = get_by_cond(driver, "save-products", By.ID)
    send_click(driver, button)
    alert = WebDriverWait(driver, 5).until(EC.alert_is_present())
    message = alert.text
    alert.accept()
    button = get_by_cond(driver, "close-send-confirmation", By.ID)
    return message


def find_saved_file(driver: webdriver.Chrome, path="data") -> Optional[str]:
    file_path = None
    path = join(CFG.home, path)
    for file in listdir(path):
        for substring in STORED_INPUTS:
            if substring not in file:
                continue
        file_path = join(path, file)
        break
    return file_path


def get_storage(driver: webdriver.Chrome, name: str):
    return driver.execute_script(
        "return JSON.parse(window.localStorage.getItem(arguments[0]));", name)


def clear_storage(driver: webdriver.Chrome, name: str):
    return driver.execute_script(
        "return window.localStorage.removeItem(arguments[0]);", name)

@mark.incremental
class Test001FirstSection:
    @fixture(autouse=True)
    def setup_class(self, selenium_driver):
        self.app = selenium_driver
        self.elements = [get_by_cond(self.app, id, By.ID) for id in FIRST_IDS]

    def test_initial_state(self):
        for element in self.elements:
            assert element.get_attribute("value") == ""
            assert check_in_attr(element, "class", "wrong")

    def test_interaction(self):
        for idx in range(3):
            send_input(self.app, self.elements[idx], RAW_INPUTS[idx])
            assert wait_substring(self.app, FIRST_IDS[idx], By.ID, STORED_INPUTS[idx], value=True)

            for elem_idx in range(3):
                element = self.elements[elem_idx]
                value = element.get_attribute("value")
                if elem_idx > idx:
                    assert value == "", value
                    assert check_in_attr(element, "class", "wrong")
                else:
                    assert value != ""
                    assert check_in_attr(element, "class", "correct")

    def test_load(self):
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))

        self.elements = [get_by_cond(self.app, id, By.ID) for id in FIRST_IDS]
        for element, value in zip(self.elements, STORED_INPUTS):
            assert check_in_attr(element, "class", "correct")
            assert element.get_attribute("value") == value

    def test_mass_load(self):
        for _ in range(5):
            self.app.refresh()
            time.sleep(0.1)
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))

        self.elements = [get_by_cond(self.app, id, By.ID) for id in FIRST_IDS]
        for element, value in zip(self.elements, STORED_INPUTS):
            assert check_in_attr(element, "class", "correct")
            assert element.get_attribute("value") == value


@mark.incremental
class Test002SecondSection:
    @fixture(autouse=True)
    def setup_class(self, selenium_driver):
        self.app = selenium_driver

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

    def test_red_icon(self):
        for product in CFG.products:
            icon = get_by_cond(self.app, f"icon-{product}", By.ID)
            assert check_in_attr(icon, "style", "red")

    def test_interaction(self):
        for idx0, product in enumerate(CFG.products):
            scroll_to_product(self.app, product, 2 if idx0 == 0 else 0)
            prices = get_all_by_cond(
                self.app, f'[id*="price-{product}"]', By.CSS_SELECTOR)

            for idx, current_price in enumerate(prices):
                send_input(self.app, current_price, str(idx0 + (idx / 10)))
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
                    send_input(self.app, brd, brd.find_elements(By.TAG_NAME, 'option')[-1].text)
            if idx < 8:
                for i, qty in enumerate(
                    section.find_elements(By.CSS_SELECTOR, selector[1])
                ):
                    send_input(self.app, qty, f"0.{idx}{i}")
            if idx > 8:
                for obs in section.find_elements(By.CSS_SELECTOR, selector[2]):
                    send_input(self.app, obs, f"observation-{idx}")
            assert check_in_attr(badge, "class", "success")

    def test_green_icon(self):
        for product in CFG.products:
            icon = get_by_cond(self.app, f"icon-{product}", By.ID)
            assert check_in_attr(icon, "style", "green")

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
    def setup_class(self, selenium_driver):
        self.app = selenium_driver

    def test_valid_save(self):
        fill_first_section(self.app, True)

        for idx, product in enumerate(CFG.products):
            scroll_to_product(self.app, product)
            section = get_by_cond(self.app, f"{product}-heading", By.ID)

            selector = [
                f'[id*="brand-{product}"]', f'[id*="price-{product}"]',
                f'[id*="quantity-{product}"]', f'[id*="obs-{product}"]']

            if idx < 9:
                for brd in section.find_elements(By.CSS_SELECTOR, selector[0]):
                    send_input(self.app, brd, brd.find_elements(By.TAG_NAME, 'option')[-1].text)
            for idx2, prc in enumerate(section.find_elements(By.CSS_SELECTOR, selector[1])):
                send_input(self.app, prc, str(idx + (idx2 / 10)))
            if idx < 8:
                for i, qty in enumerate(
                    section.find_elements(By.CSS_SELECTOR, selector[2])
                ):
                    send_input(self.app, qty, f"0.{idx}{i}")
            for obs in section.find_elements(By.CSS_SELECTOR, selector[3]):
                send_input(self.app, obs, f"observation-{idx}")

        for path in ["data", "data_obs"]:
            file_path = find_saved_file(self.app, path)
            while file_path is not None:
                remove(file_path)
                file_path = find_saved_file(self.app, path)

        assert wait_substring(self.app, "save-products", By.ID, "success", attr="class")
        container = get_by_cond(self.app, "save-container", By.ID)
        assert check_in_attr(container, "class", "unclickable", True)

        observation = get_by_cond(self.app, "general_observations", By.ID)
        send_input(self.app, observation, "Test observation")
        assert check_in_attr(observation, "value", "Test observation")

    def test_no_messages(self):
        messages = perform_save(self.app).splitlines()
        assert any("poucos itens" in string for string in messages), messages
        assert not any("Envio em dia diferente" in string for string in messages), messages

        for line in messages:
            if "poucos itens" in line:
                assert int(line.split(":")[-1].strip()) == 0, line
                break

    def test_full_save(self):
        file_path = find_saved_file(self.app, "data")
        assert file_path is not None
        dataframe = pd.read_csv(file_path)

        assert len(dataframe) == 33, dataframe
        assert list(dataframe.Nome.unique()) == [STORED_INPUTS[0]], dataframe
        assert list(dataframe.Data.unique()) == [datetime.now().strftime('%Y-%m-%d')], dataframe
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

        obs_path = find_saved_file(self.app, "data_obs")
        assert obs_path is not None
        with open(obs_path, 'r') as file:
            observations = file.read()
        assert "Test observation" in observations
        remove(obs_path)

    def test_animation(self):
        button = get_by_cond(self.app, "close-send-confirmation", By.ID)
        assert not check_logs(self.app, "Began confetti")
        send_click(self.app, button)

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
        fill_first_section(self.app)

        for product in CFG.products:
            scroll_to_product(self.app, product)
            elements = get_all_by_cond(self.app, f'[id*="delete-{product}"]', By.CSS_SELECTOR)
            badge = get_by_cond(self.app, f"status-{product}", By.ID)

            for element in elements:
                send_click(self.app, element)
            assert check_in_attr(badge, "class", "warning")

    def test_yellow_icon(self):
        for product in CFG.products:
            icon = get_by_cond(self.app, f"icon-{product}", By.ID)
            assert check_in_attr(icon, "style", "rgb(252, 174, 30)")

    def test_load_deletion(self):
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))

        for product in CFG.products:
            scroll_to_product(self.app, product)

            section_div = get_by_cond(self.app, f"{product}-heading", By.ID)
            productElems = section_div.find_elements(By.CSS_SELECTOR,
                f'[id*="price-{product}"]')
            assert len(productElems) == 0, product

    def test_all_messages(self):
        messages = perform_save(self.app).splitlines()
        assert any("poucos itens" in string for string in messages), messages
        assert any("Envio em dia diferente" in string for string in messages), messages
        assert any("Data atual:" in string for string in messages), messages
        assert any("Registrado:" in string for string in messages), messages
        today = None

        for line in messages:
            if "poucos itens" in line:
                assert int(line.split(":")[-1].strip()) == len(CFG.products), line
            if "Data atual" in line:
                today = line.split(":")[-1].strip()
                assert len(today) == 10, today
            if "Registrado" in line:
                registered = line.split(":")[-1].strip()
                assert len(registered) == 10, registered
                assert today != registered, (today, registered)

    def test_empty_save(self):
        file_path = find_saved_file(self.app, "data")
        assert file_path is not None
        dataframe = pd.read_csv(file_path)
        assert dataframe.empty, dataframe
        assert list(dataframe.columns) == CSV_COLUMNS, dataframe.columns
        remove(file_path)
        obs_path = find_saved_file(self.app, "data_obs")
        assert obs_path is not None
        with open(obs_path, 'r') as file:
            observations = file.read()
        assert "Sem observações" in observations
        remove(obs_path)


@mark.incremental
class Test004AuxiliaryFunctions:
    @fixture(autouse=True)
    def setup_class(self, selenium_driver):
        self.app = selenium_driver

    def test_clear_contents(self):
        for idx, product in enumerate(CFG.products):
            scroll_to_product(self.app, product)
            prices = get_all_by_cond(
                self.app, f'[id*="price-{product}"]', By.CSS_SELECTOR)
            for price in prices:
                send_input(self.app, price, "1")

        fill_first_section(self.app)
        button = get_by_cond(self.app, "clear-products", By.ID)
        wait_interactable(self.app, button)
        send_click(self.app, button)
        alert = WebDriverWait(self.app, 5).until(EC.alert_is_present())
        alert.accept()
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))

        for idx, product in enumerate(CFG.products):
            scroll_to_product(self.app, product, 2 if idx == 0 else 0)
            prices = get_all_by_cond(
                self.app, f'[id*="price-{product}"]', By.CSS_SELECTOR)
            for price in prices:
                assert price.get_attribute("value") == ""

    def test_navigation(self):
        scroll_command = "return document.documentElement.scrollTop;"
        self.app.set_window_size(self.app.get_window_size()["width"], 500)
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))
        old_posY = self.app.execute_script(scroll_command)
        old_url = self.app.current_url
        for product in CFG.products:
            icon = get_by_cond(self.app, f"icon-{product}", By.ID)
            send_click(self.app, icon)
            time.sleep(1)
            posY = self.app.execute_script(scroll_command)
            url = self.app.current_url
            assert posY > old_posY, product
            assert url != old_url, product
            old_posY, old_url = posY, url


@mark.incremental
class Test005Geolocation:
    locs=[
        {"latitude": -22.90941581120983, "longitude": -47.09562084004908, "accuracy": 1},
        {"latitude": -22.909484367468764, "longitude": -47.0956975543658, "accuracy": 1},
        {"latitude": -22.910638316402963, "longitude": -47.09626919284236, "accuracy": 1},
        {"latitude": -22.915114994305828, "longitude": -47.09577448705569, "accuracy": 1}
    ]

    @fixture(autouse=True)
    def setup_class(self, selenium_driver):
        self.app = selenium_driver

    def test_no_error(self):
        self.app.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": -22.84858326747608,
            "longitude": -47.018732241496316,
            "accuracy": 1
        })
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))
        button = get_by_cond(self.app, "fill-establishment", By.ID)
        send_click(self.app, button)
        dist = wait_substring(
            self.app, "establishment-subformtext", By.ID, "km", 5)
        dist = float(dist.text.split(":")[1].split("km")[0])
        assert 0.95 <= dist <= 1.05, dist
        establishment = get_by_cond(self.app, FIRST_IDS[2], By.ID)
        assert check_in_attr(establishment, "value", "CRF-DPE")

    def test_50m_error(self):
        self.app.execute_cdp_cmd("Emulation.setGeolocationOverride", {
            "latitude": -22.90941581120983,
            "longitude": -47.09562084004908,
            "accuracy": 1
        })
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))
        button = get_by_cond(self.app, "fill-establishment", By.ID)
        send_click(self.app, button)
        dist = wait_substring(
            self.app, "establishment-subformtext", By.ID, "km", 5)
        dist = float(dist.text.split(":")[1].split("km")[0])
        assert 0.01 <= dist <= 0.09, dist
        establishment = get_by_cond(self.app, FIRST_IDS[2], By.ID)
        assert check_in_attr(establishment, "value", "ENX-JB")

    def test_load(self):
        clear_storage(self.app, "geo-history")
        loc = self.locs[0]
        self.app.execute_cdp_cmd("Emulation.setGeolocationOverride", loc)
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))
        time.sleep(1)

        history = get_storage(self.app, "geo-history")
        assert len(history) == 1, history
        assert history[0][0] == loc["latitude"]
        assert history[0][1] == loc["longitude"]

    def test_badge(self):
        loc = self.locs[0]
        badge = wait_substring(self.app, "geolocation-badge", By.ID, ",").text
        assert badge == f"{round(loc["latitude"], 4)}, {round(loc["longitude"], 4)}"

    def test_10m_shift(self):
        loc = self.locs[1]
        self.app.execute_cdp_cmd("Emulation.setGeolocationOverride", loc)
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))
        time.sleep(1)

        history = get_storage(self.app, "geo-history")
        assert len(history) == 1, history
        assert history[0][0:2] != [loc["latitude"], loc["longitude"]]

    def test_150m_shift(self):
        loc = self.locs[2]
        self.app.execute_cdp_cmd("Emulation.setGeolocationOverride", loc)
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))
        time.sleep(1)

        history = get_storage(self.app, "geo-history")
        assert len(history) == 2, history
        assert history[1][0] == loc["latitude"]
        assert history[1][1] == loc["longitude"]

    def test_500m_shift(self):
        loc = self.locs[3]
        self.app.execute_cdp_cmd("Emulation.setGeolocationOverride", loc)
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))
        time.sleep(1)

        history = get_storage(self.app, "geo-history")
        assert len(history) == 3, history
        assert history[2][0] == loc["latitude"]
        assert history[2][1] == loc["longitude"]

    def test_no_permission(self):
        self.app.execute_cdp_cmd("Emulation.setGeolocationOverride", {})
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))
        assert wait_substring(self.app, "geo-loading-modal", By.ID, "tente novamente", 5)

    def test_0m_shift(self):
        loc = self.locs[3]
        self.app.execute_cdp_cmd("Emulation.setGeolocationOverride", loc)
        self.app.refresh()
        WebDriverWait(self.app, 10).until(EC.title_is("ICB"))
        time.sleep(1)

        history = get_storage(self.app, "geo-history")
        assert len(history) == 3, history
        assert history[2][0] == loc["latitude"]
        assert history[2][1] == loc["longitude"]

    def test_save_filename(self):
        loc = self.locs[3]
        fill_first_section(self.app)
        for product in CFG.products:
            scroll_to_product(self.app, product)
            elements = get_all_by_cond(self.app, f'[id*="delete-{product}"]', By.CSS_SELECTOR)
            for element in elements:
                send_click(self.app, element)
            time.sleep(0.2)
        perform_save(self.app)
        file_name = find_saved_file(self.app, "data")
        assert file_name is not None
        fields = file_name.split("|")
        assert len(fields) == 6, fields
        assert fields[4] == str(loc["latitude"]), fields
        assert fields[5].replace(".csv", "") == str(loc["longitude"]), fields
        remove(file_name)

    def test_obs_file(self):
        file_name = find_saved_file(self.app, "data_obs")
        assert file_name is not None
        with open(file_name, 'r') as file:
            observations = file.readlines()
        assert "Histórico de geolocalização" == observations[2].strip()
        locs = self.locs
        locs.pop(1)
        for i, obs in enumerate(observations[3:]):
            geo = self.locs[i]
            assert f"{geo["latitude"]}, {geo["longitude"]}" in obs, i
