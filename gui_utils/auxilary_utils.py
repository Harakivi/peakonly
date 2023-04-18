import os
from PyQt5 import QtWidgets, QtCore, QtGui


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
        formulas = ""
        if len(feature.chemSpyder_mz_Results) > 0:
            self.setColumnCount(4)
            # Set the table headers
            self.setHorizontalHeaderLabels(["m/z", "intensities", "rt", "chemSpyderF Results"])
            for id in  feature.chemSpyder_mz_Results:
                formulas += str(id) + "   " + feature.chemSpyder_mz_Results[id]["CommonName"] + "   " + feature.chemSpyder_mz_Results[id]["Formula"] + "\r\n"
            self.setItem(row, 3, QtWidgets.QTableWidgetItem(formulas))
        self.displayedfeatures.append(feature)
    
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
            case "chemSpyderF Results":
                self.features = sorted(self.features, key=lambda x: x.chemSpyder_mz_Results.items(), reverse = True)
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