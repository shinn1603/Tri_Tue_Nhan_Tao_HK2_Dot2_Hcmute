import numpy as np
import random
import sys
from collections import deque
from core.puzzle_state import NODE, Find_blank, get_move, action, pathcost

# ================= CSP MODE ALGORITHMS =================

def backtracking_csp_mode(puzzle, target, max_nodes, log_callback, stats, is_searching_func):
    sys.setrecursionlimit(100000)
    start_node = NODE(puzzle, None, None, -1, -1)
    
    def recursive_backtracking(assignment):
        if not is_searching_func(): return None
        if stats:
            stats["nodes"] += 1
            
        state = assignment.state
        empty_cells = np.argwhere(state == -1)
        
        if len(empty_cells) == 0:
            if log_callback: log_callback(f"[Bước {stats['nodes']}] Hoàn tất gán toàn bộ các biến.")
            return assignment
            
        r, c = random.choice(empty_cells)
        show_log = stats and stats["nodes"] <= 50
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Backtracking - Chọn biến: Ô ({r},{c})")
        elif log_callback and stats and stats["nodes"] == 51: log_callback("... (Đã ẩn bớt log chi tiết để đảm bảo hiệu suất) ...")
        
        used_values = set(state[state != -1])
        domain = [v for v in range(9) if v not in used_values]
        random.shuffle(domain) 
        
        for val in domain:
            new_state = state.copy()
            new_state[r, c] = val
            
            if show_log and log_callback: log_callback(f"  |- Gán giá trị: {val}")
            
            # Kiểm tra ràng buộc đích
            if val != target[r, c]:
                if show_log and log_callback: log_callback(f"  |- Kiểm tra ràng buộc: Giá trị {val} != Đích {target[r,c]} -> Vi phạm. Quay lui.")
                continue
            
            new_node = NODE(new_state, assignment, f"Điền {val} vào ({r},{c})", r, c)
            result = recursive_backtracking(new_node)
            if result is not None:
                return result
                
            if show_log and log_callback: log_callback(f"  |- Trạng thái ngõ cụt tại ô ({r},{c}). Tiến hành quay lui.")
            
        return None

    return recursive_backtracking(start_node)


def forward_checking_csp_mode(puzzle, target, max_nodes, log_callback, stats, is_searching_func):
    start_node = NODE(puzzle, None, None, -1, -1)
    stack = [start_node]
    
    while stack and is_searching_func():
        cur_node = stack.pop()
        state = cur_node.state
        
        if stats: stats["nodes"] += 1
            
        empty_cells = np.argwhere(state == -1)
        if len(empty_cells) == 0:
            if log_callback: log_callback(f"[Bước {stats['nodes']}] Hoàn tất gán toàn bộ các biến.")
            return cur_node
            
        r, c = random.choice(empty_cells)
        show_log = stats and stats["nodes"] <= 50
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Forward Checking - Chọn biến: Ô ({r},{c})")
        elif log_callback and stats and stats["nodes"] == 51: log_callback("... (Đã ẩn bớt log chi tiết để đảm bảo hiệu suất) ...")
        
        used_values = set(state[state != -1])
        domain = [v for v in range(9) if v not in used_values]
        random.shuffle(domain)
        
        for val in domain:
            new_state = state.copy()
            new_state[r, c] = val
            if show_log and log_callback: log_callback(f"  |- Gán giá trị: {val}. Kiểm tra phân bổ miền giá trị tương lai...")
            
            if val != target[r, c]:
                if show_log and log_callback: log_callback(f"  |- Cắt tỉa nhánh: Ràng buộc đích không thỏa mãn.")
                continue
            
            # Forward check: Trong ràng buộc AllDiff đơn giản, không cần cắt tỉa thêm nếu ta duy trì tập used_values.
            stack.append(NODE(new_state, cur_node, f"Điền {val} vào ({r},{c})", r, c))
            
    return None


