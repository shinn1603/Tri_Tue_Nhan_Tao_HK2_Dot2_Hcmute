# -*- coding: utf-8 -*-
"""
local_beam_solver.py
Cài đặt thuật toán Local Beam Search giải Sudoku.
"""
import copy
import random
from sudoku_utils import SIZE, count_conflicts

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



class LocalBeamSolver:
    def __init__(self, puzzle, k=5, max_steps=1000):
        self.puzzle = copy.deepcopy(puzzle)
        self.k = k
        self.max_steps = max_steps
        self.steps = []
        self.is_clue = [[puzzle[r][c] != 0 for c in range(SIZE)] for r in range(SIZE)]

    def _init_random_board(self):
        board = copy.deepcopy(self.puzzle)
        for r in range(SIZE):
            existing = set(board[r])
            missing = [n for n in range(1, 10) if n not in existing]
            random.shuffle(missing)
            idx = 0
            for c in range(SIZE):
                if board[r][c] == 0:
                    board[r][c] = missing[idx]
                    idx += 1
        return board

    def _empty_cols_in_row(self, row):
        return [c for c in range(SIZE) if not self.is_clue[row][c]]

    def solve(self):
        rows_with_freedom = [r for r in range(SIZE) if len(self._empty_cols_in_row(r)) >= 2]
        
        if not rows_with_freedom:
            current = self._init_random_board()
            current_h = count_conflicts(current)
            stats = {'steps': 0}
            return (current if current_h == 0 else None), self.steps, stats

        # Khởi tạo k trạng thái
        k_states = []
        for _ in range(self.k):
            b = self._init_random_board()
            k_states.append((count_conflicts(b), b))
            
        k_states.sort(key=lambda x: x[0])
        best_h, best_board = k_states[0]
        
        step_count = 0
        while step_count < self.max_steps and best_h > 0:
            step_count += 1
            
            all_neighbors = []
            
            # Sinh tất cả neighbor của cả k trạng thái
            for h, state in k_states:
                for row in rows_with_freedom:
                    cols = self._empty_cols_in_row(row)
                    for i in range(len(cols)):
                        for j in range(i + 1, len(cols)):
                            c1, c2 = cols[i], cols[j]
                            neighbor = copy.deepcopy(state)
                            neighbor[row][c1], neighbor[row][c2] = neighbor[row][c2], neighbor[row][c1]
                            neighbor_h = count_conflicts(neighbor)
                            all_neighbors.append((neighbor_h, neighbor))
                            
            # Tránh trùng lặp (nếu cần) hoặc lấy trực tiếp
            # Sắp xếp và lấy k neighbor tốt nhất
            all_neighbors.sort(key=lambda x: x[0])
            next_k_states = all_neighbors[:self.k]
            
            new_best_h, new_best_board = next_k_states[0]
            
            # Nếu chùm k không cải thiện gì (ví dụ toàn kẹt), có thể stop hoặc tiếp tục
            # Ở đây ta cứ gán và cập nhật
            k_states = next_k_states
            
            if new_best_h < best_h:
                self.steps.append(SearchStep(new_best_board, -1, -1, -1, 'beam_update', detail=f"Beam Search: Chọn k states tốt nhất. Best H={new_best_h}", new_best_h=new_best_h))
            else:
                self.steps.append(SearchStep(new_best_board, -1, -1, -1, 'stuck', detail=f"Các beam kẹt tại Local Optimum (Best H={new_best_h}).", new_best_h=new_best_h))
                break # Kẹt hoàn toàn
                
            best_h = new_best_h
            best_board = new_best_board
            
        stats = {'steps': step_count}
        return (best_board if best_h == 0 else None), self.steps, stats
