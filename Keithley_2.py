import serial
import csv
import time
import datetime
import matplotlib.pyplot as plt
import numpy as np
from decimal import Decimal
class Keithley_6517b:
    def __init__(self):

        communication = "RJ45"          #RJ45 ou RS232
        self.NPLC = 2               #Nombre de PLC (0.01 à 10)
        self.trig_points = "250"        #Nombre de points trig (50000 max)
        self.voltage = 100              #Tension par le 6517b (changer la ligne 191)
        name = "6075_10tir_1Hz_200us_2PLC_4"

        date = datetime.datetime.now().strftime("%Y%m%d%H%M%S%z") #Date et heure
        self.csv_file_path = f'C:/Users/larran/Desktop/Arronax_15052024/Data_{date}_{name}.csv'#Path du fichier des données

        if communication == "RJ45":
            ip = "10.220.0.72"  #adresse ip du prologix
            GPIB = b'28'        #Adresse GPIB sur le keithley (sur le Keithley: menu ==> communication ==> GPIB ==> adresse)
            port = None
            
        if communication == "RS232":
            port = 'COM5'       #Vérifier sur le gestionnaire de périph
            ip = None

        if ip: #RJ45
             t = tcp_device(ip)
             t.config()
             self._write = t.write
             self._query = t.query
             self._write(b'++addr %s'%GPIB)

        else: #RS232
            self.ser = serial.Serial(port, timeout=1, baudrate=115200, rtscts=False, xonxoff=True)
            self.eol = b'\r'

    def _query(self, cmd):
        self._write(cmd)
        return self.ser.readline()

    def _write(self, cmd):
        self.ser.write(cmd + self.eol)
        #self._write = _write
        #self._query = _query

    def keithley_charge_init(self):
        self._write(b"*RST") 
        self._write(b':SYST:ZCH ON')
        self._write(b":TRACE:CLEAR")

    def test_param(self):
        self._write(b":SENSE:FUNC 'CHAR'")
        time.sleep(2)
        self._write(b':SYST:ZCH OFF')

        self._write(bytes(f"SENSE:CHAR:NPLC {self.NPLC}",'UTF-8'))
        self._write(b":SENSE:CHAR:AVER:TYPE NONE")
        self._write(b':SENSE:CHAR:RANGE:AUTO OFF')
        self._write(b':SENSE:CHAR:DIG:AUTO ON')
        self._write(b":SENSE:CHAR:MED:STAT OFF")
        #self._write(b":FORM:ELEM READ, RNUM, UNIT, TST")
        self._write(b':CALC:STAT OFF') #Opération math sur les données
        self._write(b':SYSTEM:LSYN:STAT OFF') #Synchronisation entre PLC et intégration du signal

    def trig_parameters(self):
        #Automatic trig
        self._write(bytes(f":TRAC:POINTS {self.trig_points}",'UTF-8'))
        self._write(bytes(f":TRIG:COUNT {self.trig_points}",'UTF-8'))
        self._write(b":TRIG:DEL 0.0")
        self._write(b':TRAC:FEED:CONT NEXT')

        #External Trig
        # self._write(b":TRIG:SOUR TLINK")
        # self._write(bytes(f":TRAC:POINTS {self.trig_points}",'UTF-8'))
        # self._write(bytes(f":TRIG:COUNT {self.trig_points}",'UTF-8'))
        # self._write(b":TRIG:DEL 0.0")
        # self._write(b':TRAC:FEED:CONT NEXT')

    def start_readings(self):
        self._write(b':INIT')

    def set_voltage(self):
        voltage = float(self.voltage)
        command = bytes(f":SOUR:VOLT {voltage}\n", 'UTF-8')
        self._write(command)

    def output_on(self):
        command = b"OUTPUT ON\n"
        self._write(command)

    def fetch_readings(self):
        actual_reading_number = 0
        while actual_reading_number < int(self.trig_points):
            print(actual_reading_number)
            actual_reading_number = int(self._query(b':TRAC:POINTS:ACT?'))
            #########################
            # if actual_reading_number == 1:
            #     self._write(b":TRIG:SOUR IMM")
            ########################
        self.data = self._query(b":TRAC:DATA?")

    def export_csv(self):
        string_data = self.data.decode('utf-8')
        fields = string_data.split(',')
        data = [fields[i:i + 3] for i in range(0, len(fields), 3)]
        transposed_data = list(map(list, zip(*data)))
        with open(self.csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerows(transposed_data)

    def import_csv(self):
        self.data = []
        with open(self.csv_file_path, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile, delimiter=',')
            for row in csv_reader:
                self.data.append(row)
        if int(self.trig_points) > 1:
            time = float(self.data[1][2][:-4]) - float(self.data[1][1][:-4])
            print(time)
        total_time = float(self.data[1][-1][:-4])
        print(total_time)

    def plot_graph(self):
        numeric_values = []
        for item in self.data[0]:
            value, text = item[:-5], item[-5:]
            numeric_values.append(float(value))

        time_values = []
        for item in self.data[1]:
            value, text = item[:-4], item[-4:]
            time_values.append(float(value))

        corrected_values = []
        for i in range(len(numeric_values) - 1):
            value = numeric_values[i+1] - numeric_values[i]
            corrected_values.append(float(value))

        mean_data = '%.2E' % Decimal(np.mean(corrected_values))
        std_data = '%.2E' % Decimal(np.std(corrected_values))
        time = '%.3E' % Decimal(float(self.data[1][2][:-4]) - float(self.data[1][1][:-4]))

        plt.subplot(2, 1, 1)
        plt.plot(time_values[1:], numeric_values[1:])
        plt.ylabel('Coulombs')
        plt.title('Real Values')

        plt.subplot(2, 1, 2)
        plt.plot(time_values[1:], corrected_values)
        plt.xlabel('Seconds')
        plt.ylabel('Coulombs')
        plt.title('Substracted values')

        plt.annotate(f'Mean: {mean_data} C', (time_values[int(np.ceil(len(time_values) * 0.80))], np.max(corrected_values)))
        plt.annotate(f'Standard deviation: {std_data} C',(time_values[int(np.ceil(len(time_values) * 0.80))], float(mean_data)))
        plt.annotate(f'Time: {time} s',(time_values[int(np.ceil(len(time_values) * 0.80))], np.min(corrected_values)))

        plt.show()

class tcp_device():
    def __init__(self, ip=None, timeout=10):
        import socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((ip, 1234))
        self.sock.settimeout(timeout)
        self.gpib_eot = b"\r\n"
    def write(self, msg):
        self.sock.sendall(msg + self.gpib_eot)
    def query(self, msg):
        r = b""
        self.write(msg)
        self.write(b"++read 65535\n")
        while True:
            t = self.sock.recv(65535)
            r += t
            if b'\n' in t:
                return r

    def read(self, n):
        self.write(b"++read 65535\n")
        return (self.sock.recv(n))
    def config(self, mode=1, auto=0, eoi=1, eos=1, eot_enable=0, eot_char=10):
        # see https://github.com/rambo/python-scpi/blob/master/scpi/transports/gpib/prologix.py for some values
        self.write(b"++mode %d\n" % mode)
        self.write(b"++auto %d\n" % auto)
        self.write(b"++eoi %d\n" % eoi)
        self.write(b"++eos %d\n" % eos)
        self.write(b"++eot_enable %d\n" % eot_enable)
        self.write(b"++eot_char %d\n" % eot_char)

if __name__ == "__main__":
    start_time = time.time()


    k = Keithley_6517b()
    #k = Keithley_6517b(ip = "10.220.0.72", GPIB = b'28')

    k.keithley_charge_init()
    k.trig_parameters()
    k.test_param()

    #Pour utiliser la sortie tension du Keithley
    #k.set_voltage()
    #k.output_on()

    k.start_readings()
    k.fetch_readings()
    stop_time = time.time()
    k.export_csv()
    k.import_csv()
    k.plot_graph()
    print(stop_time - start_time)

