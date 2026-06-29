# -*- coding: utf-8 -*-
"""
dfs_solver.py
Cài đặt thuật toán Depth-First Search (DFS) để giải Sudoku.
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



class DFSSolver:
    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def solve(self):
        stack = [self.puzzle]
        
        while stack:
            board = stack.pop()
            self.nodes_expanded += 1
            
            empties = find_empty_cells(board)
            if not empties:
                stats = {
                    'nodes_expanded': self.nodes_expanded,
                    'total_steps_recorded': len(self.steps),
                }
                return board, self.steps, stats
                
            row, col = empties[0]
            
            # DFS thường thêm vào stack theo thứ tự ngược để duyệt xuôi,
            # hoặc đơn giản thử 9->1 để khi pop ra nó là 1->9.
            for num in range(9, 0, -1):
                if is_valid(board, row, col, num):
                    new_board = copy.deepcopy(board)
                    new_board[row][col] = num
                    self.steps.append(SearchStep(new_board, row, col, num, 'try', detail=f"Frontier (Stack) size: {len(stack)}. Pop State, đánh dấu Explored. Mở rộng ({row},{col}) = {num}."))
                    stack.append(new_board)
                    
        stats = {
            'nodes_expanded': self.nodes_expanded,
            'total_steps_recorded': len(self.steps),
        }
        return None, self.steps, stats
