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
# Giá trị từ 0-9
POSITION_VALUES = {
    "General": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 1, 1, 1, 0, 0, 0],
        [0, 0, 0, 2, 2, 2, 0, 0, 0],
        [0, 0, 0, 3, 3, 3, 0, 0, 0],
    ],
    "Advisor": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 3, 0, 3, 0, 0, 0],
        [0, 0, 0, 0, 5, 0, 0, 0, 0],
        [0, 0, 0, 3, 0, 3, 0, 0, 0],
    ],
    "Elephant": [
        [0, 0, 5, 0, 0, 0, 5, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [5, 0, 0, 0, 7, 0, 0, 0, 5],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 5, 0, 0, 0, 5, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
    "Horse": [
        [0, 1, 2, 2, 0, 2, 2, 1, 0],
        [1, 2, 4, 4, 4, 4, 4, 2, 1],
        [2, 4, 6, 6, 6, 6, 6, 4, 2],
        [2, 4, 6, 8, 8, 8, 6, 4, 2],
        [2, 4, 6, 8, 8, 8, 6, 4, 2],
        [2, 4, 6, 8, 8, 8, 6, 4, 2],
        [2, 4, 6, 6, 6, 6, 6, 4, 2],
        [1, 2, 4, 4, 4, 4, 4, 2, 1],
        [0, 1, 2, 2, 2, 2, 2, 1, 0],
        [0, 0, 1, 1, 1, 1, 1, 0, 0],
    ],
    "Chariot": [
        [6, 6, 6, 8, 10, 8, 6, 6, 6],
        [6, 8, 8, 10, 12, 10, 8, 8, 6],
        [6, 8, 8, 10, 12, 10, 8, 8, 6],
        [8, 10, 10, 12, 14, 12, 10, 10, 8],
        [10, 12, 12, 14, 16, 14, 12, 12, 10],
        [8, 10, 10, 12, 14, 12, 10, 10, 8],
        [6, 8, 8, 10, 12, 10, 8, 8, 6],
        [6, 8, 8, 10, 12, 10, 8, 8, 6],
        [4, 6, 6, 8, 10, 8, 6, 6, 4],
        [2, 4, 4, 6, 8, 6, 4, 4, 2],
    ],
    "Cannon": [
        [6, 6, 6, 8, 10, 8, 6, 6, 6],
        [6, 8, 8, 10, 12, 10, 8, 8, 6],
        [6, 8, 8, 10, 12, 10, 8, 8, 6],
        [8, 10, 10, 12, 14, 12, 10, 10, 8],
        [10, 12, 12, 14, 16, 14, 12, 12, 10],
        [8, 10, 10, 12, 14, 12, 10, 10, 8],
        [6, 8, 8, 10, 12, 10, 8, 8, 6],
        [6, 8, 8, 10, 12, 10, 8, 8, 6],
        [4, 6, 6, 8, 10, 8, 6, 6, 4],
        [2, 4, 4, 6, 8, 6, 4, 4, 2],
    ],
    "Soldier": [
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 3, 5, 7, 9, 7, 5, 3, 1],
        [2, 4, 6, 8, 10, 8, 6, 4, 2],
        [3, 5, 7, 9, 11, 9, 7, 5, 3],
        [4, 6, 8, 10, 12, 10, 8, 6, 4],
        [5, 7, 9, 11, 13, 11, 9, 7, 5],
        [6, 8, 10, 12, 14, 12, 10, 8, 6],
        [7, 9, 11, 13, 15, 13, 11, 9, 7],
    ],
}

def get_valid_moves(board, player_color):
    """Lấy tất cả các nước đi hợp lệ cho một người chơi"""
    valid_moves = []
    for row in range(10):
        for col in range(9):
            piece = board[row][col]
            if piece != 0 and piece.color == player_color:
                # Kiểm tra tất cả các ô trên bàn cờ
                for to_row in range(10):
                    for to_col in range(9):
                        # Thử mỗi nước đi có thể
                        if piece.is_valid_move(board, (row, col), (to_row, to_col)):
                            # Kiểm tra nước đi không gây ra tự chiếu tướng
                            if not causes_self_check(board, row, col, to_row, to_col, player_color):
                                valid_moves.append(((row, col), (to_row, to_col)))
    return valid_moves

