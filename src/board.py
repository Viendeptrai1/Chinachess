#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPixmap, QFont, QImage
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from pieces import Piece, General, Advisor, Elephant, Horse, Chariot, Cannon, Soldier
import copy
import time
from ai import ChineseChessAI
from PIL import Image, ImageDraw, ImageFont

# Kích thước bàn cờ
BOARD_WIDTH = 9  # Số cột
BOARD_HEIGHT = 10  # Số hàng

# Màu sắc
RED = QColor(255, 0, 0)
BLACK = QColor(0, 0, 0)
BOARD_COLOR = QColor(238, 203, 173)
LINE_COLOR = QColor(0, 0, 0)
SELECTED_COLOR = QColor(0, 255, 0, 100)  # Màu hiển thị nước đi cuối cùng
LAST_MOVE_COLOR = QColor(0, 0, 255, 80)  # Màu hiển thị nước đi cuối cùng
VALID_MOVE_COLOR = QColor(200, 200, 0, 150)  # Màu hiển thị các điểm có thể đi

class ChineseChessBoard(QWidget):
    """Lớp hiển thị và xử lý bàn cờ tướng"""
    
    # Tín hiệu phát ra khi có nước đi
    move_made = pyqtSignal(QColor, str, tuple, tuple, bool, str)
    # Tín hiệu phát ra khi có chiếu tướng
    check_status_changed = pyqtSignal(bool, str)
    # Tín hiệu báo khi quân cờ bị bắt
    piece_captured = pyqtSignal(str)
    # Tín hiệu báo khi game kết thúc
    game_over = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 667)  # Tỷ lệ 9:10
        
        # Kích thước ô cờ và màu sắc
        self.cell_size = 60
        self.board_margin = 30  # Lề bàn cờ
        self.grid_color = QColor(0, 0, 0)
        self.board_color = BOARD_COLOR
        self.selected_color = SELECTED_COLOR
        self.hint_color = QColor(0, 255, 0, 100)
        
        # Khởi tạo bàn cờ
        self.board = [[0 for _ in range(9)] for _ in range(10)]
        self.reset_board()
        
        # Khởi tạo AI
        self.ai = ChineseChessAI()
        self.ai_level = "medium"  # Mặc định là mức trung bình
        
        # Theo dõi trạng thái chọn quân cờ
        self.selected_piece = None
        self.selected_position = None
        
        # Chế độ chơi
        self.game_mode = "human_vs_human"  # Mặc định là người vs người
        
        # Lịch sử nước đi để hoàn tác
        self.move_history = []
        
        # Quân cờ bị bắt
        self.captured_pieces = []
        
        # Trạng thái game
        self.current_player = RED  # Quân đỏ đi trước
        self.game_over_state = False
        
        # Biến theo dõi chiếu tướng
        self.red_in_check = False
        self.black_in_check = False
        
        # Biến lưu trữ nước đi gần nhất
        self.last_move = None  # tuple ((from_row, from_col), (to_row, to_col))
        self.last_move_is_ai = False
        
        # Cho phép theo dõi chuột để di chuyển quân cờ
        self.setMouseTracking(True)
        
        # Tạo cache cho hình ảnh quân cờ
        self.piece_images = {}
        self.create_piece_images()
    
    def reset_board(self):
        """Khởi tạo lại bàn cờ"""
        # Khởi tạo bàn cờ trống (10x9)
        self.board = [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        
        # Đặt quân cờ cho bên Đỏ (phía dưới)
        # Tướng
        self.board[9][4] = General(RED, (9, 4))
        # Sĩ
        self.board[9][3] = Advisor(RED, (9, 3))
        self.board[9][5] = Advisor(RED, (9, 5))
        # Tượng
        self.board[9][2] = Elephant(RED, (9, 2))
        self.board[9][6] = Elephant(RED, (9, 6))
        # Mã
        self.board[9][1] = Horse(RED, (9, 1))
        self.board[9][7] = Horse(RED, (9, 7))
        # Xe
        self.board[9][0] = Chariot(RED, (9, 0))
        self.board[9][8] = Chariot(RED, (9, 8))
        # Pháo
        self.board[7][1] = Cannon(RED, (7, 1))
        self.board[7][7] = Cannon(RED, (7, 7))
        # Tốt
        self.board[6][0] = Soldier(RED, (6, 0))
        self.board[6][2] = Soldier(RED, (6, 2))
        self.board[6][4] = Soldier(RED, (6, 4))
        self.board[6][6] = Soldier(RED, (6, 6))
        self.board[6][8] = Soldier(RED, (6, 8))
        
        # Đặt quân cờ cho bên Đen (phía trên)
        # Tướng
        self.board[0][4] = General(BLACK, (0, 4))
        # Sĩ
        self.board[0][3] = Advisor(BLACK, (0, 3))
        self.board[0][5] = Advisor(BLACK, (0, 5))
        # Tượng
        self.board[0][2] = Elephant(BLACK, (0, 2))
        self.board[0][6] = Elephant(BLACK, (0, 6))
        # Mã
        self.board[0][1] = Horse(BLACK, (0, 1))
        self.board[0][7] = Horse(BLACK, (0, 7))
        # Xe
        self.board[0][0] = Chariot(BLACK, (0, 0))
        self.board[0][8] = Chariot(BLACK, (0, 8))
        # Pháo
        self.board[2][1] = Cannon(BLACK, (2, 1))
        self.board[2][7] = Cannon(BLACK, (2, 7))
        # Tốt
        self.board[3][0] = Soldier(BLACK, (3, 0))
        self.board[3][2] = Soldier(BLACK, (3, 2))
        self.board[3][4] = Soldier(BLACK, (3, 4))
        self.board[3][6] = Soldier(BLACK, (3, 6))
        self.board[3][8] = Soldier(BLACK, (3, 8))
        
        # Đỏ đi trước
        self.current_player = RED
        self.selected_piece = None
        self.selected_position = None
        
        # Đặt lại nước đi cuối cùng
        self.last_move = None
        self.last_move_is_ai = False
        
        # Đặt lại trạng thái chiếu tướng
        self.red_in_check = False
        self.black_in_check = False
        
        # Đặt lại lịch sử
        self.move_history = []
        self.captured_pieces = []
        
        # Đặt lại trạng thái kết thúc trò chơi
        self.game_over_state = False
        
        # Cập nhật giao diện
        self.update()
    
    def set_ai_level(self, level):
        """Thiết lập cấp độ AI"""
        self.ai_level = level
        self.ai.set_difficulty(level)
    
    def set_game_mode(self, mode):
        """Thiết lập chế độ chơi"""
        if self.game_mode != mode:
            old_mode = self.game_mode
            self.game_mode = mode
            # KHÔNG gọi lại bất kỳ phương thức nào khác ở đây để tránh đệ quy
    
    def create_piece_images(self):
        """Tạo hình ảnh quân cờ bằng Pillow"""
        piece_size = int(self.cell_size * 0.85)  # Kích thước quân cờ (85% ô)
        
        piece_types = {
            "general": "帅",
            "advisor": "仕",
            "elephant": "相",
            "horse": "馬",
            "chariot": "車",
            "cannon": "炮",
            "soldier": "兵",
        }
        
        black_piece_types = {
            "general": "将",
            "advisor": "士",
            "elephant": "象",
            "horse": "馬",
            "chariot": "車",
            "cannon": "砲",
            "soldier": "卒",
        }
        
        colors = {
            "red": ((231, 76, 60), (255, 220, 220)),  # (Viền, Nền)
            "black": ((52, 73, 94), (220, 220, 255))  # (Viền, Nền)
        }
        
        for color_name, (border_color, bg_color) in colors.items():
            types = piece_types if color_name == "red" else black_piece_types
            for piece_type, symbol in types.items():
                # Tạo hình tròn
                img = Image.new('RGBA', (piece_size, piece_size), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                # Vẽ hình tròn đầy màu nền
                draw.ellipse((2, 2, piece_size-2, piece_size-2), fill=bg_color)
                
                # Vẽ viền
                draw.ellipse((2, 2, piece_size-2, piece_size-2), outline=border_color, width=3)
                
                # Thêm chữ
                try:
                    # Thử tải font tiếng Trung
                    font = ImageFont.truetype("Arial Unicode MS", int(piece_size * 0.6))
                except:
                    try:
                        # Thử font khác
                        font = ImageFont.truetype("simsun.ttc", int(piece_size * 0.6))
                    except:
                        # Dùng font mặc định
                        font = ImageFont.load_default()
                
                # Tính toán vị trí text để căn giữa - sử dụng getbbox thay vì textsize
                try:
                    # Phương thức mới trong Pillow
                    bbox = draw.textbbox((0, 0), symbol, font=font)
                    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
                except:
                    try:
                        # Thử phương thức getsize (cho phiên bản cũ hơn)
                        w, h = font.getsize(symbol)
                    except:
                        # Giá trị mặc định
                        w, h = piece_size // 2, piece_size // 2
                
                position = ((piece_size-w)//2, (piece_size-h)//2 - 5)  # -5 để điều chỉnh độ cao
                
                # Vẽ text
                draw.text(position, symbol, fill=border_color, font=font)
                
                # Chuyển đổi PIL Image sang QPixmap
                img_data = img.convert("RGBA").tobytes("raw", "RGBA")
                qimg = QImage(img_data, img.width, img.height, QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimg)
                self.piece_images[(color_name, piece_type)] = pixmap
    
    def paintEvent(self, event):
        """Vẽ bàn cờ và quân cờ"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Vẽ nền bàn cờ
        painter.fillRect(self.rect(), self.board_color)
        
        # Vẽ lưới bàn cờ
        self._draw_board_grid(painter)
        
        # Vẽ đánh dấu nước đi cuối cùng
        self._draw_last_move(painter)
        
        # Vẽ đánh dấu các điểm có thể đi
        self._draw_valid_moves(painter)
        
        # Vẽ quân cờ
        self._draw_pieces(painter)
    
    def _draw_board_grid(self, painter):
        """Vẽ lưới bàn cờ"""
        pen = QPen(self.grid_color, 1)
        painter.setPen(pen)
        
        # Vẽ các đường ngang
        for i in range(BOARD_HEIGHT):
            y = self.board_margin + i * self.cell_size
            painter.drawLine(self.board_margin, y, 
                             self.board_margin + (BOARD_WIDTH - 1) * self.cell_size, y)
        
        # Vẽ các đường dọc
        for j in range(BOARD_WIDTH):
            x = self.board_margin + j * self.cell_size
            painter.drawLine(x, self.board_margin, 
                             x, self.board_margin + (BOARD_HEIGHT - 1) * self.cell_size)
        
        # Vẽ cung điện (3x3) cho cả hai bên
        # Cung điện dưới (Đỏ)
        palace_x = self.board_margin + 3 * self.cell_size
        palace_y_bottom = self.board_margin + 7 * self.cell_size
        painter.drawLine(palace_x, palace_y_bottom, 
                         palace_x + 2 * self.cell_size, palace_y_bottom + 2 * self.cell_size)
        painter.drawLine(palace_x + 2 * self.cell_size, palace_y_bottom, 
                         palace_x, palace_y_bottom + 2 * self.cell_size)
        
        # Cung điện trên (Đen)
        palace_y_top = self.board_margin
        painter.drawLine(palace_x, palace_y_top, 
                         palace_x + 2 * self.cell_size, palace_y_top + 2 * self.cell_size)
        painter.drawLine(palace_x + 2 * self.cell_size, palace_y_top, 
                         palace_x, palace_y_top + 2 * self.cell_size)
        
        # Vẽ sông
        painter.setPen(QPen(Qt.blue, 1, Qt.DashLine))
        river_y = self.board_margin + 4 * self.cell_size
        painter.drawLine(self.board_margin, river_y, 
                         self.board_margin + (BOARD_WIDTH - 1) * self.cell_size, river_y)
        river_y = self.board_margin + 5 * self.cell_size
        painter.drawLine(self.board_margin, river_y, 
                         self.board_margin + (BOARD_WIDTH - 1) * self.cell_size, river_y)
    
    def _draw_last_move(self, painter):
        """Vẽ đánh dấu nước đi cuối cùng"""
        if not self.last_move:
            return
            
        # Lấy vị trí đi từ và đến
        (from_row, from_col), (to_row, to_col) = self.last_move
        
        # Tính toán tọa độ
        from_x = self.board_margin + from_col * self.cell_size
        from_y = self.board_margin + from_row * self.cell_size
        to_x = self.board_margin + to_col * self.cell_size
        to_y = self.board_margin + to_row * self.cell_size
        
        # Thiết lập bút vẽ
        pen = QPen()
        pen.setColor(QColor(0, 120, 215, 200))  # Màu xanh dương đẹp với độ trong suốt
        pen.setWidth(3)
        painter.setPen(pen)
        
        # Vẽ đường nối từ vị trí đi đến vị trí đến
        painter.drawLine(from_x, from_y, to_x, to_y)
        
        # Vẽ hình tròn ở vị trí xuất phát
        painter.setBrush(QBrush(QColor(0, 120, 215, 150)))
        painter.drawEllipse(QPoint(from_x, from_y), 10, 10)
        
        # Vẽ hình tròn lớn hơn ở vị trí đến
        painter.setBrush(QBrush(QColor(0, 120, 215, 200)))
        painter.drawEllipse(QPoint(to_x, to_y), 14, 14)
    
    def _draw_valid_moves(self, painter):
        """Vẽ các vị trí hợp lệ có thể di chuyển đến"""
        if not self.selected_piece or not self.selected_position:
            return
            
        valid_moves = self.get_valid_moves(self.selected_position[0], self.selected_position[1])
        
        for move in valid_moves:
            row, col = move
            x = self.board_margin + col * self.cell_size
            y = self.board_margin + row * self.cell_size
            
            # Kiểm tra xem vị trí này có quân cờ đối phương không
            piece = self.board[row][col]
            if piece != 0 and piece.color != self.selected_piece.color:
                # Vẽ vòng tròn đỏ xung quanh quân cờ có thể ăn được
                radius = self.cell_size // 2 - 2
                painter.setBrush(Qt.NoBrush)  # Không tô màu
                painter.setPen(QPen(QColor(255, 0, 0), 3))  # Viền đỏ dày
                painter.drawEllipse(x - radius - 4, y - radius - 4, 
                                   (radius + 4) * 2, (radius + 4) * 2)
            else:
                # Vẽ điểm nhỏ tại vị trí hợp lệ không có quân
                painter.setBrush(QBrush(QColor(0, 230, 0, 150)))  # Màu xanh lá với độ trong suốt
                painter.setPen(Qt.NoPen)
                painter.drawEllipse(QPoint(x, y), 10, 10)
    
    def _draw_pieces(self, painter):
        """Vẽ quân cờ trên bàn cờ"""
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                piece = self.board[i][j]
                if piece != 0:
                    # Tọa độ tâm của quân cờ
                    x = self.board_margin + j * self.cell_size
                    y = self.board_margin + i * self.cell_size
                    
                    # Vẽ vùng được chọn
                    if self.selected_position and self.selected_position == (i, j):
                        painter.setBrush(QBrush(self.selected_color))
                        painter.setPen(Qt.NoPen)
                        painter.drawEllipse(x - self.cell_size // 2, y - self.cell_size // 2, 
                                           self.cell_size, self.cell_size)
                    
                    # Vẽ quân cờ
                    self._draw_piece(painter, i, j)
                    
                    # Vẽ vòng đỏ khi tướng bị chiếu
                    if isinstance(piece, General):
                        if (piece.color == RED and self.red_in_check) or (piece.color == BLACK and self.black_in_check):
                            # Vẽ vòng đỏ xung quanh tướng
                            painter.setBrush(Qt.NoBrush)
                            painter.setPen(QPen(Qt.red, 3))  # Viền đỏ dày
                            check_radius = self.cell_size // 2 - 4  # Vòng tròn hơi lớn hơn quân cờ
                            painter.drawEllipse(x - check_radius, y - check_radius, check_radius * 2, check_radius * 2)
    
    def _draw_piece(self, painter, row, col):
        """Vẽ quân cờ tại vị trí (row, col)"""
        piece = self.board[row][col]
        
        # Tính vị trí trung tâm của ô
        x = self.board_margin + col * self.cell_size
        y = self.board_margin + row * self.cell_size
        
        # Vẽ theo kiểu cũ (không sử dụng hình ảnh Pillow)
        # Vẽ hình tròn
        radius = self.cell_size // 2 - 2
        
        # Thiết lập màu
        painter.setBrush(QBrush(QColor(255, 255, 240)))
        
        if piece.color == RED:
            painter.setPen(QPen(RED, 2))
        else:
            painter.setPen(QPen(BLACK, 2))
        
        # Vẽ hình tròn
        painter.drawEllipse(QPoint(x, y), radius, radius)
        
        # Vẽ tên quân cờ
        painter.setPen(piece.color)
        
        # Điều chỉnh font chữ - Tăng kích thước gấp đôi
        font = QFont()
        font.setBold(True)
        font.setPointSize(24)  # Tăng từ 12 lên 24
        painter.setFont(font)
        
        # Vẽ tên
        painter.drawText(QRect(x - radius, y - radius, radius * 2, radius * 2),
                        Qt.AlignCenter, piece.get_name())
    
    def _draw_selected(self, painter, row, col):
        """Vẽ đánh dấu quân cờ được chọn"""
        x = self.board_margin + col * self.cell_size
        y = self.board_margin + row * self.cell_size
        radius = self.cell_size // 2
        
        # Vẽ hình tròn với viền đỏ
        pen = QPen(QColor(255, 0, 0))  # Viền đỏ
        pen.setWidth(3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)  # Không tô màu
        painter.drawEllipse(QPoint(x, y), radius, radius)
    
    def mousePressEvent(self, event):
        """Xử lý sự kiện click chuột"""
        if event.button() == Qt.LeftButton and not self.game_over_state:
            # Tính toán vị trí quân cờ dựa trên tọa độ chuột
            col = round((event.x() - self.board_margin) / self.cell_size)
            row = round((event.y() - self.board_margin) / self.cell_size)
            
            # Kiểm tra giới hạn bàn cờ
            if 0 <= row < 10 and 0 <= col < 9:
                # Kiểm tra xem có thể chọn quân cờ này không
                if self.game_mode == "human_vs_ai" and self.current_player == BLACK:
                    # Không cho phép chọn quân khi đến lượt AI
                    return
                
                # Kiểm tra xem đã chọn quân cờ nào trước đó chưa
                if self.selected_position is None:
                    # Chưa chọn quân nào, kiểm tra xem ô này có quân cờ không
                    if self.board[row][col] != 0 and self.board[row][col].color == self.current_player:
                        # Chọn quân cờ
                        self.selected_piece = self.board[row][col]
                        self.selected_position = (row, col)
                        self.update()
                else:
                    # Đã chọn quân, kiểm tra xem có thể di chuyển đến ô này không
                    selected_row, selected_col = self.selected_position
                    
                    # Kiểm tra xem có chọn lại quân khác cùng màu không
                    if (self.board[row][col] != 0 and 
                        self.board[row][col].color == self.current_player):
                        # Chọn quân mới
                        self.selected_piece = self.board[row][col]
                        self.selected_position = (row, col)
                        self.update()
                        return
                    
                    # Kiểm tra xem ô đích có hợp lệ không
                    valid_moves = self.get_valid_moves(selected_row, selected_col)
                    if (row, col) in valid_moves:
                        # Di chuyển quân cờ
                        move_success = self._make_move(selected_row, selected_col, row, col)
                        
                        # Đánh dấu nước đi mới nhất của người chơi
                        if move_success:
                            self.mark_last_move((selected_row, selected_col), (row, col), False)
                        
                        # Bỏ chọn quân
                        self.selected_piece = None
                        self.selected_position = None
                        
                        # Cập nhật giao diện
                        self.update()
                        
                        # Nếu thành công và ở chế độ AI, cho phép AI di chuyển
                        if move_success and self.game_mode == "human_vs_ai" and self.current_player == BLACK:
                            QTimer.singleShot(500, self.make_ai_move)
                    else:
                        # Hủy chọn nếu click vào ô không hợp lệ
                        self.selected_piece = None
                        self.selected_position = None
                        self.update()
    
    def get_valid_moves(self, row, col):
        """Lấy danh sách các nước đi hợp lệ cho quân cờ tại vị trí (row, col)"""
        if self.board[row][col] == 0 or self.board[row][col] == ' ':
            return []
            
        piece = self.board[row][col]
        valid_moves = []
        
        # Lấy tất cả nước đi có thể
        for to_row in range(10):
            for to_col in range(9):
                if self._is_valid_move(row, col, to_row, to_col):
                    valid_moves.append((to_row, to_col))
                    
        return valid_moves
    
    def _is_valid_move(self, from_row, from_col, to_row, to_col):
        """Kiểm tra nước đi có hợp lệ không"""
        piece = self.board[from_row][from_col]
        if piece == 0:
            return False
        
        # Kiểm tra nước đi có hợp lệ theo luật của từng loại quân cờ
        return piece.is_valid_move(self.board, (from_row, from_col), (to_row, to_col))
    
    def _make_move(self, from_row, from_col, to_row, to_col):
        """Thực hiện nước đi từ (from_row, from_col) đến (to_row, to_col)"""
        # Lấy quân cờ
        piece = self.board[from_row][from_col]
        
        # Kiểm tra xem nước đi có hợp lệ không
        if not self._is_valid_move(from_row, from_col, to_row, to_col):
            return False
            
        # Kiểm tra xem có ăn quân không
        captured_piece = None
        is_capture = False
        captured_piece_name = ""
        
        if self.board[to_row][to_col] != 0 and self.board[to_row][to_col] != ' ':
            captured_piece = self.board[to_row][to_col]
            is_capture = True
            captured_piece_name = captured_piece.get_name()
            
            # Thêm quân bị bắt vào danh sách
            self.captured_pieces.append(captured_piece)
            
            # Kiểm tra xem có phải tướng/general không - kết thúc game
            if isinstance(captured_piece, General):
                self.game_over_state = True
                
                # Phát tín hiệu game over
                winner = "RED" if piece.color == RED else "BLACK"
                self.game_over.emit(winner)
                return True
        
        # Lưu trạng thái hiện tại để có thể hoàn tác
        self.move_history.append({
            'board': copy.deepcopy(self.board),
            'current_player': self.current_player,
            'red_in_check': self.red_in_check,
            'black_in_check': self.black_in_check,
            'from_pos': (from_row, from_col),
            'to_pos': (to_row, to_col),
            'captured_piece': captured_piece
        })
        
        # Thực hiện di chuyển
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = 0
        
        # Chuyển lượt
        self.current_player = BLACK if self.current_player == RED else RED
        
        # Kiểm tra xem có chiếu tướng không
        self._check_for_check()
        
        # Phát tín hiệu có nước đi
        self.move_made.emit(piece.color, piece.get_name(), (from_row, from_col), (to_row, to_col), is_capture, captured_piece_name)
        
        return True
    
    def _check_for_check(self):
        """Kiểm tra xem tướng có đang bị chiếu không"""
        # Lưu trạng thái chiếu cũ để so sánh
        old_red_in_check = self.red_in_check
        old_black_in_check = self.black_in_check
        
        # Đặt lại trạng thái chiếu
        self.red_in_check = False
        self.black_in_check = False
        
        # Tìm vị trí của hai tướng
        red_general_pos = None
        black_general_pos = None
        
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                piece = self.board[i][j]
                if isinstance(piece, General):
                    if piece.color == RED:
                        red_general_pos = (i, j)
                    else:
                        black_general_pos = (i, j)
        
        # Nếu không tìm thấy một trong hai tướng, thoát
        if not red_general_pos or not black_general_pos:
            return
        
        # Kiểm tra từng quân cờ đen xem có thể ăn tướng đỏ không
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                piece = self.board[i][j]
                if piece != 0 and piece.color == BLACK:
                    if piece.is_valid_move(self.board, (i, j), red_general_pos):
                        self.red_in_check = True
                        break
        
        # Kiểm tra từng quân cờ đỏ xem có thể ăn tướng đen không
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                piece = self.board[i][j]
                if piece != 0 and piece.color == RED:
                    if piece.is_valid_move(self.board, (i, j), black_general_pos):
                        self.black_in_check = True
                        break
        
        # Phát tín hiệu nếu có thay đổi trạng thái chiếu
        if old_red_in_check != self.red_in_check:
            if self.red_in_check:
                self.check_status_changed.emit(True, "Đỏ")
                # Chỉ kiểm tra chiếu hết nếu đang là lượt của quân Đỏ
                if self.current_player == RED and self._is_checkmate(RED):
                    self.game_over_state = True
                    self.game_over.emit("BLACK")  # Đen thắng vì Đỏ bị chiếu hết
            else:
                self.check_status_changed.emit(False, "Đỏ")
        
        if old_black_in_check != self.black_in_check:
            if self.black_in_check:
                self.check_status_changed.emit(True, "Đen")
                # Chỉ kiểm tra chiếu hết nếu đang là lượt của quân Đen
                if self.current_player == BLACK and self._is_checkmate(BLACK):
                    self.game_over_state = True
                    self.game_over.emit("RED")  # Đỏ thắng vì Đen bị chiếu hết
            else:
                self.check_status_changed.emit(False, "Đen")
    
    def _check_game_over(self):
        """Kiểm tra xem trò chơi đã kết thúc chưa (tướng bị ăn)"""
        # Kiểm tra xem có tướng đỏ không
        red_general_exists = False
        # Kiểm tra xem có tướng đen không
        black_general_exists = False
        
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                piece = self.board[i][j]
                if isinstance(piece, General):
                    if piece.color == RED:
                        red_general_exists = True
                    else:
                        black_general_exists = True
        
        # Nếu một trong hai tướng không còn, trò chơi kết thúc
        return not (red_general_exists and black_general_exists)
    
    def mark_last_move(self, start_pos, end_pos, is_ai_move=False):
        """Đánh dấu nước đi cuối cùng"""
        self.last_move = (start_pos, end_pos)
        self.last_move_is_ai = is_ai_move
        self.update()

    def make_ai_move(self):
        """Thực hiện nước đi của AI"""
        if self.game_over_state:
            return False
            
        # Kiểm tra xem có phải lượt của AI không
        if self.game_mode != "human_vs_ai" or self.current_player == RED:
            return False
            
        # Tính toán nước đi tốt nhất
        from_pos, to_pos = self.ai.get_best_move(self.board, self.current_player, self.ai_level)
        
        if from_pos and to_pos:
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            
            # Lưu nước đi gần nhất cho hiển thị
            self.mark_last_move(from_pos, to_pos, True)
            
            # Thực hiện nước đi
            result = self._make_move(from_row, from_col, to_row, to_col)
            
            # Cập nhật và trả về kết quả
            self.update()
            return result
        
        return False
    
    def get_game_state(self):
        """Lấy trạng thái trò chơi hiện tại để lưu"""
        game_state = {
            'board_state': [],
            'current_player': 'red' if self.current_player.red() > 0 else 'black',
            'game_mode': self.game_mode,
            'ai_level': self.ai_level
        }
        
        # Lưu trạng thái bàn cờ
        for row in range(BOARD_HEIGHT):
            row_data = []
            for col in range(BOARD_WIDTH):
                piece = self.board[row][col]
                if piece == 0:
                    row_data.append(None)
                else:
                    piece_data = {
                        'type': piece.__class__.__name__,
                        'color': 'red' if piece.color.red() > 0 else 'black',
                        'position': piece.position
                    }
                    row_data.append(piece_data)
            game_state['board_state'].append(row_data)
        
        return game_state
    
    def set_game_state(self, game_state):
        """Thiết lập trạng thái trò chơi từ dữ liệu đã lưu"""
        try:
            # Đặt lại bàn cờ
            self.board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=object)
            
            # Thiết lập từng quân cờ
            for row_idx, row_data in enumerate(game_state['board_state']):
                for col_idx, piece_data in enumerate(row_data):
                    if piece_data is not None:
                        # Tạo quân cờ mới
                        piece_type = piece_data['type']
                        color = RED if piece_data['color'] == 'red' else BLACK
                        position = tuple(piece_data['position'])
                        
                        # Tạo đối tượng quân cờ tương ứng
                        if piece_type == 'General':
                            self.board[row_idx][col_idx] = General(color, position)
                        elif piece_type == 'Advisor':
                            self.board[row_idx][col_idx] = Advisor(color, position)
                        elif piece_type == 'Elephant':
                            self.board[row_idx][col_idx] = Elephant(color, position)
                        elif piece_type == 'Horse':
                            self.board[row_idx][col_idx] = Horse(color, position)
                        elif piece_type == 'Chariot':
                            self.board[row_idx][col_idx] = Chariot(color, position)
                        elif piece_type == 'Cannon':
                            self.board[row_idx][col_idx] = Cannon(color, position)
                        elif piece_type == 'Soldier':
                            self.board[row_idx][col_idx] = Soldier(color, position)
            
            # Thiết lập người chơi hiện tại
            self.current_player = RED if game_state['current_player'] == 'red' else BLACK
            
            # Thiết lập chế độ chơi và cấp độ AI
            self.game_mode = game_state.get('game_mode', 'human_vs_human')
            self.ai_level = game_state.get('ai_level', 'medium')
            
            # Đặt lại các biến khác
            self.selected_piece = None
            self.selected_position = None
            self.last_move = None
            self.last_move_is_ai = False
            self.move_history = []
            self.captured_pieces = []
            self.valid_moves = []
            
            # Cập nhật giao diện
            self.update()
            return True
        except Exception as e:
            print(f"Lỗi khi thiết lập trạng thái trò chơi: {str(e)}")
            return False

    def _is_checkmate(self, color):
        """
        Kiểm tra xem người chơi có bị chiếu hết không 
        (không còn nước đi nào để thoát khỏi tình trạng chiếu tướng)
        
        Args:
            color: Màu của người chơi cần kiểm tra
            
        Returns:
            bool: True nếu bị chiếu hết, False nếu không
        """
        # Nếu không bị chiếu, không thể bị chiếu hết
        if (color == RED and not self.red_in_check) or (color == BLACK and not self.black_in_check):
            return False
            
        # Kiểm tra xem còn nước đi nào để thoát khỏi tình trạng chiếu tướng
        for row in range(BOARD_HEIGHT):
            for col in range(BOARD_WIDTH):
                piece = self.board[row][col]
                if piece != 0 and piece.color == color:
                    # Tìm tất cả nước đi có thể của quân cờ này
                    for to_row in range(BOARD_HEIGHT):
                        for to_col in range(BOARD_WIDTH):
                            if (to_row, to_col) != (row, col) and piece.is_valid_move(self.board, (row, col), (to_row, to_col)):
                                # Thử đi nước này xem có thoát khỏi chiếu tướng không
                                if self._move_resolves_check(row, col, to_row, to_col):
                                    return False  # Có ít nhất một nước đi để thoát
        
        # Nếu không tìm thấy nước nào để thoát, đó là chiếu hết
        return True

    def _move_resolves_check(self, from_row, from_col, to_row, to_col):
        """Kiểm tra xem nước đi có giải quyết được tình trạng chiếu tướng không"""
        # Lưu trạng thái hiện tại
        original_board = copy.deepcopy(self.board)
        original_red_in_check = self.red_in_check
        original_black_in_check = self.black_in_check
        
        # Thử thực hiện nước đi
        piece = self.board[from_row][from_col]
        captured_piece = self.board[to_row][to_col]
        
        # Di chuyển quân cờ
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = 0
        
        # Kiểm tra lại tình trạng chiếu tướng
        self._check_for_check()
        
        # Kiểm tra xem còn bị chiếu không
        resolved = False
        if piece.color == RED:
            resolved = not self.red_in_check
        else:
            resolved = not self.black_in_check
        
        # Khôi phục trạng thái ban đầu
        self.board = original_board
        self.red_in_check = original_red_in_check
        self.black_in_check = original_black_in_check
        
        return resolved