"""
    Paradox asset files, Maya import/export interface.

    author : ross-g
"""

import json
import inspect
import webbrowser

import pymel.core as pmc
import maya.OpenMayaUI as omUI

try:
    from PySide2 import QtCore, QtGui, QtWidgets
    from shiboken2 import wrapInstance
except ImportError:
    from PySide import QtCore, QtGui
    from PySide import QtGui as QtWidgets
    from shiboken import wrapInstance

from io_pdx_mesh.pdx_data import PDXData

try:
    import maya_import_export
    reload(maya_import_export)
    from maya_import_export import *
except Exception as err:
    print err
    raise


def get_mayamainwindow():
    pointer = omUI.MQtUtil.mainWindow()
    return wrapInstance(long(pointer), QtWidgets.QMainWindow)


def h_line():
    line = QtWidgets.QFrame()
    line.setFrameShape(QtWidgets.QFrame.HLine)
    line.setFrameShadow(QtWidgets.QFrame.Sunken)
    return line


""" ================================================================================================
    UI classes for the import/export tool.
====================================================================================================
"""


class PDXmaya_ui(QtWidgets.QDialog):
    """
        Main tool window.
    """
    _script_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    _settings_file = os.path.join(os.path.split(_script_dir)[0], 'clausewitz.json')

    def __init__(self, parent=None):
        # parent to the Maya main window.
        if not parent:
            parent = get_mayamainwindow()

        super(PDXmaya_ui, self).__init__(parent)
        self.popup = None                       # reference for popup widget
        self.settings = self.load_settings()    # settings from json
        self.create_ui()
        self.setStyleSheet(
            'QGroupBox {'
            'border: 1px solid;'
            'border-color: rgba(0, 0, 0, 64);'
            'border-radius: 4px;'
            'margin-top: 8px;'
            'padding: 5px 2px 2px 2px;'
            'background-color: rgb(78, 80, 82);'
            '}'
            'QGroupBox::title {'
            'subcontrol-origin: margin;'
            'subcontrol-position: top left;'
            'left: 10px;'
            '}'
        )

    def create_ui(self):
        # window properties
        self.setWindowTitle('PDX Maya Tools')
        self.setWindowFlags(QtCore.Qt.Window)
        if self.parent():
            parent_x = self.parent().x()
            parent_y = self.parent().y()
            self.setGeometry(parent_x+60, parent_y+220, self.width(), self.height())

        # populate window
        self.create_menu()
        self.create_controls()
        self.create_signals()
        self.refresh_gui()

    def create_menu(self):
        self.menubar = QtWidgets.QMenuBar()
        file_menu = self.menubar.addMenu('&File')
        tools_menu = self.menubar.addMenu('&Tools')
        tools_menu.setTearOffEnabled(True)
        help_menu = self.menubar.addMenu('&Help')

        # file menu
        file_import_mesh = QtWidgets.QAction('Import mesh ...', self)
        file_import_mesh.triggered.connect(self.do_import_mesh)
        # file_import_mesh.setStatusTip('')
        file_import_anim = QtWidgets.QAction('Import animation ...', self)
        file_import_anim.triggered.connect(self.do_import_anim)
        file_export_mesh = QtWidgets.QAction('Export mesh ...', self)
        file_export_mesh.triggered.connect(self.do_export_mesh)
        file_export_anim = QtWidgets.QAction('Export anim ...', self)
        file_export_anim.triggered.connect(self.do_export_anim)
        file_export_anim.setDisabled(True)

        # tools menu
        tool_edit_settings = QtWidgets.QAction('Edit Clausewitz settings', self)
        tool_edit_settings.triggered.connect(lambda: os.system(self._settings_file))
        tool_ignore_joints = QtWidgets.QAction('Ignore selected joints', self)
        tool_ignore_joints.triggered.connect(lambda: set_ignore_joints(True))
        tool_unignore_joints = QtWidgets.QAction('Un-ignore selected joints', self)
        tool_unignore_joints.triggered.connect(lambda: set_ignore_joints(False))
        tool_show_jnt_localaxes = QtWidgets.QAction('Show all joint axes', self)
        tool_show_jnt_localaxes.triggered.connect(lambda: set_local_axis_display(True, object_type='joint'))
        tool_hide_jnt_localaxes = QtWidgets.QAction('Hide all joint axes', self)
        tool_hide_jnt_localaxes.triggered.connect(lambda: set_local_axis_display(False, object_type='joint'))
        tool_show_loc_localaxes = QtWidgets.QAction('Show all locator axes', self)
        tool_show_loc_localaxes.triggered.connect(lambda: set_local_axis_display(True, object_type='locator'))
        tool_hide_loc_localaxes = QtWidgets.QAction('Hide all locator axes', self)
        tool_hide_loc_localaxes.triggered.connect(lambda: set_local_axis_display(False, object_type='locator'))

        # help menu
        help_forum = QtWidgets.QAction('Paradox forums', self)
        help_forum.triggered.connect(lambda: webbrowser.open(
            'https://forum.paradoxplaza.com/forum/index.php?forums/clausewitz-maya-exporter-modding-tool.935/')
        )
        help_code = QtWidgets.QAction('Source code', self)
        help_code.triggered.connect(lambda: webbrowser.open(
            'https://github.com/ross-g/io_pdx_mesh')
        )

        file_menu.addActions([
            file_import_mesh,
            file_import_anim
        ])
        file_menu.addSeparator()
        file_menu.addActions([
            file_export_mesh,
            file_export_anim
        ])
        tools_menu.addActions([
            tool_edit_settings
        ])
        tools_menu.addSeparator()
        tools_menu.addActions([
            tool_ignore_joints,
            tool_unignore_joints
        ])
        tools_menu.addSeparator()
        tools_menu.addActions([
            tool_show_jnt_localaxes,
            tool_hide_jnt_localaxes,
            tool_show_loc_localaxes,
            tool_hide_loc_localaxes
        ])
        help_menu.addActions([
            help_forum, help_code
        ])

    def create_controls(self):
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(main_layout)

        # create all of the main controls
        self.export_ctrls = export_controls(parent=self)

        # create menubar and add widgets to main layout
        main_layout.setMenuBar(self.menubar)
        main_layout.addWidget(self.export_ctrls)

    def create_signals(self):
        # connect up controls
        pass

    def refresh_gui(self):
        # call any gui refresh functions here
        self.export_ctrls.refresh_mat_list()
        self.export_ctrls.refresh_anim_list()

    @QtCore.Slot()
    def do_import_mesh(self):
        filepath, filefilter = QtWidgets.QFileDialog.getOpenFileName(self, caption='Select .mesh file',
                                                                     filter='PDX Mesh files (*.mesh)')
        if filepath != '':
            if os.path.splitext(filepath)[1] == '.mesh':
                self.popup = import_popup(filepath, parent=self)
                self.popup.show()
            else:
                reply = QtWidgets.QMessageBox.warning(self, 'READ ERROR',
                                                      'Unable to read selected file. The filepath ... '
                                                      '\n\n\t{}'
                                                      '\n ... is not a .mesh file!'.format(filepath),
                                                      QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)
                if reply == QtWidgets.QMessageBox.Ok:
                    print "[io_pdx_mesh] Nothing to import."

    @QtCore.Slot()
    def do_import_anim(self):
        filepath, filefilter = QtWidgets.QFileDialog.getOpenFileName(self, caption='Select .anim file',
                                                                     filter='PDX Animation files (*.anim)')
        if filepath != '':
            if os.path.splitext(filepath)[1] == '.anim':
                self.popup = import_popup(filepath, parent=self)
                self.popup.show()
            else:
                reply = QtWidgets.QMessageBox.warning(self, 'READ ERROR',
                                                      'Unable to read selected file. The filepath ... '
                                                      '\n\n\t{}'
                                                      '\n ... is not a .anim file!'.format(filepath),
                                                      QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)
                if reply == QtWidgets.QMessageBox.Ok:
                    print "[io_pdx_mesh] Nothing to import."

    @QtCore.Slot()
    def do_export_mesh(self):
        export_opts = self.export_ctrls
        filepath, filename = export_opts.get_export_path()

        # validate directory
        if filepath == '':
            export_opts.select_export_path()
            filepath, filename = export_opts.get_export_path()
        if not os.path.isdir(filepath):
            reply = QtWidgets.QMessageBox.warning(self, 'WRITE ERROR',
                                                  'Unable to export content. The filepath ... '
                                                  '\n\n\t{}'
                                                  '\n ... is not a valid location!'.format(filepath),
                                                  QtWidgets.QMessageBox.Ok, defaultButton=QtWidgets.QMessageBox.Ok)
            if reply == QtWidgets.QMessageBox.Ok:
                print "[io_pdx_mesh] Nothing to export."
            return

        # determine the output mesh path
        if not os.path.splitext(filename)[1] == '.mesh':
            filename += '.mesh'
        meshpath = os.path.join(os.path.normpath(filepath), filename)

        try:
            export_meshfile(
                meshpath,
                exp_mesh=export_opts.chk_mesh.isChecked(),
                exp_skel=export_opts.chk_skeleton.isChecked(),
                exp_locs=export_opts.chk_locators.isChecked(),
                merge_verts=export_opts.chk_merge_vtx.isChecked(),
                progress_fn=MayaProgress
            )
            QtWidgets.QMessageBox.information(self, 'Success', 'Mesh export finished!\n\n{}'.format(meshpath))

        except Exception as err:
            print "[io_pdx_mesh] FAILED to export {}".format(meshpath)
            print err
            raise

    @QtCore.Slot()
    def do_export_anim(self):
        pass

    def load_settings(self):
        with open(self._settings_file, 'rt') as f:
            try:
                settings = json.load(f)
                return settings
            except Exception as err:
                QtGui.QMessageBox.critical(self, 'Warning',
                                           'Your "clausewitz.json" settings file has errors and is unreadable.\n'
                                           'Check the Maya script output for details.\n\n'
                                           'Some functions of the tool will not work without these settings.',
                                           QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.Ok)
                print "[io_pdx_mesh] CRITICAL ERROR!"
                print err
                return {}


