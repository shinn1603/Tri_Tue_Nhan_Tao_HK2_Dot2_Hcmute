from collections import deque
from core.uncertain_env import LOOP_MARKER

def conformant_search(problem, max_nodes=50000, log_callback=None, stats=None, is_searching_func=lambda: True):
    """
    Thuật toán Conformant Search (BFS) trên không gian Belief State.
    """
    initial_belief = problem.initial_belief
    if len(initial_belief) == 0:
        return None
    
    if problem.is_goal(initial_belief):
        return []
    
    all_actions = ["UP", "DOWN", "LEFT", "RIGHT"]
    queue = deque([(initial_belief, [])])
    explored = {initial_belief}
    
    while queue and is_searching_func():
        current_belief, actions = queue.popleft()
        if stats is not None:
            stats["nodes"] += 1
            if stats["nodes"] % 100 == 0:
                current_mem = len(queue) + len(explored)
                if current_mem > stats["memory"]:
                    stats["memory"] = current_mem
        
        if log_callback and stats and stats["nodes"] <= 20:
            log_callback(f"[Bước {stats['nodes']}] Belief size={len(current_belief)}, depth={len(actions)}")
        elif log_callback and stats and stats["nodes"] == 21:
            log_callback("... (Ẩn log chi tiết) ...")
        
        if stats and stats["nodes"] > max_nodes:
            if log_callback: log_callback(f"Đã vượt giới hạn {max_nodes} belief states. Dừng lại.")
            break
            
        for act in all_actions:
            new_belief = problem.apply_action_to_belief(current_belief, act)
            
            if problem.is_goal(new_belief):
                return actions + [act]
            
            if new_belief not in explored:
                explored.add(new_belief)
                queue.append((new_belief, actions + [act]))
                if log_callback and stats and stats["nodes"] <= 20:
                    log_callback(f"  + Hành động {act}: belief mới size={len(new_belief)}")
                    
    return None

def and_or_graph_search(problem, state_tuple, max_depth=10, log_callback=None, stats=None, is_searching_func=lambda: True):
    """
    Thuật toán AND-OR Graph Search cho môi trường không xác định.
    Hỗ trợ kế hoạch có vòng lặp (cyclic plan): khi bị trượt về trạng thái cũ,
    kế hoạch sẽ ghi "thử lại" thay vì thất bại.
    Sử dụng memoization để tránh tính lại các trạng thái đã giải.
    """
    solved_cache = {}
    from core.puzzle_state import Find_blank, get_move
    import numpy as np
    
    def or_search(state, path, depth):
        if not is_searching_func(): return None
        if problem.is_goal(state): return []
        if depth > max_depth: return None
        if state in path: return LOOP_MARKER
        if state in solved_cache: return solved_cache[state]
        
        if stats:
            stats["nodes"] += 1
            
        state_arr = np.array(state).reshape(3, 3)
        blank = Find_blank(state_arr)
        if blank is None: return None
        row, col = blank
        
        for act in get_move(row, col):
            plan = and_search(problem.results(state, act), act, path | {state}, depth)
            if plan is not None and plan != LOOP_MARKER:
                result = [{"action": act, "plan": plan}]
                solved_cache[state] = result
                return result
        return None
    
    def and_search(results_list, act, path, depth):
        unique_results = list(set(results_list))
        if len(unique_results) == 1:
            return or_search(unique_results[0], path, depth + 1)
        
        conditional_plan = {}
        has_progress = False
        
        for result_state in unique_results:
            sub_plan = or_search(result_state, path, depth + 1)
            if sub_plan is None: return None
            if sub_plan == LOOP_MARKER:
                conditional_plan[result_state] = LOOP_MARKER
            else:
                has_progress = True
                conditional_plan[result_state] = sub_plan
                
        if not has_progress: return None
        return conditional_plan
    
    return or_search(state_tuple, set(), 0)
