import os
import re
from datetime import datetime
from itertools import count

from httpx import get
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
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        self.driver = Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def get_infos(
        self,
        state,
        city,
        ad_type,
        property_type,
        sub_type,
        page,
        ads_count,
        folder,
    ):
        state = list(STATES.keys())[list(STATES.values()).index(state)]
        urls = []
        result = {
            'Elemento Amostral': [],
            'Código Do Anúncio': [],
            'Data': [],
            'Tipo': [],
            'Sub-Tipo': [],
            'Nome Do Anúncio': [],
            'Descrição': [],
            'Endereço': [],
            'Nome Contato': [],
            'Telefone Contato': [],
            'Bairro': [],
            'Dormitórios': [],
            'Suítes': [],
            'Quartos': [],
            'Banheiros': [],
            'Vagas': [],
            'Área Privativa': [],
            'Área Total': [],
            'Área Do Terreno': [],
            'Pavimentos': [],
            'Unidades': [],
            'Torres': [],
            'Andares': [],
            'Items Condomínio': [],
            'Link': [],
            'Imagens': [],
            'Valor': [],
            'Valor Unitário': [],
        }
        ad_type = 'locacao' if ad_type == 'Aluguel' else ad_type
        if sub_type == 'Todos':
            self.driver.get(
                f'https://sub100.com.br/imoveis/{ad_type.lower()}/{slugify(property_type)}/{slugify(city)}-{state}/pagina-{page}'
            )
        else:
            self.driver.get(
                f'https://sub100.com.br/imoveis/{ad_type.lower()}/{slugify(sub_type)}/{slugify(city)}-{state}/pagina-{page}'
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
        for e, url in enumerate(urls):
            if e == ads_count and ads_count != 0:
                break
            self.driver.get(url)
            while self.find_element('.title').text == '':
                continue
            result['Elemento Amostral'].append(
                f'EA{len(result["Elemento Amostral"]) + 1}'
            )
            result['Código Do Anúncio'].append(
                re.findall(r'imoveis/(.+?)/', self.driver.current_url)[0]
            )
            result['Nome Do Anúncio'].append(self.find_element('.title').text)
            result['Descrição'].append(self.find_element('p.mt-3').text)
            result['Endereço'].append(
                ' - '.join(
                    e.text for e in self.find_elements('.col-12 h2')[:2]
                )
            )
            result['Nome Contato'].append(
                self.find_element('#__BVID__112 h5').text
            )
            try:
                result['Telefone Contato'].append(
                    self.find_element('.btn-outline-success', wait=5).text
                )
            except TimeoutException:
                result['Telefone Contato'].append(
                    self.find_element('a .btn-outline-primary', wait=5).text
                )
            result['Bairro'].append(
                self.find_elements('.col-12 h2')[1].text.split(',')[0]
            )
            labels = []
            details = [
                key
                for key in result
                if key
                not in [
                    'Elemento Amostral',
                    'Código Do Anúncio',
                    'Nome Do Anúncio',
                    'Descrição',
                    'Endereço',
                    'Nome Contato',
                    'Telefone Contato',
                    'Bairro',
                    'Suítes',
                    'Quartos',
                    'Valor',
                    'Valor Unitário',
                    'Items Condomínio',
                    'Link',
                    'Imagens',
                    'Data',
                    'Tipo',
                    'Sub-Tipo',
                ]
            ]
            try:
                for detail in self.find_elements('.flex-50 .col-12', wait=5):
                    label = self.find_element(
                        'label', element=detail
                    ).text.title()
                    if label in details:
                        try:
                            value = int(
                                self.find_element('span', element=detail).text
                            )
                        except ValueError:
                            value = self.find_element(
                                'span', element=detail
                            ).text
                            if 'm²' in value:
                                value = float(
                                    value.split(' ')[0].replace(',', '.')
                                )
                        labels.append(label)
                        result[label].append(value)
            except TimeoutException:
                pass
            for detail in details:
                if detail not in labels:
                    result[detail].append('')
            suits = re.findall(r'(\d+) Suíte', result['Dormitórios'][-1])
            bedrooms = re.findall(r'(\d+) Quarto', result['Dormitórios'][-1])
            if suits:
                result['Suítes'].append(int(suits[0]))
            else:
                result['Suítes'].append('')
            if bedrooms:
                result['Quartos'].append(int(bedrooms[0]))
            else:
                result['Quartos'].append('')
            have_condominium_items = False
            for select in self.find_elements('.select-container'):
                text = self.find_element('.text-primary', element=select).text
                if text == 'Meu Condomínio':
                    result['Items Condomínio'].append(
                        str(
                            len(
                                self.find_elements(
                                    '.align-items-center', element=select
                                )
                            )
                        )
                    )
                    have_condominium_items = True
                elif 'Valor' in text:
                    value = self.find_elements(
                        '.text-primary', element=select
                    )[1].text
                    result['Valor'].append(
                        float(value[3:].replace('.', '').replace(',', '.'))
                    )
                    for area in [result['Área Privativa'][-1], result['Área Do Terreno'][-1], result['Área Total'][-1]]:
                        if area != '':
                            result['Valor Unitário'].append(round(result['Valor'][-1] / area, 2))
                            break
            if not have_condominium_items:
                result['Items Condomínio'].append('0')
            result['Link'].append(url)
            have_images = True
            while True:
                try:
                    self.find_element('.btn-gallery').click()
                    break
                except ElementClickInterceptedException:
                    continue
                except TimeoutException:
                    have_images = False
                    break
            if have_images:
                images_urls = []
                for image in count(0):
                    try:
                        image_url = self.find_element(
                            f'#image-{image}', wait=3
                        ).get_attribute('src')
                        images_urls.append(image_url)
                        os.makedirs(
                            f'{folder}/{result["Código Do Anúncio"][-1]}',
                            exist_ok=True,
                        )
                        with open(
                            f'{folder}/{result["Código Do Anúncio"][-1]}/image-{image}{image_url[-4:]}',
                            'wb',
                        ) as f:
                            f.write(get(image_url).content)
                    except TimeoutException:
                        result['Imagens'].append(', '.join(images_urls))
                        break
            else:
                result['Imagens'].append('')
            result['Data'].append(datetime.now().strftime('%d/%m/%Y'))
            result['Tipo'].append(property_type.title())
            result['Sub-Tipo'].append(
                self.find_elements('div.d-lg-block a')[-1].get_attribute(
                    'textContent'
                )
            )
        return result

    def find_element(self, selector, element=None, wait=10):
        return WebDriverWait(element or self.driver, wait).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )

    def find_elements(self, selector, element=None, wait=10):
        return WebDriverWait(element or self.driver, wait).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
        )
