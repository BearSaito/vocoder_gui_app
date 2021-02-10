# option
import argparse
# GUI
from PyQt5.QtCore import (QLineF, QPointF, QRectF, Qt, QTimer)
from PyQt5.QtGui import (QBrush, QColor, QPainter, QIntValidator,
                         )
from PyQt5.QtWidgets import (QApplication, QWidget, QGraphicsView, QGraphicsScene, QGraphicsItem,
                             QGridLayout, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton,
                             QMainWindow, QAction, qApp, QFileDialog, QMessageBox, QComboBox, QSlider, QRadioButton, QButtonGroup)
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import sys
# pyworld
import pyworld as pw
# audio
from audio.streamer import *
import numpy as np

DEBUG = True
DEBUG = False

"""main"""
def main(args):
    app = QtGui.QApplication([])
    mainWindow = MainWindow(args=args)
    mainWindow.show()
    sys.exit(app.exec_())


"""GUI"""
class MainWindow(QMainWindow):
    def __init__(self, parent=None, args=None):
        super(MainWindow, self).__init__(parent)
        centralWidget = QWidget()

        """波形"""
        win = pg.GraphicsWindow(title="Voice")
        win.setWindowTitle('Voice')  # windowのタイトル
        pg.setConfigOptions(antialias=True)  # アンチエイリアスをOn
        """変換前の音声データ"""
        plt = win.addPlot(row=0, col=0)
        plt.setTitle('<font size=\'4\' color=\'#FFFFFF\'>' +
                    'realtime voice' + '</font>')  # グラフのタイトル
        plt.showGrid(True, True, 1)  # 目盛り線の設定
        "表示する際にグラフをどのぐらい拡大するか設定"
        plt.setXRange(0, args.length)
        plt.setYRange(-1, 1)
        "左側に軸ラベルを設定"
        label = '<font color=\'#' + 'FFFFFF'+'\'>' + '変換前' + '</font>'
        unit = '<font color=\'#' + 'FFFFFF'+'\'>' + '' + '</font>'
        plt.setLabel('left', label, unit)
        plt.addLegend()  # 凡例を表示する
        "波形プロット"
        self.curve = plt.plot(pen=([255, 0, 0])) # 波形表示
        self.curve.setData([0])
        """変換後の音声データ"""
        plt2 = win.addPlot(row=1, col=0)
        plt2.setTitle('<font size=\'4\' color=\'#FFFFFF\'>' +
                    'conversion voice' + '</font>')  # グラフのタイトル
        plt2.showGrid(True, True, 1)  # 目盛り線の設定
        "表示する際にグラフをどのぐらい拡大するか設定"
        plt2.setXRange(0, args.length)
        plt2.setYRange(-1, 1)
        "左側に軸ラベルを設定"
        label2 = '<font color=\'#' + 'FFFFFF'+'\'>' + '変換後' + '</font>'
        unit2 = '<font color=\'#' + 'FFFFFF'+'\'>' + '' + '</font>'
        plt2.setLabel('left', label2, unit2)
        plt2.addLegend()  # 凡例を表示する
        "波形プロット"
        self.curve2 = plt2.plot(pen=([255, 0, 0])) # 波形表示
        self.curve2.setData([0])

        """メニューバー"""
        "アクション"
        openorigAction = QAction("&変換前の音声データの読み込み", self) # 読み込み
        openorigAction.setShortcut("Ctrl+O")
        openorigAction.setStatusTip("変換前の音声データの読み込み")
        openorigAction.triggered.connect(self.OrigWav_Open)
        self.saveorigAction = QAction("&変換前の音声データの書き出し", self) # 書き込み
        self.saveorigAction.setShortcut("Ctrl+S")
        self.saveorigAction.setStatusTip("変換前の音声データの書き出し")
        self.saveorigAction.triggered.connect(self.OrigWav_Save)
        self.saveorigAction.setEnabled(False)
        self.saveconvAction = QAction("&変換後の音声データの書き出し", self) # 書き込み
        self.saveconvAction.setShortcut("Ctrl+D")
        self.saveconvAction.setStatusTip("変換後の音声データの書き出し")
        self.saveconvAction.triggered.connect(self.ConvWav_Save)
        self.saveconvAction.setEnabled(False)
        exitAction = QAction("&終了", self) # 終了
        exitAction.setShortcut("Ctrl+Q")
        exitAction.setStatusTip("終了")
        exitAction.triggered.connect(qApp.quit)
        "メニューバー"
        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&ファイル")
        fileMenu.addAction(openorigAction)
        fileMenu.addAction(self.saveorigAction)
        fileMenu.addAction(self.saveconvAction)
        fileMenu.addSeparator()
        fileMenu.addAction(exitAction)

        "ステータスバー"
        self.statusBar().showMessage('Ready')
        
        """マイク・スピーカー"""
        self.ComboIn = QComboBox(self)
        self.ComboOut = QComboBox(self)
        micLayout_up = QVBoxLayout()
        micLayout_up.addWidget(QLabel("マイク"))
        micLayout_up.addWidget(self.ComboIn)
        micLayout_up.addWidget(QLabel("スピーカー"))
        micLayout_up.addWidget(self.ComboOut)
        
        


        """ボタン"""
        self.StartButton = QPushButton("&Start") # Startボタン生成
        self.StartButton.clicked.connect(self.Start) # Startボタン クリックイベント設定
        self.StopButton = QPushButton("&Stop") # Stopボタン生成
        self.StopButton.clicked.connect(self.Stop) # Stopボタン クリックイベント設定
        self.ResetButton = QPushButton("&Reset") # Resetボタン生成
        self.ResetButton.clicked.connect(self.Reset)  # Resetボタン クリックイベント設定
        self.ConveButton = QPushButton("&変換")  # Resetボタン生成
        self.ConveButton.clicked.connect(self.Conversion)  # Resetボタン クリックイベント設定
        
        buttonLayout_up = QVBoxLayout()  # レイアウト生成
        buttonLayout_up.addWidget(QLabel("ボタン"))
        buttonLayout_up.addWidget(self.StartButton) # レイアウトにStartボタン追加
        buttonLayout_up.addWidget(self.StopButton) # レイアウトにStopボタン追加
        buttonLayout_up.addWidget(self.ResetButton)  # レイアウトにResetボタン追加
        buttonLayout_up.addWidget(self.ConveButton)  # レイアウトにResetボタン追加
        
        """スライダー"""
        self.label_f0_rate = QLabel("f0 rate：1")
        self.Slider_f0_rate = QSlider(Qt.Horizontal, self)
        self.Slider_f0_rate.setGeometry(30, 40, 200, 30)
        self.Slider_f0_rate.setRange(-10, 10)
        self.Slider_f0_rate.setSingleStep(1)
        self.Slider_f0_rate.setPageStep(1)
        self.Slider_f0_rate.setValue(0)
        self.Slider_f0_rate.setTickPosition(QSlider.TicksBelow)
        self.Slider_f0_rate.setTickInterval(1)
        self.Slider_f0_rate.valueChanged[int].connect(self.change_f0_rate)
        self.Slider_f0_rate.setObjectName("f0 rate")
        
        self.label_sp_rate = QLabel("sp rate：1.0")
        self.Slider_sp_rate = QSlider(Qt.Horizontal, self)
        self.Slider_sp_rate.setGeometry(30, 40, 200, 30)
        self.Slider_sp_rate.setRange(1, 1000)
        self.Slider_sp_rate.setSingleStep(1)
        self.Slider_sp_rate.setPageStep(1)
        self.Slider_sp_rate.setValue(100)
        self.Slider_sp_rate.setTickPosition(QSlider.TicksBelow)
        self.Slider_sp_rate.setTickInterval(10)
        self.Slider_sp_rate.setObjectName("sp rate")
        self.Slider_sp_rate.valueChanged[int].connect(self.change_sp_rate)

        sliderLayout_up = QVBoxLayout()  # レイアウト生成
        sliderLayout_up.addWidget(self.label_f0_rate)
        sliderLayout_up.addWidget(self.Slider_f0_rate)
        sliderLayout_up.addWidget(self.label_sp_rate)
        sliderLayout_up.addWidget(self.Slider_sp_rate)
        
        """再生ボタン"""
        befforeButton = QRadioButton('変換前')
        aftterButton = QRadioButton('変換後')
        befforeButton.toggled.connect(self.RadioClicked)
        aftterButton.toggled.connect(self.RadioClicked)
        befforeButton.setChecked(True)
        self.gradioButton = QButtonGroup()
        self.gradioButton.addButton(befforeButton, 0)
        self.gradioButton.addButton(aftterButton, 1)
        self.PlayButton = QPushButton("&再生スタート") # Startボタン生成
        self.PlayButton.clicked.connect(self.Play)  # Startボタン クリックイベント設定
        playLayout_up = QVBoxLayout()  # レイアウト生成
        playLayout_up.addWidget(QLabel("再生"))
        playLayout_up.addWidget(befforeButton)  # レイアウトにStartボタン追加
        playLayout_up.addWidget(aftterButton)
        playLayout_up.addWidget(self.PlayButton) # レイアウトにStartボタン追加

        """全体のレイアウト"""
        propertyLayout = QVBoxLayout()
        propertyLayout.setAlignment(Qt.AlignTop)
        propertyLayout.addLayout(micLayout_up)
        propertyLayout.addLayout(buttonLayout_up)
        propertyLayout.addLayout(sliderLayout_up)
        propertyLayout.addLayout(playLayout_up)

        mainLayout = QHBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.addWidget(win)
        mainLayout.addLayout(propertyLayout)

        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle("Vocoder")
        self.timer = None
        
        """data"""
        self.wav = []  # データ
        self.synth = np.array([])
        """audio"""
        self.selected_input_device = ""
        self.streamer = self.AudioSetMic()  # audio
        self.streamer.start()
        self.speaker = self.AudioSetSpe()
        """PyWorld"""
        # self.f0_rate = 2.1
        # self.sp_rate = 0.725
        self.f0_rate = 1.0
        self.sp_rate = 1.0
        # self.f0_rate = 0
        # self.sp_rate = 0

    """マイクの設定"""
    def AudioSetMic(self, select=""):
        audio = pyaudio.PyAudio()
        
        if(select == ""):
            info = audio.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            for i in range(0, numdevices):
                if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    name = audio.get_device_info_by_host_api_device_index(0, i).get('name')
                    print(f"Input Device id {i} - {name}")
                    self.ComboIn.addItem(self.byte2str(name))

        devices = {}
        for i in range(audio.get_device_count()):
            dictionary = audio.get_device_info_by_index(i)
            device_name = dictionary["name"]
            devices[device_name] = i

        if args.device_id != -1:
            input_device_index = args.device_id
            self.selected_input_device = list(devices.keys())[list(
                devices.values()).index(args.device_id)]
        elif select != "":
            self.selected_input_device = ""
            for device in devices.keys():
                if select in device:
                    self.selected_input_device = device
                    input_device_index = devices[self.selected_input_device]
                    break
            if self.selected_input_device == "":
                input_device_index = devices[list(devices.keys())[0]]
        else:
            self.selected_input_device = ""
            for device in devices.keys():
                device = self.byte2str(device)
                if "マイク" in device:
                    self.selected_input_device = device
                    input_device_index = devices[self.selected_input_device]
                    break
            if self.selected_input_device == "":
                input_device_index = devices[list(devices.keys())[0]]
            # self.selected_input_device = self.ComboIn.currentText()
            # input_device_index = devices[self.selected_input_device]

        "その他設定"
        CHUNKS = 1024
        channel = 1
        self.RATE = dictionary['defaultSampleRate']
        "表示"
        print("=========="*4)
        print(f">selected_device:{self.selected_input_device}")
        print(f">input_device_index:{input_device_index}")
        print(f">RATE:{self.RATE}, channel:{channel}")
        print("==========" * 4)
        self.ComboIn.setCurrentIndex(self.ComboIn.findText(self.selected_input_device))
        streamer = AudioStreamer(
            self.RATE, channel, pyaudio.paInt16, CHUNKS, audio, input_device_index)
        return streamer

    """スピーカーの設定"""
    def AudioSetSpe(self, select=""):
        audio = pyaudio.PyAudio()
        
        if(select == ""):
            info = audio.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            for i in range(0, numdevices):
                if (audio.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
                    name = audio.get_device_info_by_host_api_device_index(0, i).get('name')
                    print(f"Output Device id {i} - {name}")
                    self.ComboOut.addItem(self.byte2str(name))

        devices = {}
        for i in range(audio.get_device_count()):
            dictionary = audio.get_device_info_by_index(i)
            device_name = dictionary["name"]
            devices[device_name] = i

        if args.device_id != -1:
            output_device_index = args.device_id
            self.selected_output_device = list(devices.keys())[list(
                devices.values()).index(args.device_id)]
        elif select != "":
            self.selected_output_device = ""
            for device in devices.keys():
                if select in device:
                    self.selected_output_device = device
                    output_device_index = devices[self.selected_output_device]
                    break
            if self.selected_output_device == "":
                output_device_index = devices[list(devices.keys())[0]]
        else:
            self.selected_output_device = self.ComboOut.currentText()
            output_device_index = devices[self.selected_output_device]
            
        

        "その他設定"
        CHUNKS = 1024
        channel = 1
        "表示"
        print("=========="*4)
        print(f">selected_device:{self.selected_output_device}")
        print(f">output_device_index:{output_device_index}")
        print(f">RATE:{self.RATE}, channel:{channel}")
        print("==========" * 4)
        self.ComboOut.setCurrentIndex(self.ComboOut.findText(self.selected_output_device))
        speaker = AudioPlaybackLoop(self.RATE, 1, 1024, output_device_index)
        return speaker

    def Reset(self):
        print(">Reset")
        self.saveorigAction.setEnabled(False)
        self.saveconvAction.setEnabled(False)
        self.wav = []
        self.synth = np.array([])
        self.Update_Plot()
        self.curve2.setData([0])
        self.streamer.reset()
        self.statusBar().showMessage('Reset')
        return True

    def Start(self):
        print(f">Start")
        print(f"self.selected_input_device:{self.selected_input_device}")
        print(f"self.comboIn.currentText():{self.ComboIn.currentText()}")
        if (self.selected_input_device not in self.ComboIn.currentText()):
            self.streamer = self.AudioSetMic(self.ComboIn.currentText())
            self.streamer.start()
            
        self.timer = QTimer()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.Update_Plot)
        self.timer.timeout.connect(self.Update_Date)
        self.Reset()
        self.streamer.restart()
        self.timer.start()
        self.statusBar().showMessage('Start')

    def Stop(self):
        print(f">Stop")
        self.statusBar().showMessage('Stop')
        if self.timer:
            print(f">Stop timer")
            self.saveorigAction.setEnabled(True)
            self.streamer.stop()
            self.timer.stop()
            self.timer = None
            data = self.streamer.get_all()
            if (data != b''):  # データがある場合
                res = np.frombuffer(data, dtype="int16") / \
                    32767.0
                    # 32768.0  # バイナリ->数値(int16)に変換, 正規化

    """データを更新"""
    def Update_Date(self):
        print(f">Update_Date")
        # data = self.streamer.get()  # データを取得
        data = self.streamer.get_all()
        if(DEBUG == True):print(f">data:{data}")
        if (data != b''):  # データがある場合
            res = np.frombuffer(data, dtype="int16") / \
                32767.0
                # 32768.0  # バイナリ->数値(int16)に変換, 正規化
            # self.wav.extend(res)  # データを追加
            self.wav = res

    """波形を更新"""
    def Update_Plot(self):
        print(f">Update_Plot")
        self.curve.setData(self.wav)

    """読み込み用のファイル名を取得"""
    def open(self):
        print(">open")
        r = QFileDialog.getOpenFileName(self, "Open File",
                None, "WAV Files (*.wav)")
        filename = r[0]
        return filename
    
    """書き込み用のファイル名を取得"""
    def save(self):
        print(">save")
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Save File")
        dialog.setNameFilters(["WAV Files (*.wav)", "All Files (*)"])
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        filename = ""
        if dialog.exec_():
            r = dialog.selectedFiles()
            filename = r[0]
        return filename

    """wavファイルを更新"""
    "変換前の音声データの読み込み"
    def OrigWav_Open(self):
        print(f">OrigWav_Open")
        filename = self.open()
        self.statusBar().showMessage(f'Read {filename}')
        data = self.streamer.read_wav(filename)
        self.wav = np.frombuffer(data, dtype="int16") / 32767.0
        self.saveorigAction.setEnabled(True)
        self.Update_Plot()
    "変換前の音声データの書き込み"
    def OrigWav_Save(self):
        print(f">OrigWav_Save")
        filename = self.save()
        self.statusBar().showMessage(f'Save {filename}')
        self.streamer.write_wav(self.streamer.get_all(), filename)
    "変換後の音声データの書き込み"
    def ConvWav_Save(self):
        print(f">ConvWav_Save")
        filename = self.save()
        self.statusBar().showMessage(f'Save {filename}')
        self.streamer.write_wav(self.synth.astype(np.int16).tobytes(),filename)

    """声変換"""
    def Conversion(self):
        print(f">Conversion")
        print(f"f0_rate:{self.f0_rate}, sp_rate:{self.sp_rate}")
        self.statusBar().showMessage(f'Start conversion')
        wavdata = self.streamer.get_all()
        if(len(self.wav) <= 0):
            reply = QMessageBox.information(self, "声変換", "変換前の音声データがありません\nStartボタンを押して録音するか\nファイル>変換前の音声データの読み込み から音声データを読み込んでください")
            return
        self.saveconvAction.setEnabled(True)
        wavdata = np.frombuffer(wavdata, dtype='int16').astype(np.float64)
        f0, t = pw.harvest(wavdata, self.RATE)  # 基本周波数の抽出
        sp = pw.cheaptrick(wavdata, f0, t, self.RATE)  # スペクトル包絡の抽出
        ap = pw.d4c(wavdata, f0, t, self.RATE)  # 非周期性指標の抽出

        "ピッチシフト"
        modified_f0 = self.f0_rate * f0
        "フォルマントシフト（周波数軸の一様な伸縮）"
        modified_sp = np.zeros_like(sp)
        sp_range = int(modified_sp.shape[1] * self.sp_rate)
        for f in range(modified_sp.shape[1]):
            if (f < sp_range):
                if self.sp_rate >= 1.0:
                    modified_sp[:, f] = sp[:, int(f / self.sp_rate)]
                else:
                    modified_sp[:, f] = sp[:, int(self.sp_rate * f)]
            else:
                modified_sp[:, f] = sp[:, f]

        self.synth = pw.synthesize(modified_f0, modified_sp, ap, self.RATE)
        self.curve2.setData(self.synth /32767.0)
        print(len(self.synth))
        self.statusBar().showMessage(f'Finish conversion')

    """change_f0_rate
    声の高さの調整 : 2倍にすれば1オクターブ上に、0.5倍にすれば1オクターブ下に
    """
    def change_f0_rate(self, value):
        print(f">change_f0_rate:{value}")
        # self.f0_rate = value
        # self.f0_rate = 1/4 * value +1
        self.f0_rate = 2 ** value
        self.label_f0_rate.setText(f"f0 rate：{self.f0_rate}")

    """change_sp_rate
    声色の調整 (> 0.0) : 女性の声にする場合は1.0より小さく、男性はその逆で大きく
    """
    def change_sp_rate(self, value):
        print(f">change_sp_rate:{value}")
        self.sp_rate = value / 100
        self.label_sp_rate.setText(f"sp rate：{self.sp_rate }")

    def Play(self):
        if (self.selected_output_device not in self.ComboOut.currentText()):
            self.speaker = self.AudioSetSpe(self.ComboOut.currentText())
        radioID = self.gradioButton.checkedId()
        print(f"radioID:{radioID}")
        wavdata = self.streamer.get_all() if radioID == 0 else self.synth.astype(np.int16).tobytes()

        if(len(wavdata) <= 0):
            reply = QMessageBox.information(self, "音声再生", f"再生する{self.gradioButton.checkedButton().text()}の音声データがありません")
            return
        self.statusBar().showMessage(f"Play {self.gradioButton.checkedButton().text()}の音声データ")
        self.speaker.play(wavdata)
        self.statusBar().showMessage(f"Finish {self.gradioButton.checkedButton().text()}の音声データ")

    def RadioClicked(self):
        radioBtn = self.sender()
        if radioBtn.isChecked():
            print(f"RadioButton:{radioBtn.text()}")

    def byte2str(self,input):
        if(isinstance(input, bytes)):
            return input.decode('Shift-JIS')
        else:
            return input
        

if __name__ == '__main__':
    "オプション"
    parser = argparse.ArgumentParser(
        description="vocoder")
    parser.add_argument('-wid', '--width', type=int, default=1280,
                        help="ウィンドウ幅")
    parser.add_argument('-hei', '--height', type=int, default=800,
                        help="ウィンドウ高さ")
    parser.add_argument('-l', '--length', type=int, default=3600*360,
                        help="録音時間")
    parser.add_argument('-s', '--show_devices', action="store_true", default=False,
                        help="マイクの詳細を表示")
    parser.add_argument('-d', '--device_id', type=int, default=-1,
                        help="マイクのID")
    args = parser.parse_args()
    main(args)
