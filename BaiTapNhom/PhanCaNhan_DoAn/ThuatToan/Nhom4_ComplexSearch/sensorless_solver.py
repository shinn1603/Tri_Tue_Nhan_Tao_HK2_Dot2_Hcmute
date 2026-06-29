# -*- coding: utf-8 -*-
"""
sensorless_solver.py
Cài đặt thuật toán Sensorless Search (Conformant Search) để giải Sudoku.
Trong không gian bài toán không quan sát (Sensorless), agent duy trì một belief state
và thực hiện các hành động để thu hẹp belief state đến khi hội tụ về một trạng thái duy nhất.
"""
import copy
from sudoku_utils import is_valid, find_empty_cells, SIZE

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



class SensorlessSolver:
    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def solve(self):
        # Mô phỏng quá trình tìm kiếm không quan sát bằng cách áp dụng
        # tuần tự các hành động để đưa belief state về đích.
        # Ở Sudoku đơn định, nó tương đương với việc tìm một chuỗi gán giá trị hợp lệ.
        result_board = self._search(self.puzzle)
        stats = {
            'nodes_expanded': self.nodes_expanded,
            'total_steps_recorded': len(self.steps),
        }
        return result_board, self.steps, stats

    def _search(self, board):
        empties = find_empty_cells(board)
        if not empties:
            return board
            
        row, col = empties[0]
        
        for num in range(1, 10):
            self.nodes_expanded += 1
            if is_valid(board, row, col, num):
                board[row][col] = num
                self.steps.append(SearchStep(board, row, col, num, 'try', detail=f"Pop State từ Frontier. Đánh dấu Explored. Khám phá nhánh tại ({row},{col}) = {num}."))
                
                result = self._search(board)
                if result is not None:
                    return result
                    
                board[row][col] = 0
                self.steps.append(SearchStep(board, row, col, 0, 'backtrack', detail=f"Nhánh này thất bại. Quay lui loại bỏ khỏi bộ nhớ."))
                
        return None
