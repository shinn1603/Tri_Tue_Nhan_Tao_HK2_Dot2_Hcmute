import numpy as np
import random
from collections import deque
from queue import PriorityQueue
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class NODE:
    def __init__(self, state, parent, move_action, row, col):
        self.state = state 
        self.parent = parent
        self.move_action = move_action
        self.row = row
        self.col = col

def is_solvable(puzzle):
    flat_puzzle = [val for val in puzzle.flatten() if val != 0]
    inversions = 0
    for i in range(len(flat_puzzle)):
        for j in range(i + 1, len(flat_puzzle)):
            if flat_puzzle[i] > flat_puzzle[j]:
                inversions += 1
    return inversions % 2 == 0

def count_inversions(puzzle):
    flat = [val for val in puzzle.flatten() if val != 0]
    inversions = 0
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if flat[i] > flat[j]:
                inversions += 1
    return inversions

def check_solvable(start, target):
    return (count_inversions(start) % 2) == (count_inversions(target) % 2)

def Inputpuzzle():
    while True:
        puzzle = np.random.permutation(9).reshape(3, 3)
        if is_solvable(puzzle):
            return puzzle

def Find_blank(puzzle):
    result = np.where(puzzle == 0)
    if len(result[0]) > 0:
        row = result[0][0]
        col = result[1][0]
        return (row, col)
    return None

def get_move(row, col):
    valid_moves = []
    if(row < 2): valid_moves.append("DOWN")
    if(row > 0): valid_moves.append("UP")
    if(col < 2): valid_moves.append("RIGHT")
    if(col > 0): valid_moves.append("LEFT")
    return valid_moves

def action(puzzle, move, row, col):
    new_matrix = np.copy(puzzle)
    if(move=="DOWN"): new_row, new_col = row + 1, col
    if(move=="UP"): new_row, new_col = row - 1, col
    if(move=="LEFT"): new_row, new_col = row, col - 1
    if(move=="RIGHT"): new_row, new_col = row, col + 1
    new_matrix[row, col], new_matrix[new_row, new_col] = new_matrix[new_row, new_col], new_matrix[row, col]
    return new_matrix, new_row, new_col

def pathcost(new_puzzle, target_puzzle):
    cost = (target_puzzle != new_puzzle) & (new_puzzle != 0)
    return np.sum(cost)