def causes_self_check(board, from_row, from_col, to_row, to_col, player_color):
    """Kiểm tra nước đi có gây ra tình trạng tự chiếu tướng không"""
    # Lưu trạng thái hiện tại
    piece = board[from_row][from_col]
    target = board[to_row][to_col]
    
    # Thử di chuyển
    board[to_row][to_col] = piece
    board[from_row][from_col] = 0
    piece.position = (to_row, to_col)
    
    # Kiểm tra tướng có bị chiếu không
    is_check = is_in_check(board, player_color)
    
    # Khôi phục trạng thái
    board[from_row][from_col] = piece
    board[to_row][to_col] = target
    piece.position = (from_row, from_col)
    
    return is_check

def is_in_check(board, player_color):
    """Kiểm tra một người chơi có đang bị chiếu tướng không"""
    # Tìm vị trí tướng
    general_pos = None
    for row in range(10):
        for col in range(9):
            piece = board[row][col]
            if piece != 0 and piece.color == player_color and piece.__class__.__name__ == "General":
                general_pos = (row, col)
                break
        if general_pos:
            break
    
    # Nếu không tìm thấy tướng, trả về True (giả định là đã thua)
    if not general_pos:
        return True
    
    # Kiểm tra xem có quân nào của đối phương có thể ăn tướng không
    opponent_color = BLACK if player_color == RED else RED
    for row in range(10):
        for col in range(9):
            piece = board[row][col]
            if piece != 0 and piece.color == opponent_color:
                if piece.is_valid_move(board, (row, col), general_pos):
                    return True
    
    return False

def evaluate_board(board):
    """Đánh giá giá trị của bàn cờ cho quân đỏ (giá trị dương = đỏ chiếm ưu thế)"""
    red_score = 0
    black_score = 0
    
    # Đếm và đánh giá từng quân cờ dựa trên loại và vị trí
    for row in range(10):
        for col in range(9):
            piece = board[row][col]
            if piece != 0:
                piece_type = piece.__class__.__name__
                position_value = 0
                
                # Lấy giá trị vị trí nếu có sẵn
                if piece_type in POSITION_VALUES:
                    # Với quân đen, đảo ngược bảng vị trí
                    if piece.color == RED:
                        position_value = POSITION_VALUES[piece_type][row][col]
                    else:
                        position_value = POSITION_VALUES[piece_type][9-row][col]
                
                # Tính giá trị quân cờ
                piece_value = PIECE_VALUES.get(piece_type, 0)
                
                # Xử lý đặc biệt cho tốt qua sông
                if piece_type == "Soldier":
                    # Với quân đỏ, khi tốt qua sông (row < 5)
                    if piece.color == RED and row < 5:
                        piece_value = PIECE_VALUES["AdvancedSoldier"]
                    # Với quân đen, khi tốt qua sông (row > 4)
                    elif piece.color == BLACK and row > 4:
                        piece_value = PIECE_VALUES["AdvancedSoldier"]
                
                # Cộng điểm
                total_value = piece_value + position_value * 10
                if piece.color == RED:
                    red_score += total_value
                else:
                    black_score += total_value
    
    # Kiểm tra tình trạng chiếu tướng
    if is_in_check(board, BLACK):
        red_score += 50  # Bonus khi đỏ đang chiếu tướng đen
    if is_in_check(board, RED):
        black_score += 50  # Bonus khi đen đang chiếu tướng đỏ
    
    return red_score - black_score

