import sys, json, threading, random
from pathlib import Path
from queue import Queue
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout,
    QHBoxLayout, QFileDialog, QProgressBar, QGroupBox, QComboBox,
    QCheckBox, QSpinBox, QLineEdit, QGridLayout
)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QPalette, QColor, QFont

# -------------------- GUI CLASS --------------------
class DevAutoGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 DevAuto | KaboSec-DevDark")
        self.setGeometry(250, 100, 1050, 650)
        self.queue = Queue()

        # خلفية رئيسية
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#111118"))
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # ---- Layout أساسي ----
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # ---- العنوان ----
        title = QLabel("🚀 DevAuto | KaboSec-DevDark")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00f7ff, stop:1 #00ff99);")
        main_layout.addWidget(title)

        # ---- Grid للأقسام ----
        grid = QGridLayout()
        main_layout.addLayout(grid)

        # ===== LOAD COMBO =====
        combo_group = QGroupBox("---- Load Combo ----")
        combo_group.setStyleSheet(self.group_style())
        c_layout = QVBoxLayout()
        self.btn_load_combo = QPushButton("📂 Load Combo")
        self.chk_duplicates = QCheckBox("Remove Duplicates")
        self.threads_spin = QSpinBox(); self.threads_spin.setRange(1,1000); self.threads_spin.setValue(100)
        self.timeout_spin = QSpinBox(); self.timeout_spin.setRange(1,10000); self.timeout_spin.setValue(20)
        for w in [self.btn_load_combo, self.chk_duplicates, QLabel("Threads:"), self.threads_spin, QLabel("Timeout:"), self.timeout_spin]:
            c_layout.addWidget(w)
        combo_group.setLayout(c_layout)
        grid.addWidget(combo_group, 0,0)

        # ===== LOAD PROXIES =====
        proxy_group = QGroupBox("---- Load Proxies ----")
        proxy_group.setStyleSheet(self.group_style())
        p_layout = QVBoxLayout()
        self.btn_load_proxies = QPushButton("📂 Load Proxies File")
        self.proxy_type = QComboBox(); self.proxy_type.addItems(["HTTP/S","SOCKS4","SOCKS5"])
        self.proxy_link = QLineEdit(); self.proxy_link.setPlaceholderText("Proxy List Link")
        self.btn_load_link = QPushButton("🌐 Load From Link")
        for w in [self.btn_load_proxies, QLabel("Proxies Type:"), self.proxy_type, self.proxy_link, self.btn_load_link]:
            p_layout.addWidget(w)
        proxy_group.setLayout(p_layout)
        grid.addWidget(proxy_group, 0,1)

        # ===== OPTIONS =====
        opt_group = QGroupBox("---- Options ----")
        opt_group.setStyleSheet(self.group_style())
        o_layout = QVBoxLayout()
        self.btn_start = QPushButton("▶ Start")
        self.btn_stop = QPushButton("⏹ Stop")
        self.btn_results = QPushButton("📊 Results")
        for b in [self.btn_start, self.btn_stop, self.btn_results]:
            o_layout.addWidget(b)
        opt_group.setLayout(o_layout)
        grid.addWidget(opt_group, 0,2)

        # ===== TELEGRAM HITS =====
        tg_group = QGroupBox("---- Telegram Hits ----")
        tg_group.setStyleSheet(self.group_style())
        t_layout = QVBoxLayout()
        self.tg_id = QLineEdit(); self.tg_id.setPlaceholderText("Your Telegram ID")
        self.tg_token = QLineEdit(); self.tg_token.setPlaceholderText("Your Bot Token")
        self.btn_tg_check = QPushButton("Check")
        for w in [self.tg_id, self.tg_token, self.btn_tg_check]:
            t_layout.addWidget(w)
        tg_group.setLayout(t_layout)
        grid.addWidget(tg_group, 1,0)

        # ===== STATISTICS =====
        stat_group = QGroupBox("---- Statistics ----")
        stat_group.setStyleSheet(self.group_style())
        s_layout = QVBoxLayout()
        self.lbl_remain = QLabel("Remain : 0")
        self.lbl_valid = QLabel("Valid : 0")
        self.lbl_invalid = QLabel("Invalid : 0")
        self.lbl_cpm = QLabel("CPM : 0")
        self.lbl_retry = QLabel("Retry : 0")
        for l in [self.lbl_remain,self.lbl_valid,self.lbl_invalid,self.lbl_cpm,self.lbl_retry]:
            l.setStyleSheet("color:#00ff99; font-weight:bold;")
            s_layout.addWidget(l)
        stat_group.setLayout(s_layout)
        grid.addWidget(stat_group, 1,1)

        # ===== LOGS =====
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background:#0d0d15; color:#00ffcc; font-family:Consolas; font-size:12px;")
        main_layout.addWidget(self.log_area)

        # ===== PROGRESS =====
        self.progress = QProgressBar()
        self.progress.setStyleSheet(
            "QProgressBar {border:1px solid #444; border-radius:4px; text-align:center; color:white;}"
            "QProgressBar::chunk {background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #06beb6, stop:1 #48b1bf);}"
        )
        main_layout.addWidget(self.progress)

        # ===== EXPORT BUTTONS =====
        exp_layout = QHBoxLayout()
        self.btn_json = QPushButton("💾 Export JSON")
        self.btn_csv = QPushButton("📑 Export CSV")
        exp_layout.addWidget(self.btn_json); exp_layout.addWidget(self.btn_csv)
        main_layout.addLayout(exp_layout)

        # Animation للعنوان
        self.anim = QPropertyAnimation(title, b"geometry")
        self.anim.setDuration(3000)
        self.anim.setStartValue(QRect(0, 0, 400, 40))
        self.anim.setEndValue(QRect(300, 0, 500, 40))
        self.anim.setLoopCount(-1)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

        # Timer للـ Logs
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_logs)
        self.timer.start(400)

        # ===== ربط الوظائف الرئيسية =====
        self.btn_load_combo.clicked.connect(self.load_combo)
        self.btn_load_proxies.clicked.connect(self.load_proxies)
        self.btn_load_link.clicked.connect(self.load_proxies_from_link)
        self.btn_start.clicked.connect(self.start_scan)
        self.btn_stop.clicked.connect(self.stop_scan)
        self.btn_results.clicked.connect(self.show_results)
        self.btn_json.clicked.connect(self.export_json)
        self.btn_csv.clicked.connect(self.export_csv)
        self.btn_tg_check.clicked.connect(self.check_telegram)

        # ===== متغيرات الفحص =====
        self.combo_list = []
        self.proxies_list = []
        self.results = []
        self.is_running = False
        self.threads = []
        self.stats = {"remain":0,"valid":0,"invalid":0,"cpm":0,"retry":0}

    # ---- Helpers ----
    def group_style(self):
        return ("QGroupBox {color:#00f7ff; font-weight:bold; border:1px solid #00f7ff; "
                "margin-top:6px;} QGroupBox::title{subcontrol-origin: margin; left:10px; padding:0 5px;}")

    def log(self, text):
        self.queue.put(text)

    def update_logs(self):
        while not self.queue.empty():
            self.log_area.append(self.queue.get())

    # ---- الوظائف الرئيسية ----
    def load_combo(self):
        file, _ = QFileDialog.getOpenFileName(self, "Load Combo", "", "Text Files (*.txt);;All Files (*)")
        if file:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                combos = [line.strip() for line in f if line.strip()]
            if self.chk_duplicates.isChecked():
                combos = list(set(combos))
            self.combo_list = combos
            self.stats["remain"] = len(self.combo_list)
            self.lbl_remain.setText(f"Remain : {self.stats['remain']}")
            self.log(f"Loaded {len(combos)} combos.")

    def load_proxies(self):
        file, _ = QFileDialog.getOpenFileName(self, "Load Proxies", "", "Text Files (*.txt);;All Files (*)")
        if file:
            with open(file, "r", encoding="utf-8", errors="ignore") as f:
                proxies = [line.strip() for line in f if line.strip()]
            self.proxies_list = proxies
            self.log(f"Loaded {len(proxies)} proxies.")

    def load_proxies_from_link(self):
        link = self.proxy_link.text().strip()
        if link:
            try:
                import requests
                resp = requests.get(link, timeout=5)
                proxies = [line.strip() for line in resp.text.splitlines() if line.strip()]
                self.proxies_list = proxies
                self.log(f"Loaded {len(proxies)} proxies from link.")
            except Exception as e:
                self.log(f"Proxy link failed: {e}")

    def start_scan(self):
        if not self.combo_list:
            self.log("No combos loaded.")
            return
        self.is_running = True
        self.stats["valid"] = self.stats["invalid"] = self.stats["retry"] = self.stats["cpm"] = 0
        self.lbl_valid.setText("Valid : 0")
        self.lbl_invalid.setText("Invalid : 0")
        self.lbl_retry.setText("Retry : 0")
        self.lbl_cpm.setText("CPM : 0")
        self.progress.setMaximum(len(self.combo_list))
        self.progress.setValue(0)
        self.results.clear()
        thread_count = self.threads_spin.value()
        timeout = self.timeout_spin.value()
        self.log(f"Started scan with {thread_count} threads and {timeout}s timeout.")
        self.threads = []
        for _ in range(thread_count):
            t = threading.Thread(target=self.scan_worker, args=(timeout,))
            t.start()
            self.threads.append(t)
        # CPM Timer
        self.cpm_count = 0
        self.cpm_timer = QTimer()
        self.cpm_timer.timeout.connect(self.update_cpm)
        self.cpm_timer.start(1000)

    def stop_scan(self):
        self.is_running = False
        self.log("Scan stopped.")

    def scan_worker(self, timeout):
        while self.is_running and self.combo_list:
            try:
                combo = self.combo_list.pop()
                proxy = random.choice(self.proxies_list) if self.proxies_list else None
                # --- فحص كومبو وهمي متقدم وذكي ---
                res = self.advanced_check(combo, proxy, timeout)
                self.stats["remain"] = len(self.combo_list)
                self.lbl_remain.setText(f"Remain : {self.stats['remain']}")
                if res["valid"]:
                    self.stats["valid"] += 1
                    self.lbl_valid.setText(f"Valid : {self.stats['valid']}")
                    self.results.append({"combo":combo,"proxy":proxy,"status":"valid"})
                    self.log(f"Valid: {combo}")
                else:
                    self.stats["invalid"] += 1
                    self.lbl_invalid.setText(f"Invalid : {self.stats['invalid']}")
                    self.results.append({"combo":combo,"proxy":proxy,"status":"invalid"})
                    self.log(f"Invalid: {combo}")
                self.progress.setValue(self.progress.value()+1)
                self.cpm_count += 1
            except Exception as e:
                self.stats["retry"] += 1
                self.lbl_retry.setText(f"Retry : {self.stats['retry']}")
                self.log(f"Retry: {e}")

    def advanced_check(self, combo, proxy, timeout):
        # مكانك لإضافة الفحص الذكي الحقيقي حسب نوع الخدمة
        import time
        time.sleep(random.uniform(0.05, 0.15))
        # فحص وهمي: كل كومبو ينتهي بـ 1 يعتبر valid
        return {"valid": combo.endswith("1")}

    def update_cpm(self):
        self.stats["cpm"] = self.cpm_count * 60
        self.lbl_cpm.setText(f"CPM : {self.stats['cpm']}")
        self.cpm_count = 0

    def show_results(self):
        self.log(f"Total Results: {len(self.results)}")
        valid = [r for r in self.results if r["status"] == "valid"]
        invalid = [r for r in self.results if r["status"] == "invalid"]
        self.log(f"Valid: {len(valid)} | Invalid: {len(invalid)}")

    def export_json(self):
        file, _ = QFileDialog.getSaveFileName(self, "Export JSON", "", "JSON Files (*.json)")
        if file:
            with open(file, "w", encoding="utf-8") as f:
                json.dump(self.results, f, ensure_ascii=False, indent=2)
            self.log(f"Results exported to {file}")

    def export_csv(self):
        file, _ = QFileDialog.getSaveFileName(self, "Export CSV", "", "CSV Files (*.csv)")
        if file:
            import csv
            with open(file, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=["combo","proxy","status"])
                writer.writeheader()
                writer.writerows(self.results)
            self.log(f"Results exported to {file}")

    def check_telegram(self):
        # فحص توكن الـ Telegram (وهمي)
        if self.tg_id.text() and self.tg_token.text():
            self.log("Telegram credentials seem OK.")
        else:
            self.log("Please enter Telegram ID and Bot Token.")

# -------------------- MAIN --------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DevAutoGUI()
    gui.show()
    sys.exit(app.exec_())