class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver System")
        self.root.geometry("1000x750")
        self.root.configure(padx=20, pady=20)

        self.TILE_SIZE = 100
        self.PAD = 5
        self.GRID_SIZE = (self.TILE_SIZE + self.PAD) * 3 + self.PAD

        self.target_puzzle = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.puzzle = self.generate_random_puzzle(self.target_puzzle)
        self.path = []
        self.current_step = 0
        
        self.is_playing = False
        self.is_sliding = False
        self.is_searching = False
        self.current_after_job = None 
        
        self.stats = {"nodes": 0, "memory": 0, "start_time": 0}

        self.setup_ui()
        self.populate_entries()
        self.reset_gui_state()
        self.place_tiles_instantly(self.puzzle)

    def generate_random_puzzle(self, target):
        while True:
            puzzle = np.random.permutation(9).reshape(3, 3)
            if check_solvable(puzzle, target):
                return puzzle

    def setup_ui(self):
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, padx=10, fill=tk.BOTH)
        
        tk.Label(self.left_frame, text="Mô phỏng", font=("Helvetica", 14, "bold")).pack(pady=5)

        self.canvas_bg = tk.Frame(self.left_frame, bg="#333", width=self.GRID_SIZE, height=self.GRID_SIZE)
        self.canvas_bg.pack(pady=10)
        
        self.tile_widgets = {}
        for val in range(1, 9):
            lbl = tk.Label(self.canvas_bg, text=str(val), font=("Helvetica", 36, "bold"), 
                           bg="white", relief="raised", borderwidth=3)
            lbl.place(width=self.TILE_SIZE, height=self.TILE_SIZE) 
            self.tile_widgets[val] = lbl
            
        dash_frame = tk.LabelFrame(self.left_frame, text="Thống kê", padx=10, pady=10, font=("Helvetica", 10, "bold"))
        dash_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_time = tk.Label(dash_frame, text="Thời gian: 0.00s", font=("Helvetica", 10))
        self.lbl_time.grid(row=0, column=0, sticky="w", pady=2)
        
        self.lbl_nodes = tk.Label(dash_frame, text="Đã duyệt: 0 trạng thái", font=("Helvetica", 10))
        self.lbl_nodes.grid(row=1, column=0, sticky="w", pady=2)
        
        self.lbl_mem = tk.Label(dash_frame, text="Đã lưu (RAM): 0 trạng thái", font=("Helvetica", 10))
        self.lbl_mem.grid(row=2, column=0, sticky="w", pady=2)

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        matrix_frame = tk.LabelFrame(self.right_frame, text="Dữ liệu", padx=5, pady=5)
        matrix_frame.pack(fill=tk.X, pady=5)

        start_frame = tk.Frame(matrix_frame)
        start_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(start_frame, text="Bắt đầu").grid(row=0, column=0, columnspan=3)
        self.start_entries = []
        for r in range(3):
            row_entries = []
            for c in range(3):
                e = tk.Entry(start_frame, width=3, font=("Helvetica", 12), justify="center")
                e.grid(row=r+1, column=c, padx=2, pady=2)
                row_entries.append(e)
            self.start_entries.append(row_entries)

        target_frame = tk.Frame(matrix_frame)
        target_frame.pack(side=tk.LEFT, padx=10)
        tk.Label(target_frame, text="Đích").grid(row=0, column=0, columnspan=3)
        self.target_entries = []
        for r in range(3):
            row_entries = []
            for c in range(3):
                e = tk.Entry(target_frame, width=3, font=("Helvetica", 12), justify="center")
                e.grid(row=r+1, column=c, padx=2, pady=2)
                row_entries.append(e)
            self.target_entries.append(row_entries)

        btn_frame_matrix = tk.Frame(matrix_frame)
        btn_frame_matrix.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.BOTH)
        self.btn_apply = tk.Button(btn_frame_matrix, text="Nhập liệu", command=self.apply_input)
        self.btn_apply.pack(fill=tk.X, pady=2)
        self.btn_gen = tk.Button(btn_frame_matrix, text="Sinh Ngẫu Nhiên", command=self.generate_new_puzzle)
        self.btn_gen.pack(fill=tk.X, pady=2)

        algo_frame = tk.LabelFrame(self.right_frame, text="Cài đặt", padx=10, pady=10)
        algo_frame.pack(fill=tk.X, pady=5)
        
        self.algo_var = tk.StringVar()
        self.algo_combo = ttk.Combobox(algo_frame, textvariable=self.algo_var, state="readonly", font=("Helvetica", 10))
        self.algo_combo['values'] = (
            "BFS", "DFS", "IDS", "UCS", 
            "Greedy", "A*", 
            "Leo đồi", "Leo đồi dốc nhất", 
            "Leo đồi ngẫu nhiên", "Leo đồi lặp lại",
            "Local Beam Search"
        )
        self.algo_combo.current(0)
        self.algo_combo.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.btn_solve = tk.Button(algo_frame, text="Giải", command=self.start_solve, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"), width=10)
        self.btn_solve.pack(side=tk.LEFT, padx=2)

        anim_ctrl_frame = tk.LabelFrame(self.right_frame, text="Điều khiển", padx=10, pady=10)
        anim_ctrl_frame.pack(fill=tk.X, pady=5)
        
        ctrl_btns = tk.Frame(anim_ctrl_frame)
        ctrl_btns.pack()
        self.btn_prev = tk.Button(ctrl_btns, text="|<", command=self.prev_step, state=tk.DISABLED, width=5)
        self.btn_prev.pack(side=tk.LEFT, padx=2)
        self.btn_play = tk.Button(ctrl_btns, text="Phát", command=self.toggle_play, state=tk.DISABLED, width=8)
        self.btn_play.pack(side=tk.LEFT, padx=2)
        self.btn_next = tk.Button(ctrl_btns, text=">|", command=self.next_step, state=tk.DISABLED, width=5)
        self.btn_next.pack(side=tk.LEFT, padx=2)

        self.speed_scale = tk.Scale(anim_ctrl_frame, from_=10, to=1500, resolution=10, orient=tk.HORIZONTAL, label="Tốc độ (ms):")
        self.speed_scale.set(400)
        self.speed_scale.pack(fill=tk.X, pady=5)

        style = ttk.Style()
        try: style.theme_use('clam') 
        except: pass
        style.configure('TNotebook.Tab', font=('Helvetica', 10), padding=[15, 4])
        style.map('TNotebook.Tab', 
                  background=[('selected', '#0078D7'), ('!selected', '#E1E1E1')],
                  foreground=[('selected', 'white'), ('!selected', 'black')])

        self.log_tabs = ttk.Notebook(self.right_frame)
        self.log_tabs.pack(fill=tk.BOTH, expand=True, pady=5)

        self.path_frame = tk.Frame(self.log_tabs)
        self.log_tabs.add(self.path_frame, text="Kết quả")
        self.scrollbar_path = tk.Scrollbar(self.path_frame)
        self.scrollbar_path.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox = tk.Listbox(self.path_frame, yscrollcommand=self.scrollbar_path.set, font=("Consolas", 10), bg="#f4f4f4")
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_path.config(command=self.history_listbox.yview)
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)

        self.trace_frame = tk.Frame(self.log_tabs)
        self.log_tabs.add(self.trace_frame, text="Log hệ thống")
        self.scrollbar_trace = tk.Scrollbar(self.trace_frame)
        self.scrollbar_trace.pack(side=tk.RIGHT, fill=tk.Y)
        self.trace_listbox = tk.Listbox(self.trace_frame, yscrollcommand=self.scrollbar_trace.set, font=("Consolas", 10))
        self.trace_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_trace.config(command=self.trace_listbox.yview)

    def populate_entries(self):
        for r in range(3):
            for c in range(3):
                self.start_entries[r][c].delete(0, tk.END)
                self.start_entries[r][c].insert(0, str(self.puzzle[r, c]))
                
                self.target_entries[r][c].delete(0, tk.END)
                self.target_entries[r][c].insert(0, str(self.target_puzzle[r, c]))

    def apply_input(self):
        try:
            start_vals = []
            target_vals = []
            for r in range(3):
                for c in range(3):
                    start_vals.append(int(self.start_entries[r][c].get()))
                    target_vals.append(int(self.target_entries[r][c].get()))
            
            if sorted(start_vals) != list(range(9)) or sorted(target_vals) != list(range(9)):
                messagebox.showerror("Lỗi", "Ma trận phải chứa các số từ 0 đến 8, không trùng lặp.")
                return

            new_start = np.array(start_vals).reshape(3, 3)
            new_target = np.array(target_vals).reshape(3, 3)

            if not check_solvable(new_start, new_target):
                messagebox.showerror("Lỗi", "Trạng thái bắt đầu và đích không cùng tính chẵn lẻ (không thể giải).")
                return

            self.puzzle = new_start
            self.target_puzzle = new_target
            self.reset_gui_state()
            self.place_tiles_instantly(self.puzzle)
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên hợp lệ.")

    def generate_new_puzzle(self):
        self.puzzle = self.generate_random_puzzle(self.target_puzzle)
        self.populate_entries()
        self.reset_gui_state()
        self.place_tiles_instantly(self.puzzle)

    def reset_gui_state(self):
        self.stop_current_animation()
        self.is_playing = False
        self.is_searching = False
        self.btn_play.config(text="Phát")
        self.path = []
        self.history_listbox.delete(0, tk.END)
        self.trace_listbox.delete(0, tk.END)
        self.disable_anim_controls()
        
        self.stats = {"nodes": 0, "memory": 0, "start_time": 0}
        self.lbl_time.config(text="Thời gian: 0.00s")
        self.lbl_nodes.config(text="Đã duyệt: 0 trạng thái")
        self.lbl_mem.config(text="Đã lưu (RAM): 0 trạng thái")

    def stop_current_animation(self):
        if self.current_after_job is not None:
            self.root.after_cancel(self.current_after_job)
            self.current_after_job = None
        self.is_sliding = False

    def get_coords(self, row, col):
        x = self.PAD + col * (self.TILE_SIZE + self.PAD)
        y = self.PAD + row * (self.TILE_SIZE + self.PAD)
        return x, y

    def place_tiles_instantly(self, state):
        for r in range(3):
            for c in range(3):
                val = state[r, c]
                if val != 0:
                    tile = self.tile_widgets[val]
                    tile.place(x=self.get_coords(r, c)[0], y=self.get_coords(r, c)[1])
                    tile.tkraise()

    def slide_tile(self, tile_widget, start_coords, end_coords, callback):
        self.is_sliding = True
        anim_time = self.speed_scale.get() * 0.8
        step_delay = 20 
        num_steps = max(1, int(anim_time / step_delay))
        dx = (end_coords[0] - start_coords[0]) / num_steps
        dy = (end_coords[1] - start_coords[1]) / num_steps
        current_step, current_x, current_y = 0, start_coords[0], start_coords[1]

        def animate_step():
            nonlocal current_step, current_x, current_y
            if current_step < num_steps:
                current_x += dx; current_y += dy
                tile_widget.place(x=int(current_x), y=int(current_y))
                current_step += 1
                self.current_after_job = self.root.after(step_delay, animate_step)
            else:
                tile_widget.place(x=end_coords[0], y=end_coords[1])
                self.is_sliding = False
                callback()
        self.current_after_job = self.root.after(step_delay, animate_step)

    def start_dashboard_updates(self):
        if self.is_searching:
            elapsed = time.time() - self.stats["start_time"]
            self.lbl_time.config(text=f"Thời gian: {elapsed:.2f}s")
            self.lbl_nodes.config(text=f"Đã duyệt: {self.stats['nodes']} trạng thái")
            self.lbl_mem.config(text=f"Đã lưu (RAM): {self.stats['memory']} trạng thái")
            self.root.after(100, self.start_dashboard_updates)

    def log_trace_sync(self, message):
        def update():
            self.trace_listbox.insert(tk.END, message)
            self.trace_listbox.see(tk.END)
        self.root.after(0, update)

    def start_solve(self):
        self.btn_apply.config(state=tk.DISABLED)
        self.btn_gen.config(state=tk.DISABLED)
        self.btn_solve.config(state=tk.DISABLED)
        self.disable_anim_controls()
        self.stop_current_animation()
        
        self.history_listbox.delete(0, tk.END)
        self.trace_listbox.delete(0, tk.END)
        self.place_tiles_instantly(self.puzzle) 
        
        self.is_searching = True
        self.stats["start_time"] = time.time()
        self.stats["nodes"] = 0
        self.stats["memory"] = 0
        self.start_dashboard_updates()
        
        self.log_tabs.select(self.trace_frame) 
        
        algo = self.algo_var.get()
        if algo == "BFS": threading.Thread(target=self.bfs_worker, daemon=True).start()
        elif algo == "DFS": threading.Thread(target=self.dfs_worker, daemon=True).start()
        elif algo == "IDS": threading.Thread(target=self.ids_worker, daemon=True).start()
        elif algo == "UCS": threading.Thread(target=self.ucs_worker, daemon=True).start()
        elif algo == "Greedy": threading.Thread(target=self.greedy_worker, daemon=True).start()
        elif algo == "A*": threading.Thread(target=self.astar_worker, daemon=True).start()
        elif algo == "Leo đồi": threading.Thread(target=self.hill_climbing_worker, daemon=True).start()
        elif algo == "Leo đồi dốc nhất": threading.Thread(target=self.steepest_ascent_worker, daemon=True).start()
        elif algo == "Leo đồi ngẫu nhiên": threading.Thread(target=self.stochastic_hill_climbing_worker, daemon=True).start()
        elif algo == "Leo đồi lặp lại": threading.Thread(target=self.random_restart_worker, daemon=True).start()
        elif algo == "Local Beam Search": threading.Thread(target=self.local_beam_search_worker, daemon=True).start()

    def process_solution(self, solution_node, algo_name):
        self.is_searching = False
        self.btn_apply.config(state=tk.NORMAL)
        self.btn_gen.config(state=tk.NORMAL)
        self.btn_solve.config(state=tk.NORMAL)
        
        if not solution_node:
            self.log_trace_sync("Quá trình kết thúc. Thuật toán bế tắc.")
            messagebox.showinfo("Thông báo", "Thuật toán không thể tìm được đường đi (Bế tắc tại Local Maxima hoặc giới hạn trạng thái)")
            return
            
        self.log_trace_sync("-" * 30)
        self.log_trace_sync("Giải xong. Mở tab Kết quả để xem.")

        self.path = []
        current = solution_node
        while current is not None:
            self.path.append(current)
            current = current.parent
            
        self.path = self.path[::-1]
        path_length = len(self.path) - 1
        
        self.history_listbox.delete(0, tk.END)
        items = [f"Đã hoàn thành với đường đi: {path_length} bước", "-"*20]
        
        limit_print = min(path_length, 200)
        for i in range(1, limit_print + 1):
            items.append(f"Bước {i} trạng thái {self.path[i].move_action}")
        
        if path_length > 200:
            items.append(f"... (Đã ẩn {path_length - 200} bước)")
            
        self.history_listbox.insert(tk.END, *items)
        self.enable_anim_controls()
        self.current_step = 0

    # ==================== ALGORITHMS ====================

    def bfs_worker(self):
        row, col = Find_blank(self.puzzle)
        start_node = NODE(self.puzzle, None, None, row, col)
        queue = deque([start_node])
        explored = {tuple(self.puzzle.flatten())}
        
        while queue and self.is_searching:
            cur_node = queue.popleft()
            self.stats["nodes"] += 1
            if self.stats["nodes"] % 200 == 0:
                current_mem = len(queue) + len(explored)
                if current_mem > self.stats["memory"]: self.stats["memory"] = current_mem

            show_log = self.stats["nodes"] <= 30
            if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Trích xuất Queue")

            if np.array_equal(cur_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, cur_node, "BFS")
                return

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
                    
            if show_log: self.log_trace_sync(f"  => Sinh: {generated} | Nhận: {added} | Trùng: {skipped}\n")
            elif self.stats["nodes"] == 31: self.log_trace_sync("... (Ẩn log chi tiết) ...")
                
        self.root.after(0, self.process_solution, None, "BFS")

    def dfs_worker(self):
        row, col = Find_blank(self.puzzle)
        start_node = NODE(self.puzzle, None, None, row, col)
        stack = [start_node]
        explored = {tuple(self.puzzle.flatten())}
        
        while stack and self.is_searching:
            cur_node = stack.pop()
            self.stats["nodes"] += 1
            if self.stats["nodes"] % 200 == 0:
                current_mem = len(stack) + len(explored)
                if current_mem > self.stats["memory"]: self.stats["memory"] = current_mem

            show_log = self.stats["nodes"] <= 30
            if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Trích xuất Stack")

            if np.array_equal(cur_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, cur_node, "DFS")
                return

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

            if show_log: self.log_trace_sync(f"  => Sinh: {generated} | Nhận: {added} | Trùng: {skipped}\n")
            elif self.stats["nodes"] == 31: self.log_trace_sync("... (Ẩn log chi tiết) ...")

        self.root.after(0, self.process_solution, None, "DFS")

    def ids_worker(self):
        row, col = Find_blank(self.puzzle)
        start_node = NODE(self.puzzle, None, None, row, col)
        solution = None
        max_depth = 35 
        
        def dls(node, depth_limit):
            explored = {tuple(node.state.flatten()): 0} 
            stack = [(node, 0)]
            while stack and self.is_searching:
                cur_node, cur_depth = stack.pop()
                self.stats["nodes"] += 1
                if self.stats["nodes"] % 50 == 0:
                    current_mem = len(stack) + len(explored)
                    if current_mem > self.stats["memory"]: self.stats["memory"] = current_mem
                
                show_log = self.stats["nodes"] <= 50 
                if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Xét mức sâu {cur_depth}")

                if np.array_equal(cur_node.state, self.target_puzzle): return cur_node
                    
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
                
                if show_log and cur_depth < depth_limit:
                    self.log_trace_sync(f"  => Sinh: {generated} | Nhận: {added} | Bỏ qua: {skipped}\n")
                elif self.stats["nodes"] == 51: self.log_trace_sync("... (Ẩn log chi tiết) ...")
            return None

        for limit in range(max_depth):
            if not self.is_searching: break
            self.root.after(0, self.log_trace_sync, f"\n--- Giới hạn độ sâu hiện tại: {limit} ---")
            solution = dls(start_node, limit)
            if solution is not None: break
        self.root.after(0, self.process_solution, solution, "IDS")

    def ucs_worker(self):
        row, col = Find_blank(self.puzzle)
        start_node = NODE(self.puzzle, None, None, row, col)
        queue = PriorityQueue()
        push_count = 0
        queue.put((0, push_count, start_node))
        push_count += 1
        explored = {tuple(self.puzzle.flatten())}
        
        while not queue.empty() and self.is_searching:
            g_cost, _, cur_node = queue.get()
            self.stats["nodes"] += 1
            if self.stats["nodes"] % 200 == 0:
                current_mem = queue.qsize() + len(explored)
                if current_mem > self.stats["memory"]: self.stats["memory"] = current_mem

            show_log = self.stats["nodes"] <= 30
            if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Trích xuất PriorityQueue (cost={g_cost})")

            if np.array_equal(cur_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, cur_node, "UCS")
                return

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
                    
            if show_log: self.log_trace_sync(f"  => Sinh: {generated} | Nhận: {added} | Trùng: {skipped}\n")
            elif self.stats["nodes"] == 31: self.log_trace_sync("... (Ẩn log chi tiết) ...")
        self.root.after(0, self.process_solution, None, "UCS")

    def greedy_worker(self):
        row, col = Find_blank(self.puzzle)
        start_node = NODE(self.puzzle, None, None, row, col)
        queue = PriorityQueue()
        push_count = 0
        h_cost = pathcost(start_node.state, self.target_puzzle)
        queue.put((h_cost, push_count, start_node))
        push_count += 1
        explored = {tuple(self.puzzle.flatten())}
        
        while not queue.empty() and self.is_searching:
            current_h, _, cur_node = queue.get()
            self.stats["nodes"] += 1
            if self.stats["nodes"] % 200 == 0:
                current_mem = queue.qsize() + len(explored)
                if current_mem > self.stats["memory"]: self.stats["memory"] = current_mem

            show_log = self.stats["nodes"] <= 30
            if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Trích xuất PriorityQueue (h={current_h})")

            if np.array_equal(cur_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, cur_node, "Greedy")
                return

            generated = added = skipped = 0
            for move in get_move(cur_node.row, cur_node.col):
                generated += 1
                new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
                state_tuple = tuple(new_puzzle.flatten())
                if state_tuple not in explored:
                    explored.add(state_tuple)
                    new_h = pathcost(new_puzzle, self.target_puzzle)
                    child_node = NODE(new_puzzle, cur_node, move, new_r, new_c)
                    queue.put((new_h, push_count, child_node))
                    push_count += 1
                    added += 1
                else: skipped += 1
                    
            if show_log: self.log_trace_sync(f"  => Sinh: {generated} | Nhận: {added} | Trùng: {skipped}\n")
            elif self.stats["nodes"] == 31: self.log_trace_sync("... (Ẩn log chi tiết) ...")
        self.root.after(0, self.process_solution, None, "Greedy")

    def astar_worker(self):
        row, col = Find_blank(self.puzzle)
        start_node = NODE(self.puzzle, None, None, row, col)
        queue = PriorityQueue()
        push_count = 0
        g_cost = 0
        h_cost = pathcost(start_node.state, self.target_puzzle)
        f_cost = g_cost + h_cost
        queue.put((f_cost, push_count, g_cost, start_node))
        push_count += 1
        explored = {tuple(self.puzzle.flatten())}
        
        while not queue.empty() and self.is_searching:
            current_f, _, current_g, cur_node = queue.get()
            self.stats["nodes"] += 1
            if self.stats["nodes"] % 200 == 0:
                current_mem = queue.qsize() + len(explored)
                if current_mem > self.stats["memory"]: self.stats["memory"] = current_mem

            show_log = self.stats["nodes"] <= 30
            if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Trích xuất PriorityQueue (f={current_f}, g={current_g})")

            if np.array_equal(cur_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, cur_node, "A*")
                return

            generated = added = skipped = 0
            for move in get_move(cur_node.row, cur_node.col):
                generated += 1
                new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
                state_tuple = tuple(new_puzzle.flatten())
                if state_tuple not in explored:
                    explored.add(state_tuple)
                    new_g = current_g + 1
                    new_h = pathcost(new_puzzle, self.target_puzzle)
                    new_f = new_g + new_h
                    child_node = NODE(new_puzzle, cur_node, move, new_r, new_c)
                    queue.put((new_f, push_count, new_g, child_node))
                    push_count += 1
                    added += 1
                else: skipped += 1
                    
            if show_log: self.log_trace_sync(f"  => Sinh: {generated} | Nhận: {added} | Trùng: {skipped}\n")
            elif self.stats["nodes"] == 31: self.log_trace_sync("... (Ẩn log chi tiết) ...")
        self.root.after(0, self.process_solution, None, "A*")

    def hill_climbing_worker(self):
        row, col = Find_blank(self.puzzle)
        current_node = NODE(self.puzzle, None, None, row, col)
        explored = {tuple(self.puzzle.flatten())}
        
        while self.is_searching:
            self.stats["nodes"] += 1
            if self.stats["nodes"] % 10 == 0:
                self.stats["memory"] = len(explored)

            current_h = pathcost(current_node.state, self.target_puzzle)
            show_log = self.stats["nodes"] <= 30
            if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Xét đỉnh hiện tại (h={current_h})")

            if np.array_equal(current_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, current_node, "Leo đồi")
                return

            found_better = False
            for move in get_move(current_node.row, current_node.col):
                new_puzzle, new_r, new_c = action(current_node.state, move, current_node.row, current_node.col)
                state_tuple = tuple(new_puzzle.flatten())
                if state_tuple not in explored:
                    new_h = pathcost(new_puzzle, self.target_puzzle)
                    if new_h < current_h:
                        explored.add(state_tuple)
                        current_node = NODE(new_puzzle, current_node, move, new_r, new_c)
                        found_better = True
                        if show_log: self.log_trace_sync(f"  + Áp dụng hướng {move} (h={new_h} < {current_h})\n")
                        break 
                else: pass
            if not found_better:
                self.log_trace_sync(f"Trạng thái cực đại cục bộ. Hủy bỏ thuật toán.")
                self.root.after(0, self.process_solution, None, "Leo đồi")
                return

    def steepest_ascent_worker(self):
        row, col = Find_blank(self.puzzle)
        current_node = NODE(self.puzzle, None, None, row, col)
        explored = {tuple(self.puzzle.flatten())}

        while self.is_searching:
            self.stats["nodes"] += 1
            if self.stats["nodes"] % 10 == 0:
                self.stats["memory"] = len(explored)

            current_h = pathcost(current_node.state, self.target_puzzle)
            show_log = self.stats["nodes"] <= 30
            if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Xét đỉnh hiện tại (h={current_h})")

            if np.array_equal(current_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, current_node, "Leo đồi dốc nhất")
                return

            best_move = None
            best_node = None
            best_h = current_h 

            for move in get_move(current_node.row, current_node.col):
                new_puzzle, new_r, new_c = action(current_node.state, move, current_node.row, current_node.col)
                state_tuple = tuple(new_puzzle.flatten())
                if state_tuple not in explored:
                    new_h = pathcost(new_puzzle, self.target_puzzle)
                    if new_h < best_h:
                        best_h = new_h
                        best_move = move
                        best_node = NODE(new_puzzle, current_node, move, new_r, new_c)

            if best_node is not None:
                explored.add(tuple(best_node.state.flatten()))
                current_node = best_node
                if show_log: self.log_trace_sync(f"  + Áp dụng hướng tối ưu {best_move} (h={best_h})\n")
            else:
                self.log_trace_sync(f"Trạng thái cực đại cục bộ. Hủy bỏ thuật toán.")
                self.root.after(0, self.process_solution, None, "Leo đồi dốc nhất")
                return

    def stochastic_hill_climbing_worker(self):
        row, col = Find_blank(self.puzzle)
        current_node = NODE(self.puzzle, None, None, row, col)
        explored = {tuple(self.puzzle.flatten())}

        while self.is_searching:
            self.stats["nodes"] += 1
            if self.stats["nodes"] % 10 == 0:
                self.stats["memory"] = len(explored)

            current_h = pathcost(current_node.state, self.target_puzzle)
            show_log = self.stats["nodes"] <= 30
            if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Xét đỉnh (h={current_h})")

            if np.array_equal(current_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, current_node, "Leo đồi ngẫu nhiên")
                return

            better_neighbors = []
            for move in get_move(current_node.row, current_node.col):
                new_puzzle, new_r, new_c = action(current_node.state, move, current_node.row, current_node.col)
                state_tuple = tuple(new_puzzle.flatten())

                if state_tuple not in explored:
                    new_h = pathcost(new_puzzle, self.target_puzzle)
                    if new_h < current_h:
                        better_neighbors.append((new_h, move, NODE(new_puzzle, current_node, move, new_r, new_c)))

            if better_neighbors:
                chosen_h, chosen_move, chosen_node = random.choice(better_neighbors)
                explored.add(tuple(chosen_node.state.flatten()))
                current_node = chosen_node
                if show_log: self.log_trace_sync(f"  + Lựa chọn ngẫu nhiên hướng {chosen_move} (h={chosen_h})\n")
            else:
                self.log_trace_sync(f"Trạng thái cực đại cục bộ. Hủy bỏ thuật toán.")
                self.root.after(0, self.process_solution, None, "Leo đồi ngẫu nhiên")
                return

    def random_restart_worker(self):
        row, col = Find_blank(self.puzzle)
        current_node = NODE(self.puzzle, None, None, row, col)
        explored = {tuple(self.puzzle.flatten())}
        max_restarts = 50
        restarts = 0

        while self.is_searching:
            self.stats["nodes"] += 1
            if self.stats["nodes"] % 10 == 0:
                self.stats["memory"] = len(explored)

            current_h = pathcost(current_node.state, self.target_puzzle)
            show_log = self.stats["nodes"] <= 30
            if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Xét đỉnh (h={current_h})")

            if np.array_equal(current_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, current_node, "Leo đồi lặp lại")
                return

            best_move = None
            best_node = None
            best_h = current_h 

            for move in get_move(current_node.row, current_node.col):
                new_puzzle, new_r, new_c = action(current_node.state, move, current_node.row, current_node.col)
                state_tuple = tuple(new_puzzle.flatten())

                if state_tuple not in explored:
                    new_h = pathcost(new_puzzle, self.target_puzzle)
                    if new_h < best_h:
                        best_h = new_h
                        best_move = move
                        best_node = NODE(new_puzzle, current_node, move, new_r, new_c)

            if best_node is not None:
                explored.add(tuple(best_node.state.flatten()))
                current_node = best_node
                if show_log: self.log_trace_sync(f"  + Áp dụng hướng tối ưu {best_move} (h={best_h})\n")
            else:
                if restarts < max_restarts:
                    restarts += 1
                    self.log_trace_sync(f"-> Cực đại cục bộ. Khởi động vòng lặp ngẫu nhiên (Lần {restarts})")
                    for _ in range(5):
                        valid_moves = get_move(current_node.row, current_node.col)
                        r_move = random.choice(valid_moves)
                        n_puz, n_r, n_c = action(current_node.state, r_move, current_node.row, current_node.col)
                        current_node = NODE(n_puz, current_node, r_move, n_r, n_c)
                        explored.add(tuple(n_puz.flatten()))
                else:
                    self.log_trace_sync(f"Vượt quá giới hạn lặp lại. Hủy bỏ thuật toán.")
                    self.root.after(0, self.process_solution, None, "Leo đồi lặp lại")
                    return

    def local_beam_search_worker(self):
        row, col = Find_blank(self.puzzle)
        start_node = NODE(self.puzzle, None, None, row, col)
        
        k = 3 
        beam = [start_node]
        explored = {tuple(self.puzzle.flatten())}
        
        while beam and self.is_searching:
            self.stats["nodes"] += 1
            if self.stats["nodes"] % 10 == 0:
                self.stats["memory"] = len(explored)

            show_log = self.stats["nodes"] <= 30
            if show_log: self.log_trace_sync(f"[Bước {self.stats['nodes']}] Số trạng thái duy trì: {len(beam)}")

            next_candidates = []
            for cur_node in beam:
                if np.array_equal(cur_node.state, self.target_puzzle):
                    self.root.after(0, self.process_solution, cur_node, "Local Beam Search")
                    return

                for move in get_move(cur_node.row, cur_node.col):
                    new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
                    state_tuple = tuple(new_puzzle.flatten())
                    
                    if state_tuple not in explored:
                        explored.add(state_tuple)
                        new_h = pathcost(new_puzzle, self.target_puzzle)
                        child_node = NODE(new_puzzle, cur_node, move, new_r, new_c)
                        next_candidates.append((new_h, child_node))
            
            if not next_candidates:
                self.log_trace_sync(f"Trạng thái cạn kiệt. Hủy bỏ thuật toán.")
                self.root.after(0, self.process_solution, None, "Local Beam Search")
                return

            next_candidates.sort(key=lambda x: x[0])
            beam = [item[1] for item in next_candidates[:k]]
            
            if show_log:
                best_h = next_candidates[0][0]
                self.log_trace_sync(f"  + Cập nhật tập trạng thái (h tối ưu = {best_h})\n")
            elif self.stats["nodes"] == 31:
                self.log_trace_sync("... (Ẩn log chi tiết tiếp theo) ...")

    # ==================== CONTROLS ====================

    def update_view_animate(self, step_index, direction="forward"):
        if not self.path or self.is_sliding: return
        
        offset_list = 2 
        target_lb_idx = step_index + offset_list
        if target_lb_idx < self.history_listbox.size():
            self.history_listbox.selection_clear(0, tk.END)
            self.history_listbox.selection_set(target_lb_idx)
            self.history_listbox.see(target_lb_idx)
            
        self.btn_prev.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_step < len(self.path) - 1 else tk.DISABLED)

        current_node = self.path[step_index]

        if step_index == 0 or direction == "jump":
            self.place_tiles_instantly(current_node.state)
            if self.is_playing: self.current_after_job = self.root.after(self.speed_scale.get(), self.animate_loop)
            return

        if direction == "forward":
            parent_node = self.path[step_index - 1]
            tile_value = parent_node.state[current_node.row, current_node.col]
            start_coords = self.get_coords(current_node.row, current_node.col)
            end_coords = self.get_coords(parent_node.row, parent_node.col)
        else:
            child_node = self.path[step_index + 1]
            tile_value = current_node.state[child_node.row, child_node.col]
            start_coords = self.get_coords(current_node.row, current_node.col)
            end_coords = self.get_coords(child_node.row, child_node.col)

        if tile_value == 0:
            self.place_tiles_instantly(current_node.state)
            if self.is_playing: self.current_after_job = self.root.after(self.speed_scale.get(), self.animate_loop)
            return

        self.slide_tile(self.tile_widgets[tile_value], start_coords, end_coords, self.on_slide_complete_callback)

    def on_slide_complete_callback(self):
        if self.is_playing:
            self.current_after_job = self.root.after(int(self.speed_scale.get() * 0.2), self.animate_loop)

    def animate_loop(self):
        if not self.is_playing or self.is_sliding: return
        if self.current_step < len(self.path) - 1:
            self.current_step += 1
            self.update_view_animate(self.current_step, direction="forward")
        else:
            self.is_playing = False; self.btn_play.config(text="Phát")

    def toggle_play(self):
        self.log_tabs.select(self.path_frame)
        if self.is_playing:
            self.is_playing = False; self.btn_play.config(text="Phát")
            self.stop_current_animation()
            if self.path: self.place_tiles_instantly(self.path[self.current_step].state)
        else:
            if self.current_step >= len(self.path) - 1:
                self.current_step = 0
                self.place_tiles_instantly(self.path[self.current_step].state)
            self.is_playing = True; self.btn_play.config(text="Tạm dừng")
            self.animate_loop()

    def next_step(self):
        self.log_tabs.select(self.path_frame)
        if self.current_step >= len(self.path) - 1: return
        self.is_playing = False; self.btn_play.config(text="Phát"); self.stop_current_animation()
        self.current_step += 1; self.update_view_animate(self.current_step, direction="forward")

    def prev_step(self):
        self.log_tabs.select(self.path_frame)
        if self.current_step <= 0: return
        self.is_playing = False; self.btn_play.config(text="Phát"); self.stop_current_animation()
        self.current_step -= 1; self.update_view_animate(self.current_step, direction="backward")

    def on_history_select(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            offset = 2
            if idx >= offset:
                step = idx - offset
                if step < len(self.path):
                    self.is_playing = False; self.btn_play.config(text="Phát"); self.stop_current_animation()
                    self.current_step = step
                    self.update_view_animate(self.current_step, direction="jump")

    def disable_anim_controls(self):
        self.btn_prev.config(state=tk.DISABLED); self.btn_play.config(state=tk.DISABLED); self.btn_next.config(state=tk.DISABLED)

    def enable_anim_controls(self):
        self.btn_prev.config(state=tk.NORMAL); self.btn_play.config(state=tk.NORMAL); self.btn_next.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    try: root.tk.call('tk', 'scaling', 1.5)
    except: pass
    app = PuzzleGUI(root)
    root.mainloop()
