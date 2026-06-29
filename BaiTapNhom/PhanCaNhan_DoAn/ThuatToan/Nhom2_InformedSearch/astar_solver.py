# -*- coding: utf-8 -*-
"""
astar_solver.py
Cài đặt thuật toán A* Search để giải Sudoku.
f(n) = g(n) + h(n)
g(n) = số ô đã điền
h(n) = heuristic_min_conflicts_domain(board)
"""
import copy
import heapq
from sudoku_utils import is_valid, find_empty_cells, heuristic_min_conflicts_domain, SIZE

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



class AStarSolver:
    def __init__(self, puzzle):
        self.puzzle = copy.deepcopy(puzzle)
        self.steps = []
        self.nodes_expanded = 0

    def solve(self):
        pq = []
        # g = 0
        h_initial = heuristic_min_conflicts_domain(self.puzzle)
        heapq.heappush(pq, (0 + h_initial, 0, self.puzzle, 0)) # (f, counter, board, g)
        counter = 1
        
        while pq:
            f, _, board, g = heapq.heappop(pq)
            self.nodes_expanded += 1
            
            empties = find_empty_cells(board)
            if not empties:
                stats = {'nodes_expanded': self.nodes_expanded, 'total_steps': len(self.steps)}
                return board, self.steps, stats
                
            row, col = empties[0]
            
            for num in range(1, 10):
                if is_valid(board, row, col, num):
                    new_board = copy.deepcopy(board)
                    new_board[row][col] = num
                    self.steps.append(SearchStep(new_board, row, col, num, 'try', detail=f"Frontier (Priority Queue) size: {len(pq)}. Pop best node. Đánh dấu Explored. Thử ({row},{col}) = {num}."))
                    
                    new_g = g + 1
                    new_h = heuristic_min_conflicts_domain(new_board)
                    new_f = new_g + new_h
                    
                    heapq.heappush(pq, (new_f, counter, new_board, new_g))
                    counter += 1
                    
        return None, self.steps, {'nodes_expanded': self.nodes_expanded}
