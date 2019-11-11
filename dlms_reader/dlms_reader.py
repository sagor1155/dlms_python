import sys
import serial, time
from datetime import datetime
from ctypes import *
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from subprocess import call
from dlms_app_ui import Ui_MainWindow

##Gurux library import 
import traceback
from gurux_common.io import Parity, StopBits, BaudRate
from gurux_serial import GXSerial
from gurux_net import GXNet
from gurux_dlms.enums import ObjectType
from gurux_dlms import GXReplyData
from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader
from gurux_dlms.objects import GXDLMSObjectCollection, GXDLMSData

class dlms():
    def __init__(self, parent=None):
        self.reader = None
        self.settings = GXSettings()
        self.object_list = None 

        ret = self.settings.get_fixed_config_parameters()
        self.reader = GXDLMSReader(self.settings.client, self.settings.media, self.settings.trace)

    def send_keep_alive(self):
        reply = GXReplyData()
        data = self.settings.client.keepAlive()
        if data:
            self.reader.readDLMSPacket(data, reply)
            reply.clear()

    def get_object_list(self):
        return self.object_list

    def reader_close(self):
        if self.reader:
            try:
                self.reader.close()
            except Exception:
                traceback.print_exc()

    def meter_read(self):
        try:
            ret = self.settings.get_fixed_config_parameters()
            if ret != 0:
                return
            
            self.reader = GXDLMSReader(self.settings.client, self.settings.media, self.settings.trace)
            print('------------------------------------------------------------')
            print ('Send SNRM and AARQ')
            print('------------------------------------------------------------')
            self.reader.initializeConnection()
            print('------------------------------------------------------------')
            print('Read Association View')
            print('------------------------------------------------------------')
            self.object_list = GXDLMSObjectCollection(self)
            self.object_list = self.reader.getAssociationView()
            print('------------------------------------------------------------')
            return True

        except Exception as e:
            # traceback.print_exc()
            print (str(e))
            return False
        
        # finally:
        #     if self.reader:
        #         try:
        #             self.reader.close()
        #         except Exception:
        #             traceback.print_exc()
        #     print("Ended. Press any key to continue.")
        #     pass


font_but = QtGui.QFont()
font_but.setFamily("Segoe UI Symbol")
font_but.setPointSize(10)
font_but.setWeight(95)

