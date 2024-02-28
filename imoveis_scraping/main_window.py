from itertools import count
from pathlib import Path

import pandas as pd
from PySide6 import QtCore, QtGui, QtWidgets

from imoveis_scraping.browsers.olx import OLXBrowser
from imoveis_scraping.browsers.sub100 import Sub100Browser
from imoveis_scraping.consts import STATES


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 400)
        with open('styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

        self.message_box = QtWidgets.QMessageBox()

        self.destination_folder_label = QtWidgets.QLabel('Pasta:')
        self.destination_folder_input = QtWidgets.QLineEdit()
        self.destination_folder_button = QtWidgets.QPushButton('Selecionar')
        self.destination_folder_button.clicked.connect(self.choose_directory)
        self.destination_folder_layout = QtWidgets.QHBoxLayout()
        self.destination_folder_layout.addWidget(self.destination_folder_label)
        self.destination_folder_layout.addWidget(self.destination_folder_input)
        self.destination_folder_layout.addWidget(self.destination_folder_button)

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

        self.property_type_label = QtWidgets.QLabel('Tipo de Propriedade:')
        self.property_type_combobox = QtWidgets.QComboBox()
        self.property_type_combobox.addItems(
            ['Residenciais', 'Terrenos e Áreas']
        )
        self.property_type_layout = QtWidgets.QHBoxLayout()
        self.property_type_layout.addWidget(self.property_type_label)
        self.property_type_layout.addWidget(self.property_type_combobox)

        self.page_label = QtWidgets.QLabel('Página:')
        self.page_input = QtWidgets.QLineEdit()
        self.page_input.setText('1')
        self.page_input.setValidator(QtGui.QIntValidator())
        self.page_layout = QtWidgets.QHBoxLayout()
        self.page_layout.addWidget(self.page_label)
        self.page_layout.addWidget(self.page_input)

        self.generate_spreadsheet_button = QtWidgets.QPushButton(
            'Gerar Planilha'
        )
        self.generate_spreadsheet_button.clicked.connect(
            self.generate_spreadsheet
        )

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.addLayout(self.destination_folder_layout)
        self.main_layout.addLayout(self.website_layout)
        self.main_layout.addLayout(self.state_layout)
        self.main_layout.addLayout(self.city_layout)
        self.main_layout.addLayout(self.type_layout)
        self.main_layout.addLayout(self.property_type_layout)
        self.main_layout.addLayout(self.page_layout)
        self.main_layout.addWidget(self.generate_spreadsheet_button)

    @QtCore.Slot()
    def choose_directory(self):
        self.destination_folder_input.setText(QtWidgets.QFileDialog.getExistingDirectory())

    @QtCore.Slot()
    def generate_spreadsheet(self):
        self.message_box.setText('Aguarde...')
        self.message_box.exec()
        self.message_box.close()
        browsers = {
            'Sub100': Sub100Browser,
            'OLX': OLXBrowser,
        }
        browser = browsers[self.website_combobox.currentText()]()
        state = self.state_combobox.currentText()
        city = self.city_input.text()
        ad_type = self.type_combobox.currentText()
        property_type = self.property_type_combobox.currentText()
        if self.destination_folder_input.text():
            path = Path(self.destination_folder_input.text()) / f'result-{ad_type}-{state}-{city}.xlsx'.lower()
        else:
            path = f'result-{ad_type}-{state}-{city}.xlsx'.lower()
        for page in count(int(self.page_input.text())):
            if browsers[self.website_combobox.currentText()] == Sub100Browser:
                data = browser.get_infos(
                    state, city, ad_type, property_type, page
                )
            else:
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
