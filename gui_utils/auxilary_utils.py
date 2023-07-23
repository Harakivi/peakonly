import os
from PyQt5 import QtWidgets, QtCore, QtGui
from functools import partial

class ClickableListWidget(QtWidgets.QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.double_click = None
        self.right_click = None

    def mousePressEvent(self, QMouseEvent):
        super(QtWidgets.QListWidget, self).mousePressEvent(QMouseEvent)
        if QMouseEvent.button() == QtCore.Qt.RightButton and self.right_click is not None:
            self.right_click()

    def mouseDoubleClickEvent(self, QMouseEvent):
        if self.double_click is not None:
            if QMouseEvent.button() == QtCore.Qt.LeftButton:
                item = self.itemAt(QMouseEvent.pos())
                if item is not None:
                    self.double_click(item)

    def connectDoubleClick(self, method):
        """
        Set a callable object which should be called when a user double-clicks on item
        Parameters
        ----------
        method : callable
            any callable object
        Returns
        -------
        - : None
        """
        self.double_click = method

    def connectRightClick(self, method):
        """
        Set a callable object which should be called when a user double-clicks on item
        Parameters
        ----------
        method : callable
            any callable object
        Returns
        -------
        - : None
        """
        self.right_click = method


class ClickablTableWidget(QtWidgets.QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.double_click = None
        self.right_click = None

    def mousePressEvent(self, QMouseEvent):
        super(QtWidgets.QTableWidget, self).mousePressEvent(QMouseEvent)
        if QMouseEvent.button() == QtCore.Qt.RightButton and self.right_click is not None:
            self.right_click()

    def mouseDoubleClickEvent(self, QMouseEvent):
        if self.double_click is not None:
            if QMouseEvent.button() == QtCore.Qt.LeftButton:
                item = self.itemAt(QMouseEvent.pos())
                if item is not None:
                    if item.isSelected():
                        self.double_click(item)

    def connectDoubleClick(self, method):
        """
        Set a callable object which should be called when a user double-clicks on item
        Parameters
        ----------
        method : callable
            any callable object
        Returns
        -------
        - : None
        """
        self.double_click = method

    def connectRightClick(self, method):
        """
        Set a callable object which should be called when a user double-clicks on item
        Parameters
        ----------
        method : callable
            any callable object
        Returns
        -------
        - : None
        """
        self.right_click = method

class ClickablTableChemSpiderWidget(QtWidgets.QTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.double_click = None
        self.right_click = None

    def mousePressEvent(self, QMouseEvent):
        super(QtWidgets.QTableWidget, self).mousePressEvent(QMouseEvent)
        if QMouseEvent.button() == QtCore.Qt.RightButton and self.right_click is not None:
            self.right_click()

    def mouseDoubleClickEvent(self, QMouseEvent):
        if self.double_click is not None:
            if QMouseEvent.button() == QtCore.Qt.LeftButton:
                item = self.itemAt(QMouseEvent.pos())
                if(item != None):
                    row = item.row()
                    id = self.item(row, 0).text()
                    if id is not None:
                        pic = QtWidgets.QTableWidgetItem()
                        pic.setData(QtCore.Qt.DecorationRole, self.double_click(int(id)))
                        self.setItem(row, 3, pic)

    def connectDoubleClick(self, method):
        """
        Set a callable object which should be called when a user double-clicks on item
        Parameters
        ----------
        method : callable
            any callable object
        Returns
        -------
        - : None
        """
        self.double_click = method

    def connectRightClick(self, method):
        """
        Set a callable object which should be called when a user double-clicks on item
        Parameters
        ----------
        method : callable
            any callable object
        Returns
        -------
        - : None
        """
        self.right_click = method


class FileListWidget(ClickableListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file2path = {}

    def addFile(self, path: str):
        filename = os.path.basename(path)
        self.file2path[filename] = path
        self.addItem(filename)

    def deleteFile(self, item: QtWidgets.QListWidgetItem):
        del self.file2path[item.text()]
        self.takeItem(self.row(item))

    def getPath(self, item: QtWidgets.QListWidgetItem):
        return self.file2path[item.text()]


class FeatureListWidget(ClickablTableWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.horizontalHeader().sectionClicked.connect(self.sortItems)
        self.features = []
        self.displayedfeatures = []
        self.intensityFilter = 0
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setSelectionMode(
            QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.setSelectionBehavior(
            QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.setColumnCount(3)
        # Set the table headers
        self.setHorizontalHeaderLabels(["m/z", "intensities", "rt"])
        self.getImageCallback = None

    def add_feature(self, feature):
        self.features.append(feature)
        self.__addRow(feature)

    def __addRow(self, feature):
        row = self.rowCount()
        self.insertRow(row)
        self.setItem(row, 0, QtWidgets.QTableWidgetItem(f"{feature.mz:.4f}"))
        self.setItem(row, 1, QtWidgets.QTableWidgetItem(
            f"{feature.intensities[0]:.0f}"))
        self.setItem(row, 2, QtWidgets.QTableWidgetItem(
            f"{feature.rtmin:.2f} - {feature.rtmax:.2f}"))
        if feature.chemSpider_mz_Results != None:
            self.setColumnCount(4)
            # Set the table headers
            self.setHorizontalHeaderLabels(["m/z", "intensities", "rt", "chemSpider Results"])

            chemSpider_Results = ClickablTableChemSpiderWidget(self)
            chemSpider_Results.connectDoubleClick(self.getImage)
            chemSpider_Results.connectRightClick(partial(chemSpiderResContextMenu, self))
            chemSpider_Results.setColumnCount(4) 
            # Set the table headers
            chemSpider_Results.setHorizontalHeaderLabels(["chemSpider id", "CommonName", "Formula", "Image"])
            chemSpider_Results.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
            chemSpider_Results.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollMode.ScrollPerPixel)
            chemSpider_Results.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
            chemSpider_Results.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
            chemSpider_Results.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            chemSpider_Results.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            for id in  feature.chemSpider_mz_Results:
                chemSpider_Results.insertRow(chemSpider_Results.rowCount())
                chemSpider_Results.setItem(chemSpider_Results.rowCount() - 1, 0 ,QtWidgets.QTableWidgetItem(f"{id}"))
                chemSpider_Results.setItem(chemSpider_Results.rowCount() - 1, 1 ,QtWidgets.QTableWidgetItem(f"{feature.chemSpider_mz_Results[id]['CommonName']}"))
                chemSpider_Results.setItem(chemSpider_Results.rowCount() - 1, 2 ,QtWidgets.QTableWidgetItem(f"{feature.chemSpider_mz_Results[id]['Formula']}"))
                if(feature.chemSpider_mz_Results[id].get("image") != None):
                    pic = QtWidgets.QTableWidgetItem()
                    pic.setData(QtCore.Qt.DecorationRole, feature.chemSpider_mz_Results[id]["image"])
                    chemSpider_Results.setItem(chemSpider_Results.rowCount() - 1, 3, pic)

            self.setCellWidget(row, 3, chemSpider_Results)
        self.displayedfeatures.append(feature)

    def getImage(self, id:int):
        pic = None
        for feature in self.displayedfeatures:
            if(feature.chemSpider_mz_Results != None):
                res = feature.chemSpider_mz_Results.get(id)
                if(res != None):
                    if(feature.chemSpider_mz_Results[id].get("image") == None and pic != None):
                        res["image"] = pic
                    elif(feature.chemSpider_mz_Results[id].get("image") != None and pic == None):
                        pic = res["image"]
                    elif(feature.chemSpider_mz_Results[id].get("image") == None and pic == None):
                        pic = self.getImageCallback(id)
                        res["image"] = pic
        return pic
    
    def updateDatas(self):
        self.setRowCount(0)
        self.setColumnCount(3)
        self.displayedfeatures = []
        for feature in self.features:
            if feature.intensities[0] >= self.intensityFilter:
                self.__addRow(feature)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()
            

    def get_feature(self, item):
        number = item.row()
        return self.displayedfeatures[number]

    def get_all(self):
        features = []
        for i in range(self.count()):
            item = self.item(i)
            features.append(self.get_feature(item))
        return features

    def sortItems(self, column):
        header = self.horizontalHeaderItem(column)
        self.setRowCount(0)
        self.setColumnCount(3)
        self.displayedfeatures = []
        match header.text():
            case "m/z":
                self.features = sorted(self.features, key=lambda x: x.mz)
            case "intensities":
                self.features = sorted(
                    self.features, key=lambda x: x.intensities[0])
            case "rt":
                self.features = sorted(self.features, key=lambda x: x.rtmin)
            case "chemSpiderF Results":
                self.features = sorted(self.features, key=lambda x: x.chemSpider_mz_Results.items(), reverse = True)
        for feature in self.features:
            if feature.intensities[0] >= self.intensityFilter:
                self.__addRow(feature)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

    def filterFeaturesByIntensity(self, intensity):
        self.intensityFilter = intensity
        self.setRowCount(0)
        self.setColumnCount(3)
        self.displayedfeatures = []
        for feature in self.features:
            if feature.intensities[0] >= self.intensityFilter:
                self.__addRow(feature)
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

    def clear(self):
        self.setRowCount(0)
        self.setColumnCount(3)
        self.features = []
        self.displayedfeatures = []
        self.intensityFilter = 0

class chemSpiderResContextMenu(QtWidgets.QMenu):
    def __init__(self, parent: FeatureListWidget):
        self.parent = parent
        super().__init__(parent)

        menu = QtWidgets.QMenu(parent)

        get_chemSpiderResults = QtWidgets.QAction('Get images', parent)

        menu.addAction(get_chemSpiderResults)

        action = menu.exec_(QtGui.QCursor.pos())

        cell = parent.cellWidget(self.parent.currentRow(), 3)

        items = cell.selectedItems()
        
        rows = list()
        ids = list()

        for item in items:
            if(item.column() == 0):
                rows.append(item.row())
                ids.append(int(item.text()))

        if action == get_chemSpiderResults:
            for i in range(len(ids)):
                pic = QtWidgets.QTableWidgetItem()
                pic.setData(QtCore.Qt.DecorationRole, self.parent.getImage(ids[i]))
                cell.setItem(rows[i], 3, pic)
                


class ProgressBarsListItem(QtWidgets.QWidget):
    def __init__(self, text, pb=None, parent=None):
        super().__init__(parent)
        self.pb = pb
        if self.pb is None:
            self.pb = QtWidgets.QProgressBar()

        self.label = QtWidgets.QLabel(self)
        self.label.setText(text)

        main_layout = QtWidgets.QHBoxLayout()
        main_layout.addWidget(self.label, 30)
        main_layout.addWidget(self.pb, 70)

        self.setLayout(main_layout)

    def setValue(self, value):
        self.pb.setValue(value)

    def setLabel(self, text):
        self.pb.setValue(0)
        self.label.setText(text)


class ProgressBarsList(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

    def removeItem(self, item):
        self.layout().removeWidget(item)

    def addItem(self, item):
        self.layout().addWidget(item)


class GetFolderWidget(QtWidgets.QWidget):
    def __init__(self, default_directory='', parent=None):
        super().__init__(parent)

        button = QtWidgets.QToolButton()
        button.setText('...')
        button.clicked.connect(self.set_folder)

        if not default_directory:
            default_directory = os.getcwd()
        self.lineEdit = QtWidgets.QToolButton()
        self.lineEdit.setText(default_directory)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.lineEdit, 85)
        layout.addWidget(button, 15)

        self.setLayout(layout)

    def set_folder(self):
        directory = str(QtWidgets.QFileDialog.getExistingDirectory())
        if directory:
            self.lineEdit.setText(directory)

    def get_folder(self):
        return self.lineEdit.text()


class GetFoldersWidget(QtWidgets.QWidget):
    def __init__(self, label, parent=None):
        super().__init__(parent)

        button = QtWidgets.QToolButton()
        button.setText('...')
        button.clicked.connect(self.add_folder)

        self.lineEdit = QtWidgets.QToolButton()
        self.lineEdit.setText(label)

        folder_getter_layout = QtWidgets.QHBoxLayout()
        folder_getter_layout.addWidget(self.lineEdit, 85)
        folder_getter_layout.addWidget(button, 15)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(folder_getter_layout)
        main_layout.addWidget(self.list_widget)

        self.setLayout(main_layout)

    def add_folder(self):
        directory = str(QtWidgets.QFileDialog.getExistingDirectory())
        if directory:
            self.list_widget.addItem(directory)

    def get_folders(self):
        folders = [f.text() for f in self.list_widget.selectedItems()]
        return folders


class GetFileWidget(QtWidgets.QWidget):
    def __init__(self, extension, default_file, parent):
        super().__init__(parent)

        self.extension = extension

        button = QtWidgets.QToolButton()
        button.setText('...')
        button.clicked.connect(self.set_file)

        self.lineEdit = QtWidgets.QToolButton()
        self.lineEdit.setText(default_file)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.lineEdit, 85)
        layout.addWidget(button, 15)

        self.setLayout(layout)

    def set_file(self):
        filter = f'{self.extension} (*.{self.extension})'
        file, _ = QtWidgets.QFileDialog.getOpenFileName(
            None, None, None, filter)
        if file:
            self.lineEdit.setText(file)

    def get_file(self):
        return self.lineEdit.text()
    
class IntensitySetterForFilterWindow(QtWidgets.QDialog):
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
        self.setWindowTitle('peakonly: filter features by intensity')
        self._init_ui()  # initialize user interface

    def _init_ui(self):
        self.setFixedHeight(100)
        self.setFixedWidth(400)
        self.runFilter = False

        # Selection of parameters
        settings_layout = QtWidgets.QVBoxLayout()

        intensity_label = QtWidgets.QLabel()
        intensity_label.setText('Minimal intensity:')
        self.intensity_getter = QtWidgets.QLineEdit(self)
        self.intensity_getter.setText('0')

        run_button = QtWidgets.QPushButton('Run filter')
        run_button.clicked.connect(self.__buttonClose)

        main_layout = QtWidgets.QHBoxLayout()
        settings_layout.addWidget(intensity_label)
        settings_layout.addWidget(self.intensity_getter)
        settings_layout.addWidget(run_button, 30, QtCore.Qt.AlignmentFlag.AlignRight)
        main_layout.addLayout(settings_layout, 70)

        self.setLayout(main_layout)

    def __buttonClose(self):
        self.runFilter = True
        self.close()