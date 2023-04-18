from PyQt5 import QtWidgets, QtCore
from processing_utils import requests
from gui_utils.auxilary_utils import ClickableListWidget
from functools import partial

class DataSourcesListWidget(ClickableListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)

    def addItems(self, names: list):
        for name in names:
            self.addItem(name)
        
    def getItems(self):
        names = list()
        for row in range(self.count()):
            names.append(self.item(row).text())
        return names

class GetDataSourcesListDialog(QtWidgets.QDialog):
    def __init__(self, parent, existSources = None):
        self.parent = parent
        super().__init__(parent)
        
        self.saveChanges = False
        
        self.originalList = DataSourcesListWidget()
        self.searchList = DataSourcesListWidget()

        dataSources = requests.get_DataSources()
        for existSource in existSources:
            dataSources.remove(existSource)

        self.originalList.addItems(dataSources)
        self.searchList.addItems(existSources)

        self.setWindowTitle('Select data sources')
        self._init_ui()  # initialize user interface


    def _init_ui(self):
        dataSources_layout = QtWidgets.QHBoxLayout()
            
        dataSources_layout.addWidget(self.originalList, 50)
        dataSources_layout.addWidget(self.searchList, 50)

        datasButtons_layout = QtWidgets.QHBoxLayout()

        addButton = QtWidgets.QPushButton()
        addButton.setText("Add selected")
        addButton.clicked.connect(self.addSelectedClicked)

        removeButton = QtWidgets.QPushButton()
        removeButton.setText("Remove selected")
        removeButton.clicked.connect(self.removeSelectedClicked)

        datasButtons_layout.addWidget(addButton, 20, QtCore.Qt.AlignmentFlag.AlignCenter)
        datasButtons_layout.addWidget(removeButton, 20, QtCore.Qt.AlignmentFlag.AlignCenter)

        datas_layout = QtWidgets.QVBoxLayout()
        datas_layout.addLayout(dataSources_layout, 90)
        datas_layout.addLayout(datasButtons_layout, 10)

        group = QtWidgets.QGroupBox()
        group.setLayout(datas_layout)

        saveButtons_layout = QtWidgets.QHBoxLayout()

        saveButton = QtWidgets.QPushButton()
        saveButton.setText("Save")
        saveButton.clicked.connect(partial(self.close, True))

        cancelButton = QtWidgets.QPushButton()
        cancelButton.setText("Cancel")
        cancelButton.clicked.connect(partial(self.close, False))

        saveButtons_layout.addWidget(cancelButton, 20, QtCore.Qt.AlignmentFlag.AlignLeft)
        saveButtons_layout.addWidget(saveButton, 20, QtCore.Qt.AlignmentFlag.AlignRight)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(group)
        main_layout.addLayout(saveButtons_layout)

        self.setLayout(main_layout)

    def addSelectedClicked(self):
        for item in self.originalList.selectedItems():
            self.searchList.addItem(item.text())
            self.originalList.takeItem(self.originalList.row(item))
            self.searchList.sortItems()
            self.originalList.sortItems()

    def removeSelectedClicked(self):
        for item in self.searchList.selectedItems():
            self.originalList.addItem(item.text())
            self.searchList.takeItem(self.searchList.row(item))
            self.searchList.sortItems()
            self.originalList.sortItems()
    
    def close(self, saveChanges = False):
        self.saveChanges = saveChanges
        super().close()
            

class GetChargeDialog(QtWidgets.QDialog):
    def __init__(self, parent, existSources = None):
        self.parent = parent
        super().__init__(parent)
        
        self.startSearch = False

        self.setWindowTitle('Select charge')
        self._init_ui()  # initialize user interface


    def _init_ui(self):
        self.setFixedHeight(110)
        self.setFixedWidth(250)
        # Selection of parameters
        settings_layout = QtWidgets.QVBoxLayout()

        charge_label = QtWidgets.QLabel()
        charge_label.setText('Charge:')
        self.charge_getter = QtWidgets.QSpinBox(self)
        self.charge_getter.setMaximum(100)
        self.charge_getter.setMinimum(-100)
        self.charge_getter.setValue(0)
        self.charge_getter.setSingleStep(1)

        settings_layout.addWidget(charge_label)
        settings_layout.addWidget(self.charge_getter)

        buttons_layout = QtWidgets.QHBoxLayout()

        searchButton = QtWidgets.QPushButton()
        searchButton.setText("Search")
        searchButton.clicked.connect(partial(self.close, True))

        cancelButton = QtWidgets.QPushButton()
        cancelButton.setText("Cancel")
        cancelButton.clicked.connect(partial(self.close, False))

        buttons_layout.addWidget(cancelButton, 20, QtCore.Qt.AlignmentFlag.AlignLeft)
        buttons_layout.addWidget(searchButton, 20, QtCore.Qt.AlignmentFlag.AlignRight)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(settings_layout)
        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)
    
    def close(self, startSearch = False):
        self.startSearch = startSearch
        super().close()
            
