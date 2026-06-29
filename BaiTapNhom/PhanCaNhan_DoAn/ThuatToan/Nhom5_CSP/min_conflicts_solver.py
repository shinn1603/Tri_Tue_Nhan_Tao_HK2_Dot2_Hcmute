# -*- coding: utf-8 -*-
"""
min_conflicts_solver.py
Cài đặt thuật toán Min-Conflicts cho CSP để giải Sudoku.
"""
import copy
import random
from sudoku_utils import SIZE, BOX, count_conflicts

class SearchStep:
    def __init__(self, board, row, col, value, action_type, detail="", **kwargs):
        import copy
        self.board = copy.deepcopy(board)
        self.row = row
        self.col = col
        self.value = value
        self.action_type = action_type
        self.detail = detail
        for k, v in kwargs.items():
            setattr(self, k, v)



class MinConflictsSolver:
    def __init__(self, puzzle, max_steps=5000):
        self.puzzle = copy.deepcopy(puzzle)
        self.max_steps = max_steps
        self.steps = []
        self.is_clue = [[puzzle[r][c] != 0 for c in range(SIZE)] for r in range(SIZE)]

    def _init_random_board(self):
        board = copy.deepcopy(self.puzzle)
        for r in range(SIZE):
            for c in range(SIZE):
                if not self.is_clue[r][c]:
                    board[r][c] = random.randint(1, 9)
        return board
        
    def _get_conflicted_variables(self, board):
        conflicts = []
        for r in range(SIZE):
            for c in range(SIZE):
                if not self.is_clue[r][c]:
                    if self._conflicts_for_cell(board, r, c) > 0:
                        conflicts.append((r, c))
        return conflicts
        
    def _conflicts_for_cell(self, board, row, col):
        val = board[row][col]
        conflicts = 0
        for i in range(SIZE):
            if i != col and board[row][i] == val:
                conflicts += 1
            if i != row and board[i][col] == val:
                conflicts += 1
        br, bc = (row // BOX) * BOX, (col // BOX) * BOX
        for r in range(br, br + BOX):
            for c in range(bc, bc + BOX):
                if (r != row or c != col) and board[r][c] == val:
                    conflicts += 1
        return conflicts

    def solve(self):
        current = self._init_random_board()
        self.steps.append(SearchStep(current, -1, -1, 0, 'new_iteration', detail=f"Khởi tạo bảng ngẫu nhiên. Số lỗi hiện tại: {count_conflicts(current)}"))
        
        for step_idx in range(self.max_steps):
            conflicted = self._get_conflicted_variables(current)
            if not conflicted:
                stats = {'steps': step_idx}
                return current, self.steps, stats
                
            r, c = random.choice(conflicted)
            
            min_c = float('inf')
            best_vals = []
            
            for v in range(1, 10):
                current[r][c] = v
                cnt = self._conflicts_for_cell(current, r, c)
                if cnt < min_c:
                    min_c = cnt
                    best_vals = [v]
                elif cnt == min_c:
                    best_vals.append(v)
            
            best_v = random.choice(best_vals)
            current[r][c] = best_v
            
            self.steps.append(SearchStep(current, r, c, best_v, 'try', detail=f"Min-Conflicts: Chọn biến conflict tại ({r},{c}). Đổi thành {best_v} để giảm lỗi."))
            
        # Hết max_steps mà vẫn chưa giải xong -> kẹt cục bộ
        return None, self.steps, {'steps': self.max_steps}

