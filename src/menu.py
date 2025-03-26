#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QGroupBox, QRadioButton,
    QComboBox, QMessageBox, QFileDialog
)
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize
from game import ChineseChessGame

class ChineseChessMenu(QMainWindow):
    """Form menu cho phép người dùng chọn chế độ chơi"""
    
    def __init__(self):
        super().__init__()
        
        # Thiết lập cửa sổ
        self.setWindowTitle("Cờ Tướng - Menu Chính")
        self.setMinimumSize(500, 400)
        
        # Tạo widget chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Tiêu đề
        title_label = QLabel("CỜ TƯỚNG")
        title_font = QFont("Arial", 24, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Logo/Hình ảnh (nếu có)
        logo_path = os.path.join('resources', 'images', 'logo.png')
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio))
            logo_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(logo_label)
        
        # Nhóm chọn chế độ chơi
        game_mode_group = QGroupBox("Chọn chế độ chơi")
        game_mode_layout = QVBoxLayout(game_mode_group)
        
        self.mode_human_radio = QRadioButton("Người đấu với Người")
        self.mode_human_radio.setChecked(True)
        
        self.mode_ai_radio = QRadioButton("Người đấu với Máy")
        
        self.mode_online_radio = QRadioButton("Chơi Trực tuyến (Online)")
        self.mode_online_radio.setEnabled(False)  # Chưa triển khai
        
        game_mode_layout.addWidget(self.mode_human_radio)
        game_mode_layout.addWidget(self.mode_ai_radio)
        game_mode_layout.addWidget(self.mode_online_radio)
        
        main_layout.addWidget(game_mode_group)
        
        # Mức độ AI (chỉ hiển thị khi chọn chế độ đấu với máy)
        self.ai_level_group = QGroupBox("Mức độ khó")
        ai_level_layout = QVBoxLayout(self.ai_level_group)
        
        self.ai_level_combo = QComboBox()
        self.ai_level_combo.addItems(["Dễ", "Trung bình", "Khó"])
        self.ai_level_combo.setCurrentIndex(1)  # Mặc định trung bình
        
        ai_level_layout.addWidget(self.ai_level_combo)
        main_layout.addWidget(self.ai_level_group)
        self.ai_level_group.setVisible(False)
        
        # Kết nối các sự kiện
        self.mode_human_radio.toggled.connect(self.update_ui)
        self.mode_ai_radio.toggled.connect(self.update_ui)
        self.mode_online_radio.toggled.connect(self.update_ui)
        
        # Các nút điều khiển
        buttons_layout = QHBoxLayout()
        
        self.start_button = QPushButton("Bắt đầu")
        self.start_button.clicked.connect(self.start_game)
        self.start_button.setMinimumHeight(40)
        
        # Thêm nút tải trò chơi
        self.load_button = QPushButton("Tải trò chơi")
        self.load_button.clicked.connect(self.load_game)
        self.load_button.setMinimumHeight(40)
        
        self.exit_button = QPushButton("Thoát")
        self.exit_button.clicked.connect(self.close)
        self.exit_button.setMinimumHeight(40)
        
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.load_button)
        buttons_layout.addWidget(self.exit_button)
        
        main_layout.addLayout(buttons_layout)
    
    def update_ui(self):
        """Cập nhật giao diện dựa trên chế độ chơi đã chọn"""
        # Hiển thị/ẩn mức độ AI dựa trên chế độ chơi
        self.ai_level_group.setVisible(self.mode_ai_radio.isChecked())
        
        # Hiển thị thông báo nếu chọn chế độ Online chưa triển khai
        if self.mode_online_radio.isChecked():
            QMessageBox.information(self, "Thông báo", "Chế độ chơi trực tuyến đang được phát triển")
            self.mode_human_radio.setChecked(True)
    
    def start_game(self):
        """Bắt đầu trò chơi với chế độ đã chọn"""
        game_mode = ""
        ai_level = ""
        
        # Lấy chế độ chơi
        if self.mode_human_radio.isChecked():
            game_mode = "human_vs_human"
        elif self.mode_ai_radio.isChecked():
            game_mode = "human_vs_ai"
            # Lấy cấp độ AI
            ai_index = self.ai_level_combo.currentIndex()
            if ai_index == 0:
                ai_level = "easy"
            elif ai_index == 1:
                ai_level = "medium"
            else:
                ai_level = "hard"
        elif self.mode_online_radio.isChecked():
            game_mode = "online"
        
        # Khởi tạo và hiển thị trò chơi
        self.game = ChineseChessGame()
        
        # Thiết lập chế độ chơi
        self.game.set_game_mode(game_mode)
        
        # Thiết lập cấp độ AI nếu cần
        if game_mode == "human_vs_ai":
            self.game.set_ai_level(ai_level)
        
        # Hiển thị trò chơi
        self.game.show()
        self.hide()  # Ẩn menu 

    def load_game(self):
        """Tải trạng thái trò chơi đã lưu"""
        file_name, _ = QFileDialog.getOpenFileName(self, "Tải trò chơi", "", "Tệp Cờ Tướng (*.chess);;Tất cả tệp (*)")
        if file_name:
            try:
                # Đọc trạng thái trò chơi từ tệp
                with open(file_name, 'r', encoding='utf-8') as f:
                    game_state = json.load(f)
                
                # Khởi tạo trò chơi mới
                self.game = ChineseChessGame()
                
                # Thiết lập chế độ chơi trước khi tải trạng thái
                game_mode = game_state.get('game_mode', 'human_vs_human')
                self.game.set_game_mode(game_mode)
                
                # Thiết lập cấp độ AI nếu cần
                ai_level = game_state.get('ai_level', 'medium')
                self.game.set_ai_level(ai_level)
                
                # Áp dụng trạng thái trò chơi
                success = self.game.chess_board.set_game_state(game_state)
                
                if success:
                    # Hiển thị trò chơi
                    self.game.statusBar.showMessage(f"Đã tải trò chơi từ {file_name}")
                    self.game.show()
                    self.hide()
                else:
                    QMessageBox.warning(self, "Cảnh báo", "Không thể tải trò chơi. Định dạng không hợp lệ.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể tải trò chơi: {str(e)}") 