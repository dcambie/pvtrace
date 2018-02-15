# -*- coding: utf-8 -*-

'''
subject: PvTrace_Gui
author: chong
first edit time: 06-02-2018
'''
from pvtrace.lscpm.Reactor import *
from pvtrace.lscpm.Dyes import *
from pvtrace.lscpm.Matrix import *
from pvtrace.lscpm.SolarSimulators import *
import sys, os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

lr305 = LuminophoreMaterial('Red305', 200)  # red
k160 = LuminophoreMaterial('K160', 1)  # green
blue_evonik = LuminophoreMaterial('Evonik_Blue', 1)  # blue
# Create polymeric matrix
pdms = Matrix('pdms')
pmma = Matrix('PMMA')


class PvTrace_Gui(QWidget):
    def __init__(self, reactorname='', luminophore="lr305", matix="pmma", cata="MB",
                 lamp='SolarSimulator', photo_con=0.004, solvent='ACN', pnum=100, visual=True):
        super(QWidget, self).__init__()

        self.initUI()

    def initUI(self):
        global grid
        grid = QGridLayout()
        grid.setSpacing(5)

        self.setLayout(grid)

        self.addPvTrace_label()

        self.addPvTrace_button()

        self.addPvTrace_combo()

        self.addPvTrace_linedit()

        self.addPvTrace_check()

        self.setWindowIcon(QIcon('sun.png'))
        self.setWindowTitle('PvTrace_chong')
        self.setGeometry(900, 300, 500, 200)

        self.center()
        self.show()

    def addPvTrace_label(self):
        names = ['Open file', 'Reactor name', 'Luminophor',
                 'Matrix', 'Photocatalyst', 'Photocatalyst_con',
                 'solvent', 'LampType', 'Number of Photon', 'Visualization']
        positions = [(i, j) for i in range(5) for j in [1, 3]]

        for position, name in zip(positions, names):
            Plabel = QLabel(name)
            grid.addWidget(Plabel, *position)

    def addPvTrace_button(self):
        btn = QPushButton('open file', self)
        self.fileLabel = QLabel(".ini", self)
        btn.clicked.connect(self.Choose_file)
        grid.addWidget(btn, 0, 2)
        grid.addWidget(self.fileLabel, 0, 4)

        runbtn = QPushButton('Run', self)
        grid.addWidget(runbtn, 5, 4)
        runbtn.clicked.connect(self.runPvTrace)

    def Choose_file(self):
        filename = QFileDialog.getOpenFileName(self, "open", "D:\PvTrace_git\pvtrace-fork\data/reactors")[0]
        filename_look = os.path.basename(filename)
        filename_lookshort = os.path.splitext(filename_look)[0]
        self.reactorname = filename_lookshort
        self.fileLabel.setText(filename_lookshort)

    def addPvTrace_combo(self):  # fix me
        combo_lum = QComboBox(self)
        combo_lum.addItem("lr305")
        combo_lum.addItem("k160")
        combo_lum.addItem("blue_evonik")
        grid.addWidget(combo_lum, 1, 2)

        self.luminophore = combo_lum.currentText()

        combo_matr = QComboBox(self)
        combo_matr.addItem("PMMA")
        combo_matr.addItem("PDMS")
        grid.addWidget(combo_matr, 1, 4)

        self.matrix = combo_matr.currentText()

        combo_cata = QComboBox(self)
        combo_cata.addItem("MB")
        combo_cata.addItem("EY")
        combo_cata.addItem("Ru(bpz)3")
        grid.addWidget(combo_cata, 2, 2)

        self.cata = combo_cata.currentText()

        combo_lamp = QComboBox(self)
        combo_lamp.addItem("SolarSimulator")
        combo_lamp.addItem("Sun")
        combo_lamp.addItem("Blue LEDs")
        combo_lamp.addItem("White LEDs")
        grid.addWidget(combo_lamp, 3, 4)

        self.lamp = combo_lamp.currentText()

    def addPvTrace_linedit(self):
        con_edit = QLineEdit(self)
        grid.addWidget(con_edit, 2, 4)
        con_edit.textChanged[str].connect(self.onChanged1)

        sol_edit = QLineEdit(self)
        grid.addWidget(sol_edit, 3, 2)
        sol_edit.textChanged[str].connect(self.onChanged2)

        pnum_edit = QLineEdit(self)
        grid.addWidget(pnum_edit, 4, 2)
        pnum_edit.textChanged[str].connect(self.onChanged3)

    def onChanged1(self, text):
        self.photo_con = text

    def onChanged2(self, text):
        self.solvent = text

    def onChanged3(self, text):
        self.pnum = text

    def addPvTrace_check(self):
        cb = QCheckBox('turn on', self)
        grid.addWidget(cb, 4, 4)
        # cb.toggle()
        cb.stateChanged.connect(self.changevisual)

    def changevisual(self, state):

        if state == Qt.Checked:
            self.visual = True
        else:
            self.visual = False

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # def lumonActivated(self):


    def runPvTrace(self):
        scene = pvtrace.Scene(level=logging.INFO, uuid="overwrite_me")
        logger = logging.getLogger('pvtrace')

        lr305 = LuminophoreMaterial('Red305', 200)  # red
        k160 = LuminophoreMaterial('K160', 1)  # green
        blue_evonik = LuminophoreMaterial('Evonik_Blue', 1)  # blue
        # Create polymeric matrix
        PDMS = Matrix('pdms')
        PMMA = Matrix('PMMA')

        # Create LSC-PM DYE material

        reactor = Reactor(reactor_name=self.reactorname, luminophore=vars()[self.luminophore],
                          matrix=vars()[self.matrix], photocatalyst=self.cata,
                          photocatalyst_concentration=float(self.photo_con), solvent=self.solvent)
        scene.add_objects(reactor.scene_obj)

        # lamp = LightSource(lamp_type='White LEDs')
        # lamp.set_LED_voltage(voltage=8)
        # lamp.set_lightsource(irradiated_area=(0.05, 0.05), distance=0.025)
        lamp = LightSource(lamp_type=self.lamp)
        # fixed by chong in order to run the different reactor without altering the scripts
        lamp.set_lightsource(irradiated_length=reactor.lsc.size[0], irradiated_width=reactor.lsc.size[1], distance=0.025)
        # lamp.set_lightsource(irradiated_area=(reactor.lsc.size[0], 0.15035), distance=0.025)
        # lamp.move_lightsource(vector=(0, 0.01735))

        trace = pvtrace.Tracer(scene=scene, source=lamp.source, throws=int(self.pnum), use_visualiser=self.visual,
                               show_axis=False, show_counter=False, db_split=True, preserve_db_tables=True)
        # set color on Trace.py while visualizing

        # Run simulation
        tic = time.clock()
        logger.info('Simulation Started (time: ' + str(tic) + ')')
        trace.start()
        toc = time.clock()
        logger.info('Simulation Ended (time: ' + str(toc) + ', elapsed: ' + str(toc - tic) + ' s)')

        label = subprocess.check_output(["git", "describe", "--always"], cwd=PVTDATA, shell=True)
        logger.info('PvTrace ' + str(label) + ' simulation ended')

        print(scene.stats.print_excel_header() + "\n")
        print(scene.stats.print_excel() + "\n")

        # keys = scene.stats.db.objects_with_records()
        # print(keys)
        # channels_with_photons = []
        # max = 0
        # for solid_object in keys:
        #     if solid_object.startswith("Channel"):
        #         channels_with_photons.append(solid_object)

        photons_in_object = {}
        photonsum = 0
        for obj in scene.objects:
            if type(obj) is pvtrace.Devices.Channel and len(obj.store) > 0:
                photon_loss = len(obj.store['loss'])
                photons_in_object[obj.name] = photon_loss

        logger.info("Photons in channels: " + str(photons_in_object))

        print("Channel No, Photons")
        for entry, value in photons_in_object.items():
            print(str(entry)[7:] + ", " + str(value))

        scene.stats.create_graphs()

        toc2 = time.clock()
        t_span = toc2 - tic
        # print(photons_in_object)
        print("it takes %0.1f secs to complete the whole simulation" % t_span)


def main():
    app = QApplication(sys.argv)
    PT = PvTrace_Gui()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
