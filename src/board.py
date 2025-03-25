#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import numpy as np
from PyQt5.QtWidgets import QWidget, QMessageBox
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPixmap
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from pieces import Piece, General, Advisor, Elephant, Horse, Chariot, Cannon, Soldier
import copy
import time
from ai import ChineseChessAI

# Kích thước bàn cờ
BOARD_WIDTH = 9  # Số cột
BOARD_HEIGHT = 10  # Số hàng

# Màu sắc
RED = QColor(255, 0, 0)
BLACK = QColor(0, 0, 0)
BOARD_COLOR = QColor(238, 203, 173)
LINE_COLOR = QColor(0, 0, 0)
SELECTED_COLOR = QColor(0, 255, 0, 100)
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
        
        # Khởi tạo biến
        self.cell_size = 60  # Kích thước ô cờ
        self.margin = 30  # Lề
        self.board = np.zeros((BOARD_HEIGHT, BOARD_WIDTH), dtype=object)
        self.selected_piece = None
        self.selected_pos = None
        self.current_player = RED  # Đỏ đi trước
        self.ai_level = "medium"
        self.game_mode = "human_vs_human"  # Mặc định: người đấu với người
        
        # Biến theo dõi nước đi cuối cùng
        self.last_move_from = None
        self.last_move_to = None
        
        # Biến theo dõi trạng thái chiếu tướng
        self.red_in_check = False
        self.black_in_check = False
        
        # Lịch sử nước đi
        self.move_history = []
        self.captured_pieces = []
        
        # Các vị trí hợp lệ để di chuyển
        self.valid_moves = []
        
        # Khởi tạo AI
        self.ai = ChineseChessAI()
        
        # Khởi tạo bàn cờ
        self.reset_board()
        
        # Cho phép theo dõi chuột để di chuyển quân cờ
        self.setMouseTracking(True)
    
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
        self.selected_pos = None
        
        # Đặt lại nước đi cuối cùng
        self.last_move_from = None
        self.last_move_to = None
        
        # Đặt lại trạng thái chiếu tướng
        self.red_in_check = False
        self.black_in_check = False
        
        # Đặt lại lịch sử
        self.move_history = []
        self.captured_pieces = []
        
        # Đặt lại các vị trí hợp lệ
        self.valid_moves = []
        
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
        self.game_mode = mode
    
    def paintEvent(self, event):
        """Vẽ bàn cờ và quân cờ"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Vẽ nền bàn cờ
        painter.fillRect(self.rect(), BOARD_COLOR)
        
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
        pen = QPen(LINE_COLOR, 1)
        painter.setPen(pen)
        
        # Vẽ các đường ngang
        for i in range(BOARD_HEIGHT):
            y = self.margin + i * self.cell_size
            painter.drawLine(self.margin, y, 
                             self.margin + (BOARD_WIDTH - 1) * self.cell_size, y)
        
        # Vẽ các đường dọc
        for j in range(BOARD_WIDTH):
            x = self.margin + j * self.cell_size
            painter.drawLine(x, self.margin, 
                             x, self.margin + (BOARD_HEIGHT - 1) * self.cell_size)
        
        # Vẽ cung điện (3x3) cho cả hai bên
        # Cung điện dưới (Đỏ)
        palace_x = self.margin + 3 * self.cell_size
        palace_y_bottom = self.margin + 7 * self.cell_size
        painter.drawLine(palace_x, palace_y_bottom, 
                         palace_x + 2 * self.cell_size, palace_y_bottom + 2 * self.cell_size)
        painter.drawLine(palace_x + 2 * self.cell_size, palace_y_bottom, 
                         palace_x, palace_y_bottom + 2 * self.cell_size)
        
        # Cung điện trên (Đen)
        palace_y_top = self.margin
        painter.drawLine(palace_x, palace_y_top, 
                         palace_x + 2 * self.cell_size, palace_y_top + 2 * self.cell_size)
        painter.drawLine(palace_x + 2 * self.cell_size, palace_y_top, 
                         palace_x, palace_y_top + 2 * self.cell_size)
        
        # Vẽ sông
        painter.setPen(QPen(Qt.blue, 1, Qt.DashLine))
        river_y = self.margin + 4 * self.cell_size
        painter.drawLine(self.margin, river_y, 
                         self.margin + (BOARD_WIDTH - 1) * self.cell_size, river_y)
        river_y = self.margin + 5 * self.cell_size
        painter.drawLine(self.margin, river_y, 
                         self.margin + (BOARD_WIDTH - 1) * self.cell_size, river_y)
    
    def _draw_last_move(self, painter):
        """Vẽ đánh dấu nước đi cuối cùng"""
        if self.last_move_from and self.last_move_to:
            # Vẽ ô nguồn (vị trí cũ) - vẽ một vòng tròn đỏ không có nền
            from_row, from_col = self.last_move_from
            x_from = self.margin + from_col * self.cell_size
            y_from = self.margin + from_row * self.cell_size
            
            # Thiết lập bút vẽ màu đỏ, độ dày 2
            painter.setBrush(Qt.NoBrush)  # Không có nền
            painter.setPen(QPen(Qt.red, 2))  # Viền đỏ, độ dày 2
            
            # Vẽ vòng tròn ở vị trí cũ
            radius = self.cell_size // 2 - 4  # Giảm bán kính một chút để hiển thị đẹp hơn
            painter.drawEllipse(x_from - radius, y_from - radius, radius * 2, radius * 2)
            
            # Vẽ ô đích (vị trí mới) - vẫn giữ nguyên kiểu hiện tại
            to_row, to_col = self.last_move_to
            x_to = self.margin + to_col * self.cell_size
            y_to = self.margin + to_row * self.cell_size
            
            painter.setBrush(QBrush(LAST_MOVE_COLOR))
            painter.setPen(Qt.NoPen)
            painter.drawRect(x_to - self.cell_size // 2, y_to - self.cell_size // 2,
                           self.cell_size, self.cell_size)
    
    def _draw_valid_moves(self, painter):
        """Vẽ đánh dấu các điểm có thể đi"""
        if self.valid_moves:
            for row, col in self.valid_moves:
                x = self.margin + col * self.cell_size
                y = self.margin + row * self.cell_size
                
                # Chỉ vẽ vòng tròn cho các vị trí trống (không có quân cờ)
                if self.board[row][col] == 0:
                    # Vẽ vòng tròn đánh dấu vị trí hợp lệ
                    painter.setBrush(QBrush(VALID_MOVE_COLOR))
                    painter.setPen(QPen(Qt.black, 1))
                    # Vẽ một vòng tròn nhỏ hơn để đánh dấu vị trí có thể đi
                    radius = self.cell_size // 4
                    painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
                # Không vẽ gì cả cho vị trí có quân cờ, vì quân cờ sẽ được vẽ với độ trong suốt trong _draw_pieces
    
    def _draw_pieces(self, painter):
        """Vẽ quân cờ trên bàn cờ"""
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                piece = self.board[i][j]
                if piece != 0:
                    # Tọa độ tâm của quân cờ
                    x = self.margin + j * self.cell_size
                    y = self.margin + i * self.cell_size
                    
                    # Vẽ vùng được chọn
                    if self.selected_pos and self.selected_pos == (i, j):
                        painter.setBrush(QBrush(SELECTED_COLOR))
                        painter.setPen(Qt.NoPen)
                        painter.drawEllipse(x - self.cell_size // 2, y - self.cell_size // 2, 
                                           self.cell_size, self.cell_size)
                    
                    # Vẽ quân cờ
                    radius = self.cell_size // 2 - 2
                    
                    # Màu quân cờ
                    if piece.color == RED:
                        piece_color = QColor(220, 50, 50)
                        text_color = Qt.white
                    else:
                        piece_color = QColor(30, 30, 30)
                        text_color = Qt.white
                    
                    # Nếu quân cờ có thể bị ăn (nằm trong danh sách các vị trí hợp lệ), giảm độ đục (tăng độ trong suốt)
                    if self.valid_moves and (i, j) in self.valid_moves:
                        piece_color.setAlpha(150)  # Alpha range is 0-255, 150 means 60% opacity
                    
                    # Vẽ hình tròn quân cờ
                    painter.setBrush(QBrush(piece_color))
                    painter.setPen(QPen(Qt.black, 1))
                    painter.drawEllipse(x - radius, y - radius, radius * 2, radius * 2)
                    
                    # Vẽ tên quân cờ
                    painter.setPen(QPen(text_color))
                    font = painter.font()
                    font.setBold(True)
                    font.setPointSize(12)
                    painter.setFont(font)
                    
                    # Vị trí văn bản
                    piece_name = piece.get_name()
                    text_rect = QRect(x - radius, y - radius, radius * 2, radius * 2)
                    painter.drawText(text_rect, Qt.AlignCenter, piece_name)
                    
                    # Vẽ vòng đỏ khi tướng bị chiếu
                    if isinstance(piece, General):
                        if (piece.color == RED and self.red_in_check) or (piece.color == BLACK and self.black_in_check):
                            # Vẽ vòng đỏ xung quanh tướng
                            painter.setBrush(Qt.NoBrush)
                            painter.setPen(QPen(Qt.red, 3))  # Viền đỏ dày
                            check_radius = radius + 2  # Vòng tròn hơi lớn hơn quân cờ
                            painter.drawEllipse(x - check_radius, y - check_radius, check_radius * 2, check_radius * 2)
    
    def mousePressEvent(self, event):
        """Xử lý sự kiện khi người dùng nhấp chuột vào bàn cờ"""
        # Lấy vị trí được nhấp
        col = int(event.x() / self.cell_size)
        row = int(event.y() / self.cell_size)
        
        # Nếu game đã kết thúc, không cho phép di chuyển
        if self.game_over_state:
            return
        
        # Nếu đang ở chế độ người vs máy và lượt của máy, bỏ qua click
        if self.game_mode == "human_vs_ai" and self.current_player == BLACK:
            return
        
        # Nếu đã chọn một quân cờ trước đó
        if self.selected_piece:
            selected_row, selected_col = self.selected_piece
            
            # Nếu nhấp vào vị trí đã chọn, hủy chọn
            if row == selected_row and col == selected_col:
                self.selected_piece = None
                self.valid_moves = []
                self.update()
                return
            
            # Nếu nhấp vào một vị trí hợp lệ để di chuyển
            if (row, col) in self.valid_moves:
                # Lưu trạng thái trước khi di chuyển
                self._save_move_state(selected_row, selected_col, row, col)
                
                # Kiểm tra xem có bắt được quân cờ không
                captured_piece = None
                if self.board[row][col] != 0 and self.board[row][col] != ' ':
                    captured_piece = self.board[row][col]
                    # Phát tín hiệu báo quân cờ bị bắt
                    self.piece_captured.emit(captured_piece)
                
                # Di chuyển quân cờ
                self.board[row][col] = self.board[selected_row][selected_col]
                self.board[selected_row][selected_col] = 0
                
                # Ghi nhớ nước đi cuối cùng
                self.last_move_from = (selected_row, selected_col)
                self.last_move_to = (row, col)
                
                # Hủy chọn quân cờ
                self.selected_piece = None
                self.valid_moves = []
                
                # Chuyển lượt
                self.current_player = RED if self.current_player == BLACK else BLACK
                
                # Kiểm tra tình trạng chiếu tướng
                self._check_for_check()
                
                # Kiểm tra game kết thúc
                result = self._check_game_over()
                if result:
                    self.game_over_state = True
                    self.game_over.emit(result)
                
                # Cập nhật giao diện
                self.update()
                
                # Nếu đang ở chế độ người vs máy và đến lượt máy, thực hiện nước đi của máy
                if self.game_mode == "human_vs_ai" and self.current_player == BLACK and not self.game_over_state:
                    # Chờ một chút trước khi AI đi để tạo cảm giác AI đang suy nghĩ
                    QTimer.singleShot(500, self.make_ai_move)
                
                return
            
            # Nếu nhấp vào quân cờ khác của cùng người chơi, chọn quân cờ đó
            piece = self.board[row][col]
            if piece != 0 and piece != ' ':
                if (self.current_player == RED and piece.color == RED) or \
                   (self.current_player == BLACK and piece.color == BLACK):
                    self.selected_piece = (row, col)
                    self.valid_moves = self._calculate_valid_moves(row, col)
                    self.update()
                return
        
        # Nếu chưa chọn quân cờ, kiểm tra xem ô được nhấp có phải là quân cờ của người chơi hiện tại
        piece = self.board[row][col]
        if piece != 0 and piece != ' ':
            if (self.current_player == RED and piece.color == RED) or \
               (self.current_player == BLACK and piece.color == BLACK):
                self.selected_piece = (row, col)
                self.valid_moves = self._calculate_valid_moves(row, col)
                self.update()
    
    def _calculate_valid_moves(self, row, col):
        """Tính toán các vị trí hợp lệ cho quân cờ tại vị trí (row, col)"""
        self.valid_moves = []
        piece = self.board[row][col]
        
        if piece == 0:
            return self.valid_moves
        
        print(f"Đang tính toán nước đi hợp lệ cho {piece.get_name()} tại vị trí ({row}, {col})")
        
        # Kiểm tra xem tướng có đang bị chiếu không
        is_in_check = (self.red_in_check and piece.color == RED) or (self.black_in_check and piece.color == BLACK)
        
        # Nếu đang bị chiếu, cần phải tìm các nước đi để giải quyết tình trạng chiếu tướng
        if is_in_check:
            for to_row in range(BOARD_HEIGHT):
                for to_col in range(BOARD_WIDTH):
                    # Nếu vị trí đích khác vị trí hiện tại và nước đi hợp lệ
                    if (to_row, to_col) != (row, col) and piece.is_valid_move(self.board, (row, col), (to_row, to_col)):
                        # Thử nước đi này để xem có giải quyết được tình trạng chiếu tướng không
                        if self._move_resolves_check(row, col, to_row, to_col):
                            print(f"  - Nước đi hợp lệ (giải quyết chiếu tướng): ({to_row}, {to_col})")
                            self.valid_moves.append((to_row, to_col))
        else:
            # Nếu không bị chiếu, tính toán các nước đi bình thường
            for to_row in range(BOARD_HEIGHT):
                for to_col in range(BOARD_WIDTH):
                    # Nếu vị trí đích khác vị trí hiện tại và nước đi hợp lệ
                    if (to_row, to_col) != (row, col) and piece.is_valid_move(self.board, (row, col), (to_row, to_col)):
                        # Kiểm tra xem nước đi này có khiến tướng bị chiếu không
                        if not self._move_causes_check(row, col, to_row, to_col):
                            print(f"  - Nước đi hợp lệ: ({to_row}, {to_col})")
                            self.valid_moves.append((to_row, to_col))
        
        return self.valid_moves
    
    def _move_resolves_check(self, from_row, from_col, to_row, to_col):
        """Kiểm tra xem nước đi có giải quyết được tình trạng chiếu tướng không"""
        # Lưu trạng thái hiện tại
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        color = piece.color
        
        # Thử di chuyển
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = 0
        piece.position = (to_row, to_col)
        
        # Kiểm tra xem sau khi di chuyển, tướng có còn bị chiếu không
        is_still_check = False
        
        # Tìm vị trí tướng
        general_pos = None
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                p = self.board[i][j]
                if isinstance(p, General) and p.color == color:
                    general_pos = (i, j)
                    break
            if general_pos:
                break
        
        # Kiểm tra xem có quân nào của đối phương có thể ăn tướng không
        if general_pos:
            for i in range(BOARD_HEIGHT):
                for j in range(BOARD_WIDTH):
                    p = self.board[i][j]
                    if p != 0 and p.color != color:
                        if p.is_valid_move(self.board, (i, j), general_pos):
                            is_still_check = True
                            break
                if is_still_check:
                    break
        
        # Khôi phục trạng thái
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = target
        piece.position = (from_row, from_col)
        
        # Trả về True nếu nước đi giải quyết được tình trạng chiếu tướng
        return not is_still_check

    def _move_causes_check(self, from_row, from_col, to_row, to_col):
        """Kiểm tra xem nước đi có khiến tướng bị chiếu không"""
        # Lưu trạng thái hiện tại
        piece = self.board[from_row][from_col]
        target = self.board[to_row][to_col]
        color = piece.color
        
        # Thử di chuyển
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = 0
        piece.position = (to_row, to_col)
        
        # Kiểm tra xem sau khi di chuyển, tướng có bị chiếu không
        causes_check = False
        
        # Tìm vị trí tướng
        general_pos = None
        for i in range(BOARD_HEIGHT):
            for j in range(BOARD_WIDTH):
                p = self.board[i][j]
                if isinstance(p, General) and p.color == color:
                    general_pos = (i, j)
                    break
            if general_pos:
                break
        
        # Kiểm tra xem có quân nào của đối phương có thể ăn tướng không
        if general_pos:
            for i in range(BOARD_HEIGHT):
                for j in range(BOARD_WIDTH):
                    p = self.board[i][j]
                    if p != 0 and p.color != color:
                        if p.is_valid_move(self.board, (i, j), general_pos):
                            causes_check = True
                            break
                break
        
        # Khôi phục trạng thái
        self.board[from_row][from_col] = piece
        self.board[to_row][to_col] = target
        piece.position = (from_row, from_col)
        
        return causes_check
    
    def _save_move_state(self, from_row, from_col, to_row, to_col):
        """Lưu trạng thái trước khi di chuyển (cho chức năng hoàn tác)"""
        # Lưu bàn cờ hiện tại
        board_copy = copy.deepcopy(self.board)
        
        # Lưu thông tin nước đi
        move_info = {
            'board': board_copy,
            'from_pos': (from_row, from_col),
            'to_pos': (to_row, to_col),
            'captured': self.board[to_row][to_col] if self.board[to_row][to_col] != 0 else None,
            'current_player': self.current_player,
            'last_move_from': self.last_move_from,
            'last_move_to': self.last_move_to
        }
        
        # Thêm vào lịch sử
        self.move_history.append(move_info)
        
        # Lưu quân bị bắt
        if self.board[to_row][to_col] != 0:
            captured = self.board[to_row][to_col]
            self.captured_pieces.append(captured)
    
    def undo_last_move(self):
        """Hoàn tác nước đi cuối cùng"""
        if not self.move_history:
            return False
        
        # Lấy thông tin nước đi gần nhất
        last_move = self.move_history.pop()
        
        # Khôi phục bàn cờ
        self.board = last_move['board']
        
        # Khôi phục người chơi hiện tại
        self.current_player = last_move['current_player']
        
        # Khôi phục đánh dấu nước đi cuối cùng
        self.last_move_from = last_move['last_move_from']
        self.last_move_to = last_move['last_move_to']
        
        # Nếu có quân bị bắt, xóa khỏi danh sách
        if last_move['captured'] is not None and self.captured_pieces:
            self.captured_pieces.pop()
        
        # Đặt lại các biến khác
        self.selected_piece = None
        self.selected_pos = None
        self.valid_moves = []
        
        # Kiểm tra lại trạng thái chiếu tướng
        self._check_for_check()
        
        # Cập nhật giao diện
        self.update()
        return True
    
    def _is_valid_move(self, from_row, from_col, to_row, to_col):
        """Kiểm tra nước đi có hợp lệ không"""
        piece = self.board[from_row][from_col]
        if piece == 0:
            return False
        
        # Kiểm tra nước đi có hợp lệ theo luật của từng loại quân cờ
        return piece.is_valid_move(self.board, (from_row, from_col), (to_row, to_col))
    
    def _move_piece(self, from_row, from_col, to_row, to_col):
        """Di chuyển quân cờ trên bàn cờ"""
        piece = self.board[from_row][from_col]
        
        # Cập nhật vị trí mới cho quân cờ
        piece.position = (to_row, to_col)
        
        # Di chuyển quân cờ
        self.board[to_row][to_col] = piece
        self.board[from_row][from_col] = 0
        
        # Kiểm tra xem có đang chiếu tướng không
        self._check_for_check()
        
        # Cập nhật giao diện
        self.update()
    
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
            else:
                self.check_status_changed.emit(False, "Đỏ")
        
        if old_black_in_check != self.black_in_check:
            if self.black_in_check:
                self.check_status_changed.emit(True, "Đen")
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
    
    def make_ai_move(self):
        """Thực hiện nước đi của AI"""
        if self.game_mode != "human_vs_ai" or self.game_over_state:
            return

        # Lấy nước đi từ AI
        start_time = time.time()
        best_move = self.ai.get_best_move(self.board, self.current_player, self.ai_level)
        
        # Kiểm tra xem có nước đi hợp lệ không
        if best_move is None:
            # Không có nước đi hợp lệ, có thể là bước vào trạng thái kết thúc
            self.game_over_state = True
            winner = "BLACK" if self.current_player == RED else "RED"
            self.game_over.emit(winner)
            self.update()
            return
            
        start_pos, end_pos = best_move
        
        # Thực hiện nước đi
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Lưu trạng thái trước khi di chuyển
        self._save_move_state(start_row, start_col, end_row, end_col)
        
        # Kiểm tra xem có bắt được quân cờ không
        captured_piece = None
        if self.board[end_row][end_col] != 0:
            captured_piece = self.board[end_row][end_col]
            # Phát tín hiệu báo quân cờ bị bắt
            self.piece_captured.emit(captured_piece)
        
        # Di chuyển quân cờ
        self.board[end_row][end_col] = self.board[start_row][start_col]
        self.board[start_row][start_col] = 0
        
        # Chuyển lượt chơi
        self.current_player = RED if self.current_player == BLACK else BLACK
        
        # Kiểm tra tình trạng chiếu tướng
        self._check_for_check()
        
        # Kiểm tra game kết thúc
        result = self._check_game_over()
        if result:
            self.game_over_state = True
            self.game_over.emit(result)
            
        # Cập nhật giao diện
        self.update()
            
        # Thêm độ trễ để AI có vẻ như đang "suy nghĩ"
        elapsed_time = time.time() - start_time
        min_thinking_time = 1.0  # Thời gian suy nghĩ tối thiểu (giây)
        
        if elapsed_time < min_thinking_time:
            delay = int((min_thinking_time - elapsed_time) * 1000)
            QTimer.singleShot(delay, self.update)
    
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
            self.selected_pos = None
            self.last_move_from = None
            self.last_move_to = None
            self.move_history = []
            self.captured_pieces = []
            self.valid_moves = []
            
            # Cập nhật giao diện
            self.update()
            return True
        except Exception as e:
            print(f"Lỗi khi thiết lập trạng thái trò chơi: {str(e)}")
            return False