class export_controls(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super(export_controls, self).__init__(parent)

        self.parent = parent

        self.create_controls()
        self.connect_signals()

    def create_controls(self):
        # create controls
        # materials
        self.list_materials = QtWidgets.QListWidget()
        self.btn_mat_refresh = QtWidgets.QPushButton('Refresh', self)
        self.btn_mat_create = QtWidgets.QPushButton('Create ...', self)
        self.btn_mat_edit = QtWidgets.QPushButton('Edit', self)
        # animations
        self.list_animations = QtWidgets.QListWidget()
        self.btn_anim_refresh = QtWidgets.QPushButton('Refresh', self)
        self.btn_anim_create = QtWidgets.QPushButton('Create ...', self)
        self.btn_anim_edit = QtWidgets.QPushButton('Edit', self)

        # settings
        lbl_engine = QtWidgets.QLabel('Game engine:')
        self.setup_engine = QtWidgets.QComboBox()
        self.setup_engine.addItems(self.parent.settings.keys())
        lbl_fps = QtWidgets.QLabel('Animation fps:')
        self.setup_fps = QtWidgets.QDoubleSpinBox()
        self.setup_fps.setMinimum(0.0)
        self.setup_fps.setValue(15.0)

        # export options
        self.chk_mesh = QtWidgets.QCheckBox('Export mesh')
        self.chk_skeleton = QtWidgets.QCheckBox('Export skeleton')
        self.chk_locators = QtWidgets.QCheckBox('Export locators')
        self.chk_animation = QtWidgets.QCheckBox('Export animations')
        self.chk_merge_vtx = QtWidgets.QCheckBox('Merge vertices')
        self.chk_merge_obj = QtWidgets.QCheckBox('Merge objects')
        for ctrl in [self.chk_mesh, self.chk_skeleton, self.chk_locators, self.chk_merge_vtx]:
            ctrl.setChecked(True)
        # self.chk_create = QtWidgets.QCheckBox('Create .gfx and .asset')
        # self.chk_preview = QtWidgets.QCheckBox('Preview on export')

        # output settings
        lbl_path = QtWidgets.QLabel('Output path:')
        self.txt_path = QtWidgets.QLineEdit()
        self.btn_path = QtWidgets.QPushButton('...', self)
        self.btn_path.setMaximumWidth(20)
        self.btn_path.setMaximumHeight(18)
        lbl_file = QtWidgets.QLabel('Filename:')
        self.txt_file = QtWidgets.QLineEdit()
        self.txt_file.setPlaceholderText('placeholder_name.mesh')
        self.btn_export = QtWidgets.QPushButton('Export ...', self)

        # TODO: re-enable these once export is working
        self.btn_anim_refresh.setDisabled(True)
        self.btn_anim_create.setDisabled(True)
        self.btn_anim_edit.setDisabled(True)
        self.chk_animation.setDisabled(True)
        self.chk_merge_obj.setDisabled(True)

        # create layouts
        main_layout = QtWidgets.QHBoxLayout()
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(5, 5, 5, 5)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.setSpacing(5)
        grp_mats = QtWidgets.QGroupBox('Materials')
        grp_mats_layout = QtWidgets.QVBoxLayout()
        grp_mats_layout.setContentsMargins(4, 4, 4, 4)
        grp_mats_button_layout = QtWidgets.QHBoxLayout()
        grp_anims = QtWidgets.QGroupBox('Animations')
        grp_anims_layout = QtWidgets.QVBoxLayout()
        grp_anims_layout.setContentsMargins(4, 4, 4, 4)
        grp_anims_button_layout = QtWidgets.QHBoxLayout()

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.setSpacing(5)
        grp_scene = QtWidgets.QGroupBox('Scene setup')
        grp_scene_layout = QtWidgets.QGridLayout()
        grp_scene_layout.setColumnStretch(1, 1)
        grp_scene_layout.setColumnStretch(2, 2)
        grp_scene_layout.setContentsMargins(4, 4, 4, 4)
        grp_scene_layout.setVerticalSpacing(5)
        grp_export = QtWidgets.QGroupBox('Export settings')
        grp_export_layout = QtWidgets.QVBoxLayout()
        grp_export_layout.setContentsMargins(4, 4, 4, 4)
        grp_export_fields_layout = QtWidgets.QGridLayout()
        grp_export_fields_layout.setVerticalSpacing(5)
        grp_export_fields_layout.setHorizontalSpacing(4)

        for grp in [grp_mats, grp_anims, grp_scene, grp_export]:
            grp.setMinimumWidth(250)
            # grp.setFont(QtGui.QFont('SansSerif', 8, QtGui.QFont.Bold))

        # add controls
        self.setLayout(main_layout)
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

        left_layout.addWidget(grp_mats)
        grp_mats.setLayout(grp_mats_layout)
        grp_mats_layout.addWidget(self.list_materials)
        grp_mats_layout.addLayout(grp_mats_button_layout)
        grp_mats_button_layout.addWidget(self.btn_mat_refresh)
        grp_mats_button_layout.addWidget(self.btn_mat_create)
        grp_mats_button_layout.addWidget(self.btn_mat_edit)

        left_layout.addWidget(grp_anims)
        grp_anims.setLayout(grp_anims_layout)
        grp_anims_layout.addWidget(self.list_animations)
        grp_anims_layout.addLayout(grp_anims_button_layout)
        grp_anims_button_layout.addWidget(self.btn_anim_refresh)
        grp_anims_button_layout.addWidget(self.btn_anim_create)
        grp_anims_button_layout.addWidget(self.btn_anim_edit)

        right_layout.addWidget(grp_scene)
        grp_scene.setLayout(grp_scene_layout)
        grp_scene_layout.addWidget(lbl_engine, 1, 1)
        grp_scene_layout.addWidget(self.setup_engine, 1, 2)
        grp_scene_layout.addWidget(lbl_fps, 2, 1)
        grp_scene_layout.addWidget(self.setup_fps, 2, 2)

        right_layout.addWidget(grp_export)
        grp_export.setLayout(grp_export_layout)
        grp_export_layout.addWidget(self.chk_mesh)
        grp_export_layout.addWidget(self.chk_skeleton)
        grp_export_layout.addWidget(self.chk_locators)
        grp_export_layout.addWidget(self.chk_animation)
        grp_export_layout.addWidget(h_line())
        grp_export_layout.addWidget(self.chk_merge_vtx)
        grp_export_layout.addWidget(self.chk_merge_obj)
        grp_export_layout.addWidget(h_line())
        # grp_export_layout.addWidget(self.chk_create)
        # grp_export_layout.addWidget(self.chk_preview)
        # grp_export_layout.addWidget(h_line())
        grp_export_layout.addLayout(grp_export_fields_layout)
        grp_export_fields_layout.addWidget(lbl_path, 1, 1)
        grp_export_fields_layout.addWidget(self.txt_path, 1, 2)
        grp_export_fields_layout.addWidget(self.btn_path, 1, 3)
        grp_export_fields_layout.addWidget(lbl_file, 2, 1)
        grp_export_fields_layout.addWidget(self.txt_file, 2, 2, 1, 2)
        grp_export_layout.addWidget(self.btn_export)

    def connect_signals(self):
        self.list_materials.itemClicked.connect(self.select_mat)
        self.list_materials.itemDoubleClicked.connect(self.edit_selected_mat)
        self.btn_mat_refresh.clicked.connect(self.refresh_mat_list)
        self.btn_mat_create.clicked.connect(self.create_new_mat)
        self.btn_mat_edit.clicked.connect(self.edit_selected_mat)
        self.btn_anim_refresh.clicked.connect(self.refresh_anim_list)
        self.btn_path.clicked.connect(self.select_export_path)
        self.btn_export.clicked.connect(self.do_export)

    def refresh_mat_list(self):
        self.list_materials.clearSelection()
        self.list_materials.clear()
        pdx_scenemats = [mat.name() for mat in list_scene_materials() if hasattr(mat, PDX_SHADER)]

        for mat in pdx_scenemats:
            list_item = QtWidgets.QListWidgetItem()
            list_item.setText(mat)
            self.list_materials.insertItem(self.list_materials.count(), list_item)

        self.list_materials.sortItems()

    def edit_selected_mat(self):
        if self.list_materials.selectedItems():
            selected_mat = self.list_materials.selectedItems()[0]
            self.popup = material_popup(material=selected_mat, parent=self.parent)
            self.popup.show()

    def create_new_mat(self):
        self.popup = material_popup(parent=self.parent)
        self.popup.show()

    def select_mat(self, curr_sel):
        try:
            pmc.select(curr_sel.text())
        except pmc.MayaNodeError:
            self.refresh_mat_list()

    def refresh_anim_list(self):
        self.list_animations.clearSelection()
        self.list_animations.clear()
        # pdx_scenemats = [mat.name() for mat in list_scene_materials() if hasattr(mat, PDX_SHADER)]

        # for mat in pdx_scenemats:
        #     list_item = QtWidgets.QListWidgetItem()
        #     list_item.setText(mat)
        #     self.list_animations.insertItem(self.list_animations.count(), list_item)

        self.list_animations.sortItems()

    def select_export_path(self):
        filepath, filefilter = QtWidgets.QFileDialog.getSaveFileName(self, caption='Select export folder',
                                                                     filter='PDX Mesh files (*.mesh)')
        path, name = os.path.split(filepath)

        if filepath != '' and os.path.isdir(path):
            self.txt_path.setText(path)
            self.txt_file.setText(name)
            self.txt_file.setToolTip(filepath)

    def get_export_path(self):
        filepath = self.txt_path.text()
        filename = self.txt_file.text() or self.txt_file.placeholderText()
        return filepath, filename

    def do_export(self):
        if self.chk_mesh.isChecked() or self.chk_skeleton.isChecked() or self.chk_locators.isChecked():
            self.parent.do_export_mesh()


class import_popup(QtWidgets.QWidget):

    def __init__(self, filepath, parent=None):
        super(import_popup, self).__init__(parent)

        self.pdx_file = filepath
        self.pdx_type = os.path.splitext(filepath)[1]
        self.parent = parent

        self.setWindowTitle('Import options')
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(250, 100)
        if self.parent:
            center_x = self.parent.frameGeometry().center().x() - (self.width() / 2)
            center_y = self.parent.frameGeometry().center().y() - (self.height() / 2)
            self.setGeometry(center_x, center_y, self.width(), self.height())

        self.create_controls()
        self.connect_signals()

    def create_controls(self):
        # create controls
        lbl_filepath = QtWidgets.QLabel('Filename:  {}'.format(os.path.split(self.pdx_file)[-1]))
        self.btn_import = QtWidgets.QPushButton('Import ...', self)
        self.btn_import.setToolTip('Select a {} file to import.'.format(self.pdx_type))
        self.btn_cancel = QtWidgets.QPushButton('Cancel', self)
        # mesh specific controls
        self.chk_mesh = QtWidgets.QCheckBox('Mesh')
        self.chk_skeleton = QtWidgets.QCheckBox('Skeleton')
        self.chk_locators = QtWidgets.QCheckBox('Locators')
        # anim specific controls
        lbl_starttime = QtWidgets.QLabel('start time:')
        lbl_starttime.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.spn_start = QtWidgets.QSpinBox()
        self.spn_start.setMaximumWidth(50)
        self.spn_start.setValue(1)

        # create layouts
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        opts_layout = QtWidgets.QHBoxLayout()
        btn_layout = QtWidgets.QHBoxLayout()

        # add controls
        self.setLayout(main_layout)
        main_layout.addWidget(lbl_filepath)
        main_layout.addSpacing(5)
        # add mode specific import option controls
        if self.pdx_type == '.mesh':
            for chk_box in [self.chk_mesh, self.chk_skeleton, self.chk_locators]:
                opts_layout.addWidget(chk_box)
                chk_box.setChecked(True)
        elif self.pdx_type == '.anim':
            for qt_control in [lbl_starttime, self.spn_start]:
                opts_layout.addWidget(qt_control)
        main_layout.addLayout(opts_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(btn_layout)
        btn_layout.addWidget(self.btn_import)
        btn_layout.addWidget(self.btn_cancel)

    def connect_signals(self):
        if self.pdx_type == '.mesh':
            self.btn_import.clicked.connect(self.import_mesh)
        elif self.pdx_type == '.anim':
            self.btn_import.clicked.connect(self.import_anim)
        self.btn_cancel.clicked.connect(self.close)

    def import_mesh(self):
        try:
            self.close()
            import_meshfile(
                self.pdx_file,
                imp_mesh=self.chk_mesh.isChecked(),
                imp_skel=self.chk_skeleton.isChecked(),
                imp_locs=self.chk_locators.isChecked(),
                progress_fn=MayaProgress
            )
            self.parent.refresh_gui()
        except Exception as err:
            print "[io_pdx_mesh] FAILED to import {}".format(self.pdx_file)
            print err
            MayaProgress.finished()
            self.close()
            raise

        self.close()

    def import_anim(self):
        try:
            self.close()
            import_animfile(
                self.pdx_file,
                timestart=self.spn_start.value(),
                progress_fn=MayaProgress
            )
            self.parent.refresh_gui()
        except Exception as err:
            print "[io_pdx_mesh] FAILED to import {}".format(self.pdx_file)
            print err
            MayaProgress.finished()
            self.close()
            raise

        self.close()


class material_popup(QtWidgets.QWidget):

    def __init__(self, material=None, parent=None):
        super(material_popup, self).__init__(parent)

        self.parent = parent
        self.material = material

        self.setWindowTitle('PDX material')
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.MSWindowsFixedSizeDialogHint)
        self.setFixedSize(300, 100)
        if self.parent:
            center_x = self.parent.frameGeometry().center().x() - (self.width() / 2)
            center_y = self.parent.frameGeometry().center().y() - (self.height() / 2)
            self.setGeometry(center_x, center_y, self.width(), self.height())

        self.create_controls()
        self.connect_signals()

    def create_controls(self):
        # create controls
        self.mat_name = QtWidgets.QLineEdit()
        self.mat_name.setObjectName('Name')
        self.mat_type = QtWidgets.QComboBox()
        self.mat_type.setObjectName('Shader')
        self.mat_type.setEditable(True)
        self.mat_type.addItems(self.get_shader_presets())
        self.mat_type.setCurrentIndex(-1)
        self.btn_okay = QtWidgets.QPushButton('Okay', self)
        self.btn_cancel = QtWidgets.QPushButton('Cancel', self)

        # create layouts
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(5, 5, 5, 5)
        form_layout = QtWidgets.QFormLayout()
        btn_layout = QtWidgets.QHBoxLayout()

        # add controls
        self.setLayout(main_layout)
        main_layout.addLayout(form_layout)
        for ctrl in [self.mat_name, self.mat_type]:
            form_layout.addRow(ctrl.objectName(), ctrl)
        main_layout.addLayout(btn_layout)
        btn_layout.addWidget(self.btn_okay)
        btn_layout.addWidget(self.btn_cancel)

        # editing a selected material
        if self.material:
            mat_name = self.material.text()
            mat_node = pmc.PyNode(mat_name)
            mat_shader = getattr(mat_node, PDX_SHADER).get()

            self.mat_name.setText(mat_name)
            if self.mat_type.findText(mat_shader) is not -1:
                self.mat_type.setCurrentIndex(self.mat_type.findText(mat_shader))
            else:
                self.mat_type.setEditText(mat_shader)

            self.btn_okay.setText('Okay')
        # creating a new material
        else:
            self.btn_okay.setText('Save')

    def connect_signals(self):
        self.btn_okay.clicked.connect(self.save_mat)
        self.btn_cancel.clicked.connect(self.close)

    def get_shader_presets(self):
        sel_engine = self.parent.export_ctrls.setup_engine.currentText()
        return self.parent.settings[sel_engine]['material']

    def save_mat(self):
        # editing a selected material
        if self.material:
            mat_name = self.material.text()
            mat_node = pmc.PyNode(mat_name)

            pmc.rename(mat_node, self.mat_name.text())
            getattr(mat_node, PDX_SHADER).set(self.mat_type.currentText())
        # creating a new material
        else:
            mat_name = self.mat_name.text()
            # create a mock PDXData object for convenience here to pass to the create_shader function
            mat_pdx = type(
                'Material',
                (PDXData, object),
                {
                    'shader': [self.mat_type.currentText()]
                }
            )

            create_shader(mat_name, mat_pdx, None)

        self.parent.export_ctrls.refresh_mat_list()
        self.close()


class MayaProgress(object):
    """
        Wrapping the Maya progress window for convenience.
    """
    def __init__(self, title, max_value):
        super(MayaProgress, self).__init__()
        pmc.progressWindow(title=title, progress=0, min=0, max=max_value, status='', isInterruptable=False)

    def __del__(self):
        self.finished()

    @staticmethod
    def update(step, status):
        progress = pmc.progressWindow(query=True, progress=True)
        max_value = pmc.progressWindow(query=True, max=True)
        if progress >= max_value:
            pmc.progressWindow(edit=True, progress=0)
        pmc.progressWindow(edit=True, step=step, status=status)

    @staticmethod
    def finished():
        pmc.progressWindow(endProgress=True)


""" ================================================================================================
    Main entry point.
====================================================================================================
"""


def main():
    print "[io_pdx_mesh] Launching Maya UI."
    global pdx_tools

    try:
        pdx_tools.close()
        pdx_tools.deleteLater()
    except Exception:
        pass

    pdx_tools = PDXmaya_ui()

    try:
        pdx_tools.show()
    except Exception:
        pdx_tools.deleteLater()
        pdx_tools = None
        raise


if __name__ == '__main__':
    main()
