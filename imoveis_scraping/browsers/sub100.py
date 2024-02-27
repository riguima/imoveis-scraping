from datetime import datetime
from itertools import count

from selenium.common.exceptions import (ElementClickInterceptedException,
                                        StaleElementReferenceException,
                                        TimeoutException)
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from slugify import slugify
from webdriver_manager.chrome import ChromeDriverManager

from imoveis_scraping.consts import STATES


class Sub100Browser:
    def __init__(self):
        options = Options()
        self.driver = Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def get_infos(self, state, city, ad_type, page):
        state = list(STATES.keys())[list(STATES.values()).index(state)]
        urls = []
        result = {
            'Nome': [],
            'Endereço': [],
            'Dormitórios': [],
            'Banheiros': [],
            'Vagas': [],
            'Área Privativa': [],
            'Área Total': [],
            'Link': [],
            'Imagens': [],
            'Data': [],
        }
        ad_type = 'locacao' if ad_type == 'Aluguel' else ad_type
        self.driver.get(
            f'https://sub100.com.br/imoveis/{ad_type.lower()}/residenciais/{slugify(city)}-{state}/pagina-{page}'
        )
        try:
            self.find_elements('.result--body')
        except TimeoutException:
            return result
        while True:
            try:
                for ad in self.find_elements('.result--body'):
                    urls.append(
                        self.find_element('a', element=ad).get_attribute(
                            'href'
                        )
                    )
                break
            except StaleElementReferenceException:
                continue
        for url in urls:
            self.driver.get(url)
            while self.find_element('.title').text == '':
                continue
            result['Nome'].append(self.find_element('.title').text)
            result['Endereço'].append(
                ' - '.join(
                    e.text for e in self.find_elements('.col-12 h2')[:2]
                )
            )
            labels = []
            details = [
                'Dormitórios',
                'Banheiros',
                'Vagas',
                'Área Privativa',
                'Área Total',
            ]
            for detail in self.find_elements('.flex-50 .col-12'):
                label = self.find_element('label', element=detail).text.title()
                if label in details:
                    value = self.find_element('span', element=detail).text
                    labels.append(label)
                    result[label].append(value)
            for detail in details:
                if detail not in labels:
                    result[detail].append('')
            result['Link'].append(url)
            while True:
                try:
                    self.find_element('.btn-gallery').click()
                    break
                except ElementClickInterceptedException:
                    continue
            images_urls = []
            for image in count(0):
                try:
                    images_urls.append(
                        self.find_element(
                            f'#image-{image}', wait=5
                        ).get_attribute('src')
                    )
                except TimeoutException:
                    result['Imagens'].append(', '.join(images_urls))
                    break
            result['Data'].append(datetime.now().strftime('%d/%m/%Y'))
        return result

    def find_element(self, selector, element=None, wait=10):
        return WebDriverWait(element or self.driver, wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def find_elements(self, selector, element=None, wait=10):
        return WebDriverWait(element or self.driver, wait).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
        )
