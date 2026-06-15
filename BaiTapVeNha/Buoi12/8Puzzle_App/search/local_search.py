import random
import numpy as np
from core.puzzle_state import NODE, Find_blank, get_move, action, pathcost

def hill_climbing_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    row, col = Find_blank(puzzle)
    current_node = NODE(puzzle, None, None, row, col)
    explored = {tuple(puzzle.flatten())}
    
    while is_searching_func():
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 10 == 0: stats["memory"] = len(explored)

        current_h = pathcost(current_node.state, target)
        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Xét đỉnh hiện tại (h={current_h})")

        if np.array_equal(current_node.state, target):
            return current_node

        found_better = False
        for move in get_move(current_node.row, current_node.col):
            new_puzzle, new_r, new_c = action(current_node.state, move, current_node.row, current_node.col)
            state_tuple = tuple(new_puzzle.flatten())
            if state_tuple not in explored:
                new_h = pathcost(new_puzzle, target)
                if new_h < current_h:
                    explored.add(state_tuple)
                    current_node = NODE(new_puzzle, current_node, move, new_r, new_c)
                    found_better = True
                    if show_log and log_callback: log_callback(f"  + Áp dụng hướng {move} (h={new_h} < {current_h})\n")
                    break 
        
        if not found_better:
            if log_callback: log_callback(f"Trạng thái cực đại cục bộ. Hủy bỏ thuật toán.")
            return None

def steepest_ascent_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    row, col = Find_blank(puzzle)
    current_node = NODE(puzzle, None, None, row, col)
    explored = {tuple(puzzle.flatten())}

    while is_searching_func():
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 10 == 0: stats["memory"] = len(explored)

        current_h = pathcost(current_node.state, target)
        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Xét đỉnh hiện tại (h={current_h})")

        if np.array_equal(current_node.state, target):
            return current_node

        best_move = None
        best_node = None
        best_h = current_h 

        for move in get_move(current_node.row, current_node.col):
            new_puzzle, new_r, new_c = action(current_node.state, move, current_node.row, current_node.col)
            state_tuple = tuple(new_puzzle.flatten())
            if state_tuple not in explored:
                new_h = pathcost(new_puzzle, target)
                if new_h < best_h:
                    best_h = new_h
                    best_move = move
                    best_node = NODE(new_puzzle, current_node, move, new_r, new_c)

        if best_node is not None:
            explored.add(tuple(best_node.state.flatten()))
            current_node = best_node
            if show_log and log_callback: log_callback(f"  + Áp dụng hướng tối ưu {best_move} (h={best_h})\n")
        else:
            if log_callback: log_callback(f"Trạng thái cực đại cục bộ. Hủy bỏ thuật toán.")
            return None

def stochastic_hill_climbing_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    row, col = Find_blank(puzzle)
    current_node = NODE(puzzle, None, None, row, col)
    explored = {tuple(puzzle.flatten())}

    while is_searching_func():
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 10 == 0: stats["memory"] = len(explored)

        current_h = pathcost(current_node.state, target)
        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Xét đỉnh (h={current_h})")

        if np.array_equal(current_node.state, target):
            return current_node

        better_neighbors = []
        for move in get_move(current_node.row, current_node.col):
            new_puzzle, new_r, new_c = action(current_node.state, move, current_node.row, current_node.col)
            state_tuple = tuple(new_puzzle.flatten())

            if state_tuple not in explored:
                new_h = pathcost(new_puzzle, target)
                if new_h < current_h:
                    better_neighbors.append((new_h, move, NODE(new_puzzle, current_node, move, new_r, new_c)))

        if better_neighbors:
            chosen_h, chosen_move, chosen_node = random.choice(better_neighbors)
            explored.add(tuple(chosen_node.state.flatten()))
            current_node = chosen_node
            if show_log and log_callback: log_callback(f"  + Chọn ngẫu nhiên hướng {chosen_move} (h={chosen_h})\n")
        else:
            if log_callback: log_callback(f"Trạng thái cực đại cục bộ. Hủy bỏ thuật toán.")
            return None

def random_restart_hill_climbing_search(puzzle, target, max_nodes=50000, max_restarts=10, log_callback=None, stats=None, is_searching_func=lambda: True):
    row, col = Find_blank(puzzle)
    current_node = NODE(puzzle, None, None, row, col)
    explored = {tuple(puzzle.flatten())}
    restarts = 0

    while is_searching_func():
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 10 == 0: stats["memory"] = len(explored)

        current_h = pathcost(current_node.state, target)
        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Xét đỉnh (h={current_h})")

        if np.array_equal(current_node.state, target):
            return current_node

        best_move = None
        best_node = None
        best_h = current_h 

        for move in get_move(current_node.row, current_node.col):
            new_puzzle, new_r, new_c = action(current_node.state, move, current_node.row, current_node.col)
            state_tuple = tuple(new_puzzle.flatten())
            if state_tuple not in explored:
                new_h = pathcost(new_puzzle, target)
                if new_h < best_h:
                    best_h = new_h
                    best_move = move
                    best_node = NODE(new_puzzle, current_node, move, new_r, new_c)

        if best_node is not None:
            explored.add(tuple(best_node.state.flatten()))
            current_node = best_node
            if show_log and log_callback: log_callback(f"  + Áp dụng hướng {best_move} (h={best_h})\n")
        else:
            restarts += 1
            if restarts <= max_restarts:
                if log_callback: log_callback(f"-> Cực đại cục bộ. Khởi động vòng lặp ngẫu nhiên (Lần {restarts})")
                for _ in range(5):
                    valid_moves = get_move(current_node.row, current_node.col)
                    r_move = random.choice(valid_moves)
                    n_puz, n_r, n_c = action(current_node.state, r_move, current_node.row, current_node.col)
                    current_node = NODE(n_puz, current_node, r_move, n_r, n_c)
                    explored.add(tuple(n_puz.flatten()))
            else:
                if log_callback: log_callback(f"Vượt quá giới hạn lặp lại. Hủy bỏ thuật toán.")
                return None

def local_beam_search(puzzle, target, max_nodes=50000, k=3, log_callback=None, stats=None, is_searching_func=lambda: True):
    row, col = Find_blank(puzzle)
    start_node = NODE(puzzle, None, None, row, col)
    
    beam = [start_node]
    explored = {tuple(puzzle.flatten())}
    
    while beam and is_searching_func():
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 10 == 0: stats["memory"] = len(explored)

        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Số trạng thái duy trì: {len(beam)}")

        next_candidates = []
        for cur_node in beam:
            if np.array_equal(cur_node.state, target):
                return cur_node

            for move in get_move(cur_node.row, cur_node.col):
                new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
                state_tuple = tuple(new_puzzle.flatten())
                
                if state_tuple not in explored:
                    explored.add(state_tuple)
                    new_h = pathcost(new_puzzle, target)
                    child_node = NODE(new_puzzle, cur_node, move, new_r, new_c)
                    next_candidates.append((new_h, child_node))
        
        if not next_candidates:
            if log_callback: log_callback(f"Trạng thái cạn kiệt. Hủy bỏ thuật toán.")
            return None

        next_candidates.sort(key=lambda x: x[0])
        beam = [item[1] for item in next_candidates[:k]]
        
        if show_log and log_callback:
            best_h = next_candidates[0][0]
            log_callback(f"  + Cập nhật tập trạng thái (h tối ưu = {best_h})\n")
        elif log_callback and stats and stats["nodes"] == 31:
            log_callback("... (Ẩn log chi tiết tiếp theo) ...")
    return None
