import matplotlib.pyplot as plt
from functools import partial
from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from processing_utils.roi import construct_tic, construct_eic
from gui_utils.auxilary_utils import ProgressBarsList, ProgressBarsListItem, FileListWidget, FeatureListWidget, IntensitySetterForFilterWindow
from gui_utils.threading import Worker
from gui_utils.chemSpyder import GetDataSourcesListDialog, GetChargeDialog
from processing_utils.requests import get_ChemSpyederDatas_For_Features, get_Image_For_Feature
import yaml


class AbtractMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self._thread_pool = QtCore.QThreadPool()
        self._pb_list = ProgressBarsList(self)

        self._list_of_files = FileListWidget()

        self._list_of_features = FeatureListWidget()
        self._feature_parameters = None

        self._figure = plt.figure()
        self._ax = self._figure.add_subplot(111)  # plot here
        self._ax.set_xlabel('Retention time [min]')
        self._ax.set_ylabel('Intensity')
        self._ax.ticklabel_format(axis='y', scilimits=(0, 0))
        self._label2line = dict()  # a label (aka line name) to plotted line
        self._canvas = FigureCanvas(self._figure)
        self._toolbar = NavigationToolbar(self._canvas, self)

    def run_thread(self, caption: str, worker: Worker, text=None, icon=None):
        pb = ProgressBarsListItem(caption, parent=self._pb_list)
        self._pb_list.addItem(pb)
        worker.signals.progress.connect(pb.setValue)
        worker.signals.operation.connect(pb.setLabel)
        worker.signals.finished.connect(partial(self._threads_finisher,
                                                text=text, icon=icon, pb=pb))
        self._thread_pool.start(worker)

    def _threads_finisher(self, text=None, icon=None, pb=None):
        if pb is not None:
            self._pb_list.removeItem(pb)
            pb.setParent(None)
        if text is not None:
            msg = QtWidgets.QMessageBox(self)
            msg.setText(text)
            msg.setIcon(icon)
            msg.exec_()
        for id in  self._list_of_features.displayedfeatures[1].chemSpyder_mz_Results:
            get_Image_For_Feature(id).show()

    def set_features(self, obj):
        features, parameters = obj
        self._list_of_features.clear()
        for feature in sorted(features, key=lambda x: x.mz):
            self._list_of_features.add_feature(feature)
        self._feature_parameters = parameters

    def set_chemSpyder_DataSources(self):
        file = open('settings.yaml')
        setttingsFile = yaml.safe_load(file)
        file.close()
        dataSourcesSetter = GetDataSourcesListDialog(self, setttingsFile['chemSpyderDataSources'])
        dataSourcesSetter.exec_()
        if dataSourcesSetter.saveChanges:
            setttingsFile['chemSpyderDataSources'] = dataSourcesSetter.searchList.getItems()
            file = open("settings.yaml", 'w')
            yaml.dump(setttingsFile, file)

    def get_chemSpyderResults(self):
        charge = GetChargeDialog(self)
        charge.exec_()
        if charge.startSearch:
            file = open('settings.yaml')
            setttingsFile = yaml.safe_load(file)
            dataSources = setttingsFile['chemSpyderDataSources']
        
            pb = ProgressBarsListItem('chemSpyder Search', parent=self._pb_list)
            self._pb_list.addItem(pb)
            worker = Worker(get_ChemSpyederDatas_For_Features, self._list_of_features.displayedfeatures, dataSources, charge.charge_getter.value())
            worker.signals.progress.connect(pb.setValue)
            worker.signals.result.connect(self._list_of_features.updateDatas)
            worker.signals.finished.connect(partial(self._threads_finisher, pb=pb))

            self._thread_pool.start(worker)
        
    
    
    def filter_features_by_intensity(self):
        intensitySetter = IntensitySetterForFilterWindow(self)
        intensitySetter.exec_()
        if intensitySetter.runFilter:
            self._list_of_features.filterFeaturesByIntensity(int(intensitySetter.intensity_getter.text()))

    def plotter(self, obj):
        if not self._label2line:  # in case if 'feature' was plotted
            self._figure.clear()
            self._ax = self._figure.add_subplot(111)
            self._ax.set_xlabel('Retention time [min]')
            self._ax.set_ylabel('Intensity')
            self._ax.ticklabel_format(axis='y', scilimits=(0, 0))

        line = self._ax.plot(obj['x'], obj['y'], label=obj['label'])
        self._label2line[obj['label']] = line[0]  # save line
        self._ax.legend(loc='best')
        self._figure.tight_layout()
        self._canvas.draw()

    def close_file(self, item):
        self._list_of_files.deleteFile(item)

    def get_selected_files(self):
        return self._list_of_files.selectedItems()

    def get_selected_features(self):
        return self._list_of_features.selectedItems()

    def get_plotted_lines(self):
        return list(self._label2line.keys())

    def plot_feature(self, item, shifted=True):
        feature = self._list_of_features.get_feature(item)
        self._label2line = dict()  # empty plotted TIC and EIC
        self._figure.clear()
        self._ax = self._figure.add_subplot(111)
        feature.plot(self._ax, shifted=shifted)
        self._ax.set_title("m/z:"+ str(feature.mz))
        self._ax.set_xlabel('Retention time')
        self._ax.set_ylabel('Intensity')
        self._ax.ticklabel_format(axis='y', scilimits=(0, 0))
        self._figure.tight_layout()
        self._canvas.draw()  # refresh canvas

    def plot_tic(self, file):
        label = f'TIC: {file[:file.rfind(".")]}'
        plotted = False
        path = self._list_of_files.file2path[file]

        construct_tic( path, label)
        if label not in self._label2line:
            path = self._list_of_files.file2path[file]

            pb = ProgressBarsListItem(f'Plotting TIC: {file}', parent=self._pb_list)
            self._pb_list.addItem(pb)
            worker = Worker(construct_tic, path, label)
            worker.signals.progress.connect(pb.setValue)
            worker.signals.result.connect(self.plotter)
            worker.signals.finished.connect(partial(self._threads_finisher, pb=pb))

            self._thread_pool.start(worker)

            plotted = True
        return plotted, label

    def plot_eic(self, file, mz, delta):
        label = f'EIC {mz:.4f} ± {delta:.4f}: {file[:file.rfind(".")]}'
        plotted = False
        path = self._list_of_files.file2path[file]

        construct_eic( path, label, mz, delta)
        if label not in self._label2line:
            path = self._list_of_files.file2path[file]

            pb = ProgressBarsListItem(f'Plotting EIC (mz={mz:.4f}): {file}', parent=self._pb_list)
            self._pb_list.addItem(pb)
            worker = Worker(construct_eic, path, label, mz, delta)
            worker.signals.progress.connect(pb.setValue)
            worker.signals.result.connect(self.plotter)
            worker.signals.finished.connect(partial(self._threads_finisher, pb=pb))

            self._thread_pool.start(worker)

            plotted = True
        return plotted, label

    def delete_line(self, label):
        self._ax.lines.remove(self._label2line[label])
        del self._label2line[label]

    def refresh_canvas(self):
        if self._label2line:
            self._ax.legend(loc='best')
            self._ax.relim()  # recompute the ax.dataLim
            self._ax.autoscale_view()  # update ax.viewLim using the new dataLim
        else:
            self._figure.clear()
            self._ax = self._figure.add_subplot(111)
            self._ax.set_xlabel('Retention time [min]')
            self._ax.set_ylabel('Intensity')
            self._ax.ticklabel_format(axis='y', scilimits=(0, 0))
        self._canvas.draw()