def ac3_csp_mode(puzzle, target, max_nodes, log_callback, stats, is_searching_func):
    start_node = NODE(puzzle, None, None, -1, -1)
    queue = deque([start_node])
    
    while queue and is_searching_func():
        cur_node = queue.popleft()
        state = cur_node.state
        if stats: stats["nodes"] += 1
            
        empty_cells = np.argwhere(state == -1)
        if len(empty_cells) == 0:
            if log_callback: log_callback(f"[Bước {stats['nodes']}] Hoàn tất gán toàn bộ các biến.")
            return cur_node
            
        r, c = random.choice(empty_cells)
        show_log = stats and stats["nodes"] <= 50
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] AC-3 - Lọc cung (Arc Consistency): Ô ({r},{c})")
        elif log_callback and stats and stats["nodes"] == 51: log_callback("... (Đã ẩn bớt log chi tiết để đảm bảo hiệu suất) ...")
        
        used_values = set(state[state != -1])
        domain = [v for v in range(9) if v not in used_values]
        random.shuffle(domain)
        
        for val in domain:
            new_state = state.copy()
            new_state[r, c] = val
            
            if val != target[r, c]:
                if show_log and log_callback: log_callback(f"  |- Loại bỏ {val} khỏi miền giá trị của ô ({r},{c}) do không khớp đích.")
                continue
                
            if show_log and log_callback: log_callback(f"  |- Giá trị {val} hợp lệ. Thêm vào hàng đợi xử lý.")
            queue.append(NODE(new_state, cur_node, f"Điền {val} vào ({r},{c})", r, c))
            
    return None


def min_conflict_csp_mode(puzzle, target, max_nodes, log_callback, stats, is_searching_func):
    # Khởi tạo ngẫu nhiên một bảng đầy đủ (sai vị trí)
    values = list(range(9))
    random.shuffle(values)
    initial_state = np.array(values).reshape(3, 3)
    
    # Tạo node giả từ trạng thái rỗng để GUI hiểu bước đầu tiên
    start_node = NODE(puzzle, None, "Bắt đầu Min-Conflicts", -1, -1)
    current = NODE(initial_state, start_node, "Khởi tạo bảng ngẫu nhiên", -1, -1)
    
    for i in range(1, max_nodes + 1):
        if not is_searching_func(): break
        if stats: stats["nodes"] += 1
            
        state = current.state
        conflicts = np.sum(state != target)
        
        if conflicts == 0:
            if log_callback: log_callback(f"[Bước {stats['nodes']}] Trạng thái đích đã đạt được. Xung đột: 0.")
            return current
            
        show_log = stats and stats["nodes"] <= 50
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Min-Conflicts - Đánh giá trạng thái. Xung đột hiện tại: {conflicts} ô sai vị trí.")
        elif log_callback and stats and stats["nodes"] == 51: log_callback("... (Đã ẩn bớt log chi tiết để đảm bảo hiệu suất) ...")
        
        wrong_cells = np.argwhere(state != target)
        r1, c1 = random.choice(wrong_cells)
        
        best_children = []
        min_c = float('inf')
        
        for r2 in range(3):
            for c2 in range(3):
                if (r1, c1) != (r2, c2):
                    new_state = state.copy()
                    new_state[r1, c1], new_state[r2, c2] = new_state[r2, c2], new_state[r1, c1]
                    c = np.sum(new_state != target)
                    
                    if c < min_c:
                        min_c = c
                        best_children = [(new_state, r1, c1, r2, c2)]
                    elif c == min_c:
                        best_children.append((new_state, r1, c1, r2, c2))
                        
        if not best_children:
            return None
            
        new_state, r1, c1, r2, c2 = random.choice(best_children)
        if show_log and log_callback: log_callback(f"  |- Hoán đổi vị trí ô ({r1},{c1}) và ô ({r2},{c2}) để tối thiểu hóa xung đột.")
        
        current = NODE(new_state, current, f"Swap ({r1},{c1}) và ({r2},{c2})", -1, -1)
        
    return None

# ================= NORMAL MODE ALGORITHMS =================

def backtracking_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    if np.any(puzzle == -1):
        return backtracking_csp_mode(puzzle, target, max_nodes, log_callback, stats, is_searching_func)
        
    sys.setrecursionlimit(100000)
    row, col = Find_blank(puzzle)
    start_node = NODE(puzzle, None, None, row, col)
    explored = set()

    def recursive_backtracking(assignment):
        if not is_searching_func(): return None
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 200 == 0:
                if len(explored) > stats["memory"]: stats["memory"] = len(explored)

        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Backtracking: Xét trạng thái")

        if np.array_equal(assignment.state, target): return assignment
        explored.add(tuple(assignment.state.flatten()))
        valid_moves = get_move(assignment.row, assignment.col)
        
        for value in valid_moves:
            new_puzzle, new_r, new_c = action(assignment.state, value, assignment.row, assignment.col)
            state_tuple = tuple(new_puzzle.flatten())
            
            if state_tuple not in explored:
                new_assignment = NODE(new_puzzle, assignment, value, new_r, new_c)
                result = recursive_backtracking(new_assignment)
                if result is not None: return result
        return None

    return recursive_backtracking(start_node)


