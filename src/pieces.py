#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from PyQt5.QtGui import QColor

class Piece:
    """Lớp cơ sở cho tất cả các loại quân cờ"""
    
    def __init__(self, color, position):
        """
        Khởi tạo quân cờ
        
        Args:
            color: Màu quân cờ (RED hoặc BLACK)
            position: Vị trí của quân cờ dưới dạng tuple (row, col)
        """
        self.color = color
        self.position = position
    
    def get_name(self):
        """Lấy tên hiển thị của quân cờ"""
        return "?"
    
    def is_valid_move(self, board, from_pos, to_pos):
        """
        Kiểm tra nước đi có hợp lệ không
        
        Args:
            board: Bàn cờ hiện tại
            from_pos: Vị trí xuất phát (row, col)
            to_pos: Vị trí đích (row, col)
            
        Returns:
            bool: True nếu nước đi hợp lệ, False nếu không
        """
        # Kiểm tra vị trí đích có quân cờ cùng màu không
        to_row, to_col = to_pos
        
        # In thông tin gỡ lỗi
        print(f"Kiểm tra nước đi từ {from_pos} đến {to_pos}")
        
        # Kiểm tra nếu vị trí đích có quân cờ cùng màu
        if board[to_row][to_col] != 0:
            if board[to_row][to_col].color == self.color:
                print(f"  - Không hợp lệ: Vị trí đích có quân cờ cùng màu")
                return False
            else:
                print(f"  - Vị trí đích có quân cờ đối phương: {board[to_row][to_col].get_name()}")
        
        # Các quân cờ cụ thể sẽ ghi đè phương thức này
        return True  # Đổi từ False sang True để các lớp con có thể kiểm tra tiếp


class General(Piece):
    """Quân Tướng/Vua"""
    
    def get_name(self):
        """Lấy tên hiển thị của quân cờ"""
        return "帅" if self.color.red() > 0 else "将"
    
    def is_valid_move(self, board, from_pos, to_pos):
        """Kiểm tra nước đi của Tướng có hợp lệ không"""
        # Kiểm tra điều kiện chung trước
        if not super().is_valid_move(board, from_pos, to_pos):
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        print(f"Kiểm tra nước đi của Tướng từ ({from_row},{from_col}) đến ({to_row},{to_col})")
        
        # Tướng chỉ có thể di chuyển trong cung điện (3x3)
        # Cung điện đỏ: (7-9, 3-5)
        # Cung điện đen: (0-2, 3-5)
        if self.color.red() > 0:  # Tướng đỏ
            if not (7 <= to_row <= 9 and 3 <= to_col <= 5):
                print(f"  - Không hợp lệ: Tướng đỏ phải ở trong cung điện (7-9, 3-5)")
                return False
        else:  # Tướng đen
            if not (0 <= to_row <= 2 and 3 <= to_col <= 5):
                print(f"  - Không hợp lệ: Tướng đen phải ở trong cung điện (0-2, 3-5)")
                return False
        
        # Tướng chỉ có thể di chuyển 1 ô theo chiều ngang hoặc dọc
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        if (row_diff == 1 and col_diff == 0) or (row_diff == 0 and col_diff == 1):
            # Kiểm tra tướng đối phương
            if self._check_facing_general(board, to_pos):
                print(f"  - Hợp lệ: Tướng di chuyển 1 ô theo chiều ngang hoặc dọc")
                return True
            else:
                print(f"  - Không hợp lệ: Hai tướng không được đối mặt trực tiếp")
                return False
        else:
            print(f"  - Không hợp lệ: Tướng chỉ có thể di chuyển 1 ô theo chiều ngang hoặc dọc")
            return False
    
    def _check_facing_general(self, board, new_pos):
        """Kiểm tra hai tướng có đối mặt nhau không"""
        new_row, new_col = new_pos
        
        print(f"Kiểm tra hai tướng đối mặt khi Tướng di chuyển đến ({new_row}, {new_col})")
        
        # Kiểm tra cột
        if 3 <= new_col <= 5:
            # Tìm tướng đối phương
            for row in range(10):
                piece = board[row][new_col]
                if isinstance(piece, General) and piece.color != self.color:
                    print(f"  - Tìm thấy tướng đối phương tại ({row}, {new_col})")
                    
                    # Kiểm tra có quân cờ nào ở giữa hai tướng không
                    min_row = min(new_row, row)
                    max_row = max(new_row, row)
                    
                    has_piece_between = False
                    for r in range(min_row + 1, max_row):
                        if board[r][new_col] != 0:
                            print(f"    + Có quân cờ {board[r][new_col].get_name()} tại ({r}, {new_col})")
                            has_piece_between = True
                            break
                    
                    # Nếu không có quân cờ nào ở giữa, không cho phép nước đi này
                    if not has_piece_between:
                        print(f"  - Không hợp lệ: Hai tướng đối mặt trực tiếp")
                        return False
                    
                    break
        
        return True  # Không có vấn đề với hai tướng đối mặt


