import json
import os
import sys
import requests
import webbrowser
import pygetwindow as gw
import time
from datetime import datetime, date

from PyQt5.QtWidgets import QApplication, QMainWindow, QListWidget, QPushButton, QVBoxLayout, QWidget, QMessageBox, QComboBox, QDateEdit
from PyQt5.QtCore import QDate

# Mendaftarkan browser
webbrowser.register('basilisk', None, webbrowser.BackgroundBrowser("C:/Program Files/Basilisk/basilisk.exe"))
webbrowser.register('palemoon', None, webbrowser.BackgroundBrowser("C:/Program Files/Pale Moon/palemoon.exe"))
webbrowser.register('seamonkey', None, webbrowser.BackgroundBrowser("C:/Program Files/SeaMonkey/seamonkey.exe"))
webbrowser.register('maxthon', None, webbrowser.BackgroundBrowser("C:/Users/USER/AppData/Local/Maxthon/Maxthon.exe"))
webbrowser.register('vivaldi', None, webbrowser.BackgroundBrowser("C:/Users/USER/AppData/Local/Vivaldi/Application/vivaldi.exe"))
webbrowser.register('waterfox', None, webbrowser.BackgroundBrowser("C:/Program Files/Waterfox/waterfox.exe"))
webbrowser.register('chrome', None, webbrowser.BackgroundBrowser("C:/Program Files/Google/Chrome/Application/chrome.exe"))
webbrowser.register('firefox', None, webbrowser.BackgroundBrowser("C:/Program Files/Mozilla Firefox/firefox.exe"))
webbrowser.register('edge', None, webbrowser.BackgroundBrowser("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"))
webbrowser.register('brave', None, webbrowser.BackgroundBrowser("C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe"))
webbrowser.register('opera', None, webbrowser.BackgroundBrowser("C:/Users/USER/AppData/Local/Programs/Opera/opera.exe"))
webbrowser.register('operagx', None, webbrowser.BackgroundBrowser("C:/Users/USER/AppData/Local/Programs/Opera GX/opera.exe"))

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_click = 0

        self.setWindowTitle('URL Opener')
        self.setGeometry(100, 100, 400, 350)  # Mengatur ukuran window

        # Kombobox untuk memilih browser
        self.browser_choice = QComboBox()
        self.browser_choice.addItems(['Basilisk','Pale Moon','SeaMonkey','Firefox','Maxthon','Vivaldi','Waterfox','GX', 'Opera', 'Edge','Brave' ])
        # self.browser_choice.addItems(['Basilisk','Pale Moon','SeaMonkey','Maxthon','Vivaldi','Waterfox','GX', 'Opera', 'Edge','Brave' ])
        # self.browser_choice.addItems(['Brave'])

        # Date Picker (QDateEdit) untuk memilih tanggal
        self.date_picker = QDateEdit(QDate.currentDate())  # Initialize QDateEdit dengan tanggal saat ini
        self.date_picker.setDisplayFormat('yyyy-MM-dd')  # Mengatur format tampilan tanggal
        self.date_picker.setCalendarPopup(True)  # Menampilkan popup kalender

        # Daftar URL yang akan ditampilkan
        self.url_list = QListWidget()

        # Tombol untuk memuat URL dan membuka URL
        self.load_button = QPushButton('Load URLs')
        self.open_button = QPushButton('Open URL')

        # Menghubungkan tombol dengan fungsinya
        self.load_button.clicked.connect(self.load_urls)
        self.open_button.clicked.connect(self.open_url)

        # Menambahkan widget ke layout
        layout = QVBoxLayout()
        layout.addWidget(self.browser_choice)
        layout.addWidget(self.date_picker)  # Menambahkan date picker ke layout
        layout.addWidget(self.url_list)
        layout.addWidget(self.load_button)
        layout.addWidget(self.open_button)

        # Membuat kontainer dan menetapkannya sebagai widget utama
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Memuat riwayat URL dari file
        self.history_file = 'url_history.json'
        self.history = self.load_history()

    def load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r') as f:
                return json.load(f)
        return {}

    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f)

    def load_urls(self):
        selected_date = self.date_picker.date().toString('yyyy-MM-dd')

        try:
            url = f'http://iseng.test/api.php/?tanggal={selected_date}'

            print(url);

            response = requests.get(url)            
            response.raise_for_status()
            data = response.json()
            self.url_list.clear()
            for item in data:
                self.url_list.addItem(item['url'])
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    # import time  # Pastikan untuk mengimpor modul time di bagian atas

    def close_browser(self,browser):
        print('Close Browser : ')
        print(browser)

        if (browser == 'GX'):
            open_windows = gw.getWindowsWithTitle('Opera')
        else:
            open_windows = gw.getWindowsWithTitle(browser)
            
        print(open_windows)
        for j in range(len(open_windows)):  # Ubah ini untuk menghitung jendela yang terbuka
            open_windows[j].close()

    def open_url(self):
        browsers = [self.browser_choice.itemText(i) for i in range(self.browser_choice.count())]
        browser_terakhir = browsers[0]

        for browser in browsers:
            for i in range(self.url_list.count()):
                item = self.url_list.item(i)
                url = item.text()
                today = date.today().isoformat()  # Format tanggal yyyy-mm-dd

                # Cek apakah URL sudah dibuka hari ini di browser tertentu
                key = f"{url}|{browser}"
                if self.history.get(key) == today:
                    print(f"URL '{url}' sudah dibuka hari ini di {browser}. Melewatkan...")
                    continue

                if (browser_terakhir != browser):
                    self.close_browser(browser_terakhir)
                    browser_terakhir = browser

                # Menyimpan URL ke riwayat
                self.history[key] = today
                self.save_history()  # Simpan riwayat ke file

                try:
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    print(f"{browser} Item {i} dari {self.url_list.count()} Jam: {current_time}")
                    
                    brw = self.get_browser(browser)
                    brw.open(url)
                    time.sleep(10)  # Tambahkan jeda 10 detik setelah membuka URL

                    if (i % 5 == 0 and i>0):
                        self.close_browser(browser)

                except webbrowser.Error:
                    pass
            

    def get_browser(self, nama):
        if nama == 'Chrome':
            return webbrowser.get('chrome')
        elif nama == 'Basilisk':
            return webbrowser.get('basilisk')
        elif nama == 'SeaMonkey':
            return webbrowser.get('seamonkey')
        elif nama == 'Pale Moon':
            return webbrowser.get('palemoon')
        elif nama == 'Maxthon':
            return webbrowser.get('maxthon')
        elif nama == 'Vivaldi':
            return webbrowser.get('vivaldi')
        elif nama == 'Firefox':
            return webbrowser.get('firefox')
        elif nama == 'Waterfox':
            return webbrowser.get('waterfox')
        elif nama == 'Edge':
            return webbrowser.get('edge')
        elif nama == 'Brave':
            return webbrowser.get('brave')
        elif nama == 'Opera':
            return webbrowser.get('opera')
        elif nama == 'GX':
            return webbrowser.get('operagx')

    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
