import numpy as np
import random
from collections import deque
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

class AdvancedPuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver (BFS / DFS / IDS)")
        self.root.geometry("900x650")
        self.root.configure(padx=20, pady=20)

        self.TILE_SIZE = 100
        self.PAD = 5
        self.GRID_SIZE = (self.TILE_SIZE + self.PAD) * 3 + self.PAD

        self.target_puzzle = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 0]])
        self.puzzle = None
        self.path = []
        self.current_step = 0
        
        self.is_playing = False
        self.is_sliding = False
        self.is_searching = False
        self.current_after_job = None 
        
        self.stats = {"nodes": 0, "memory": 0, "start_time": 0}

        self.setup_ui()
        self.generate_new_puzzle()

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
            
        dash_frame = tk.LabelFrame(self.left_frame, text="Thống kê trực tiếp", padx=10, pady=10, font=("Helvetica", 10, "bold"))
        dash_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_time = tk.Label(dash_frame, text="Thời gian: 0.00s", font=("Helvetica", 10))
        self.lbl_time.grid(row=0, column=0, sticky="w", pady=2)
        
        self.lbl_nodes = tk.Label(dash_frame, text="Số nút đã duyệt: 0", font=("Helvetica", 10))
        self.lbl_nodes.grid(row=1, column=0, sticky="w", pady=2)
        
        self.lbl_mem = tk.Label(dash_frame, text="Trạng thái lưu trữ (RAM): 0", font=("Helvetica", 10))
        self.lbl_mem.grid(row=2, column=0, sticky="w", pady=2)

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        algo_frame = tk.LabelFrame(self.right_frame, text="Điều khiển", padx=10, pady=10)
        algo_frame.pack(fill=tk.X)
        
        self.algo_var = tk.StringVar()
        self.algo_combo = ttk.Combobox(algo_frame, textvariable=self.algo_var, state="readonly", font=("Helvetica", 10))
        self.algo_combo['values'] = ("BFS", "DFS", "IDS")
        self.algo_combo.current(0)
        self.algo_combo.pack(fill=tk.X, pady=5)
        
        btn_frame = tk.Frame(algo_frame)
        btn_frame.pack(fill=tk.X)
        self.btn_gen = tk.Button(btn_frame, text="Sinh Mới", command=self.generate_new_puzzle)
        self.btn_gen.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.btn_solve = tk.Button(btn_frame, text="Giải", command=self.start_solve, bg="#4CAF50", fg="white", font=("Helvetica", 10, "bold"))
        self.btn_solve.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        anim_ctrl_frame = tk.LabelFrame(self.right_frame, text="Trình phát", padx=10, pady=10)
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

        hist_frame = tk.LabelFrame(self.right_frame, text="Chi tiết", padx=10, pady=5)
        hist_frame.pack(fill=tk.BOTH, expand=True)
        
        self.scrollbar = tk.Scrollbar(hist_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox = tk.Listbox(hist_frame, yscrollcommand=self.scrollbar.set, font=("Consolas", 10), bg="#f4f4f4")
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.history_listbox.yview)
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)

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
            self.lbl_nodes.config(text=f"Số nút đã duyệt: {self.stats['nodes']}")
            self.lbl_mem.config(text=f"Trạng thái lưu trữ (RAM): {self.stats['memory']}")
            self.root.after(100, self.start_dashboard_updates)

    def log_sync(self, message):
        self.history_listbox.insert(tk.END, message)
        self.history_listbox.see(tk.END)
        self.history_listbox.update_idletasks()

    def generate_new_puzzle(self):
        self.stop_current_animation()
        self.is_playing = False; self.is_searching = False
        self.btn_play.config(text="Phát")
        self.puzzle = Inputpuzzle()
        self.path = []
        self.place_tiles_instantly(self.puzzle)
        self.history_listbox.delete(0, tk.END)
        self.disable_anim_controls()
        
        self.stats = {"nodes": 0, "memory": 0, "start_time": 0}
        self.lbl_time.config(text="Thời gian: 0.00s")
        self.lbl_nodes.config(text="Số nút đã duyệt: 0")
        self.lbl_mem.config(text="Trạng thái lưu trữ (RAM): 0")

    def start_solve(self):
        self.btn_gen.config(state=tk.DISABLED)
        self.btn_solve.config(state=tk.DISABLED)
        self.disable_anim_controls()
        self.stop_current_animation()
        
        self.history_listbox.delete(0, tk.END)
        self.place_tiles_instantly(self.puzzle) 
        
        self.is_searching = True
        self.stats["start_time"] = time.time()
        self.stats["nodes"] = 0
        self.stats["memory"] = 0
        self.start_dashboard_updates()
        
        algo = self.algo_var.get()
        if algo == "BFS":
            threading.Thread(target=self.bfs_worker, daemon=True).start()
        elif algo == "DFS":
            threading.Thread(target=self.dfs_worker, daemon=True).start()
        else:
            threading.Thread(target=self.ids_worker, daemon=True).start()

    def process_solution(self, solution_node, algo_name):
        self.is_searching = False
        self.btn_gen.config(state=tk.NORMAL)
        self.btn_solve.config(state=tk.NORMAL)
        
        if not solution_node:
            messagebox.showerror("Lỗi", "Không tìm thấy đường đi")
            return

        self.path = []
        current = solution_node
        while current is not None:
            self.path.append(current)
            current = current.parent
            
        self.path = self.path[::-1]
        path_length = len(self.path) - 1
        elapsed = time.time() - self.stats["start_time"]

        self.history_listbox.delete(0, tk.END)
        
        items = []
        items.append(f"=== TỔNG KẾT {algo_name} ===")
        items.append(f"Thời gian chạy: {elapsed:.2f} giây")
        items.append(f"Độ dài đường đi: {path_length} bước")
        items.append(f"Số trạng thái duyệt: {self.stats['nodes']}")
        items.append(f"Lượng RAM tiêu thụ: {self.stats['memory']} trạng thái")
        items.append("-" * 30)
        items.append("CHI TIẾT CÁC BƯỚC DI CHUYỂN:")
        
        limit_print = min(path_length, 200)
        for i in range(1, limit_print + 1):
            items.append(f"Bước {i} trạng thái {self.path[i].move_action}")
        
        if path_length > 200:
            items.append(f"... (Đã ẩn {path_length - 200} bước)")
            
        self.history_listbox.insert(tk.END, *items)
        self.enable_anim_controls()
        self.current_step = 0
    
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

            if np.array_equal(cur_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, cur_node, "BFS")
                return

            for move in get_move(cur_node.row, cur_node.col):
                new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
                state_tuple = tuple(new_puzzle.flatten())
                if state_tuple not in explored:
                    explored.add(state_tuple)
                    queue.append(NODE(new_puzzle, cur_node, move, new_r, new_c))
                    
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

            if np.array_equal(cur_node.state, self.target_puzzle):
                self.root.after(0, self.process_solution, cur_node, "DFS")
                return

            valid_moves = get_move(cur_node.row, cur_node.col)
            valid_moves.reverse()
            for move in valid_moves:
                new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
                state_tuple = tuple(new_puzzle.flatten())
                if state_tuple not in explored:
                    explored.add(state_tuple)
                    stack.append(NODE(new_puzzle, cur_node, move, new_r, new_c))

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
                
                if np.array_equal(cur_node.state, self.target_puzzle):
                    return cur_node
                    
                if cur_depth < depth_limit:
                    valid_moves = get_move(cur_node.row, cur_node.col)
                    valid_moves.reverse()
                    for move in valid_moves:
                        new_puzzle, new_r, new_c = action(cur_node.state, move, cur_node.row, cur_node.col)
                        state_tuple = tuple(new_puzzle.flatten())
                        
                        if state_tuple not in explored or explored[state_tuple] > cur_depth + 1:
                            explored[state_tuple] = cur_depth + 1
                            stack.append((NODE(new_puzzle, cur_node, move, new_r, new_c), cur_depth + 1))
            return None

        for limit in range(max_depth):
            if not self.is_searching: break
            self.root.after(0, self.log_sync, f"Đang duyệt độ sâu: L = {limit}")
            
            solution = dls(start_node, limit)
            if solution is not None:
                break
                
        self.root.after(0, self.process_solution, solution, "IDS")
    
    def update_view_animate(self, step_index, direction="forward"):
        if not self.path or self.is_sliding: return
        
        offset_list = 7 
        target_lb_idx = step_index - 1 + offset_list
        if target_lb_idx < self.history_listbox.size() and step_index > 0:
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
        if self.current_step >= len(self.path) - 1: return
        self.is_playing = False; self.btn_play.config(text="Phát"); self.stop_current_animation()
        self.current_step += 1; self.update_view_animate(self.current_step, direction="forward")

    def prev_step(self):
        if self.current_step <= 0: return
        self.is_playing = False; self.btn_play.config(text="Phát"); self.stop_current_animation()
        self.current_step -= 1; self.update_view_animate(self.current_step, direction="backward")

    def on_history_select(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            offset = 7
            if idx >= offset:
                step = idx - offset + 1
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
    app = AdvancedPuzzleGUI(root)
    root.mainloop()