class window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 
        self.dlms = dlms()
        self.selected_obis = []
        self.tree_classid = None
        
    def ui_configure(self):
        self.setWindowTitle('DLMS Reader APL')
        self.setMinimumWidth(resolution.width() / 3)
        self.setMinimumHeight(resolution.height() / 1.5)
        # self.setStyleSheet("QWidget {\
        #                    background-color: rgba(0,41,59,255);}\
        #                    QScrollBar:horizontal {width: 1px;\
        #                    height: 1px;\
        #                    background-color: rgba(0,41,59,255);}\
        #                    QScrollBar:vertical {width: 1px;\
        #                    height: 1px;\
        #                    background-color: rgba(0,41,59,255);}")

        self.ui.pushButton_connect.setStyleSheet("margin: 1px;  padding: 7px; background-color: rgba(1,255,255,100); color: rgba(0,190,255,255); \
            border-style: solid; border-radius: 3px; border-width: 0.5px; border-color: rgba(127,127,255,255);")
        
        self.ui.pushButton_disconnect.setStyleSheet("margin: 1px;  padding: 7px; background-color: rgba(255,50,50,100); color: rgba(0,190,255,255); \
            border-style: solid; border-radius: 3px; border-width: 0.5px; border-color: rgba(127,127,255,255);")
        
        self.ui.pushButton_read_selected.setStyleSheet("margin: 1px;  padding: 7px; background-color: rgba(1,255,255,100); color: rgba(0,190,255,255); \
            border-style: solid; border-radius: 3px; border-width: 0.5px; border-color: rgba(127,127,255,255);")

        # self.ui.treeWidget.setStyleSheet("background-color: rgba(128,255,240,100); color: rgba(0,190,255,255); \
        #     border-style: solid; border-color: rgba(127,127,255,255);")

        ## Signals & Slots ##
        self.ui.textBrowser.append('DLMS Reader APL')
        self.ui.pushButton_connect.clicked.connect(self.meter_connect)
        self.ui.pushButton_disconnect.clicked.connect(self.meter_disconnect)
        self.ui.pushButton_read_selected.clicked.connect(self.read_all_selected)
        
        self.dlms.reader.displaymsg.connect(self.display)
        
        # self.model = QtWidgets.QFileSystemModel()
        # self.model.setRootPath('')
        # self.ui.treeView.setModel(self.model)
        # self.ui.treeView.setAnimated(False)
        # self.ui.treeView.setIndentation(20)
        # self.ui.treeView.setSortingEnabled(False)
        # self.ui.treeView.setWindowTitle("Object Tree")

        # self.tree = QtWidgets.QTreeWidget()
        # self.tree.setHeaderLabels(['logical name', 'description'])
        # self.tree.setAlternatingRowColors(True)

        # layout = QtWidgets.QVBoxLayout(self)
        # layout.addWidget(self.tree)
        # self.ui.tab_2.setLayout(layout)

        self.tree = self.ui.treeWidget
        #self.tree.setHeaderLabels(['logical name', 'description'])
        self.tree.setAlternatingRowColors(True)
        self.tree.setIndentation(30)
        # Connect the contextmenu
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.tree_context_menu)


    def tree_context_menu(self, point):
        # Infos about the node selected.
        index = self.tree.indexAt(point)
        if not index.isValid():
            return

        item = self.tree.itemAt(point)
        name = item.text(0)  # The text of the node.

        if item==self.tree_classid:
            return

        # We build the menu.
        menu = QtWidgets.QMenu()
        # menu.setTitle(str(name))
        action_name = menu.addAction(name)
        menu.addSeparator()
        action_read = menu.addAction("Read")
        action_write = menu.addAction("Write")
        action_read_all = menu.addAction("Read All Attribute")
        
        action = menu.exec_(self.tree.mapToGlobal(point))
        if action == action_read:
            self.display('Read Action Triggered: ' + str(name))
            # connect
            self.dlms.reader.initializeConnection()
            # read 
            val = self.dlms.reader.read(self.dlms.settings.client.objects.findByLN(ObjectType.NONE, str(name)), 2)
            val_str = self.dlms.reader.showValue(2, val)
            self.display('Attribute 2 value: ' + val_str)
            # disconnect
            self.dlms.reader_close()

        elif action == action_write:
            self.display('Write Action Triggered: ' + str(name))
        elif action == action_read_all:
            self.display('Read All Action Triggered: ' + str(name))            

    def display(self, msg):
        self.ui.textBrowser.append(msg)

    def meter_connect(self):
        # call('python3 main.py -r ln -t "Info" -c 16 -s 144 -a None -P "12345678" -S "/dev/ttyUSB0" -g "0.0.1.0.0.255:1" -g "0.0.1.0.0.255:2"', shell=True)
        if self.dlms.meter_read()==True:
            self.display('Connected with meter')
            object_list = GXDLMSObjectCollection(self)
            object_list = self.dlms.get_object_list()
            self.display('total objects: ' + str(len(object_list)))
            
            register_class_obj = GXDLMSObjectCollection(self)
            register_class_obj = object_list.getObjects(ObjectType.REGISTER)
            self.display('------------------------------------------------------------')
            self.display('total register objects: ' + str(len(register_class_obj)))
            
            self.tree_classid = QtWidgets.QTreeWidgetItem(self.tree, ['REGISTER CLASS', str(len(register_class_obj))])
            # self.tree_classid.setCheckState(0, QtCore.Qt.Checked)
            for i in range(0, len(register_class_obj), 1):
                tree_obis = QtWidgets.QTreeWidgetItem(self.tree_classid, [str(register_class_obj[i].logicalName), str(register_class_obj[i].description)])
                tree_obis.setCheckState(0, QtCore.Qt.Unchecked)

            self.display('reading scalar and units')
            self.dlms.reader.readScalerAndUnits()
            self.display('------------------------------------------------------------')
            self.dlms.reader_close()
        
    def meter_connect_other(self):
        ret_val = False
        # self.dlms.reader = GXDLMSReader(self.dlms.settings.client, self.dlms.settings.media, self.dlms.settings.trace)
        for physicalAdd in range(0, 0x3FFF):
            try:
                self.dlms.settings.get_dynamic_config_parameters(physicalAdd)
                self.dlms.reader = GXDLMSReader(self.dlms.settings.client, self.dlms.settings.media, self.dlms.settings.trace)
                self.dlms.reader.initializeConnection()
                print ('########################################')
                print("physical address is: " + str(physicalAdd))
                print ('########################################')
                ret_val = True
                break
            except Exception as e:
                print(str(e))

        if ret_val==True:
            self.display('------------------------------------------------------------')
            self.display('Connected with meter')
            # self.dlms.reader.getAssociationView()
            # object_list = GXDLMSObjectCollection(self)
            # object_list = self.dlms.get_object_list()
            # self.display('total objects: ' + str(len(object_list)))
            # register_class_obj = GXDLMSObjectCollection(self)
            # register_class_obj = object_list.getObjects(ObjectType.REGISTER)
            # self.display('------------------------------------------------------------')
            # self.display('total register objects: ' + str(len(register_class_obj)))
            
            # self.tree_classid = QtWidgets.QTreeWidgetItem(self.tree, ['REGISTER CLASS', str(len(register_class_obj))])
            # # self.tree_classid.setCheckState(0, QtCore.Qt.Unchecked)
            # for i in range(0, len(register_class_obj), 1):
            #     tree_obis = QtWidgets.QTreeWidgetItem(self.tree_classid, [str(register_class_obj[i].logicalName), str(register_class_obj[i].description)])
            #     tree_obis.setCheckState(0, QtCore.Qt.Unchecked)
                
            # self.display('reading scalar and units')
            # self.dlms.reader.readScalerAndUnits()
            # self.display('------------------------------------------------------------')
            self.dlms.reader_close()        


    def read_all_selected(self):
        total_child = self.tree_classid.childCount()
        self.selected_obis = []
        self.display('Total child: ' + str(total_child))
        for i in range(0, total_child, 1): 
            child = self.tree_classid.child(i)
            if child.checkState(0)==QtCore.Qt.Checked:
                # self.display('Child-' + str(i) + ' text: ' + str(child.text(0)))
                self.selected_obis.append(str(child.text(0)))        
        
        if self.selected_obis != [] and len(self.selected_obis) > 0:
            self.display ('read selected obis')
            self.display ('connect')
            # connect
            self.dlms.reader.initializeConnection()            
            for i in range(0, len(self.selected_obis), 1):
                self.display('read obis: ' + str(self.selected_obis[i]))
                val = self.dlms.reader.read(self.dlms.settings.client.objects.findByLN(ObjectType.NONE, self.selected_obis[i]), 2)
                self.display ('attribute 2 value: ' + str(val))
                time.sleep(0.5)
            # disconnect
            self.display ('disconnect')
            self.dlms.reader_close()                        


    def meter_disconnect(self):
        self.dlms.reader_close()
        self.display('Meter Disconnected')


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    # form = window()         # Instantiate the MyForm class above
    # #form.setWindowFlags(QtCore.Qt.FramelessWindowHint)
    # form.show()             # Call the show method to make visible
    # #splash.finish(myForm)
    # form.ui_configure()
    # sys.exit(app.exec_())     # This does not return until we close the window

    desktop = QtWidgets.QApplication.desktop()
    resolution = desktop.availableGeometry()
    myapp = window()
    myapp.setWindowOpacity(0.85)
    myapp.show()
    myapp.ui_configure()
    myapp.move(resolution.center() - myapp.rect().center())
    sys.exit(app.exec_())