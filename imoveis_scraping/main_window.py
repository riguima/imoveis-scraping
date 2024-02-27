from itertools import count
from pathlib import Path

import pandas as pd
from PySide6 import QtCore, QtWidgets

from imoveis_scraping.browsers.olx import OLXBrowser
from imoveis_scraping.browsers.sub100 import Sub100Browser
from imoveis_scraping.consts import STATES


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(300, 300)
        with open('styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

        self.message_box = QtWidgets.QMessageBox()

        self.website_label = QtWidgets.QLabel('Site:')
        self.website_combobox = QtWidgets.QComboBox()
        self.website_combobox.addItems(['Sub100', 'OLX'])
        self.website_layout = QtWidgets.QHBoxLayout()
        self.website_layout.addWidget(self.website_label)
        self.website_layout.addWidget(self.website_combobox)

        self.state_label = QtWidgets.QLabel('Estado:')
        self.state_combobox = QtWidgets.QComboBox()
        self.state_combobox.addItems(list(STATES.values()))
        self.state_layout = QtWidgets.QHBoxLayout()
        self.state_layout.addWidget(self.state_label)
        self.state_layout.addWidget(self.state_combobox)

        self.city_label = QtWidgets.QLabel('Cidade:')
        self.city_input = QtWidgets.QLineEdit()
        self.city_layout = QtWidgets.QHBoxLayout()
        self.city_layout.addWidget(self.city_label)
        self.city_layout.addWidget(self.city_input)

        self.type_label = QtWidgets.QLabel('Tipo:')
        self.type_combobox = QtWidgets.QComboBox()
        self.type_combobox.addItems(['Venda', 'Aluguel'])
        self.type_layout = QtWidgets.QHBoxLayout()
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_combobox)

        self.generate_spreadsheet_button = QtWidgets.QPushButton(
            'Gerar Planilha'
        )
        self.generate_spreadsheet_button.clicked.connect(
            self.generate_spreadsheet
        )

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(self.website_layout)
        self.main_layout.addLayout(self.state_layout)
        self.main_layout.addLayout(self.city_layout)
        self.main_layout.addLayout(self.type_layout)
        self.main_layout.addWidget(self.generate_spreadsheet_button)

    @QtCore.Slot()
    def generate_spreadsheet(self):
        self.message_box.setText('Aguarde...')
        self.message_box.exec()
        self.message_box.close()
        browsers = {
            'Sub100': Sub100Browser(),
            'OLX': OLXBrowser(),
        }
        browser = browsers[self.website_combobox.currentText()]
        state = self.state_combobox.currentText()
        city = self.city_input.text()
        ad_type = self.type_combobox.currentText()
        path = f'result-{ad_type}-{state}-{city}.xlsx'.lower()
        for page in count(1):
            data = browser.get_infos(state, city, ad_type, page)
            if data['Nome'] == []:
                break
            dataframe = pd.DataFrame.from_dict(data)
            if Path(path).exists():
                dataframe_excel = pd.read_excel(path)
                final_dataframe = pd.concat([dataframe_excel, dataframe])
                final_dataframe.to_excel(path, index=False)
            else:
                dataframe.to_excel(path, index=False)
        self.message_box.setText('Finalizado!')
        self.message_box.show()
