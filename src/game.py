#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import pygame
import time
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QAction, QStatusBar, QFileDialog, QMessageBox,
    QGroupBox, QRadioButton, QComboBox, QFrame, QGridLayout, QScrollArea
)
from PyQt5.QtGui import QIcon, QColor, QPalette, QPixmap, QFont
from PyQt5.QtCore import Qt, QSize, QTimer, QCoreApplication
from board import ChineseChessBoard, RED, BLACK
from ai import ChineseChessAI

class ChineseChessGame(QMainWindow):
    """Lớp trò chơi Cờ Tướng chính"""
    
    def __init__(self):
        super().__init__()
        
        # Thiết lập cửa sổ
        self.setWindowTitle("Cờ Tướng - Chinese Chess")
        self.setMinimumSize(1000, 700)  # Tăng kích thước để có chỗ cho panel bên phải
        
        # Thiết lập biến
        self.game_mode = "human_vs_human"  # Chế độ mặc định: người vs người
        self.audio_enabled = True
        
        # Khởi tạo AI 
        self.ai = ChineseChessAI()
        self.ai_level = "medium"  # Mặc định là mức trung bình
        
        # Khởi tạo âm thanh nếu pygame được cài đặt
        try:
            pygame.mixer.init()
            self.move_sound = pygame.mixer.Sound(os.path.join('resources', 'sounds', 'move.wav'))
            self.capture_sound = pygame.mixer.Sound(os.path.join('resources', 'sounds', 'capture.wav'))
            self.check_sound = pygame.mixer.Sound(os.path.join('resources', 'sounds', 'check.wav'))
        except:
            self.audio_enabled = False
            print("Không thể khởi tạo âm thanh. Đảm bảo pygame được cài đặt và có tệp âm thanh phù hợp.")
        
        # Tạo bàn cờ
        self.chess_board = ChineseChessBoard()
        self.chess_board.move_made.connect(self._on_move_made)
        self.chess_board.check_status_changed.connect(self._on_check_status_changed)
        self.chess_board.game_over.connect(self._on_game_over)
        
        # Tạo layout chính
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Thêm bàn cờ vào bên trái
        main_layout.addWidget(self.chess_board, 3)  # Tỷ lệ 3
        
        # Tạo panel bên phải
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(10)
        main_layout.addWidget(right_panel, 1)  # Tỷ lệ 1
        
        # Tạo các panel con
        self._create_info_panel(right_layout)
        self._create_captured_panel(right_layout)
        self._create_controls_panel(right_layout)
        self._create_settings_panel(right_layout)
        
        # Thêm thanh trạng thái
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Sẵn sàng chơi. Lượt của quân Đỏ.")
        
        # Tạo menu
        self._create_menu()
        
        # Khởi tạo trò chơi mới
        self._new_game()
    
    def _create_info_panel(self, parent_layout):
        """Tạo panel hiển thị thông tin lượt chơi"""
        info_group = QGroupBox("Thông tin trò chơi")
        info_layout = QVBoxLayout(info_group)
        
        # Hiển thị chế độ chơi
        mode_text = "Người vs Người" if self.game_mode == "human_vs_human" else "Người vs Máy"
        self.mode_label = QLabel(f"Chế độ: {mode_text}")
        self.mode_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.mode_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.mode_label)
        
        # Nhãn trạng thái hiện tại
        self.status_label = QLabel("Lượt: Đỏ")
        self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        self.status_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.status_label)
        
        # Thêm panel vào layout chính
        parent_layout.addWidget(info_group)
    
    def _create_captured_panel(self, parent_layout):
        """Tạo panel hiển thị quân cờ bị bắt"""
        captured_group = QGroupBox("Quân cờ bị bắt")
        captured_layout = QVBoxLayout(captured_group)
        
        # Panel quân đỏ bị bắt
        red_captured_group = QGroupBox("Quân đỏ bị bắt")
        self.red_captured_layout = QGridLayout(red_captured_group)
        
        # Panel quân đen bị bắt
        black_captured_group = QGroupBox("Quân đen bị bắt")
        self.black_captured_layout = QGridLayout(black_captured_group)
        
        # Thêm vào panel chính
        captured_layout.addWidget(red_captured_group)
        captured_layout.addWidget(black_captured_group)
        
        # Tạo scroll area cho panel quân bị bắt
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(captured_group)
        
        # Thêm panel vào layout chính
        parent_layout.addWidget(scroll_area)
    
    def _create_controls_panel(self, parent_layout):
        """Tạo panel điều khiển trò chơi"""
        controls_group = QGroupBox("Điều khiển")
        controls_layout = QVBoxLayout(controls_group)
        
        # Nút trò chơi mới
        new_game_btn = QPushButton("Trò chơi mới")
        new_game_btn.clicked.connect(self._new_game)
        controls_layout.addWidget(new_game_btn)
        
        # Nút hoàn tác
        undo_btn = QPushButton("Hoàn tác nước đi")
        undo_btn.clicked.connect(self._undo_move)
        controls_layout.addWidget(undo_btn)
        
        # Nút lưu trò chơi
        save_btn = QPushButton("Lưu trò chơi")
        save_btn.clicked.connect(self._save_game)
        controls_layout.addWidget(save_btn)
        
        # Nút bật/tắt âm thanh
        self.sound_btn = QPushButton("Tắt âm thanh" if self.audio_enabled else "Bật âm thanh")
        self.sound_btn.clicked.connect(self._toggle_sound)
        controls_layout.addWidget(self.sound_btn)
        
        # Nút trở về menu
        back_to_menu_btn = QPushButton("Trở về Menu")
        back_to_menu_btn.clicked.connect(self._back_to_menu)
        controls_layout.addWidget(back_to_menu_btn)
        
        # Thêm panel vào layout chính
        parent_layout.addWidget(controls_group)
    
    def _create_settings_panel(self, parent_layout):
        """Tạo panel cài đặt trò chơi"""
        settings_group = QGroupBox("Cài đặt")
        settings_layout = QVBoxLayout(settings_group)
        
        # Chỉ giữ lại phần cấp độ AI nếu chế độ chơi là người vs máy
        if self.game_mode == "human_vs_ai":
            # Cấp độ AI
            ai_group = QGroupBox("Cấp độ AI")
            ai_layout = QVBoxLayout(ai_group)
            
            self.ai_level_combo = QComboBox()
            self.ai_level_combo.addItems(["Dễ", "Trung bình", "Khó"])
            self.ai_level_combo.setCurrentIndex(1)  # Mặc định là trung bình
            self.ai_level_combo.currentIndexChanged.connect(self._change_ai_level)
            ai_layout.addWidget(self.ai_level_combo)
            settings_layout.addWidget(ai_group)
        
        # Thêm panel vào layout chính
        parent_layout.addWidget(settings_group)
        
        # Thêm khoảng trống co giãn ở cuối
        parent_layout.addStretch()
    
    def _create_menu(self):
        """Tạo menu trò chơi"""
        menu_bar = self.menuBar()
        
        # Menu trò chơi
        game_menu = menu_bar.addMenu("Trò chơi")
        
        # Hành động trò chơi mới
        new_game_action = QAction("Trò chơi mới", self)
        new_game_action.triggered.connect(self._new_game)
        game_menu.addAction(new_game_action)
        
        # Hành động hoàn tác
        undo_action = QAction("Hoàn tác nước đi", self)
        undo_action.triggered.connect(self._undo_move)
        game_menu.addAction(undo_action)
        
        # Hành động lưu trò chơi
        save_action = QAction("Lưu trò chơi", self)
        save_action.triggered.connect(self._save_game)
        game_menu.addAction(save_action)
        
        # Thêm separator
        game_menu.addSeparator()
        
        # Hành động trở về menu
        back_to_menu_action = QAction("Trở về Menu chính", self)
        back_to_menu_action.triggered.connect(self._back_to_menu)
        game_menu.addAction(back_to_menu_action)
        
        # Thêm separator
        game_menu.addSeparator()
        
        # Hành động thoát
        exit_action = QAction("Thoát", self)
        exit_action.triggered.connect(self.close)
        game_menu.addAction(exit_action)
        
        # Menu cài đặt
        settings_menu = menu_bar.addMenu("Cài đặt")
        
        # Hành động bật/tắt âm thanh
        sound_action = QAction("Tắt âm thanh" if self.audio_enabled else "Bật âm thanh", self)
        sound_action.triggered.connect(self._toggle_sound)
        settings_menu.addAction(sound_action)
        
        # Chỉ hiển thị submenu cấp độ AI nếu chế độ là người vs máy
        if self.game_mode == "human_vs_ai":
            # Submenu cấp độ AI
            ai_level_menu = settings_menu.addMenu("Cấp độ AI")
            
            # Các cấp độ AI
            easy_action = QAction("Dễ", self)
            easy_action.triggered.connect(lambda: self._change_ai_level(0))
            ai_level_menu.addAction(easy_action)
            
            medium_action = QAction("Trung bình", self)
            medium_action.triggered.connect(lambda: self._change_ai_level(1))
            ai_level_menu.addAction(medium_action)
            
            hard_action = QAction("Khó", self)
            hard_action.triggered.connect(lambda: self._change_ai_level(2))
            ai_level_menu.addAction(hard_action)
        
        # Menu Trợ giúp
        help_menu = menu_bar.addMenu("Trợ giúp")
        
        # Luật chơi
        rules_action = QAction("Luật chơi", self)
        rules_action.triggered.connect(self._show_rules)
        help_menu.addAction(rules_action)
        
        # Giới thiệu
        about_action = QAction("Giới thiệu", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _new_game(self):
        """Bắt đầu trò chơi mới - không cần xác nhận nữa"""
        # Thiết lập trò chơi mới trực tiếp, không cần xác nhận
        self.chess_board.reset_board()
        self._update_status()
        self.statusBar.showMessage("Trò chơi mới bắt đầu. Lượt của quân Đỏ.")
        
        # Xóa tất cả quân bị bắt
        self._clear_captured_display()
    
    def _change_ai_level(self, index):
        """Thay đổi cấp độ AI"""
        level_text = self.ai_level_combo.currentText()
        if level_text == "Dễ":
            self.ai_level = "easy"
            self.chess_board.set_ai_level("easy")
        elif level_text == "Khó":
            self.ai_level = "hard"
            self.chess_board.set_ai_level("hard")
        else:
            self.ai_level = "medium"
            self.chess_board.set_ai_level("medium")
        
        self.statusBar.showMessage(f"Cấp độ AI: {level_text}")
    
    def _undo_move(self):
        """Hoàn tác nước đi cuối cùng"""
        success = self.chess_board.undo_last_move()
        if success:
            self._update_status()
            self.statusBar.showMessage("Đã hoàn tác nước đi cuối cùng")
            
            # Cập nhật lại hiển thị quân bị bắt
            self._update_captured_display()
        else:
            self.statusBar.showMessage("Không thể hoàn tác")
    
    def _save_game(self):
        """Lưu trạng thái trò chơi"""
        file_name, _ = QFileDialog.getSaveFileName(self, "Lưu trò chơi", "", "Tệp Cờ Tướng (*.chess);;Tất cả tệp (*)")
        if file_name:
            game_state = self.chess_board.get_game_state()
            try:
                with open(file_name, 'w', encoding='utf-8') as f:
                    json.dump(game_state, f, ensure_ascii=False, indent=4)
                self.statusBar.showMessage(f"Đã lưu trò chơi vào {file_name}")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu trò chơi: {str(e)}")
    
    def _toggle_sound(self):
        """Bật/tắt âm thanh"""
        self.audio_enabled = not self.audio_enabled
        self.sound_btn.setText("Tắt âm thanh" if self.audio_enabled else "Bật âm thanh")
        self.statusBar.showMessage(f"Âm thanh đã {'bật' if self.audio_enabled else 'tắt'}")
    
    def _show_rules(self):
        """Hiển thị luật chơi"""
        rules = """
        <h2>Luật chơi Cờ Tướng</h2>
        
        <h3>Mục tiêu</h3>
        <p>Mục tiêu của trò chơi là chiếu tướng đối phương (trong tình trạng không thể cứu).</p>
        
        <h3>Di chuyển</h3>
        <ul>
            <li><b>Tướng</b>: Di chuyển 1 ô theo chiều ngang hoặc dọc, nhưng không được ra khỏi cung điện.</li>
            <li><b>Sĩ</b>: Di chuyển 1 ô theo đường chéo, nhưng không được ra khỏi cung điện.</li>
            <li><b>Tượng</b>: Di chuyển 2 ô theo đường chéo, không được vượt sông. Nếu có quân cản đường thì không thể di chuyển.</li>
            <li><b>Mã</b>: Di chuyển theo hình chữ L (1 ô ngang/dọc rồi 1 ô chéo). Nếu có quân cản đường thì không thể di chuyển.</li>
            <li><b>Xe</b>: Di chuyển theo hàng ngang hoặc dọc, không giới hạn số ô, nhưng không thể nhảy qua quân khác.</li>
            <li><b>Pháo</b>: Di chuyển như Xe, nhưng khi ăn quân phải có đúng 1 quân làm bàn đạp.</li>
            <li><b>Tốt</b>: Di chuyển 1 ô về phía trước. Sau khi qua sông có thể di chuyển 1 ô theo chiều ngang.</li>
        </ul>
        
        <h3>Luật đặc biệt</h3>
        <ul>
            <li><b>Chiếu tướng</b>: Khi tướng bị đe dọa, bạn phải di chuyển để thoát khỏi tình trạng bị chiếu.</li>
            <li><b>Tướng đối mặt</b>: Hai tướng không được đối mặt trực tiếp mà không có quân cờ nào ở giữa.</li>
        </ul>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Luật chơi Cờ Tướng")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(rules)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def _show_about(self):
        """Hiển thị thông tin giới thiệu"""
        about = """
        <h2>Cờ Tướng - Chinese Chess</h2>
        <p>Phiên bản 1.0</p>
        <p>Trò chơi cờ tướng truyền thống.</p>
        <p>Phát triển bởi: Dự án Cờ Tướng Python</p>
        <p>Sử dụng Python, PyQt5 và thuật toán AI</p>
        """
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Giới thiệu")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(about)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def _on_move_made(self, color, piece_name, from_pos, to_pos, is_capture, captured_piece_name):
        """Xử lý khi có nước đi"""
        # Cập nhật trạng thái
        self._update_status()
        
        # Hiển thị thông tin
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        player = "Đỏ" if color == RED else "Đen"
        move_info = f"{player} di chuyển {piece_name} từ ({from_row},{from_col}) đến ({to_row},{to_col})"
        
        if is_capture:
            move_info += f", ăn {captured_piece_name}"
            # Cập nhật hiển thị quân bị bắt
            self._update_captured_display()
        
        # Phát âm thanh
        if self.audio_enabled:
            if is_capture:
                pygame.mixer.Sound.play(self.capture_sound)
            else:
                pygame.mixer.Sound.play(self.move_sound)
        
        # Hiển thị thông tin trên thanh trạng thái
        self.statusBar.showMessage(move_info)
    
    def _on_check_status_changed(self, is_check, side):
        """Xử lý sự kiện khi có chiếu tướng"""
        if is_check:
            # Phát âm thanh chiếu tướng
            if self.audio_enabled:
                pygame.mixer.Sound.play(self.check_sound)
            
            # Hiển thị thông báo
            self.statusBar.showMessage(f"Chiếu tướng! Tướng {side} đang bị chiếu.")
            
            # Đổi màu nhãn trạng thái nếu cần
            if side == "Đỏ":
                self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red; background-color: #FFEEEE;")
            else:
                self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black; background-color: #EEEEEE;")
        else:
            # Không còn chiếu tướng, đặt lại trạng thái
            self._update_status()
            
            # Hiển thị thông báo
            self.statusBar.showMessage(f"Tướng {side} không còn bị chiếu.")
    
    def _update_status(self):
        """Cập nhật hiển thị trạng thái"""
        player_color = self.chess_board.current_player
        if player_color.red() > 0:
            self.status_label.setText("Lượt: Đỏ")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        else:
            self.status_label.setText("Lượt: Đen")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
    
    def _clear_captured_display(self):
        """Xóa hiển thị quân bị bắt"""
        # Xóa tất cả các item trong layout hiển thị quân bị bắt
        while self.red_captured_layout.count():
            item = self.red_captured_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        while self.black_captured_layout.count():
            item = self.black_captured_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
    
    def _update_captured_display(self):
        """Cập nhật hiển thị quân bị bắt"""
        # Xóa hiển thị cũ
        self._clear_captured_display()
        
        # Lấy danh sách quân cờ bị bắt
        captured_pieces = self.chess_board.captured_pieces
        
        # Phân loại quân cờ bị bắt theo màu
        red_pieces = []
        black_pieces = []
        
        for piece in captured_pieces:
            if piece.color == RED:
                red_pieces.append(piece)
            else:
                black_pieces.append(piece)
        
        # Hiển thị quân đỏ bị bắt
        for i, piece in enumerate(red_pieces):
            label = QLabel(piece.get_name())
            label.setStyleSheet("color: red; font-size: 14px;")
            self.red_captured_layout.addWidget(label, i // 3, i % 3)
        
        # Hiển thị quân đen bị bắt
        for i, piece in enumerate(black_pieces):
            label = QLabel(piece.get_name())
            label.setStyleSheet("color: black; font-size: 14px;")
            self.black_captured_layout.addWidget(label, i // 3, i % 3)

    def set_game_mode(self, mode):
        """Thiết lập chế độ chơi"""
        if self.game_mode != mode:
            # Gán trực tiếp, không cập nhật giao diện để tránh đệ quy
            self.game_mode = mode
            self.chess_board.set_game_mode(mode)
            
            # Cập nhật nhãn chế độ chơi
            if hasattr(self, 'mode_label'):
                mode_text = "Người vs Người" if mode == "human_vs_human" else "Người vs Máy"
                self.mode_label.setText(f"Chế độ: {mode_text}")
            
            # Lưu ý: KHÔNG cập nhật giao diện tại đây để tránh đệ quy vô hạn

    def set_ai_level(self, level):
        """Thiết lập cấp độ AI"""
        self.ai_level = level
        self.chess_board.set_ai_level(level)
        
        # Cập nhật giao diện
        if hasattr(self, 'ai_level_combo'):
            if level == "easy":
                self.ai_level_combo.setCurrentIndex(0)
            elif level == "medium":
                self.ai_level_combo.setCurrentIndex(1)
            else:  # hard
                self.ai_level_combo.setCurrentIndex(2)
                
    def _on_game_over(self, result):
        """Xử lý khi trò chơi kết thúc"""
        message = ""
        title = "Trò chơi kết thúc"
        
        if result == "RED":
            message = "Quân Đỏ đã thắng!"
            # Cập nhật nhãn trạng thái
            self.status_label.setText("Kết quả: Đỏ thắng")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: red;")
        elif result == "BLACK":
            message = "Quân Đen đã thắng!"
            # Cập nhật nhãn trạng thái
            self.status_label.setText("Kết quả: Đen thắng")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: black;")
        else:
            message = "Trò chơi kết thúc hòa!"
            # Cập nhật nhãn trạng thái
            self.status_label.setText("Kết quả: Hòa")
            self.status_label.setStyleSheet("font-size: 16px; font-weight: bold; color: blue;")
        
        # Kiểm tra xem có phải kết thúc do chiếu hết không
        if self.chess_board.red_in_check and result == "BLACK":
            message += "\nQuân Đỏ bị chiếu hết!"
            title = "Chiếu hết!"
        elif self.chess_board.black_in_check and result == "RED":
            message += "\nQuân Đen bị chiếu hết!"
            title = "Chiếu hết!"
        
        # Hiển thị hộp thoại thông báo
        QMessageBox.information(self, title, message)
        
        # Cập nhật thanh trạng thái
        self.statusBar.showMessage(f"Trò chơi kết thúc. {message}")

    def _back_to_menu(self):
        """Trở về màn hình menu chính"""
        # Hiển thị xác nhận nếu trò chơi chưa kết thúc
        if not self.chess_board.game_over_state:
            reply = QMessageBox.question(self, 'Xác nhận', 
                                          'Bạn có chắc muốn trở về menu? Tiến độ trò chơi hiện tại sẽ bị mất.',
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.No:
                return
                
        # Import lại để tránh import vòng
        from menu import ChineseChessMenu
        self.menu = ChineseChessMenu()
        self.menu.show()
        self.close()

def main():
    """Hàm chính chạy trò chơi"""
    app = QApplication(sys.argv)
    game = ChineseChessGame()
    game.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