class Advisor(Piece):
    """Quân Sĩ"""
    
    def get_name(self):
        """Lấy tên hiển thị của quân cờ"""
        return "仕" if self.color.red() > 0 else "士"
    
    def is_valid_move(self, board, from_pos, to_pos):
        """Kiểm tra nước đi của Sĩ có hợp lệ không"""
        if not super().is_valid_move(board, from_pos, to_pos):
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Sĩ chỉ có thể di chuyển trong cung điện (3x3)
        if self.color.red() > 0:  # Sĩ đỏ
            if not (7 <= to_row <= 9 and 3 <= to_col <= 5):
                return False
        else:  # Sĩ đen
            if not (0 <= to_row <= 2 and 3 <= to_col <= 5):
                return False
        
        # Sĩ chỉ có thể di chuyển 1 ô theo đường chéo
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        return row_diff == 1 and col_diff == 1


class Elephant(Piece):
    """Quân Tượng"""
    
    def get_name(self):
        """Lấy tên hiển thị của quân cờ"""
        return "相" if self.color.red() > 0 else "象"
    
    def is_valid_move(self, board, from_pos, to_pos):
        """Kiểm tra nước đi của Tượng có hợp lệ không"""
        if not super().is_valid_move(board, from_pos, to_pos):
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Tượng không thể vượt sông (giới hạn nửa bàn cờ)
        if self.color.red() > 0:  # Tượng đỏ
            if to_row < 5:  # Không thể vượt qua sông
                return False
        else:  # Tượng đen
            if to_row > 4:  # Không thể vượt qua sông
                return False
        
        # Tượng di chuyển theo kiểu "田" (2 ô theo đường chéo)
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        if row_diff != 2 or col_diff != 2:
            return False
        
        # Kiểm tra xem có bị chặn ở điểm giữa không
        mid_row = (from_row + to_row) // 2
        mid_col = (from_col + to_col) // 2
        
        return board[mid_row][mid_col] == 0  # Không có quân cờ ở giữa


class Horse(Piece):
    """Quân Mã"""
    
    def get_name(self):
        """Lấy tên hiển thị của quân cờ"""
        return "傌" if self.color.red() > 0 else "馬"
    
    def is_valid_move(self, board, from_pos, to_pos):
        """Kiểm tra nước đi của Mã có hợp lệ không"""
        if not super().is_valid_move(board, from_pos, to_pos):
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        print(f"Kiểm tra nước đi của Mã từ ({from_row},{from_col}) đến ({to_row},{to_col})")
        
        # Mã di chuyển theo kiểu "日" (1 ô theo chiều ngang/dọc + 1 ô theo đường chéo)
        row_diff = abs(to_row - from_row)
        col_diff = abs(to_col - from_col)
        
        if not ((row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)):
            print(f"  - Không hợp lệ: Mã chỉ có thể di chuyển theo kiểu 'nhảy' (1-2 hoặc 2-1)")
            return False
        
        # Kiểm tra xem có bị "bẻ chân" không
        if row_diff == 2:  # Di chuyển 2 ô theo hàng
            block_row = from_row + (1 if to_row > from_row else -1)
            block_col = from_col
        else:  # Di chuyển 2 ô theo cột
            block_row = from_row
            block_col = from_col + (1 if to_col > from_col else -1)
        
        if board[block_row][block_col] != 0:
            print(f"  - Không hợp lệ: Có quân cờ {board[block_row][block_col].get_name()} chặn đường tại ({block_row}, {block_col})")
            return False
        
        print(f"  - Hợp lệ: Mã di chuyển theo kiểu 'nhảy' và không bị chặn")
        return True  # Không có quân cờ chặn đường


