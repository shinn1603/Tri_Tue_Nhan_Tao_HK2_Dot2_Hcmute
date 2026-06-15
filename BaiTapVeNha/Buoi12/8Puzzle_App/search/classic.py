from collections import deque
from queue import PriorityQueue
import numpy as np
from core.puzzle_state import NODE, Find_blank, get_move, action, pathcost

def bfs_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    row, col = Find_blank(puzzle)
    start_node = NODE(puzzle, None, None, row, col)
    queue = deque([start_node])
    explored = {tuple(puzzle.flatten())}
    
    while queue and is_searching_func():
        cur_node = queue.popleft()
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 200 == 0:
                current_mem = len(queue) + len(explored)
                if current_mem > stats["memory"]: stats["memory"] = current_mem

        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Trích xuất Queue")

        if np.array_equal(cur_node.state, target):
            return cur_node

        generated = added = skipped = 0
        for move in get_move(cur_node.row, cur_node.col):
            generated += 1
            new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
            state_tuple = tuple(new_puzzle.flatten())
            if state_tuple not in explored:
                explored.add(state_tuple)
                queue.append(NODE(new_puzzle, cur_node, move, new_r, new_c))
                added += 1
            else: skipped += 1
                
        if show_log and log_callback: log_callback(f"  => Sinh: {generated} | Nhận: {added} | Trùng: {skipped}\n")
        elif log_callback and stats and stats["nodes"] == 31: log_callback("... (Ẩn log chi tiết) ...")
            
    return None

def dfs_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
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
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Trích xuất Stack")

        if np.array_equal(cur_node.state, target):
            return cur_node

        generated = added = skipped = 0
        valid_moves = get_move(cur_node.row, cur_node.col)
        valid_moves.reverse()
        for move in valid_moves:
            generated += 1
            new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
            state_tuple = tuple(new_puzzle.flatten())
            if state_tuple not in explored:
                explored.add(state_tuple)
                stack.append(NODE(new_puzzle, cur_node, move, new_r, new_c))
                added += 1
            else: skipped += 1

        if show_log and log_callback: log_callback(f"  => Sinh: {generated} | Nhận: {added} | Trùng: {skipped}\n")
        elif log_callback and stats and stats["nodes"] == 31: log_callback("... (Ẩn log chi tiết) ...")

    return None

def ids_search(puzzle, target, max_nodes=50000, max_depth_limit=35, log_callback=None, stats=None, is_searching_func=lambda: True):
    row, col = Find_blank(puzzle)
    start_node = NODE(puzzle, None, None, row, col)
    solution = None
    
    def dls(node, depth_limit):
        explored = {tuple(node.state.flatten()): 0} 
        stack = [(node, 0)]
        while stack and is_searching_func():
            cur_node, cur_depth = stack.pop()
            if stats:
                stats["nodes"] += 1
                if stats["nodes"] % 50 == 0:
                    current_mem = len(stack) + len(explored)
                    if current_mem > stats["memory"]: stats["memory"] = current_mem
            
            show_log = stats and stats["nodes"] <= 50 
            if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Xét mức sâu {cur_depth}")

            if np.array_equal(cur_node.state, target): return cur_node
                
            generated = added = skipped = 0
            if cur_depth < depth_limit:
                valid_moves = get_move(cur_node.row, cur_node.col)
                valid_moves.reverse()
                for move in valid_moves:
                    generated += 1
                    new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
                    state_tuple = tuple(new_puzzle.flatten())
                    if state_tuple not in explored or explored[state_tuple] > cur_depth + 1:
                        explored[state_tuple] = cur_depth + 1
                        stack.append((NODE(new_puzzle, cur_node, move, new_r, new_c), cur_depth + 1))
                        added += 1
                    else: skipped += 1
            
            if show_log and cur_depth < depth_limit and log_callback:
                log_callback(f"  => Sinh: {generated} | Nhận: {added} | Bỏ qua: {skipped}\n")
            elif log_callback and stats and stats["nodes"] == 51: log_callback("... (Ẩn log chi tiết) ...")
        return None

    for limit in range(max_depth_limit):
        if not is_searching_func(): break
        if log_callback: log_callback(f"\n--- Giới hạn độ sâu hiện tại: {limit} ---")
        solution = dls(start_node, limit)
        if solution is not None: break
    return solution