def minimax(board, depth, alpha, beta, maximizing_player, player_color):
    """Thuật toán Minimax với cắt tỉa Alpha-Beta"""
    
    # Đạt đến độ sâu tối đa, trả về giá trị đánh giá
    if depth == 0:
        return evaluate_board(board) if player_color == RED else -evaluate_board(board)
    
    # Lấy tất cả nước đi hợp lệ
    valid_moves = get_valid_moves(board, player_color)
    
    # Không còn nước đi hợp lệ, người chơi thua
    if not valid_moves:
        return -100000 if maximizing_player else 100000
    
    # Nếu đang tối đa hóa (lượt của người chơi đỏ)
    if maximizing_player:
        max_eval = float('-inf')
        for from_pos, to_pos in valid_moves:
            # Thực hiện nước đi
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            piece = board[from_row][from_col]
            target = board[to_row][to_col]
            
            board[to_row][to_col] = piece
            board[from_row][from_col] = 0
            old_position = piece.position
            piece.position = (to_row, to_col)
            
            # Gọi đệ quy minimax cho đối thủ
            opponent_color = BLACK if player_color == RED else RED
            eval = minimax(board, depth - 1, alpha, beta, False, opponent_color)
            
            # Khôi phục nước đi
            board[from_row][from_col] = piece
            board[to_row][to_col] = target
            piece.position = old_position
            
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Cắt tỉa beta
        
        return max_eval
    
    # Nếu đang tối thiểu hóa (lượt của người chơi đen)
    else:
        min_eval = float('inf')
        for from_pos, to_pos in valid_moves:
            # Thực hiện nước đi
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            piece = board[from_row][from_col]
            target = board[to_row][to_col]
            
            board[to_row][to_col] = piece
            board[from_row][from_col] = 0
            old_position = piece.position
            piece.position = (to_row, to_col)
            
            # Gọi đệ quy minimax cho đối thủ
            opponent_color = BLACK if player_color == RED else RED
            eval = minimax(board, depth - 1, alpha, beta, True, opponent_color)
            
            # Khôi phục nước đi
            board[from_row][from_col] = piece
            board[to_row][to_col] = target
            piece.position = old_position
            
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Cắt tỉa alpha
        
        return min_eval

def find_best_move_minimax(board, player_color, depth=3):
    """Tìm nước đi tốt nhất sử dụng thuật toán Minimax với Alpha-Beta"""
    valid_moves = get_valid_moves(board, player_color)
    
    # Không còn nước đi hợp lệ
    if not valid_moves:
        return None
    
    best_move = None
    
    # Đỏ tối đa hóa điểm, đen tối thiểu hóa điểm
    if player_color == RED:
        best_value = float('-inf')
        for from_pos, to_pos in valid_moves:
            # Thực hiện nước đi
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            piece = board[from_row][from_col]
            target = board[to_row][to_col]
            
            board[to_row][to_col] = piece
            board[from_row][from_col] = 0
            old_position = piece.position
            piece.position = (to_row, to_col)
            
            # Đánh giá
            value = minimax(board, depth - 1, float('-inf'), float('inf'), False, BLACK)
            
            # Khôi phục nước đi
            board[from_row][from_col] = piece
            board[to_row][to_col] = target
            piece.position = old_position
            
            if value > best_value:
                best_value = value
                best_move = (from_pos, to_pos)
    else:
        best_value = float('inf')
        for from_pos, to_pos in valid_moves:
            # Thực hiện nước đi
            from_row, from_col = from_pos
            to_row, to_col = to_pos
            piece = board[from_row][from_col]
            target = board[to_row][to_col]
            
            board[to_row][to_col] = piece
            board[from_row][from_col] = 0
            old_position = piece.position
            piece.position = (to_row, to_col)
            
            # Đánh giá
            value = minimax(board, depth - 1, float('-inf'), float('inf'), True, RED)
            
            # Khôi phục nước đi
            board[from_row][from_col] = piece
            board[to_row][to_col] = target
            piece.position = old_position
            
            if value < best_value:
                best_value = value
                best_move = (from_pos, to_pos)
    
    return best_move

