# -*- coding: utf-8 -*-
import copy
import random
from sudoku_utils import SIZE, is_valid, find_empty_cells

class AlphaBetaSudokuBattle:
    """
    SUDOKU BATTLE (Luật Mới: ÉP ĐỐI THỦ GIẢI Ô CHỈ ĐỊNH) - Tối ưu với Alpha-Beta Pruning
    """
    def __init__(self, puzzle, real_solution, search_depth=2):
        self.puzzle = copy.deepcopy(puzzle)
        self.real_solution = real_solution
        self.board = copy.deepcopy(puzzle)
        self.search_depth = search_depth
        
        self.human_mistakes = 0
        self.agent_mistakes = 0
        self.nodes_evaluated = 0

    def get_empty_cells(self):
        return find_empty_cells(self.board)

    def is_game_over(self):
        if self.human_mistakes >= 5 or self.agent_mistakes >= 5:
            return True
        return len(self.get_empty_cells()) == 0

    def human_move(self, row, col, value):
        is_correct = (value == self.real_solution[row][col])
        if is_correct:
            self.board[row][col] = value
        else:
            self.human_mistakes += 1
        return is_correct

    def agent_move(self, row, col, value):
        is_correct = (value == self.real_solution[row][col])
        if is_correct:
            self.board[row][col] = value
        else:
            self.agent_mistakes += 1
        return is_correct

    def _hardness(self, board, r, c):
        return sum(1 for v in range(1, 10) if is_valid(board, r, c, v))

    def _alphabeta(self, board, depth, alpha, beta, is_max_turn):
        self.nodes_evaluated += 1
        empty_cells = find_empty_cells(board)
        if depth == 0 or not empty_cells:
            return 0

        if is_max_turn:
            best_val = float('-inf')
            for r, c in empty_cells:
                hardness = self._hardness(board, r, c)
                board[r][c] = self.real_solution[r][c]
                val = hardness + self._alphabeta(board, depth - 1, alpha, beta, False)
                board[r][c] = 0
                
                best_val = max(best_val, val)
                alpha = max(alpha, best_val)
                if beta <= alpha:
                    break
            return best_val
        else:
            best_val = float('inf')
            for r, c in empty_cells:
                hardness = self._hardness(board, r, c)
                board[r][c] = self.real_solution[r][c]
                val = -hardness + self._alphabeta(board, depth - 1, alpha, beta, True)
                board[r][c] = 0
                
                best_val = min(best_val, val)
                beta = min(beta, best_val)
                if beta <= alpha:
                    break
            return best_val

    def agent_choose_target(self):
        empty_cells = find_empty_cells(self.board)
        if not empty_cells:
            return None

        candidates = []
        for r, c in empty_cells:
            candidates.append((r, c, self._hardness(self.board, r, c)))
        
        candidates.sort(key=lambda x: x[2], reverse=True)
        candidates = candidates[:6]

        best_val = float('-inf')
        alpha = float('-inf')
        beta = float('inf')
        best_move = None
        trace = []

        for r, c, hardness in candidates:
            self.board[r][c] = self.real_solution[r][c]
            val = hardness + self._alphabeta(self.board, self.search_depth - 1, alpha, beta, False)
            self.board[r][c] = 0
            
            trace.append({'row': r, 'col': c, 'score': val, 'hardness': hardness, 'alpha': alpha, 'beta': beta})
            if val > best_val:
                best_val = val
                best_move = (r, c)
            alpha = max(alpha, best_val)
                
        if best_move is None:
            best_move = (candidates[0][0], candidates[0][1])

        nodes = self.nodes_evaluated
        self.nodes_evaluated = 0
        return best_move[0], best_move[1], trace, nodes
