#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import random
import time
from collections import deque
import heapq
from pieces import General, Advisor, Elephant, Horse, Chariot, Cannon, Soldier

# Định nghĩa hằng số cho các bên
RED = 'r'
BLACK = 'b'

# Định nghĩa các giá trị của quân cờ
PIECE_VALUES = {
    "General": 10000,  # Tướng
    "Advisor": 200,    # Sĩ
    "Elephant": 200,   # Tượng
    "Horse": 400,      # Mã
    "Chariot": 900,    # Xe
    "Cannon": 450,     # Pháo
    "Soldier": 100,    # Tốt
    # Sau khi tốt qua sông giá trị tăng lên
    "AdvancedSoldier": 200,
}

# Bảng vị trí cho từng loại quân, thể hiện giá trị của quân khi ở các vị trí khác nhau
# Giá trị từ 0-20 (cao hơn giá trị cũ)
POSITION_VALUES = {
    "General": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 2, 2, 2, 0, 0, 0],
        [0, 0, 0, 5, 8, 5, 0, 0, 0],
        [0, 0, 0, 10, 15, 10, 0, 0, 0],
    ],
    "Advisor": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 5, 0, 5, 0, 0, 0],
        [0, 0, 0, 0, 8, 0, 0, 0, 0],
        [0, 0, 0, 5, 0, 5, 0, 0, 0],
    ],
    "Elephant": [
        [0, 0, 8, 0, 0, 0, 8, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [7, 0, 0, 0, 10, 0, 0, 0, 7],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 8, 0, 0, 0, 8, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "Horse": [
        [0, 2, 4, 4, 0, 4, 4, 2, 0],
        [2, 4, 6, 6, 6, 6, 6, 4, 2],
        [4, 6, 8, 8, 8, 8, 8, 6, 4],
        [4, 6, 8, 10, 10, 10, 8, 6, 4],
        [4, 6, 8, 10, 10, 10, 8, 6, 4],
        [4, 6, 8, 10, 10, 10, 8, 6, 4],
        [4, 6, 8, 8, 8, 8, 8, 6, 4],
        [2, 4, 6, 6, 6, 6, 6, 4, 2],
        [0, 2, 4, 4, 4, 4, 4, 2, 0],
        [0, 0, 2, 2, 2, 2, 2, 0, 0],
    ],
    "Chariot": [
        [10, 10, 10, 12, 14, 12, 10, 10, 10],
        [10, 12, 12, 14, 16, 14, 12, 12, 10],
        [10, 12, 12, 14, 16, 14, 12, 12, 10],
        [12, 14, 14, 16, 18, 16, 14, 14, 12],
        [14, 16, 16, 18, 20, 18, 16, 16, 14],
        [12, 14, 14, 16, 18, 16, 14, 14, 12],
        [10, 12, 12, 14, 16, 14, 12, 12, 10],
        [10, 12, 12, 14, 16, 14, 12, 12, 10],
        [8, 10, 10, 12, 14, 12, 10, 10, 8],
        [6, 8, 8, 10, 12, 10, 8, 8, 6],
    ],
    "Cannon": [
        [8, 8, 8, 10, 12, 10, 8, 8, 8],
        [8, 10, 10, 12, 14, 12, 10, 10, 8],
        [8, 10, 10, 12, 14, 12, 10, 10, 8],
        [10, 12, 12, 14, 16, 14, 12, 12, 10],
        [12, 14, 14, 16, 18, 16, 14, 14, 12],
        [10, 12, 12, 14, 16, 14, 12, 12, 10],
        [8, 10, 10, 12, 14, 12, 10, 10, 8],
        [8, 10, 10, 12, 14, 12, 10, 10, 8],
        [6, 8, 8, 10, 12, 10, 8, 8, 6],
        [4, 6, 6, 8, 10, 8, 6, 6, 4],
    ],
    "Soldier": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [2, 4, 6, 8, 10, 8, 6, 4, 2],
        [4, 6, 8, 10, 12, 10, 8, 6, 4],
        [6, 8, 10, 12, 14, 12, 10, 8, 6],
        [8, 10, 12, 14, 16, 14, 12, 10, 8],
        [10, 12, 14, 16, 18, 16, 14, 12, 10],
        [12, 14, 16, 18, 20, 18, 16, 14, 12],
        [14, 16, 18, 20, 22, 20, 18, 16, 14],
    ],
}

# Đánh giá chiến thuật bổ sung
TACTICS_BONUS = {
    "control_center": 30,      # Kiểm soát trung tâm
    "connected_chariots": 30,  # Xe liên kết
    "protected_general": 50,   # Tướng được bảo vệ
    "advanced_pawn": 20,       # Tốt tiến xa
    "doubled_cannons": 40,     # Pháo đôi cùng hàng/cột
    "horse_pair": 25,          # Cặp mã
    "attacking_position": 35,  # Vị trí tấn công
    "mobility": 5,             # Điểm cho mỗi nước đi hợp lệ
}