# Triển khai BFS đơn giản cho cấp độ Dễ
def find_best_move_bfs(board, player_color):
    """Tìm nước đi sử dụng BFS đơn giản - ưu tiên ăn quân có giá trị cao"""
    valid_moves = get_valid_moves(board, player_color)
    
    if not valid_moves:
        return None
    
    # Sắp xếp nước đi theo giá trị quân bị ăn
    valued_moves = []
    for from_pos, to_pos in valid_moves:
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        target = board[to_row][to_col]
        
        # Giá trị của nước đi dựa trên quân bị ăn
        if target != 0 and target.color != player_color:
            piece_type = target.__class__.__name__
            value = PIECE_VALUES.get(piece_type, 0)
            valued_moves.append((from_pos, to_pos, value))
        else:
            # Nước đi không ăn quân nào
            valued_moves.append((from_pos, to_pos, 0))
    
    # Sắp xếp theo giá trị, ưu tiên nước ăn quân có giá trị cao
    valued_moves.sort(key=lambda x: x[2], reverse=True)
    
    # Nếu có nước ăn quân, chọn nước ăn quân có giá trị cao nhất
    if valued_moves and valued_moves[0][2] > 0:
        return (valued_moves[0][0], valued_moves[0][1])
    
    # Nếu không có nước ăn quân, chọn ngẫu nhiên trong số các nước có thể
    return (valued_moves[0][0], valued_moves[0][1]) if valued_moves else None

# Monte Carlo Tree Search - phiên bản đơn giản
class MCTSNode:
    def __init__(self, board, player_color, parent=None, move=None):
        self.board = board
        self.player_color = player_color
        self.parent = parent
        self.move = move  # Nước đi dẫn đến trạng thái này
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = get_valid_moves(board, player_color)
    
    def select_child(self):
        """Chọn con có UCB1 cao nhất"""
        import math
        
        # Chọn con có UCB1 cao nhất
        s = sorted(self.children, key=lambda c: c.wins/c.visits + 1.41 * math.sqrt(math.log(self.visits)/c.visits))
        return s[-1]
    
    def expand(self):
        """Mở rộng node hiện tại bằng cách thêm một con mới"""
        if not self.untried_moves:
            return None
        
        # Chọn ngẫu nhiên một nước đi chưa thử
        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)
        
        # Tạo bàn cờ mới
        new_board = [row[:] for row in self.board]
        from_pos, to_pos = move
        from_row, from_col = from_pos
        to_row, to_col = to_pos
        piece = new_board[from_row][from_col]
        new_board[to_row][to_col] = piece
        new_board[from_row][from_col] = 0
        
        # Tạo node con
        opponent_color = BLACK if self.player_color == RED else RED
        child = MCTSNode(new_board, opponent_color, self, move)
        self.children.append(child)
        return child
    
    def update(self, result):
        """Cập nhật kết quả sau khi mô phỏng"""
        self.visits += 1
        self.wins += result
        
def find_best_move_mcts(board, player_color, simulations=1000, max_time=5):
    """Tìm nước đi tốt nhất sử dụng Monte Carlo Tree Search"""
    # Do MCTS cần triển khai phức tạp, chúng ta chỉ mô phỏng phần cơ bản
    return find_best_move_minimax(board, player_color, depth=2)

def make_ai_move(board, current_player, level="medium"):
    """
    Hàm AI chọn nước đi tốt nhất dựa trên độ khó
    """
    # Sẽ triển khai sau
    pass

