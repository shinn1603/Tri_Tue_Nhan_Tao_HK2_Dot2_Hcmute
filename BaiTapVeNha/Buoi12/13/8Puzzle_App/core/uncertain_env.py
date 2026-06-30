import numpy as np
from itertools import permutations
from .puzzle_state import check_solvable, Find_blank, get_move, action

# Hằng số đánh dấu vòng lặp (khi trượt quay về trạng thái cũ → thử lại)
LOOP_MARKER = "LOOP"

class BeliefStateProblem:
    """
    Xử lý bài toán Không gian Niềm tin (Belief State) cho 8-Puzzle.
    Khi đầu vào có ô '*' (không xác định), lớp này sinh ra tất cả
    các trạng thái hợp lệ có thể và hỗ trợ Conformant Search.
    """
    def __init__(self, input_grid, target):
        self.target = target
        self.target_tuple = tuple(target.flatten())
        self.initial_belief = self._generate_belief_states(input_grid)
    
    def _generate_belief_states(self, input_grid):
        star_positions = []
        known_values = set()
        
        for i, val in enumerate(input_grid):
            if val == '*':
                star_positions.append(i)
            else:
                known_values.add(int(val))
        
        all_values = set(range(9))
        missing_values = list(all_values - known_values)
        
        states = set()
        for perm in permutations(missing_values):
            grid = list(input_grid)
            for idx, pos in enumerate(star_positions):
                grid[pos] = perm[idx]
            
            arr = np.array(grid, dtype=int).reshape(3, 3)
            if check_solvable(arr, self.target):
                states.add(tuple(arr.flatten()))
        
        return frozenset(states)
    
    def apply_action_to_belief(self, belief, action_name):
        new_states = set()
        for state_tuple in belief:
            state = np.array(state_tuple).reshape(3, 3)
            blank = Find_blank(state)
            if blank is None:
                new_states.add(state_tuple)
                continue
            row, col = blank
            valid_moves = get_move(row, col)
            
            if action_name in valid_moves:
                new_state, _, _ = action(state, action_name, row, col)
                new_states.add(tuple(new_state.flatten()))
            else:
                new_states.add(state_tuple)
        
        return frozenset(new_states)
    
    def is_goal(self, belief):
        for state_tuple in belief:
            if state_tuple != self.target_tuple:
                return False
        return True

class NonDeterministicPuzzle:
    """
    Mô phỏng môi trường trơn trượt (hoặc gạch bị kẹt) cho 8-Puzzle.
    Khi chọn một hành động:
      - Thành công: đi đúng hướng
      - Thất bại: gạch bị kẹt, giữ nguyên vị trí cũ (trạng thái không đổi)
    """
    def __init__(self, target):
        self.target = target
        self.target_tuple = tuple(target.flatten())
    
    def results(self, state_tuple, action_name):
        state = np.array(state_tuple).reshape(3, 3)
        blank = Find_blank(state)
        if blank is None:
            return [state_tuple]
        row, col = blank
        valid_moves = get_move(row, col)
        
        results_set = set()
        
        if action_name in valid_moves:
            new_state, _, _ = action(state, action_name, row, col)
            results_set.add(tuple(new_state.flatten()))
        else:
            results_set.add(state_tuple)
        
        results_set.add(state_tuple)
        
        return list(results_set)
    
    def is_goal(self, state_tuple):
        return state_tuple == self.target_tuple
