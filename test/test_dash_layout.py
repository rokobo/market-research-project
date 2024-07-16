import sys
from os.path import join, dirname
from os import getenv
from itertools import zip_longest
import chromedriver_autoinstaller
from dotenv import load_dotenv

sys.path.append(join(dirname(dirname(__file__)), "src"))

from CONFIG import PRODUCT_ROWS, PRODUCTS, FIELDS

# Update/download chrome driver automatically, then add chromedriver to path
chromedriver_autoinstaller.install()
load_dotenv()

# Do note that you cannot get authenticated directly. TODO add to readme
# You need to try authentication, then re-load the page.
# That is because the browser saves the credentials as cookies.

FIRST_IDS = ["collector_name", "collection_date", "establishment"]
PROCESS_ARGS = dict(
    app_module="src.main", application_name="app", port=8060, start_timeout=10)
BASE_URL = "http://localhost:8060"
AUTHENTICATED_URL = BASE_URL.replace(
    "//", f"//{getenv("APP_USERNAME")}:{getenv("APP_PASSWORD")}@")
import time


def set_server(dash_br, dash_process_server):
    dash_process_server(**PROCESS_ARGS)
    dash_br.driver.get(AUTHENTICATED_URL)
    dash_br.driver.get(BASE_URL)
    dash_br.driver.set_window_position(10**4, 0)
    time.sleep(1)
    dash_br.wait_for_page(BASE_URL)
    dash_br.driver.get(BASE_URL)


def test_initial_first_section(dash_br, dash_process_server):
    set_server(dash_br, dash_process_server)

    for id in FIRST_IDS:
        dash_br.wait_for_element_by_id(id)
    elements = [dash_br.driver.find_element_by_id(id) for id in FIRST_IDS]

    for element in elements:
        assert element.get_attribute("value") == ""
        assert "wrong" in element.get_attribute("class")


def test_interaction_first_section(dash_br, dash_process_server):
    set_server(dash_br, dash_process_server)

    for id in FIRST_IDS:
        dash_br.wait_for_element_by_id(id)
    elements = [dash_br.driver.find_element_by_id(id) for id in FIRST_IDS]
    inputs = ["Name", "02112020", "AAA_TESTE"]

    for idx in range(3):
        elements[idx].send_keys(inputs[idx])
        dash_br.wait_for_element_by_id(FIRST_IDS[idx])
        for elem_idx in range(3):
            element = elements[elem_idx]
            if elem_idx > idx:
                assert element.get_attribute("value") == ""
                assert "wrong" in element.get_attribute("class")
            else:
                assert element.get_attribute("value") != ""
                assert "correct" in element.get_attribute("class")


def test_initial_second_section(dash_br, dash_process_server):
    set_server(dash_br, dash_process_server)

    products = [PRODUCTS[0], PRODUCTS[-1]]
    for product in products:
        section_div = dash_br.driver.find_element_by_id(f"{product}-heading")
        dash_br.wait_for_element(f'[id*="price-{product}"]')
        productElements = [section_div.find_elements_by_css_selector(
            f'[id*="{field}-{product}"]') for field in FIELDS]

        assert len(productElements[1]) == PRODUCT_ROWS[product], product
        for idx, elements in enumerate(productElements):
            for element in elements:
                class_name = "wrong" if idx < 2 else "correct"
                assert element.get_attribute("value") == ""
                assert class_name in element.get_attribute("class")


def test_interaction_second_section(dash_br, dash_process_server):
    set_server(dash_br, dash_process_server)

    for product in PRODUCTS:
        dash_br.wait_for_element(f'[id*="price-{product}"]')
        cells = dash_br.find_elements(f'[id*="price-{product}"]')
        dash_br.wait_for_element_by_id(f"status-{product}")
        dash_br.driver.execute_script("arguments[0].scrollIntoView(true);",
            dash_br.driver.find_element_by_id(f"status-{product}"))
        time.sleep(0.2)

        for idx, cell in enumerate(cells):
            cell.send_keys(10)
            for idx2, cell2 in enumerate(cells):
                class_name = "wrong" if idx2 > idx else "correct"
                assert class_name in cell2.get_attribute("class")


def test_deletion_second_section(dash_br, dash_process_server):
    set_server(dash_br, dash_process_server)

    for product in PRODUCTS:
        dash_br.wait_for_element(f'[id*="delete-{product}"]')
        elements = dash_br.find_elements(f'[id*="delete-{product}"]')
        dash_br.wait_for_element_by_id(f"status-{product}")
        badge = dash_br.driver.find_element_by_id(f"status-{product}")
        dash_br.driver.execute_script("arguments[0].scrollIntoView(true);", badge)
        time.sleep(0.15)

        assert "danger" in badge.get_attribute("class")
        for element in elements:
            element.click()
        assert "warning" in badge.get_attribute("class")


def test_correct_second_section(dash_br, dash_process_server):
    set_server(dash_br, dash_process_server)

    for idx, product in enumerate(PRODUCTS):
        section_div = dash_br.driver.find_element_by_id(f"{product}-heading")
        dash_br.wait_for_element(f'[id*="price-{product}"]')
        badge = section_div.find_element_by_id(f"status-{product}")
        dash_br.driver.execute_script("arguments[0].scrollIntoView(true);",
            badge)
        time.sleep(0.15)
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