class ChineseChessAI:
    def __init__(self, difficulty='medium'):
        self.difficulty = difficulty
        # Hash table lưu trữ trạng thái đã đánh giá
        self.transposition_table = {}  
        
        # Độ sâu tìm kiếm dựa theo độ khó
        self.depths = {
            'easy': 2,
            'medium': 3,
            'hard': 4,
            'expert': 5
        }
        
        # Lịch sử các nước đi để hỗ trợ sắp xếp
        self.move_history = {}
        
        # Thời gian tối đa cho mỗi lượt (msec)
        self.time_limits = {
            'easy': 1000,
            'medium': 2000,
            'hard': 5000,
            'expert': 10000
        }

    def set_difficulty(self, level):
        """Thiết lập độ khó cho AI"""
        if level in self.depths:
            self.difficulty = level
        else:
            self.difficulty = 'medium'  # Mặc định

    def get_board_hash(self, board):
        """Tạo hash key từ trạng thái bàn cờ"""
        hash_key = ""
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece == 0 or piece == ' ':
                    hash_key += "_"
                else:
                    piece_type = piece.__class__.__name__
                    is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
                    color_char = "r" if is_red else "b"
                    piece_char = piece_type[0]
                    hash_key += color_char + piece_char
        return hash_key

    def get_best_move(self, board, player_color):
        """Trả về nước đi tốt nhất sử dụng Iterative Deepening"""
        start_time = time.time()
        time_limit = self.time_limits[self.difficulty] / 1000  # Chuyển từ msec sang sec
        max_depth = self.depths[self.difficulty]
        
        best_move = None
        best_value = float('-inf')
        
        # Iterative Deepening
        for depth in range(1, max_depth + 1):
            # Kiểm tra thời gian
            if time.time() - start_time > time_limit * 0.8:  # Sử dụng 80% thời gian
                break
            
            move, value = self._get_best_move_at_depth(board, player_color, depth)
            if move:
                best_move = move
                best_value = value
                
            # Kiểm tra chiếu tướng/chiếu hết
            if abs(value) > 9000:
                break  # Đã tìm thấy nước dẫn đến thắng/thua
                
        # Sử dụng chiến lược ngẫu nhiên cho cấp độ dễ
        if self.difficulty == 'easy' and random.random() < 0.3:
            valid_moves = self._get_all_valid_moves(board, player_color)
            if valid_moves:
                best_move = random.choice(valid_moves)
        
        return best_move
    
    def _get_best_move_at_depth(self, board, player_color, depth):
        """Tìm nước đi tốt nhất với độ sâu cụ thể"""
        alpha = float('-inf')
        beta = float('inf')
        best_move = None
        best_value = float('-inf')
        
        # Lấy tất cả nước đi hợp lệ
        valid_moves = self._get_all_valid_moves(board, player_color)
        if not valid_moves:
            return None, -10000  # Thua nếu không có nước đi hợp lệ
        
        # Sắp xếp nước đi để tối ưu cắt tỉa Alpha-Beta
        ordered_moves = self._order_moves(board, valid_moves, player_color)
        
        for move in ordered_moves:
            # Thực hiện nước đi
            new_board = self._make_move_on_copy(board, move[0], move[1])
            
            # Đánh giá nước đi bằng minimax
            value = -self._alpha_beta(new_board, depth-1, -beta, -alpha, self._get_opponent(player_color))
            
            if value > best_value:
                best_value = value
                best_move = move
                
            alpha = max(alpha, value)
            
            # Cập nhật lịch sử nước đi
            move_key = f"{move[0][0]},{move[0][1]}-{move[1][0]},{move[1][1]}"
            self.move_history[move_key] = self.move_history.get(move_key, 0) + (1 << depth)
            
        return best_move, best_value
    
    def _alpha_beta(self, board, depth, alpha, beta, player_color):
        """Alpha-Beta Pruning với Transposition Table"""
        # Kiểm tra hash trước
        board_hash = self.get_board_hash(board)
        if board_hash in self.transposition_table and self.transposition_table[board_hash]['depth'] >= depth:
            entry = self.transposition_table[board_hash]
            if entry['flag'] == 'exact':
                return entry['value']
            elif entry['flag'] == 'lower' and entry['value'] > alpha:
                alpha = entry['value']
            elif entry['flag'] == 'upper' and entry['value'] < beta:
                beta = entry['value']
            
            if alpha >= beta:
                return entry['value']
        
        # Điều kiện dừng
        if depth == 0:
            value = self._evaluate_board(board, player_color)
            return value
            
        # Kiểm tra kết thúc
        if self._is_game_over(board):
            # Kiểm tra chiếu hết - người hiện tại thua
            if self._is_in_check(board, player_color):
                return -10000  # Thua
            return 0  # Hòa - trường hợp khác
        
        # Thu thập nước đi hợp lệ
        valid_moves = self._get_all_valid_moves(board, player_color)
        
        if not valid_moves:
            return -10000  # Không có nước đi hợp lệ - thua
        
        # Sắp xếp nước đi
        ordered_moves = self._order_moves(board, valid_moves, player_color)
        
        max_value = float('-inf')
        flag = 'upper'  # Mặc định là giới hạn trên
        
        for move in ordered_moves:
            new_board = self._make_move_on_copy(board, move[0], move[1])
            value = -self._alpha_beta(new_board, depth-1, -beta, -alpha, self._get_opponent(player_color))
            
            if value > max_value:
                max_value = value
                
            if value > alpha:
                alpha = value
                flag = 'exact'  # Giá trị chính xác
                
            if alpha >= beta:
                flag = 'lower'  # Giới hạn dưới
                break  # Cắt tỉa Beta
        
        # Lưu vào hash table
        self.transposition_table[board_hash] = {
            'value': max_value,
            'depth': depth,
            'flag': flag
        }
        
        return max_value
    
    def _order_moves(self, board, moves, player_color):
        """Sắp xếp nước đi để tối ưu Alpha-Beta"""
        move_scores = []
        
        for move in moves:
            start_pos, end_pos = move
            start_row, start_col = start_pos
            end_row, end_col = end_pos
            piece = board[start_row][start_col]
            target = board[end_row][end_col]
            
            # Tính điểm cho nước đi
            score = 0
            
            # 1. Nước ăn quân - MVV/LVA (Most Valuable Victim / Least Valuable Aggressor)
            if target != 0 and target != ' ':
                target_value = self._get_piece_value(target)
                attacker_value = self._get_piece_value(piece)
                score += 10 * target_value - attacker_value
                
            # 2. Nước thăng cấp cho tốt
            if isinstance(piece, Soldier):
                is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
                if (is_red and end_row < 5) or (not is_red and end_row > 4):
                    score += 300
                    
            # 3. Nước đi vào vị trí tốt
            score += self._get_position_value(piece, end_row, end_col) * 2
            
            # 4. Nước chiếu tướng
            if self._is_check_move(board, start_pos, end_pos, player_color):
                score += 500
                
            # 5. Từ lịch sử nước đi
            move_key = f"{start_pos[0]},{start_pos[1]}-{end_pos[0]},{end_pos[1]}"
            score += self.move_history.get(move_key, 0)
            
            move_scores.append((move, score))
            
        # Sắp xếp nước đi theo điểm cao nhất
        return [move for move, score in sorted(move_scores, key=lambda x: x[1], reverse=True)]
    
    def _is_check_move(self, board, start_pos, end_pos, player_color):
        """Kiểm tra nước đi có chiếu tướng đối phương không"""
        new_board = self._make_move_on_copy(board, start_pos, end_pos)
        return self._is_in_check(new_board, self._get_opponent(player_color))
    
    def _get_piece_value(self, piece):
        """Trả về giá trị cơ bản của quân cờ"""
        if piece == 0 or piece == ' ':
            return 0
            
        piece_type = piece.__class__.__name__
        
        if piece_type == "General":
            return 10000
        elif piece_type == "Advisor":
            return 200
        elif piece_type == "Elephant":
            return 200
        elif piece_type == "Horse":
            return 400
        elif piece_type == "Chariot":
            return 900
        elif piece_type == "Cannon":
            return 450
        elif piece_type == "Soldier":
            # Kiểm tra tốt qua sông
            is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
            if (is_red and piece.position[0] < 5) or (not is_red and piece.position[0] > 4):
                return 200
            return 100
        return 0
    
    def _get_position_value(self, piece, row, col):
        """Lấy giá trị vị trí của quân cờ"""
        if piece == 0 or piece == ' ':
            return 0
            
        piece_type = piece.__class__.__name__
        
        if piece_type not in POSITION_VALUES:
            return 0
            
        # Đảo ngược bảng cho quân đen
        is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
        if is_red:
            return POSITION_VALUES[piece_type][row][col]
        else:
            return POSITION_VALUES[piece_type][9-row][col]
    
    def _evaluate_board(self, board, player_color):
        """Đánh giá trạng thái bàn cờ"""
        my_score = 0
        opponent_score = 0
        
        # Đếm quân và đánh giá vị trí
        my_pieces = []
        opponent_pieces = []
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ':
                    is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
                    is_my_piece = (player_color == RED and is_red) or (player_color == BLACK and not is_red)
                    
                    piece_value = self._get_piece_value(piece)
                    position_value = self._get_position_value(piece, row, col)
                    
                    if is_my_piece:
                        my_score += piece_value + position_value
                        my_pieces.append((piece, row, col))
                    else:
                        opponent_score += piece_value + position_value
                        opponent_pieces.append((piece, row, col))
        
        # Đánh giá tình hình chiến thuật
        my_tactics = self._evaluate_tactics(board, my_pieces, player_color)
        opponent_tactics = self._evaluate_tactics(board, opponent_pieces, self._get_opponent(player_color))
        
        my_score += my_tactics
        opponent_score += opponent_tactics
        
        # Đánh giá trạng thái chiếu tướng
        if self._is_in_check(board, self._get_opponent(player_color)):
            my_score += 100  # Chiếu tướng đối phương
        if self._is_in_check(board, player_color):
            opponent_score += 100  # Bị đối phương chiếu tướng
        
        # Tính điểm di chuyển (mobility)
        my_mobility = len(self._get_all_valid_moves(board, player_color)) * TACTICS_BONUS["mobility"]
        opponent_mobility = len(self._get_all_valid_moves(board, self._get_opponent(player_color))) * TACTICS_BONUS["mobility"]
        
        my_score += my_mobility
        opponent_score += opponent_mobility
        
        return my_score - opponent_score
    
    def _evaluate_tactics(self, board, pieces, player_color):
        """Đánh giá chiến thuật"""
        tactics_score = 0
        
        # Vị trí các quân theo loại
        chariots = []
        cannons = []
        horses = []
        pawns = []
        general_pos = None
        
        for piece, row, col in pieces:
            piece_type = piece.__class__.__name__
            if piece_type == "Chariot":
                chariots.append((row, col))
            elif piece_type == "Cannon":
                cannons.append((row, col))
            elif piece_type == "Horse":
                horses.append((row, col))
            elif piece_type == "Soldier":
                pawns.append((row, col))
            elif piece_type == "General":
                general_pos = (row, col)
        
        # Kiểm soát trung tâm
        center_pieces = []
        for piece, row, col in pieces:
            if 3 <= row <= 6 and 3 <= col <= 5:
                center_pieces.append((row, col))
        tactics_score += len(center_pieces) * TACTICS_BONUS["control_center"]
        
        # Xe liên kết
        if len(chariots) >= 2:
            for i in range(len(chariots)):
                for j in range(i+1, len(chariots)):
                    r1, c1 = chariots[i]
                    r2, c2 = chariots[j]
                    if r1 == r2 or c1 == c2:
                        # Kiểm tra không có quân nào chặn giữa
                        blocked = False
                        if r1 == r2:  # Cùng hàng ngang
                            start_c, end_c = min(c1, c2), max(c1, c2)
                            for c in range(start_c + 1, end_c):
                                if board[r1][c] != 0 and board[r1][c] != ' ':
                                    blocked = True
                                    break
                        else:  # Cùng hàng dọc
                            start_r, end_r = min(r1, r2), max(r1, r2)
                            for r in range(start_r + 1, end_r):
                                if board[r][c1] != 0 and board[r][c1] != ' ':
                                    blocked = True
                                    break
                        if not blocked:
                            tactics_score += TACTICS_BONUS["connected_chariots"]
        
        # Tướng được bảo vệ
        if general_pos:
            gen_row, gen_col = general_pos
            protected = False
            for piece, row, col in pieces:
                if piece.__class__.__name__ in ["Advisor", "Elephant"]:
                    # Kiểm tra sĩ, tượng bảo vệ tướng
                    if abs(row - gen_row) <= 1 and abs(col - gen_col) <= 1:
                        protected = True
                        break
            if protected:
                tactics_score += TACTICS_BONUS["protected_general"]
        
        # Tốt tiến xa
        for row, col in pawns:
            is_red = player_color == RED
            if (is_red and row < 3) or (not is_red and row > 6):
                tactics_score += TACTICS_BONUS["advanced_pawn"]
        
        # Pháo đôi
        if len(cannons) >= 2:
            for i in range(len(cannons)):
                for j in range(i+1, len(cannons)):
                    r1, c1 = cannons[i]
                    r2, c2 = cannons[j]
                    if r1 == r2 or c1 == c2:
                        tactics_score += TACTICS_BONUS["doubled_cannons"]
        
        # Cặp mã
        if len(horses) >= 2:
            tactics_score += TACTICS_BONUS["horse_pair"]
        
        # Vị trí tấn công - quân ở nửa sân đối phương
        attack_pieces = []
        for piece, row, col in pieces:
            is_red = player_color == RED
            if (is_red and row < 5) or (not is_red and row > 4):
                attack_pieces.append((row, col))
        tactics_score += len(attack_pieces) * TACTICS_BONUS["attacking_position"]
        
        return tactics_score
    
    def _get_all_valid_moves(self, board, player_color):
        """Trả về tất cả các nước đi hợp lệ"""
        valid_moves = []
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ' and hasattr(piece, 'color'):
                    # Kiểm tra màu quân
                    is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
                    if (player_color == RED and is_red) or (player_color == BLACK and not is_red):
                        # Lấy các nước đi hợp lệ của quân này
                        for end_row in range(10):
                            for end_col in range(9):
                                if (end_row, end_col) != (row, col) and piece.is_valid_move(board, (row, col), (end_row, end_col)):
                                    # Kiểm tra nước đi không gây ra tự chiếu tướng
                                    if not self._causes_self_check(board, row, col, end_row, end_col, player_color):
                                        valid_moves.append(((row, col), (end_row, end_col)))
        
        return valid_moves
    
    def _causes_self_check(self, board, start_row, start_col, end_row, end_col, player_color):
        """Kiểm tra nước đi có gây ra tự chiếu tướng không"""
        # Lưu trạng thái hiện tại
        piece = board[start_row][start_col]
        target = board[end_row][end_col]
        
        # Thực hiện nước đi tạm thời
        old_position = piece.position
        board[end_row][end_col] = piece
        board[start_row][start_col] = 0
        piece.position = (end_row, end_col)
        
        # Kiểm tra tướng có bị chiếu không
        is_check = self._is_in_check(board, player_color)
        
        # Khôi phục trạng thái ban đầu
        board[start_row][start_col] = piece
        board[end_row][end_col] = target
        piece.position = old_position
        
        return is_check
    
    def _is_in_check(self, board, player_color):
        """Kiểm tra một người chơi có đang bị chiếu tướng không"""
        # Tìm vị trí tướng
        general_pos = None
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ' and hasattr(piece, 'color'):
                    is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
                    if piece.__class__.__name__ == "General" and ((player_color == RED and is_red) or (player_color == BLACK and not is_red)):
                        general_pos = (row, col)
                        break
            if general_pos:
                break
        
        # Nếu không tìm thấy tướng, trả về True (giả định là đã thua)
        if not general_pos:
            return True
        
        # Tìm một đối tượng màu sắc để sử dụng
        color_class = None
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ' and hasattr(piece, 'color') and hasattr(piece.color, '__class__'):
                    color_class = piece.color.__class__
                    break
            if color_class:
                break
                
        # Nếu không tìm thấy lớp màu sắc, trả về False
        if not color_class:
            return False
            
        # Tạo đối tượng màu đối thủ
        opponent_color = color_class(0, 0, 0) if player_color == RED else color_class(255, 0, 0)
        
        # Kiểm tra các nước đi của đối thủ
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ' and hasattr(piece, 'color'):
                    is_opponent = (player_color == RED and piece.color.red() == 0) or (player_color == BLACK and piece.color.red() > 0)
                    if is_opponent and piece.is_valid_move(board, (row, col), general_pos):
                        return True
        
        return False
    
    def _is_game_over(self, board):
        """Kiểm tra trò chơi đã kết thúc chưa"""
        red_general_exists = False
        black_general_exists = False
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ' and hasattr(piece, '__class__'):
                    if piece.__class__.__name__ == "General":
                        is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
                        if is_red:
                            red_general_exists = True
                        else:
                            black_general_exists = True
                            
                        if red_general_exists and black_general_exists:
                            return False  # Cả hai tướng đều còn
        
        return True  # Một trong hai tướng đã bị ăn
    
    def _make_move_on_copy(self, board, start_pos, end_pos):
        """Tạo bản sao của bàn cờ và thực hiện nước đi"""
        import copy
        
        board_copy = copy.deepcopy(board)
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Di chuyển quân cờ
        piece = board_copy[start_row][start_col]
        old_pos = piece.position if hasattr(piece, 'position') else None
        board_copy[end_row][end_col] = piece
        board_copy[start_row][start_col] = 0
        
        # Cập nhật vị trí của quân cờ
        if hasattr(piece, 'position'):
            piece.position = (end_row, end_col)
        
        return board_copy
    
    def _get_opponent(self, player_color):
        """Trả về màu đối thủ"""
        return BLACK if player_color == RED else RED 

    def _minimax(self, board, depth, alpha, beta, is_maximizing):
        """Thuật toán Minimax với Alpha-Beta Pruning để đánh giá nước đi"""
        # Thiết lập thời gian bắt đầu nếu chưa có
        if not hasattr(self, 'start_time'):
            self.start_time = time.time()
            
        # Kiểm tra thời gian
        if time.time() - self.start_time > self.max_time:
            raise TimeoutError("Hết thời gian tìm kiếm")
        
        # Trường hợp cơ sở: đạt đến độ sâu 0 hoặc trạng thái cuối
        if depth == 0:
            return self._evaluate_board(board)
        
        # Lấy màu của người chơi hiện tại
        current_color = self.color if is_maximizing else self.opponent_color
        
        # Lấy tất cả nước đi hợp lệ
        valid_moves = self._get_all_valid_moves_from_board(board, current_color)
        
        # Kiểm tra nếu không có nước đi hợp lệ (thua)
        if not valid_moves:
            return float('-inf') if is_maximizing else float('inf')
        
        # Người chơi tối đa (AI)
        if is_maximizing:
            max_eval = float('-inf')
            for move in valid_moves:
                start_pos, end_pos = move
                captured_piece = self._make_move(board, start_pos, end_pos)
                
                eval = self._minimax(board, depth - 1, alpha, beta, False)
                
                self._undo_move(board, start_pos, end_pos, captured_piece)
                
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                
                # Alpha-Beta Pruning
                if beta <= alpha:
                    break
                    
            return max_eval
        
        # Người chơi tối thiểu (đối thủ)
        else:
            min_eval = float('inf')
            for move in valid_moves:
                start_pos, end_pos = move
                captured_piece = self._make_move(board, start_pos, end_pos)
                
                eval = self._minimax(board, depth - 1, alpha, beta, True)
                
                self._undo_move(board, start_pos, end_pos, captured_piece)
                
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                
                # Alpha-Beta Pruning
                if beta <= alpha:
                    break
                    
            return min_eval
    
    def _get_all_valid_moves_from_board(self, board, color):
        """Lấy tất cả nước đi hợp lệ từ bàn cờ sao chép"""
        valid_moves = []
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and hasattr(piece, 'color') and piece.color.name.lower() == color:
                    # Lấy tất cả nước đi hợp lệ của quân cờ này
                    valid_destinations = self._get_valid_moves_for_piece(board, (row, col), piece)
                    
                    # Thêm vào danh sách nước đi hợp lệ
                    for dest in valid_destinations:
                        valid_moves.append(((row, col), dest))
        
        return valid_moves
    
    def _get_valid_moves_for_piece(self, board, position, piece):
        """Lấy các nước đi hợp lệ cho một quân cờ cụ thể"""
        # Gọi phương thức tương ứng dựa vào loại quân cờ
        piece_type = piece.__class__.__name__
        row, col = position
        
        if "General" in piece_type:  # Tướng/Vua
            return self._get_general_moves(board, position, piece)
        elif "Advisor" in piece_type:  # Sĩ
            return self._get_advisor_moves(board, position, piece)
        elif "Elephant" in piece_type:  # Tượng
            return self._get_elephant_moves(board, position, piece)
        elif "Horse" in piece_type:  # Mã
            return self._get_horse_moves(board, position, piece)
        elif "Chariot" in piece_type:  # Xe
            return self._get_chariot_moves(board, position, piece)
        elif "Cannon" in piece_type:  # Pháo
            return self._get_cannon_moves(board, position, piece)
        elif "Soldier" in piece_type:  # Tốt/Binh
            return self._get_soldier_moves(board, position, piece)
        
        return []  # Mặc định, không có nước đi hợp lệ
    
    def _get_general_moves(self, board, position, piece):
        """Lấy nước đi hợp lệ cho Tướng/Vua"""
        row, col = position
        valid_moves = []
        color = piece.color.name.lower()
        
        # Xác định cung cấm
        if color == "red":
            min_row, max_row = 7, 9
        else:  # black
            min_row, max_row = 0, 2
        min_col, max_col = 3, 5
        
        # Các hướng di chuyển của Tướng: lên, xuống, trái, phải
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra vị trí mới có hợp lệ không
            if (min_row <= new_row <= max_row and 
                min_col <= new_col <= max_col and
                (board[new_row][new_col] == 0 or  # Ô trống
                 (hasattr(board[new_row][new_col], 'color') and  
                  board[new_row][new_col].color.name.lower() != color))):  # Ô có quân đối phương
                valid_moves.append((new_row, new_col))
        
        # Kiểm tra "Tướng đối diện" (Flying general)
        if color == "red":
            # Tìm vị trí Tướng đen
            for black_row in range(0, 3):
                if (board[black_row][col] != 0 and 
                    hasattr(board[black_row][col], 'color') and
                    "General" in board[black_row][col].__class__.__name__ and
                    board[black_row][col].color.name.lower() == "black"):
                    
                    # Kiểm tra xem có quân nào ở giữa hai Tướng không
                    has_piece_between = False
                    for r in range(row - 1, black_row, -1):
                        if board[r][col] != 0:
                            has_piece_between = True
                            break
                    
                    # Nếu không có quân ở giữa, có thể "ăn" Tướng đối phương
                    if not has_piece_between:
                        valid_moves.append((black_row, col))
                    
                    break
        else:  # black
            # Tìm vị trí Tướng đỏ
            for red_row in range(7, 10):
                if (board[red_row][col] != 0 and 
                    hasattr(board[red_row][col], 'color') and
                    "General" in board[red_row][col].__class__.__name__ and
                    board[red_row][col].color.name.lower() == "red"):
                    
                    # Kiểm tra xem có quân nào ở giữa hai Tướng không
                    has_piece_between = False
                    for r in range(row + 1, red_row):
                        if board[r][col] != 0:
                            has_piece_between = True
                            break
                    
                    # Nếu không có quân ở giữa, có thể "ăn" Tướng đối phương
                    if not has_piece_between:
                        valid_moves.append((red_row, col))
                    
                    break
        
        return valid_moves
    
    def _get_advisor_moves(self, board, position, piece):
        """Lấy nước đi hợp lệ cho Sĩ"""
        row, col = position
        valid_moves = []
        color = piece.color.name.lower()
        
        # Xác định cung cấm
        if color == "red":
            min_row, max_row = 7, 9
        else:  # black
            min_row, max_row = 0, 2
        min_col, max_col = 3, 5
        
        # Các hướng di chuyển của Sĩ: đường chéo
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra vị trí mới có hợp lệ không
            if (min_row <= new_row <= max_row and 
                min_col <= new_col <= max_col and
                (board[new_row][new_col] == 0 or  # Ô trống
                 (hasattr(board[new_row][new_col], 'color') and
                  board[new_row][new_col].color.name.lower() != color))):  # Ô có quân đối phương
                valid_moves.append((new_row, new_col))
        
        return valid_moves
    
    def _get_elephant_moves(self, board, position, piece):
        """Lấy nước đi hợp lệ cho Tượng"""
        row, col = position
        valid_moves = []
        color = piece.color.name.lower()
        
        # Xác định nửa bàn cờ
        if color == "red":
            min_row, max_row = 5, 9
        else:  # black
            min_row, max_row = 0, 4
        
        # Các hướng di chuyển của Tượng: đường chéo 2 ô
        directions = [(-2, -2), (-2, 2), (2, -2), (2, 2)]
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Vị trí giữa (để kiểm tra "vướng chân")
            mid_row, mid_col = row + dr // 2, col + dc // 2
            
            # Kiểm tra vị trí mới có hợp lệ không
            if (0 <= new_row < 10 and 
                0 <= new_col < 9 and
                min_row <= new_row <= max_row and  # Không vượt qua sông
                board[mid_row][mid_col] == 0 and  # Không bị "vướng chân"
                (board[new_row][new_col] == 0 or  # Ô trống
                 (hasattr(board[new_row][new_col], 'color') and
                  board[new_row][new_col].color.name.lower() != color))):  # Ô có quân đối phương
                valid_moves.append((new_row, new_col))
        
        return valid_moves
    
    def _get_horse_moves(self, board, position, piece):
        """Lấy nước đi hợp lệ cho Mã"""
        row, col = position
        valid_moves = []
        color = piece.color.name.lower()
        
        # Các hướng di chuyển của Mã: hình chữ L
        directions = [
            (-2, -1, -1, 0), (-2, 1, -1, 0),  # Lên 2, trái/phải 1
            (2, -1, 1, 0), (2, 1, 1, 0),      # Xuống 2, trái/phải 1
            (-1, -2, 0, -1), (1, -2, 0, -1),  # Trái 2, lên/xuống 1
            (-1, 2, 0, 1), (1, 2, 0, 1)       # Phải 2, lên/xuống 1
        ]
        
        for dr, dc, hr, hc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Vị trí "vướng chân"
            hobble_row, hobble_col = row + hr, col + hc
            
            # Kiểm tra vị trí mới có hợp lệ không
            if (0 <= new_row < 10 and 
                0 <= new_col < 9 and
                board[hobble_row][hobble_col] == 0 and  # Không bị "vướng chân"
                (board[new_row][new_col] == 0 or  # Ô trống
                 (hasattr(board[new_row][new_col], 'color') and
                  board[new_row][new_col].color.name.lower() != color))):  # Ô có quân đối phương
                valid_moves.append((new_row, new_col))
        
        return valid_moves
    
    def _get_chariot_moves(self, board, position, piece):
        """Lấy nước đi hợp lệ cho Xe"""
        row, col = position
        valid_moves = []
        color = piece.color.name.lower()
        
        # Các hướng di chuyển của Xe: lên, xuống, trái, phải
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            for i in range(1, 10):  # Tối đa 9 ô
                new_row, new_col = row + i * dr, col + i * dc
                
                # Nếu vị trí mới ra ngoài bàn cờ, dừng lại
                if not (0 <= new_row < 10 and 0 <= new_col < 9):
                    break
                
                # Nếu ô trống, thêm vào danh sách nước đi hợp lệ
                if board[new_row][new_col] == 0:
                    valid_moves.append((new_row, new_col))
                # Nếu ô có quân đối phương, thêm vào danh sách và dừng lại
                elif hasattr(board[new_row][new_col], 'color') and board[new_row][new_col].color.name.lower() != color:
                    valid_moves.append((new_row, new_col))
                    break
                # Nếu ô có quân cùng màu, dừng lại
                else:
                    break
        
        return valid_moves
    
    def _get_cannon_moves(self, board, position, piece):
        """Lấy nước đi hợp lệ cho Pháo"""
        row, col = position
        valid_moves = []
        color = piece.color.name.lower()
        
        # Các hướng di chuyển của Pháo: lên, xuống, trái, phải
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for dr, dc in directions:
            has_platform = False  # Có "bệ phóng" hay chưa
            
            for i in range(1, 10):  # Tối đa 9 ô
                new_row, new_col = row + i * dr, col + i * dc
                
                # Nếu vị trí mới ra ngoài bàn cờ, dừng lại
                if not (0 <= new_row < 10 and 0 <= new_col < 9):
                    break
                
                # Nếu chưa có "bệ phóng"
                if not has_platform:
                    # Nếu ô trống, thêm vào danh sách nước đi hợp lệ
                    if board[new_row][new_col] == 0:
                        valid_moves.append((new_row, new_col))
                    # Nếu ô có quân (bất kỳ màu nào), đánh dấu là "bệ phóng" và tiếp tục
                    else:
                        has_platform = True
                # Nếu đã có "bệ phóng"
                else:
                    # Nếu ô trống, tiếp tục
                    if board[new_row][new_col] == 0:
                        continue
                    # Nếu ô có quân đối phương, thêm vào danh sách và dừng lại
                    elif hasattr(board[new_row][new_col], 'color') and board[new_row][new_col].color.name.lower() != color:
                        valid_moves.append((new_row, new_col))
                        break
                    # Nếu ô có quân cùng màu, dừng lại
                    else:
                        break
        
        return valid_moves
    
    def _get_soldier_moves(self, board, position, piece):
        """Lấy nước đi hợp lệ cho Tốt/Binh"""
        row, col = position
        valid_moves = []
        color = piece.color.name.lower()
        
        # Xác định hướng di chuyển của Tốt (lên với đen, xuống với đỏ)
        if color == "red":
            directions = [(-1, 0)]  # Đỏ đi lên
            has_crossed_river = row < 5  # Đỏ qua sông khi row < 5
        else:  # black
            directions = [(1, 0)]  # Đen đi xuống
            has_crossed_river = row > 4  # Đen qua sông khi row > 4
        
        # Nếu đã qua sông, thêm hướng di chuyển sang trái và phải
        if has_crossed_river:
            directions.extend([(0, -1), (0, 1)])
        
        for dr, dc in directions:
            new_row, new_col = row + dr, col + dc
            
            # Kiểm tra vị trí mới có hợp lệ không
            if (0 <= new_row < 10 and 
                0 <= new_col < 9 and
                (board[new_row][new_col] == 0 or  # Ô trống
                 (hasattr(board[new_row][new_col], 'color') and
                  board[new_row][new_col].color.name.lower() != color))):  # Ô có quân đối phương
                valid_moves.append((new_row, new_col))
        
        return valid_moves
    
    def _evaluate_board(self, board):
        """Đánh giá trạng thái bàn cờ hiện tại"""
        score = 0
        
        # Đếm quân và tính giá trị
        piece_count = {"red": defaultdict(int), "black": defaultdict(int)}
        piece_value = {"red": 0, "black": 0}
        
        # Phân tích bàn cờ
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and hasattr(piece, 'color'):
                    color = piece.color.name.lower()
                    piece_type = piece.__class__.__name__
                    
                    # Lấy loại quân cờ cơ bản
                    basic_type = None
                    for pt in PIECE_VALUES.keys():
                        if pt in piece_type:
                            basic_type = pt
                            break
                    
                    if basic_type:
                        # Đếm quân
                        piece_count[color][basic_type] += 1
                        
                        # Tính giá trị quân cờ
                        value = PIECE_VALUES[basic_type]
                        
                        # Cộng thêm giá trị vị trí
                        position_value = 0
                        if color == "red" and basic_type in POSITION_VALUES:
                            position_value = POSITION_VALUES[basic_type][row][col]
                        elif color == "black" and basic_type in POSITION_VALUES:
                            position_value = POSITION_VALUES[basic_type][row][col]
                        
                        # Tổng giá trị
                        piece_value[color] += value + position_value * 0.1
        
        # Tính điểm dựa trên sự chênh lệch giá trị quân cờ
        ai_value = piece_value[self.color]
        opponent_value = piece_value[self.opponent_color]
        material_score = ai_value - opponent_value
        
        # Đánh giá khả năng di chuyển (mobility)
        ai_mobility = len(self._get_all_valid_moves_from_board(board, self.color))
        opponent_mobility = len(self._get_all_valid_moves_from_board(board, self.opponent_color))
        mobility_score = ai_mobility - opponent_mobility
        
        # Đánh giá an toàn của Tướng (king safety)
        ai_king_safety = self._evaluate_king_safety(board, self.color)
        opponent_king_safety = self._evaluate_king_safety(board, self.opponent_color)
        king_safety_score = ai_king_safety - opponent_king_safety
        
        # Đánh giá vị trí Tốt/Binh (pawn advancement)
        ai_pawn_score = self._evaluate_pawn_advancement(board, self.color)
        opponent_pawn_score = self._evaluate_pawn_advancement(board, self.opponent_color)
        pawn_score = ai_pawn_score - opponent_pawn_score
        
        # Tổng hợp điểm số
        score = (
            material_score * FEATURE_WEIGHTS["piece_value"] +
            mobility_score * FEATURE_WEIGHTS["mobility"] +
            king_safety_score * FEATURE_WEIGHTS["king_safety"] +
            pawn_score * FEATURE_WEIGHTS["pawn_advancement"]
        )
        
        return score
    
    def _evaluate_king_safety(self, board, color):
        """Đánh giá an toàn của Tướng"""
        safety_score = 100  # Điểm cơ bản
        
        # Tìm vị trí Tướng
        king_pos = None
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if (piece != 0 and hasattr(piece, 'color') and 
                    piece.color.name.lower() == color and 
                    "General" in piece.__class__.__name__):
                    king_pos = (row, col)
                    break
            if king_pos:
                break
        
        if not king_pos:
            return -10000  # Tướng đã bị bắt, điểm rất thấp
        
        king_row, king_col = king_pos
        
        # Kiểm tra các quân bảo vệ xung quanh Tướng
        protectors = 0
        opponent = "black" if color == "red" else "red"
        
        # Đếm Sĩ và Tượng còn lại
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if (piece != 0 and hasattr(piece, 'color') and 
                    piece.color.name.lower() == color):
                    if "Advisor" in piece.__class__.__name__ or "Elephant" in piece.__class__.__name__:
                        protectors += 1
        
        # Cộng điểm cho mỗi quân bảo vệ
        safety_score += protectors * 10
        
        # Kiểm tra số quân tấn công hướng đến Tướng
        attackers = 0
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if (piece != 0 and hasattr(piece, 'color') and 
                    piece.color.name.lower() == opponent):
                    # Lấy các nước đi hợp lệ của quân đối phương
                    valid_moves = self._get_valid_moves_for_piece(board, (row, col), piece)
                    # Kiểm tra xem có thể tấn công Tướng không
                    if king_pos in valid_moves:
                        attackers += 1
        
        # Trừ điểm cho mỗi quân tấn công
        safety_score -= attackers * 20
        
        # Kiểm tra "Tướng đối diện"
        if color == "red":
            # Kiểm tra cột của Tướng đỏ
            for row in range(king_row - 1, -1, -1):
                piece = board[row][king_col]
                if piece == 0:
                    continue
                if (hasattr(piece, 'color') and 
                    piece.color.name.lower() == "black" and 
                    "General" in piece.__class__.__name__):
                    # Tướng đối diện, điểm rất thấp
                    safety_score -= 50
                break  # Dừng khi gặp quân đầu tiên
        else:  # black
            # Kiểm tra cột của Tướng đen
            for row in range(king_row + 1, 10):
                piece = board[row][king_col]
                if piece == 0:
                    continue
                if (hasattr(piece, 'color') and 
                    piece.color.name.lower() == "red" and 
                    "General" in piece.__class__.__name__):
                    # Tướng đối diện, điểm rất thấp
                    safety_score -= 50
                break  # Dừng khi gặp quân đầu tiên
        
        return safety_score
    
    def _evaluate_pawn_advancement(self, board, color):
        """Đánh giá sự tiến triển của Tốt/Binh"""
        score = 0
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if (piece != 0 and hasattr(piece, 'color') and 
                    piece.color.name.lower() == color and 
                    "Soldier" in piece.__class__.__name__):
                    
                    if color == "red":
                        # Tốt đỏ càng lên trên (row càng nhỏ) càng tốt
                        score += (9 - row) * 2
                        # Cộng thêm điểm nếu đã qua sông
                        if row < 5:
                            score += 10
                    else:  # black
                        # Tốt đen càng xuống dưới (row càng lớn) càng tốt
                        score += row * 2
                        # Cộng thêm điểm nếu đã qua sông
                        if row > 4:
                            score += 10
        
        return score 