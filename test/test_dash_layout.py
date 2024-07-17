import sys
from os.path import join, dirname
from os import getenv
import time
from dotenv import load_dotenv
import chromedriver_autoinstaller
from pytest import fixture, fail
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
BASE_URL = "http://127.0.0.1:8060"
AUTHENTICATED_URL = BASE_URL.replace(
    "//", f"//{getenv("APP_USERNAME")}:{getenv("APP_PASSWORD")}@")


@fixture(scope="module")
def gunicorn_server():
    command = ["gunicorn", "src.main:server", "-b", BASE_URL.split("//")[1]]
    process = subprocess.Popen(command)

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
    return


@fixture(scope="function")
def app():
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)

    driver.get(AUTHENTICATED_URL)
    WebDriverWait(driver, 10).until(EC.title_is("ICB"))
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.title_is("ICB"))
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.title_is("ICB"))

    yield driver

    driver.quit()
    return


def get_by_cond(driver, id, cond=By.ID, all=False):
    if all:
        return WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((cond, id)))
    return WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((cond, id)))


def test_initial_first_section(gunicorn_server, app):
    elements = [get_by_cond(app, id, By.ID) for id in FIRST_IDS]

    for element in elements:
        assert element.get_attribute("value") == ""
        assert "wrong" in element.get_attribute("class")


def test_interaction_first_section(gunicorn_server, app):
    elements = [get_by_cond(app, id, By.ID) for id in FIRST_IDS]
    inputs = ["Name", "02112020", "AAA_TESTE"]

    for idx in range(3):
        elements[idx].send_keys(inputs[idx])
        get_by_cond(app, FIRST_IDS[idx], By.ID)

        for elem_idx in range(3):
            element = elements[elem_idx]
            if elem_idx > idx:
                assert element.get_attribute("value") == ""
                assert "wrong" in element.get_attribute("class")
            else:
                assert element.get_attribute("value") != ""
                assert "correct" in element.get_attribute("class")


def test_initial_second_section(gunicorn_server, app):
    products = [CFG.products[0], CFG.products[-1]]
    get_by_cond(app, '[id*="price-"]', By.CSS_SELECTOR, True)

    for product in products:
        section_div = get_by_cond(app, f"{product}-heading", By.ID)
        productElements = [section_div.find_elements_by_css_selector(
            f'[id*="{field}-{product}"]') for field in CFG.fields]
        assert len(productElements[1]) == CFG.product_rows[product], product

        for idx, elements in enumerate(productElements):
            for element in elements:
                class_name = "wrong" if idx < 2 else "correct"
                assert element.get_attribute("value") == ""
                assert class_name in element.get_attribute("class")


def test_interaction_second_section(gunicorn_server, app):
    for product in CFG.products:
        prices = get_by_cond(
            app, f'[id*="price-{product}"]', By.CSS_SELECTOR, True)
        app.execute_script(
            "arguments[0].scrollIntoView(true);",
            get_by_cond(app, f"status-{product}", By.ID))
        time.sleep(0.2)

        for idx, current_price in enumerate(prices):
            current_price.send_keys(10)
            for idx2, price in enumerate(prices):
                class_name = "wrong" if idx2 > idx else "correct"
                assert class_name in price.get_attribute("class")


def test_deletion_second_section(gunicorn_server, app):
    for product in CFG.products:
        elements = get_by_cond(
            app, f'[id*="delete-{product}"]', By.CSS_SELECTOR, True)
        badge = get_by_cond(app, f"status-{product}", By.ID)
        app.execute_script("arguments[0].scrollIntoView(true);", badge)
        time.sleep(0.2)

        assert "danger" in badge.get_attribute("class")
        for element in elements:
            element.click()
        assert "warning" in badge.get_attribute("class")


def test_correct_second_section(gunicorn_server, app):
    for idx, product in enumerate(CFG.products):
        section_div = get_by_cond(app, f"{product}-heading", By.ID)
        badge = get_by_cond(app, f"status-{product}", By.ID)
        app.execute_script("arguments[0].scrollIntoView(true);", badge)
        time.sleep(0.2)

        assert "danger" in badge.get_attribute("class")
        selector = [
            f'[id*="brand-{product}"]', f'[id*="price-{product}"]',
            f'[id*="quantity-{product}"]', f'[id*="obs-{product}"]']

        if idx < 9:
            for brd in section_div.find_elements_by_css_selector(selector[0]):
                brd.send_keys(brd.find_elements_by_tag_name('option')[-1].text)
        for prc in section_div.find_elements_by_css_selector(selector[1]):
            prc.send_keys(20)
        if idx < 8:
            for qty in section_div.find_elements_by_css_selector(selector[2]):
                qty.send_keys(1.9)
        if idx > 8:
            for obs in section_div.find_elements_by_css_selector(selector[3]):
                obs.send_keys("observation")

        assert "success" in badge.get_attribute("class")
