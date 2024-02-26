import re
from datetime import datetime
from itertools import count

from httpx import get
from parsel import Selector
from slugify import slugify

from imoveis_scraping.consts import STATES


class OLXBrowser:
    def get_infos(self, state, city, ad_type):
        state = list(STATES.keys())[list(STATES.values()).index(state)]
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'
        }
        result = {
            'Nome': [],
            'Endereço': [],
            'Dormitórios': [],
            'Banheiros': [],
            'Vagas': [],
            'Área Util': [],
            'Link': [],
            'Imagens': [],
            'Data': [],
        }
        response = get(
            f'https://www.olx.com.br/imoveis/{ad_type.lower()}/estado-{state}',
            headers=headers,
        )
        city_url = None
        urls = []
        for url in re.findall('"url":"(.+?)"', response.text, re.DOTALL):
            try:
                if re.findall('.+regiao-[^/]+', url, re.DOTALL)[0] == url:
                    urls.append(url)
            except IndexError:
                continue
        for region_url in urls:
            response = get(region_url, headers=headers)
            for url in re.findall('"url":"(.+?)"', response.text, re.DOTALL):
                if slugify(city) == url.split('/')[-1]:
                    city_url = url
        if city_url is None:
            return result
        for page in count(1):
            response = get(
                f'{city_url}?o={page}', headers=headers, timeout=10000
            )
            selector = Selector(response.text)
            if not selector.css('.sc-74d68375-2 .olx-ad-card__link-wrapper'):
                break
            for url in selector.css(
                '.sc-74d68375-2 .olx-ad-card__link-wrapper'
            ):
                response = get(
                    url.attrib['href'], headers=headers, timeout=10000
                )
                selector = Selector(response.text)
                address = ' - '.join(
                    [
                        e.get()
                        for e in selector.css('.ad__sc-o5hdud-2 span::text')
                    ]
                )
                result['Nome'].append(selector.css('.bdcWAn::text').get())
                result['Endereço'].append(address)
                result['Dormitórios'].append(
                    selector.css('.ad__sc-2h9gkk-3::text').get()
                )
                details = selector.css('.eYIDXs::text')
                if len(details) == 3:
                    result['Área Util'].append(details[0].get())
                    result['Banheiros'].append(details[1].get())
                    result['Vagas'].append(details[2].get())
                elif len(details) == 2 and re.findall(
                    r'\d+m', details[0].get()
                ):
                    result['Área Util'].append(details[0].get())
                    result['Banheiros'].append(details[1].get())
                    result['Vagas'].append('')
                elif len(details) == 2:
                    result['Área Util'].append('')
                    result['Banheiros'].append(details[0].get())
                    result['Vagas'].append(details[1].get())
                elif len(details) == 1:
                    result['Área Util'].append('')
                    result['Banheiros'].append(details[0].get())
                    result['Vagas'].append('')
                elif len(details) == 0:
                    result['Área Util'].append('')
                    result['Banheiros'].append('')
                    result['Vagas'].append('')
                result['Link'].append(url.attrib['href'])
                result['Imagens'].append(
                    ', '.join(
                        [e.attrib['src'] for e in selector.css('#gallery img')]
                    )
                )
                result['Data'].append(datetime.now().strftime('%d/%m/%Y'))
        return result