class Chariot(Piece):
    """Quân Xe"""
    
    def get_name(self):
        """Lấy tên hiển thị của quân cờ"""
        return "俥" if self.color.red() > 0 else "車"
    
    def is_valid_move(self, board, from_pos, to_pos):
        """Kiểm tra nước đi của Xe có hợp lệ không"""
        if not super().is_valid_move(board, from_pos, to_pos):
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        print(f"Kiểm tra nước đi của Xe từ ({from_row},{from_col}) đến ({to_row},{to_col})")
        
        # Xe chỉ có thể di chuyển theo hàng ngang hoặc dọc
        if from_row != to_row and from_col != to_col:
            print(f"  - Không hợp lệ: Xe chỉ có thể di chuyển theo hàng ngang hoặc dọc")
            return False
        
        # Kiểm tra xem có quân cờ nào chặn đường không
        if from_row == to_row:  # Di chuyển theo hàng ngang
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            
            for col in range(start_col, end_col):
                if board[from_row][col] != 0:
                    print(f"  - Không hợp lệ: Có quân cờ {board[from_row][col].get_name()} chặn đường tại ({from_row}, {col})")
                    return False
        else:  # Di chuyển theo hàng dọc
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            
            for row in range(start_row, end_row):
                if board[row][from_col] != 0:
                    print(f"  - Không hợp lệ: Có quân cờ {board[row][from_col].get_name()} chặn đường tại ({row}, {from_col})")
                    return False
        
        print(f"  - Hợp lệ: Xe di chuyển theo đường thẳng và không bị chặn")
        return True


class Cannon(Piece):
    """Quân Pháo"""
    
    def get_name(self):
        """Lấy tên hiển thị của quân cờ"""
        return "炮" if self.color.red() > 0 else "砲"
    
    def is_valid_move(self, board, from_pos, to_pos):
        """Kiểm tra nước đi của Pháo có hợp lệ không"""
        if not super().is_valid_move(board, from_pos, to_pos):
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        to_piece = board[to_row][to_col]
        
        # Pháo chỉ có thể di chuyển theo hàng ngang hoặc dọc
        if from_row != to_row and from_col != to_col:
            return False
        
        # Đếm số quân cờ ở giữa
        pieces_between = 0
        
        if from_row == to_row:  # Di chuyển theo hàng ngang
            start_col = min(from_col, to_col) + 1
            end_col = max(from_col, to_col)
            
            for col in range(start_col, end_col):
                if board[from_row][col] != 0:
                    pieces_between += 1
        else:  # Di chuyển theo hàng dọc
            start_row = min(from_row, to_row) + 1
            end_row = max(from_row, to_row)
            
            for row in range(start_row, end_row):
                if board[row][from_col] != 0:
                    pieces_between += 1
        
        # Nếu di chuyển tới ô trống
        if to_piece == 0:
            return pieces_between == 0  # Không có quân cờ ở giữa
        else:
            # Nếu di chuyển để ăn quân
            return pieces_between == 1  # Chỉ có một quân cờ ở giữa để làm "đài"
        

class Soldier(Piece):
    """Quân Tốt/Binh"""
    
    def get_name(self):
        """Lấy tên hiển thị của quân cờ"""
        return "兵" if self.color.red() > 0 else "卒"
    
    def is_valid_move(self, board, from_pos, to_pos):
        """Kiểm tra nước đi của Tốt có hợp lệ không"""
        if not super().is_valid_move(board, from_pos, to_pos):
            return False
        
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        
        # Tốt chỉ có thể di chuyển 1 ô
        if abs(to_row - from_row) + abs(to_col - from_col) != 1:
            return False
        
        # Quy tắc di chuyển khác nhau tùy thuộc vào vị trí và màu
        if self.color.red() > 0:  # Tốt đỏ
            # Chưa vượt sông (row >= 5): chỉ có thể di chuyển lên trên
            if from_row >= 5:
                return to_row == from_row - 1 and to_col == from_col
            # Đã vượt sông (row < 5): có thể di chuyển lên trên hoặc sang ngang
            else:
                if to_col != from_col:  # Di chuyển sang ngang
                    return to_row == from_row
                else:  # Di chuyển lên trên
                    return to_row == from_row - 1
        else:  # Tốt đen
            # Chưa vượt sông (row <= 4): chỉ có thể di chuyển xuống dưới
            if from_row <= 4:
                return to_row == from_row + 1 and to_col == from_col
            # Đã vượt sông (row > 4): có thể di chuyển xuống dưới hoặc sang ngang
            else:
                if to_col != from_col:  # Di chuyển sang ngang
                    return to_row == from_row
                else:  # Di chuyển xuống dưới
                    return to_row == from_row + 1