def ucs_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    row, col = Find_blank(puzzle)
    start_node = NODE(puzzle, None, None, row, col)
    queue = PriorityQueue()
    push_count = 0
    queue.put((0, push_count, start_node))
    push_count += 1
    explored = {tuple(puzzle.flatten())}
    
    while not queue.empty() and is_searching_func():
        g_cost, _, cur_node = queue.get()
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 200 == 0:
                current_mem = queue.qsize() + len(explored)
                if current_mem > stats["memory"]: stats["memory"] = current_mem

        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Trích xuất PriorityQueue (cost={g_cost})")

        if np.array_equal(cur_node.state, target):
            return cur_node

        generated = added = skipped = 0
        for move in get_move(cur_node.row, cur_node.col):
            generated += 1
            new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
            state_tuple = tuple(new_puzzle.flatten())
            if state_tuple not in explored:
                explored.add(state_tuple)
                new_cost = g_cost + 1
                child_node = NODE(new_puzzle, cur_node, move, new_r, new_c)
                queue.put((new_cost, push_count, child_node))
                push_count += 1
                added += 1
            else: skipped += 1
                
        if show_log and log_callback: log_callback(f"  => Sinh: {generated} | Nhận: {added} | Trùng: {skipped}\n")
        elif log_callback and stats and stats["nodes"] == 31: log_callback("... (Ẩn log chi tiết) ...")
    return None

def greedy_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    row, col = Find_blank(puzzle)
    start_node = NODE(puzzle, None, None, row, col)
    queue = PriorityQueue()
    push_count = 0
    h_cost = pathcost(start_node.state, target)
    queue.put((h_cost, push_count, start_node))
    push_count += 1
    explored = {tuple(puzzle.flatten())}
    
    while not queue.empty() and is_searching_func():
        current_h, _, cur_node = queue.get()
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 200 == 0:
                current_mem = queue.qsize() + len(explored)
                if current_mem > stats["memory"]: stats["memory"] = current_mem

        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Trích xuất PriorityQueue (h={current_h})")

        if np.array_equal(cur_node.state, target):
            return cur_node

        generated = added = skipped = 0
        for move in get_move(cur_node.row, cur_node.col):
            generated += 1
            new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
            state_tuple = tuple(new_puzzle.flatten())
            if state_tuple not in explored:
                explored.add(state_tuple)
                new_h = pathcost(new_puzzle, target)
                child_node = NODE(new_puzzle, cur_node, move, new_r, new_c)
                queue.put((new_h, push_count, child_node))
                push_count += 1
                added += 1
            else: skipped += 1
                
        if show_log and log_callback: log_callback(f"  => Sinh: {generated} | Nhận: {added} | Trùng: {skipped}\n")
        elif log_callback and stats and stats["nodes"] == 31: log_callback("... (Ẩn log chi tiết) ...")
    return None

def astar_search(puzzle, target, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    row, col = Find_blank(puzzle)
    start_node = NODE(puzzle, None, None, row, col)
    queue = PriorityQueue()
    push_count = 0
    g_cost = 0
    h_cost = pathcost(start_node.state, target)
    f_cost = g_cost + h_cost
    queue.put((f_cost, push_count, g_cost, start_node))
    push_count += 1
    explored = {tuple(puzzle.flatten())}
    
    while not queue.empty() and is_searching_func():
        current_f, _, current_g, cur_node = queue.get()
        if stats:
            stats["nodes"] += 1
            if stats["nodes"] % 200 == 0:
                current_mem = queue.qsize() + len(explored)
                if current_mem > stats["memory"]: stats["memory"] = current_mem

        show_log = stats and stats["nodes"] <= 30
        if show_log and log_callback: log_callback(f"[Bước {stats['nodes']}] Trích xuất PriorityQueue (f={current_f}, g={current_g})")

        if np.array_equal(cur_node.state, target):
            return cur_node

        generated = added = skipped = 0
        for move in get_move(cur_node.row, cur_node.col):
            generated += 1
            new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
            state_tuple = tuple(new_puzzle.flatten())
            if state_tuple not in explored:
                explored.add(state_tuple)
                new_g = current_g + 1
                new_h = pathcost(new_puzzle, target)
                new_f = new_g + new_h
                child_node = NODE(new_puzzle, cur_node, move, new_r, new_c)
                queue.put((new_f, push_count, new_g, child_node))
                push_count += 1
                added += 1
            else: skipped += 1
                
        if show_log and log_callback: log_callback(f"  => Sinh: {generated} | Nhận: {added} | Trùng: {skipped}\n")
        elif log_callback and stats and stats["nodes"] == 31: log_callback("... (Ẩn log chi tiết) ...")
    return None