class ChineseChessAI:
    def __init__(self):
        self.difficulty = "medium"
        self.max_depth = 3  # Giá trị mặc định cho độ sâu
        self.piece_values = {
            '将': 10000, '帅': 10000,  # Tướng
            '士': 200, '仕': 200,      # Sĩ
            '象': 200, '相': 200,      # Tượng
            '马': 450, '傌': 450,      # Mã
            '车': 900, '俥': 900,      # Xe
            '炮': 450, '砲': 450,      # Pháo
            '卒': 100, '兵': 100       # Tốt
        }
        
    def set_difficulty(self, level):
        """Thiết lập độ khó cho AI"""
        self.difficulty = level
        if level == "easy":
            self.max_depth = 2
        elif level == "medium":
            self.max_depth = 3
        else:  # hard
            self.max_depth = 4
            
    def get_best_move(self, board, current_player, difficulty=None):
        """Trả về nước đi tốt nhất dựa trên các thuật toán AI"""
        if difficulty:
            self.set_difficulty(difficulty)
            
        # Tùy thuộc vào độ khó, chọn thuật toán phù hợp
        if self.difficulty == "easy":
            return self._get_random_move(board, current_player)
        else:
            return self._get_minimax_move(board, current_player, self.max_depth)
            
    def _get_random_move(self, board, player):
        """Trả về một nước đi ngẫu nhiên hợp lệ"""
        import random
        
        # Tìm tất cả quân cờ của người chơi hiện tại
        player_pieces = []
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ':
                    # Kiểm tra màu sắc của quân cờ
                    is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
                    if (player.red() > 0 and is_red) or (player.red() == 0 and not is_red):
                        player_pieces.append((row, col))
        
        # Trộn danh sách các quân cờ để tạo tính ngẫu nhiên
        random.shuffle(player_pieces)
        
        # Thử lần lượt mỗi quân cờ cho đến khi tìm được nước đi hợp lệ
        for start_pos in player_pieces:
            start_row, start_col = start_pos
            piece = board[start_row][start_col]
            
            # Tạo danh sách các vị trí đích tiềm năng
            potential_end_positions = []
            for end_row in range(10):
                for end_col in range(9):
                    # Kiểm tra xem nước đi có hợp lệ không
                    if (end_row, end_col) != start_pos and piece.is_valid_move(board, start_pos, (end_row, end_col)):
                        # Kiểm tra nước đi không gây ra tự chiếu tướng
                        if not self._causes_self_check(board, start_row, start_col, end_row, end_col, player):
                            potential_end_positions.append((end_row, end_col))
            
            # Nếu có vị trí đích hợp lệ, chọn ngẫu nhiên một vị trí
            if potential_end_positions:
                end_pos = random.choice(potential_end_positions)
                return (start_pos, end_pos)
                
        # Nếu không tìm thấy nước đi hợp lệ
        return None

    def _is_valid_move(self, board, start_row, start_col, end_row, end_col, player):
        """Kiểm tra nước đi có hợp lệ không"""
        # Kiểm tra vị trí bắt đầu có quân cờ không
        piece = board[start_row][start_col]
        if piece == 0 or piece == ' ':
            return False
            
        # Kiểm tra quân cờ có đúng màu không
        is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
        if (player.red() > 0 and not is_red) or (player.red() == 0 and is_red):
            return False
            
        # Kiểm tra nước đi có hợp lệ theo luật chơi không
        if not piece.is_valid_move(board, (start_row, start_col), (end_row, end_col)):
            return False
            
        # Kiểm tra nước đi không gây ra tự chiếu tướng
        return not self._causes_self_check(board, start_row, start_col, end_row, end_col, player)
        
    def _causes_self_check(self, board, start_row, start_col, end_row, end_col, player):
        """Kiểm tra nước đi có gây ra tự chiếu tướng không"""
        # Lưu trạng thái hiện tại
        piece = board[start_row][start_col]
        target = board[end_row][end_col]
        
        # Thực hiện nước đi tạm thời
        board[end_row][end_col] = piece
        board[start_row][start_col] = 0
        original_position = piece.position
        piece.position = (end_row, end_col)
        
        # Kiểm tra tướng có bị chiếu không
        is_check = self._is_in_check(board, player)
        
        # Khôi phục trạng thái ban đầu
        board[start_row][start_col] = piece
        board[end_row][end_col] = target
        piece.position = original_position
        
        return is_check
        
    def _is_in_check(self, board, player):
        """Kiểm tra một người chơi có đang bị chiếu tướng không"""
        # Tìm vị trí tướng
        general_pos = None
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ' and hasattr(piece, '__class__'):
                    is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
                    if piece.__class__.__name__ == "General" and ((player.red() > 0 and is_red) or (player.red() == 0 and not is_red)):
                        general_pos = (row, col)
                        break
            if general_pos:
                break
        
        # Nếu không tìm thấy tướng, trả về True (giả định là đã thua)
        if not general_pos:
            return True
        
        # Tìm một đối tượng quân cờ để lấy lớp màu sắc
        color_class = None
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ' and hasattr(piece, 'color') and hasattr(piece.color, '__class__'):
                    color_class = piece.color.__class__
                    break
            if color_class:
                break
                
        # Nếu không tìm được lớp màu sắc, trả về False
        if not color_class:
            return False
            
        # Tạo đối tượng màu đối thủ
        opponent_color = color_class(0, 0, 0) if player.red() > 0 else color_class(255, 0, 0)
        
        # Kiểm tra xem có quân nào của đối phương có thể ăn tướng không
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ' and hasattr(piece, 'color'):
                    is_opponent = (player.red() > 0 and piece.color.red() == 0) or (player.red() == 0 and piece.color.red() > 0)
                    if is_opponent and piece.is_valid_move(board, (row, col), general_pos):
                        return True
        
        return False
        
    def _get_minimax_move(self, board, player, depth):
        """Sử dụng thuật toán minimax với cắt tỉa alpha-beta để tìm nước đi tốt nhất"""
        best_move = None
        best_value = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        
        # Tìm tất cả các nước đi hợp lệ
        valid_moves = self._get_all_valid_moves(board, player)
        
        # Nếu không có nước đi hợp lệ, trả về None
        if not valid_moves:
            return None
        
        for start_pos, end_pos in valid_moves:
            # Thực hiện nước đi trên bản sao của bàn cờ
            temp_board = self._make_move_on_copy(board, start_pos, end_pos)
            
            # Đánh giá giá trị của nước đi bằng minimax
            move_value = self._minimax(temp_board, depth-1, alpha, beta, False, player)
            
            # Cập nhật nước đi tốt nhất
            if move_value > best_value:
                best_value = move_value
                best_move = (start_pos, end_pos)
                
            alpha = max(alpha, best_value)
        
        # Kiểm tra xem best_move có phải là None không
        return best_move
        
    def _minimax(self, board, depth, alpha, beta, is_maximizing, original_player):
        """Thuật toán minimax với cắt tỉa alpha-beta"""
        # Điều kiện dừng
        if depth == 0 or self._is_game_over(board):
            return self._evaluate_board(board, original_player)
            
        current_player = original_player if is_maximizing else self._get_opponent(original_player)
        
        if is_maximizing:
            best_value = float('-inf')
            valid_moves = self._get_all_valid_moves(board, current_player)
            
            for start_pos, end_pos in valid_moves:
                temp_board = self._make_move_on_copy(board, start_pos, end_pos)
                value = self._minimax(temp_board, depth-1, alpha, beta, False, original_player)
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break  # Cắt tỉa beta
            return best_value
        else:
            best_value = float('inf')
            valid_moves = self._get_all_valid_moves(board, current_player)
            
            for start_pos, end_pos in valid_moves:
                temp_board = self._make_move_on_copy(board, start_pos, end_pos)
                value = self._minimax(temp_board, depth-1, alpha, beta, True, original_player)
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if beta <= alpha:
                    break  # Cắt tỉa alpha
            return best_value
            
    def _evaluate_board(self, board, player):
        """Đánh giá trạng thái bàn cờ từ góc nhìn của player"""
        score = 0
        
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ' and hasattr(piece, '__class__'):
                    piece_type = piece.__class__.__name__
                    is_red = hasattr(piece.color, 'red') and piece.color.red() > 0
                    
                    # Lấy giá trị cơ bản của quân cờ
                    value = 0
                    if piece_type == "General":
                        value = 10000
                    elif piece_type == "Advisor":
                        value = 200
                    elif piece_type == "Elephant":
                        value = 200
                    elif piece_type == "Horse":
                        value = 450
                    elif piece_type == "Chariot":
                        value = 900
                    elif piece_type == "Cannon":
                        value = 450
                    elif piece_type == "Soldier":
                        # Tốt qua sông giá trị tăng lên
                        if (is_red and row < 5) or (not is_red and row > 4):
                            value = 200
                        else:
                            value = 100
                    
                    # Thêm giá trị vị trí nếu có
                    if piece_type in POSITION_VALUES:
                        # Với quân đen, đảo ngược bảng vị trí
                        if is_red:
                            position_value = POSITION_VALUES[piece_type][row][col]
                        else:
                            position_value = POSITION_VALUES[piece_type][9-row][col]
                        value += position_value * 10  # Nhân 10 để tăng tầm quan trọng của vị trí
                    
                    # Cộng hoặc trừ giá trị tùy thuộc vào màu quân cờ
                    if (player.red() > 0 and is_red) or (player.red() == 0 and not is_red):
                        score += value
                    else:
                        score -= value
                            
        return score
        
    def _get_all_valid_moves(self, board, player):
        """Trả về tất cả các nước đi hợp lệ của player"""
        valid_moves = []
        
        for start_row in range(10):
            for start_col in range(9):
                piece = board[start_row][start_col]
                if piece != 0 and piece != ' ' and hasattr(piece, 'color'):
                    # Kiểm tra xem quân cờ có thuộc về người chơi hiện tại không
                    is_player_piece = (player.red() > 0 and piece.color.red() > 0) or (player.red() == 0 and piece.color.red() == 0)
                    
                    if is_player_piece:
                        # Tìm các vị trí đích hợp lệ
                        for end_row in range(10):
                            for end_col in range(9):
                                if (end_row, end_col) != (start_row, start_col) and piece.is_valid_move(board, (start_row, start_col), (end_row, end_col)):
                                    # Kiểm tra nước đi không gây ra tự chiếu tướng
                                    if not self._causes_self_check(board, start_row, start_col, end_row, end_col, player):
                                        valid_moves.append(((start_row, start_col), (end_row, end_col)))
                                    
        return valid_moves
        
    def _make_move_on_copy(self, board, start_pos, end_pos):
        """Tạo bản sao của bàn cờ và thực hiện nước đi"""
        import copy
        
        # Tạo bản sao sâu của bàn cờ
        board_copy = copy.deepcopy(board)
        
        start_row, start_col = start_pos
        end_row, end_col = end_pos
        
        # Thực hiện nước đi
        board_copy[end_row][end_col] = board_copy[start_row][start_col]
        board_copy[start_row][start_col] = 0
        
        # Cập nhật vị trí của quân cờ
        board_copy[end_row][end_col].position = (end_row, end_col)
        
        return board_copy
        
    def _get_opponent(self, player):
        """Trả về đối thủ của người chơi"""
        if player.red() > 0:
            # Nếu player là RED, trả về BLACK
            return player.__class__(0, 0, 0)  # Màu đen
        else:
            # Nếu player là BLACK, trả về RED
            return player.__class__(255, 0, 0)  # Màu đỏ
            
    def _is_game_over(self, board):
        """Kiểm tra xem trò chơi đã kết thúc chưa (một trong hai tướng bị bắt)"""
        red_general_exists = False
        black_general_exists = False
        
        # Kiểm tra xem cả hai tướng có còn trên bàn cờ không
        for row in range(10):
            for col in range(9):
                piece = board[row][col]
                if piece != 0 and piece != ' ' and hasattr(piece, '__class__'):
                    if piece.__class__.__name__ == "General":
                        if hasattr(piece.color, 'red') and piece.color.red() > 0:
                            red_general_exists = True
                        else:
                            black_general_exists = True
                        
                        if red_general_exists and black_general_exists:
                            return False  # Trò chơi chưa kết thúc
        
        # Nếu một trong hai tướng không còn, trò chơi kết thúc
        return True
