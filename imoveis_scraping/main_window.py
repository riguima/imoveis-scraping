from PySide6 import QtCore, QtWidgets


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(600, 300)
        with open('styles.qss', 'r') as f:
            self.setStyleSheet(f.read())

        self.website_label = QtWidgets.QLabel('Site:')
        self.website_combobox = QtWidgets.QComboBox()
        self.website_combobox.addItems(['Sub100', 'OLX'])
        self.website_layout = QtWidgets.QHBoxLayout()
        self.website_layout.addWidget(self.website_label)
        self.website_layout.addWidget(self.website_combobox)

        self.state_label = QtWidgets.QLabel('Estado:')
        self.state_combobox = QtWidgets.QComboBox()
        self.state_layout = QtWidgets.QHBoxLayout()
        self.state_layout.addWidget(self.state_label)
        self.state_layout.addWidget(self.state_combobox)
        self.update_state_combobox()
        self.website_combobox.currentTextChanged.connect(
            self.update_state_combobox
        )

        self.city_label = QtWidgets.QLabel('Cidade:')
        self.city_combobox = QtWidgets.QComboBox()
        self.city_layout = QtWidgets.QHBoxLayout()
        self.city_layout.addWidget(self.city_label)
        self.city_layout.addWidget(self.city_combobox)
        self.update_city_combobox()
        self.state_combobox.currentTextChanged.connect(
            self.update_city_combobox
        )

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
    def update_state_combobox(self):
        pass

    @QtCore.Slot()
    def update_city_combobox(self):
        pass

    @QtCore.Slot()
    def generate_spreadsheet(self):
        pass