def forward_checking_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    if np.any(puzzle == -1):
        return forward_checking_csp_mode(puzzle, target, max_nodes, log_callback, stats, is_searching_func)
        
    row, col = Find_blank(puzzle)
    start_node = NODE(puzzle, None, None, row, col)
    stack = [start_node]
    explored = {tuple(puzzle.flatten())}
    
    while stack and is_searching_func():
        cur_node = stack.pop()
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 200 == 0:
                current_mem = len(stack) + len(explored)
                if current_mem > stats["memory"]: stats["memory"] = current_mem

        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Forward Checking: Đánh giá domain")

        if np.array_equal(cur_node.state, target): return cur_node
        valid_moves = get_move(cur_node.row, cur_node.col)
        valid_moves.reverse()
        for move in valid_moves:
            new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
            state_tuple = tuple(new_puzzle.flatten())
            
            if state_tuple not in explored:
                future_moves = get_move(new_r, new_c)
                has_valid_future = False
                for f_move in future_moves:
                    f_puzzle, _, _ = action(new_puzzle, f_move, new_r, new_c)
                    if tuple(f_puzzle.flatten()) not in explored:
                        has_valid_future = True
                        break
                
                if not has_valid_future and not np.array_equal(new_puzzle, target):
                    if show_log and log_callback: log_callback(f"  -> Đã cắt tỉa một nhánh cụt (Forward Check)!")
                    continue

                explored.add(state_tuple)
                stack.append(NODE(new_puzzle, cur_node, move, new_r, new_c))

        if log_callback and stats and stats["nodes"] == 31: log_callback("... (Ẩn log chi tiết) ...")
    return None


def ac3_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    if np.any(puzzle == -1):
        return ac3_csp_mode(puzzle, target, max_nodes, log_callback, stats, is_searching_func)
        
    row, col = Find_blank(puzzle)
    start_node = NODE(puzzle, None, None, row, col)
    queue = deque([start_node])
    explored = {tuple(puzzle.flatten())}
    
    def rm_inconsistent_values(node):
        consistent = []
        for move in get_move(node.row, node.col):
            new_puzzle, new_r, new_c = action(node.state, move, node.row, node.col)
            state_tuple = tuple(new_puzzle.flatten())
            if state_tuple not in explored:
                explored.add(state_tuple)
                consistent.append(NODE(new_puzzle, node, move, new_r, new_c))
        return consistent

    while queue and is_searching_func():
        cur_node = queue.popleft()
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 200 == 0:
                current_mem = len(queue) + len(explored)
                if current_mem > stats["memory"]: stats["memory"] = current_mem

        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] AC-3: RM-Inconsistent-Values")

        if np.array_equal(cur_node.state, target): return cur_node
        consistent_neighbors = rm_inconsistent_values(cur_node)
        for neighbor in consistent_neighbors:
            queue.append(neighbor)

        if log_callback and stats and stats["nodes"] == 31: log_callback("... (Ẩn log chi tiết) ...")
    return None


def min_conflict_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    if np.any(puzzle == -1):
        return min_conflict_csp_mode(puzzle, target, max_nodes, log_callback, stats, is_searching_func)
        
    row, col = Find_blank(puzzle)
    current = NODE(puzzle, None, None, row, col)
    explored = {tuple(puzzle.flatten())}
    
    for i in range(1, max_nodes + 1):
        if not is_searching_func(): break
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 50 == 0:
                if len(explored) > stats["memory"]: stats["memory"] = len(explored)

        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Min-Conflicts: Chọn biến và giá trị tốt nhất")

        if np.array_equal(current.state, target): return current
        valid_moves = get_move(current.row, current.col)
        best_values = []
        min_conflicts = float('inf')
        
        for value in valid_moves:
            new_puzzle, new_r, new_c = action(current.state, value, current.row, current.col)
            state_tuple = tuple(new_puzzle.flatten())
            
            if state_tuple not in explored:
                conflicts = np.sum((new_puzzle != target) & (new_puzzle != 0))
                if conflicts < min_conflicts:
                    min_conflicts = conflicts
                    best_values = [(new_puzzle, new_r, new_c, value)]
                elif conflicts == min_conflicts:
                    best_values.append((new_puzzle, new_r, new_c, value))

        if not best_values:
            if log_callback: log_callback("Min-Conflicts: Thất bại (Kẹt ở local minimum).")
            return None
            
        chosen = random.choice(best_values)
        new_puzzle, new_r, new_c, value = chosen
        explored.add(tuple(new_puzzle.flatten()))
        current = NODE(new_puzzle, current, value, new_r, new_c)

        if log_callback and stats and stats["nodes"] == 31: log_callback("... (Ẩn log chi tiết) ...")
    return None
