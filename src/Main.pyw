from PyQt5 import QtCore
from PyQt5.QtGui import QFont, QColor, QTextCursor
from PyQt5.QtWidgets import QApplication, QWidget, QStyle, QPushButton, QMessageBox, QGridLayout, QVBoxLayout, QHBoxLayout, QStackedLayout,\
                            QGroupBox, QLabel, QComboBox, QFileDialog, QTextEdit, QLineEdit, QSpacerItem, QProgressBar, QMenuBar, QAction
import os, sys
import DriverFunc

class MainWindow(QWidget):

    fileNames = []
    modifyPattern = DriverFunc.ModifyPattern.MP_YYYYMMDD

    def __init__(self):
        QWidget.__init__(self)

        self.setGeometry(700, 400, 1, 1)
        self.setWindowTitle("Date2Exif")
        self.setStyleSheet('QGroupBox { margin-top: 7px; border-style: outset; border-width: 2px; border-radius: 5px; border-color: grey; }'
                           'QGroupBox:title { subcontrol-origin: margin; left: 7px; }'
                           'QMenuBar { background-color: #E8E8E8; border-style: solid; border-width: 1px; border-color: grey}')


        QMessageBox.warning(self, "Warning", "Remember to backup your images before proceding.", QMessageBox.Ok)
        

        mainLayout = QGridLayout()
        self.setLayout(mainLayout)

        menuBar = QMenuBar()
        mainLayout.setMenuBar(menuBar)

        menuBar = menuBar.addMenu("&Help")
        action = QAction("How to use", self)
        action.triggered.connect(self.displayHelp)
        menuBar.addAction(action)

        action = QAction("About", self)
        action.triggered.connect(lambda : QMessageBox.about(self, "About", "This is a batch image exif date modifier\n\nMade using:\nPyqt5\nPieixf"))
        menuBar.addAction(action)


        self.createStackPage1()
        mainLayout.addWidget(self.page1, 0, 0, 2, 1)

        self.createOutputBox()
        mainLayout.addWidget(self.outputBox, 2, 0, 12, 1)
        

    def displayHelp(self):
        QMessageBox.about(self, "Help", """
1. This only works for .jpg/.jpeg files.
Make sure the there are no other numbers to the
left of the "YYYYMMDD"/date format in the filename,
spaces or dashes between the date format are fine.
     e.g [abc@2020_11_28-img.jpg]<-ok
           [n13_2015_06_21_gmi.jpg]<-not ok\n
2. There are two modes (Set) and (Remove).
Set will add the timestamp onto the images
while Remove will revert it back to normal.\n
3. Click on the file icon to select your images.\n
4. Select the date format that correspond to
the chosen images' name.\n
5. Press start.\n
If the application is not responding, wait for
awhile, it is still running in the background
""")



    def createStackPage1(self):
        self.page1 = QGroupBox()
        self.page1.setMaximumWidth(1000)

        vlayout = QVBoxLayout()
        vlayout.setAlignment(QtCore.Qt.AlignTop)
        self.page1.setLayout(vlayout)

        #

        self.modeSelectComboBox = QComboBox()
        self.modeSelectComboBox.addItems(["Set Date", "Remove Date"])
        self.modeSelectComboBox.currentIndexChanged.connect(self.modeChange)
        self.modeSelectLabel = QLabel("Select Mode      ")
        
        hlayout = QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignLeft)
        hlayout.addWidget(self.modeSelectLabel)
        hlayout.addWidget(self.modeSelectComboBox)


        vlayout.addLayout(hlayout)
        vlayout.addSpacerItem(QSpacerItem(1, 20))

        #

        label = QLabel("Select Image(s)")
        button = QPushButton(self.style().standardIcon(getattr(QStyle, "SP_DialogOpenButton")), "")
        button.clicked.connect(self.selectFile)
        button.setMinimumSize(50, 25)
        self.fileDisplay = QLineEdit()
        self.fileDisplay.setMinimumWidth(200)
        self.fileDisplay.setReadOnly(True)

        hlayout = QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignCenter)
        hlayout.setSpacing(10)
        hlayout.addWidget(label)
        hlayout.addWidget(self.fileDisplay)
        hlayout.addWidget(button)

        vlayout.addLayout(hlayout)

        #
        
        self.dateComboBox = QComboBox()
        self.dateComboBox.addItems(["YYYY-MM-DD (Whatsapp)", "YYYY-DD-MM", "DD-MM-YYYY", "MM-DD-YYYY"])
        self.dateComboBox.currentIndexChanged.connect(self.formatChange)
        self.dateComboBox.setFixedWidth(175)
        label = QLabel("Date Format      ")

        hlayout = QHBoxLayout()
        hlayout.setAlignment(QtCore.Qt.AlignLeft)
        hlayout.addWidget(label)
        hlayout.addWidget(self.dateComboBox)

        vlayout.addLayout(hlayout)
        vlayout.addSpacerItem(QSpacerItem(1, 20))

        #

        self.startButton = QPushButton("Start")
        self.startButton.clicked.connect(self.processFiles)
        vlayout.addWidget(self.startButton, QtCore.Qt.AlignBottom)



    def createOutputBox(self):
        self.outputBox = QGroupBox("Output")
        self.outputBox.setMaximumWidth(1000)

        vlayout = QVBoxLayout()
        vlayout.setAlignment(QtCore.Qt.AlignTop)
        self.outputBox.setLayout(vlayout)

        self.outputBoxText = QTextEdit()
        vlayout.addWidget(self.outputBoxText)

        self.outputBoxPbar = QProgressBar()
        self.outputBoxPbar.setValue(0)
        self.outputBoxPbar.setDisabled(True)
        button = QPushButton("Clear")
        button.clicked.connect(self.clearOutput)
        button.setMinimumSize(50, 25)
        
        hlayout = QHBoxLayout()
        hlayout.setSpacing(30)
        hlayout.addWidget(self.outputBoxPbar)
        hlayout.addWidget(button)

        vlayout.addLayout(hlayout)
        


    def modeChange(self, idx):
        if idx == 0:
            self.dateComboBox.setDisabled(False)
            self.dateComboBox.setCurrentIndex(1)
            self.dateComboBox.setCurrentIndex(0)
        else:
            self.dateComboBox.setDisabled(True)
            self.modifyPattern = DriverFunc.ModifyPattern.MP_REMOVE 



    def formatChange(self, idx):
        self.modifyPattern = idx



    def clearOutput(self):
        self.outputBoxPbar.setValue(0)
        self.outputBoxPbar.setDisabled(True)
        self.outputBoxText.setText("")



    def selectFile(self):
        defualtDir = os.environ.get("HOMEPATH", "")
        file = QFileDialog.getOpenFileNames(self, "Select File/Folder", defualtDir, "Images (*.jpg *.jpeg)")
        self.fileNames = file[0] # get the list of file names from [0] element of the tuple
        
        count = len(self.fileNames)
        if count > 0:
            self.fileDisplay.setText(self.fileNames[0] + ("" if count < 2 else f"...+{count-1} item(s)"))
        else:
            self.fileDisplay.setText("")

        self.startButton.setText("Start")



    def processFiles(self):
        if(self.fileNames == None or len(self.fileNames) == 0):
            QMessageBox.warning(self, "Warning", "There are no files selected", QMessageBox.Ok)
        else:
            retryCases = []

            self.outputBoxPbar.setDisabled(False)
            self.outputBoxPbar.setMaximum(len(self.fileNames))
            self.page1.setDisabled(True)


            for idx, fileName in enumerate(self.fileNames):
                result = DriverFunc.loadImg(fileName, self.modifyPattern)

                if(result == DriverFunc.ErrorTypes.ET_sucess):
                    self.outputBoxText.setTextColor(QColor(21, 194, 21))
                    self.outputBoxText.insertPlainText(f"Done: " + fileName + "\n")
                else:
                    self.outputBoxText.setTextColor(QColor(194, 21, 21))
                    if(result == DriverFunc.ErrorTypes.ET_wrong_file_type):
                        self.outputBoxText.insertPlainText(f"Error -Wrong file format- : " + fileName + "\n")
                    elif(result == DriverFunc.ErrorTypes.ET_cant_open):
                        self.outputBoxText.insertPlainText(f"Error -File not found  or data might be corrupted- : " + fileName + "\n")
                    elif(result == DriverFunc.ErrorTypes.ET_wrong_format):
                        self.outputBoxText.insertPlainText(f"Error -Unable to find date in image's title- : " + fileName + "\n")

                    retryCases.append(fileName)
                
                self.outputBoxText.moveCursor(QTextCursor.End)
                self.outputBoxPbar.setValue(idx + 1)

            
            self.outputBoxText.setTextColor(QColor(0, 0, 0))
            self.outputBoxText.insertPlainText("Finished!")
            self.page1.setDisabled(False)

            count = len(retryCases)
            if count > 0:
                self.outputBoxText.insertPlainText(f" There were {count} file(s) that faced an error, you can retry them\n\n")
                self.outputBoxText.moveCursor(QTextCursor.End)
                self.fileNames = retryCases
                self.fileDisplay.setText(self.fileNames[0] + ("" if count < 2 else f"...+{count-1} item(s)"))
                self.startButton.setText("Retry")
            else:
                self.outputBoxText.insertPlainText("\n\n")
                self.fileNames = []
                self.startButton.setText("Start")
                self.fileDisplay.setText("")


if __name__ == "__main__":
    app = QApplication([])
    app.setFont(QFont("SansSerif", 10))
    UI = MainWindow()
    UI.show()

    sys.exit(app.exec_())