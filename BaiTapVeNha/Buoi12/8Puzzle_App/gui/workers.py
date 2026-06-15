import threading
import search

def start_search_thread(app, algo_name):
    if algo_name == "BFS": target = lambda: _run_classic(app, search.bfs_search, "BFS")
    elif algo_name == "DFS": target = lambda: _run_classic(app, search.dfs_search, "DFS")
    elif algo_name == "IDS": target = lambda: _run_classic(app, search.ids_search, "IDS")
    elif algo_name == "UCS": target = lambda: _run_classic(app, search.ucs_search, "UCS")
    elif algo_name == "Greedy": target = lambda: _run_classic(app, search.greedy_search, "Greedy")
    elif algo_name == "A*": target = lambda: _run_classic(app, search.astar_search, "A*")
    elif algo_name == "Leo đồi": target = lambda: _run_classic(app, search.hill_climbing_search, "Leo đồi")
    elif algo_name == "Leo đồi dốc nhất": target = lambda: _run_classic(app, search.steepest_ascent_search, "Leo đồi dốc nhất")
    elif algo_name == "Leo đồi ngẫu nhiên": target = lambda: _run_classic(app, search.stochastic_hill_climbing_search, "Leo đồi ngẫu nhiên")
    elif algo_name == "Leo đồi lặp lại": target = lambda: _run_classic(app, search.random_restart_hill_climbing_search, "Leo đồi lặp lại")
    elif algo_name == "Local Beam Search": target = lambda: _run_classic(app, search.local_beam_search, "Local Beam Search")
    elif algo_name == "Conformant Search": target = lambda: _run_conformant(app)
    elif algo_name == "AND-OR Search": target = lambda: _run_andor(app)
    else:
        return

    threading.Thread(target=target, daemon=True).start()

def _run_classic(app, search_func, name):
    solution = search_func(
        puzzle=app.puzzle,
        target=app.target_puzzle,
        log_callback=app.log_trace_sync,
        stats=app.stats,
        is_searching_func=lambda: app.is_searching
    )
    app.root.after(0, app.process_solution, solution, name)

def _run_conformant(app):
    app.log_trace_sync("=== CONFORMANT SEARCH ===")
    app.log_trace_sync("Đang sinh Belief State ban đầu từ đầu vào có '*'...")
    
    from core.uncertain_env import BeliefStateProblem
    problem = BeliefStateProblem(app.wildcard_input, app.target_puzzle)
    
    app.log_trace_sync(f"Belief State ban đầu: {len(problem.initial_belief)} trạng thái hợp lệ")
    if len(problem.initial_belief) == 0:
        app.root.after(0, app.process_conformant_solution, None)
        return
        
    app.log_trace_sync("\nBắt đầu BFS trên không gian Belief State...")
    actions = search.conformant_search(
        problem=problem,
        log_callback=app.log_trace_sync,
        stats=app.stats,
        is_searching_func=lambda: app.is_searching
    )
    if actions is not None:
        app.log_trace_sync(f"\n*** TÌM THẤY LỜI GIẢI! ***\nChuỗi hành động: {actions}\nSố bước: {len(actions)}")
    else:
        app.log_trace_sync("Không tìm được chuỗi hành động chung.")
        
    app.root.after(0, app.process_conformant_solution, actions)

def _run_andor(app):
    app.log_trace_sync("=== AND-OR GRAPH SEARCH ===")
    app.log_trace_sync("Môi trường: Gạch kẹt (Thành công đi đúng hướng, thất bại đứng im)")
    
    from core.uncertain_env import NonDeterministicPuzzle
    problem = NonDeterministicPuzzle(app.target_puzzle)
    state_tuple = tuple(app.puzzle.flatten())
    
    app.log_trace_sync(f"Trạng thái bắt đầu: {list(state_tuple)}")
    app.log_trace_sync(f"Giới hạn độ sâu: 10\nBắt đầu tìm kiếm AND-OR...\n")
    
    plan = search.and_or_graph_search(
        problem=problem,
        state_tuple=state_tuple,
        max_depth=10,
        log_callback=app.log_trace_sync,
        stats=app.stats,
        is_searching_func=lambda: app.is_searching
    )
    
    if plan is not None:
        app.log_trace_sync(f"\n*** TÌM THẤY KẾ HOẠCH DỰ PHÒNG! ***")
        
    app.root.after(0, app.process_andor_solution, plan)
