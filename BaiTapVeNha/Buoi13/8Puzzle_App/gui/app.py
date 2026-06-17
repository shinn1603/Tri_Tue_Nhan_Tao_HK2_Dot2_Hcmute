import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import time

from core.puzzle_state import check_solvable
from core.uncertain_env import LOOP_MARKER
from .style import setup_styles
from .workers import start_search_thread

class PuzzleGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle Solver System")
        self.root.geometry("1100x800")
        
        setup_styles(self.root)
        
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
        
        self.has_wildcards = False
        self.wildcard_input = None
        
        self.stats = {"nodes": 0, "memory": 0, "start_time": 0}
        self.app_mode = "Normal" # Có thể là "Normal" hoặc "CSPs"

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
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.left_frame = ttk.Frame(main_paned, padding=10)
        main_paned.add(self.left_frame, weight=1)

        ttk.Label(self.left_frame, text="Mô phỏng 8-Puzzle", style="Title.TLabel").pack(pady=5)

        self.canvas_bg = tk.Frame(self.left_frame, bg="#2C3E50", width=self.GRID_SIZE, height=self.GRID_SIZE)
        self.canvas_bg.pack(pady=15)
        
        self.tile_widgets = {}
        for val in range(0, 9):
            lbl = tk.Label(self.canvas_bg, text=str(val), font=("Segoe UI", 48, "bold"), 
                           bg="white", fg="#2C3E50", relief="flat", borderwidth=0)
            lbl.place(width=self.TILE_SIZE, height=self.TILE_SIZE) 
            self.tile_widgets[val] = lbl
            
        dash_frame = ttk.LabelFrame(self.left_frame, text="Thống kê", padding=15)
        dash_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_time = ttk.Label(dash_frame, text="Thời gian: 0.00s")
        self.lbl_time.grid(row=0, column=0, sticky="w", pady=4)
        
        self.lbl_nodes = ttk.Label(dash_frame, text="Đã duyệt: 0 trạng thái")
        self.lbl_nodes.grid(row=1, column=0, sticky="w", pady=4)
        
        self.lbl_mem = ttk.Label(dash_frame, text="Đã lưu (RAM): 0 trạng thái")
        self.lbl_mem.grid(row=2, column=0, sticky="w", pady=4)

        self.right_frame = ttk.Frame(main_paned, padding=10)
        main_paned.add(self.right_frame, weight=2)

        matrix_frame = ttk.LabelFrame(self.right_frame, text="Dữ liệu Trạng Thái", padding=10)
        matrix_frame.pack(fill=tk.X, pady=5)

        start_frame = ttk.Frame(matrix_frame)
        start_frame.pack(side=tk.LEFT, padx=15)
        ttk.Label(start_frame, text="Bắt đầu (dùng * cho ô chưa biết)").grid(row=0, column=0, columnspan=3, pady=(0, 5))
        self.start_entries = []
        for r in range(3):
            row_entries = []
            for c in range(3):
                e = ttk.Entry(start_frame, width=3, font=("Segoe UI", 12), justify="center")
                e.grid(row=r+1, column=c, padx=2, pady=2)
                row_entries.append(e)
            self.start_entries.append(row_entries)

        target_frame = ttk.Frame(matrix_frame)
        target_frame.pack(side=tk.LEFT, padx=15)
        ttk.Label(target_frame, text="Đích (dùng * cho ô chưa biết)").grid(row=0, column=0, columnspan=3, pady=(0, 5))
        self.target_entries = []
        for r in range(3):
            row_entries = []
            for c in range(3):
                e = ttk.Entry(target_frame, width=3, font=("Segoe UI", 12), justify="center")
                e.grid(row=r+1, column=c, padx=2, pady=2)
                row_entries.append(e)
            self.target_entries.append(row_entries)

        btn_frame_matrix = ttk.Frame(matrix_frame)
        btn_frame_matrix.pack(side=tk.LEFT, padx=15, expand=True, fill=tk.BOTH)
        self.btn_apply = ttk.Button(btn_frame_matrix, text="Cập nhật Nhập liệu", command=self.apply_input)
        self.btn_apply.pack(fill=tk.X, pady=2)
        self.btn_gen = ttk.Button(btn_frame_matrix, text="Sinh Ngẫu Nhiên", command=self.generate_new_puzzle)
        self.btn_gen.pack(fill=tk.X, pady=2)

        algo_frame = ttk.LabelFrame(self.right_frame, text="Cài đặt Thuật Toán", padding=10)
        algo_frame.pack(fill=tk.X, pady=10)
        
        mode_frame = ttk.Frame(algo_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(mode_frame, text="Chế độ:").pack(side=tk.LEFT, padx=(0, 5))
        self.mode_var = tk.StringVar(value="Normal")
        ttk.Radiobutton(mode_frame, text="Bình thường", variable=self.mode_var, value="Normal", command=self.on_mode_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="CSPs (Điền số)", variable=self.mode_var, value="CSPs", command=self.on_mode_change).pack(side=tk.LEFT, padx=5)

        self.algo_var = tk.StringVar()
        self.algo_combo = ttk.Combobox(algo_frame, textvariable=self.algo_var, state="readonly", font=("Segoe UI", 10))
        self.on_mode_change()
        self.algo_combo.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        
        self.btn_solve = ttk.Button(algo_frame, text="🚀 GIẢI", command=self.start_solve, style="Success.TButton")
        self.btn_solve.pack(side=tk.LEFT, padx=5)

        anim_ctrl_frame = ttk.LabelFrame(self.right_frame, text="Điều khiển Hoạt ảnh", padding=10)
        anim_ctrl_frame.pack(fill=tk.X, pady=5)
        
        ctrl_btns = ttk.Frame(anim_ctrl_frame)
        ctrl_btns.pack()
        self.btn_prev = ttk.Button(ctrl_btns, text="⏮ Trước", command=self.prev_step, state=tk.DISABLED, width=8)
        self.btn_prev.pack(side=tk.LEFT, padx=5)
        self.btn_play = ttk.Button(ctrl_btns, text="▶ Phát", command=self.toggle_play, state=tk.DISABLED, width=10)
        self.btn_play.pack(side=tk.LEFT, padx=5)
        self.btn_next = ttk.Button(ctrl_btns, text="Tiếp ⏭", command=self.next_step, state=tk.DISABLED, width=8)
        self.btn_next.pack(side=tk.LEFT, padx=5)

        self.speed_scale = tk.Scale(anim_ctrl_frame, from_=10, to=1500, resolution=10, orient=tk.HORIZONTAL, label="Tốc độ (ms):", font=("Segoe UI", 9), bg="#FFFFFF", highlightthickness=0)
        self.speed_scale.set(400)
        self.speed_scale.pack(fill=tk.X, pady=(10, 0))

        self.log_tabs = ttk.Notebook(self.right_frame)
        self.log_tabs.pack(fill=tk.BOTH, expand=True, pady=10)

        self.path_frame = ttk.Frame(self.log_tabs)
        self.log_tabs.add(self.path_frame, text="Kết quả")
        self.scrollbar_path = ttk.Scrollbar(self.path_frame)
        self.scrollbar_path.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox = tk.Listbox(self.path_frame, yscrollcommand=self.scrollbar_path.set, font=("Consolas", 11), bg="#FAFAFA", relief="flat")
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_path.config(command=self.history_listbox.yview)
        self.history_listbox.bind('<<ListboxSelect>>', self.on_history_select)

        self.trace_frame = ttk.Frame(self.log_tabs)
        self.log_tabs.add(self.trace_frame, text="Log hệ thống")
        self.scrollbar_trace = ttk.Scrollbar(self.trace_frame)
        self.scrollbar_trace.pack(side=tk.RIGHT, fill=tk.Y)
        self.trace_listbox = tk.Listbox(self.trace_frame, yscrollcommand=self.scrollbar_trace.set, font=("Consolas", 10), bg="#FAFAFA", relief="flat")
        self.trace_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_trace.config(command=self.trace_listbox.yview)

        self.csp_frame = ttk.Frame(self.log_tabs)
        self.log_tabs.add(self.csp_frame, text="Chi tiết CSP & Logic")
        self.scrollbar_csp = ttk.Scrollbar(self.csp_frame)
        self.scrollbar_csp.pack(side=tk.RIGHT, fill=tk.Y)
        self.csp_listbox = tk.Listbox(self.csp_frame, yscrollcommand=self.scrollbar_csp.set, font=("Consolas", 10), bg="#FAFAFA", relief="flat")
        self.csp_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar_csp.config(command=self.csp_listbox.yview)

    def populate_entries(self):
        for r in range(3):
            for c in range(3):
                self.start_entries[r][c].delete(0, tk.END)
                self.start_entries[r][c].insert(0, str(self.puzzle[r, c]))
                
                self.target_entries[r][c].delete(0, tk.END)
                self.target_entries[r][c].insert(0, str(self.target_puzzle[r, c]))

    def on_mode_change(self):
        self.app_mode = self.mode_var.get()
        if self.app_mode == "Normal":
            self.algo_combo['values'] = (
                "BFS", "DFS", "IDS", "UCS", 
                "Greedy", "A*", 
                "Leo đồi", "Leo đồi dốc nhất", 
                "Leo đồi ngẫu nhiên", "Leo đồi lặp lại",
                "Local Beam Search",
                "Conformant Search", "AND-OR Search"
            )
            self.place_tiles_instantly(self.puzzle)
        else:
            self.algo_combo['values'] = (
                "backtracking", "forward checking", "ac3", "min_conflict"
            )
            # Khi chọn CSPs, khởi tạo puzzle trống (mảng -1)
            self.place_tiles_instantly(np.full((3, 3), -1))
        self.algo_combo.current(0)


    def apply_input(self):
        try:
            start_vals = []
            target_vals = []
            has_star = False
            has_star_target = False
            
            for r in range(3):
                for c in range(3):
                    val = self.start_entries[r][c].get().strip()
                    if val == '*':
                        start_vals.append('*')
                        has_star = True
                    else:
                        start_vals.append(int(val))
                        
                    tval = self.target_entries[r][c].get().strip()
                    if tval == '*':
                        target_vals.append('*')
                        has_star_target = True
                    else:
                        target_vals.append(int(tval))
            
            if not has_star_target:
                if sorted(target_vals) != list(range(9)):
                    messagebox.showerror("Lỗi", "Ma trận đích phải chứa các số từ 0 đến 8, không trùng lặp.")
                    return
                new_target = np.array(target_vals).reshape(3, 3)
            else:
                known_tvals = [v for v in target_vals if v != '*']
                if len(known_tvals) != len(set(known_tvals)):
                    messagebox.showerror("Lỗi", "Các số đích đã nhập không được trùng lặp.")
                    return
                for v in known_tvals:
                    if v < 0 or v > 8:
                        messagebox.showerror("Lỗi", "Các số đích phải nằm trong khoảng 0 đến 8.")
                        return
                new_target = np.array(target_vals, dtype=object).reshape(3, 3)
            
            if has_star or has_star_target:
                known_vals = [v for v in start_vals if v != '*']
                star_count = start_vals.count('*')
                
                if star_count > 2:
                    messagebox.showerror("Lỗi", "Chỉ hỗ trợ tối đa 2 ô '*' để đảm bảo tính khả thi.")
                    return
                
                if len(known_vals) != len(set(known_vals)):
                    messagebox.showerror("Lỗi", "Các số đã nhập không được trùng lặp.")
                    return
                
                for v in known_vals:
                    if v < 0 or v > 8:
                        messagebox.showerror("Lỗi", "Các số phải nằm trong khoảng 0 đến 8.")
                        return
                
                self.has_wildcards = True
                self.wildcard_input = start_vals
                self.target_puzzle = new_target
                
                display_vals = []
                missing = list(set(range(9)) - set(known_vals))
                star_idx = 0
                for v in start_vals:
                    if v == '*':
                        display_vals.append(missing[star_idx] if star_idx < len(missing) else 0)
                        star_idx += 1
                    else:
                        display_vals.append(v)
                self.puzzle = np.array(display_vals).reshape(3, 3)
                
                self.reset_gui_state()
                self.place_tiles_instantly(self.puzzle)
                self.log_trace_sync("Đã nhập dữ liệu có ô '*'. Chọn 'Conformant Search' hoặc 'AND-OR Search'.")
            else:
                if sorted(start_vals) != list(range(9)):
                    messagebox.showerror("Lỗi", "Ma trận phải chứa các số từ 0 đến 8, không trùng lặp.")
                    return

                new_start = np.array(start_vals).reshape(3, 3)

                if not check_solvable(new_start, new_target):
                    messagebox.showerror("Lỗi", "Trạng thái bắt đầu và đích không cùng tính chẵn lẻ (không thể giải).")
                    return

                self.has_wildcards = False
                self.wildcard_input = None
                self.puzzle = new_start
                self.target_puzzle = new_target
                self.reset_gui_state()
                self.place_tiles_instantly(self.puzzle)
        except ValueError:
            messagebox.showerror("Lỗi", "Vui lòng nhập số nguyên hợp lệ hoặc ký tự '*'.")

    def generate_new_puzzle(self):
        self.has_wildcards = False
        self.wildcard_input = None
        self.puzzle = self.generate_random_puzzle(self.target_puzzle)
        self.populate_entries()
        self.reset_gui_state()
        self.place_tiles_instantly(self.puzzle)

    def reset_gui_state(self):
        self.stop_current_animation()
        self.is_playing = False
        self.is_searching = False
        self.btn_play.config(text="▶ Phát")
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
        # Ẩn tất cả tile đi trước
        for tile in self.tile_widgets.values():
            tile.place_forget()
            
        for r in range(3):
            for c in range(3):
                val = state[r, c]
                if val > 0 and val <= 8:
                    tile = self.tile_widgets[val]
                    tile.place(x=self.get_coords(r, c)[0], y=self.get_coords(r, c)[1], width=self.TILE_SIZE, height=self.TILE_SIZE)
                    tile.tkraise()
                elif val == 0:
                    if self.app_mode == "CSPs":
                        tile = self.tile_widgets[val]
                        tile.place(x=self.get_coords(r, c)[0], y=self.get_coords(r, c)[1], width=self.TILE_SIZE, height=self.TILE_SIZE)
                        tile.tkraise()
                    else:
                        self.tile_widgets[0].place_forget()

    def slide_tile(self, tile_widget, start_coords, end_coords, callback):
        self.is_sliding = True
        anim_time = self.speed_scale.get() * 0.8
        step_delay = 20 
        steps = max(1, int(anim_time / step_delay))
        
        dx = (end_coords[0] - start_coords[0]) / steps
        dy = (end_coords[1] - start_coords[1]) / steps

        def do_step(step):
            if not self.is_sliding: return
            if step < steps:
                new_x = start_coords[0] + dx * step
                new_y = start_coords[1] + dy * step
                tile_widget.place(x=new_x, y=new_y, width=self.TILE_SIZE, height=self.TILE_SIZE)
                self.current_after_job = self.root.after(step_delay, do_step, step + 1)
            else:
                tile_widget.place(x=end_coords[0], y=end_coords[1], width=self.TILE_SIZE, height=self.TILE_SIZE)
                self.is_sliding = False
                callback()

        do_step(1)

    def start_dashboard_updates(self):
        if self.is_searching:
            elapsed = time.time() - self.stats["start_time"]
            self.lbl_time.config(text=f"Thời gian: {elapsed:.2f}s")
            self.lbl_nodes.config(text=f"Đã duyệt: {self.stats['nodes']} trạng thái")
            self.lbl_mem.config(text=f"Đã lưu (RAM): {self.stats['memory']} trạng thái")
            self.root.after(100, self.start_dashboard_updates)

    def log_trace_sync(self, message):
        if not self.root.winfo_exists(): return
        def update():
            if not self.trace_listbox.winfo_exists(): return
            self.trace_listbox.insert(tk.END, message)
            self.trace_listbox.see(tk.END)
        self.root.after(0, update)

    def log_csp_sync(self, message):
        if not self.root.winfo_exists(): return
        def update():
            if not self.csp_listbox.winfo_exists(): return
            self.csp_listbox.insert(tk.END, message)
            self.csp_listbox.see(tk.END)
        self.root.after(0, update)

    def start_solve(self):
        algo = self.algo_var.get()
        
        if algo == "Conformant Search" and not self.has_wildcards:
            messagebox.showerror("Lỗi", "Conformant Search yêu cầu ít nhất 1 ô '*' trong trạng thái Bắt đầu.")
            return
        
        if self.has_wildcards and algo not in ("Conformant Search", "AND-OR Search"):
            messagebox.showerror("Lỗi", f"Thuật toán '{algo}' không hỗ trợ ô '*'. Chọn 'Conformant Search' hoặc 'AND-OR Search'.")
            return
        
        self.btn_apply.config(state=tk.DISABLED)
        self.btn_gen.config(state=tk.DISABLED)
        self.btn_solve.config(state=tk.DISABLED)
        self.disable_anim_controls()
        self.stop_current_animation()
        
        self.history_listbox.delete(0, tk.END)
        self.trace_listbox.delete(0, tk.END)
        self.csp_listbox.delete(0, tk.END)
        
        if self.app_mode == "CSPs":
            self.puzzle = np.full((3, 3), -1)
            
        self.place_tiles_instantly(self.puzzle) 
        
        self.is_searching = True
        self.stats["start_time"] = time.time()
        self.stats["nodes"] = 0
        self.stats["memory"] = 0
        self.start_dashboard_updates()
        
        self.log_tabs.select(self.trace_frame) 
        
        start_search_thread(self, algo)

    def process_csp_solution(self, log_lines, algo_name):
        self.is_searching = False
        self.btn_apply.config(state=tk.NORMAL)
        self.btn_gen.config(state=tk.NORMAL)
        self.btn_solve.config(state=tk.NORMAL)
        
        self.log_trace_sync("-" * 30)
        self.log_trace_sync(f"{algo_name} hoàn tất. Mở tab Chi tiết CSP để xem.")
        
        self.csp_listbox.delete(0, tk.END)
        self.csp_listbox.insert(tk.END, f"═══ KẾT QUẢ: {algo_name.upper()} ═══")
        self.csp_listbox.insert(tk.END, "-" * 40)
        
        if log_lines:
            for line in log_lines:
                self.csp_listbox.insert(tk.END, line)
        else:
            self.csp_listbox.insert(tk.END, "Không tìm thấy kết quả hoặc bị kẹt/bế tắc.")
            
        self.log_tabs.select(self.csp_frame)

    def process_solution(self, solution_node, algo_name):
        self.is_searching = False
        self.btn_apply.config(state=tk.NORMAL)
        self.btn_gen.config(state=tk.NORMAL)
        self.btn_solve.config(state=tk.NORMAL)
        
        if not solution_node:
            self.log_trace_sync("Quá trình kết thúc. Thuật toán bế tắc.")
            messagebox.showinfo("Thông báo", "Thuật toán không thể tìm được đường đi.")
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

    def process_conformant_solution(self, action_list):
        self.is_searching = False
        self.btn_apply.config(state=tk.NORMAL)
        self.btn_gen.config(state=tk.NORMAL)
        self.btn_solve.config(state=tk.NORMAL)
        
        if action_list is None:
            self.log_trace_sync("Conformant Search: Không tìm được lời giải.")
            messagebox.showinfo("Thông báo", "Không tìm được chuỗi hành động chung cho tất cả trạng thái trong Belief State.")
            return
        
        self.log_trace_sync("-" * 30)
        self.log_trace_sync(f"Conformant Search tìm được chuỗi {len(action_list)} hành động!")
        
        self.csp_listbox.delete(0, tk.END)
        items = [
            "═══ KẾT QUẢ CONFORMANT SEARCH ═══",
            f"Chuỗi hành động chung: {len(action_list)} bước",
            "(Áp dụng cho TẤT CẢ trạng thái trong Belief State)",
            "-" * 35,
        ]
        
        for i, act in enumerate(action_list, 1):
            items.append(f"  Bước {i}: {act}")
        
        items.append("-" * 35)
        items.append("Chuỗi hành động này đảm bảo đưa mọi")
        items.append("trạng thái khả thi về trạng thái đích.")
        
        self.csp_listbox.insert(tk.END, *items)
        self.log_tabs.select(self.csp_frame)

    def process_andor_solution(self, plan):
        self.is_searching = False
        self.btn_apply.config(state=tk.NORMAL)
        self.btn_gen.config(state=tk.NORMAL)
        self.btn_solve.config(state=tk.NORMAL)
        
        if plan is None:
            self.log_trace_sync("AND-OR Search: Không tìm được kế hoạch dự phòng.")
            messagebox.showinfo("Thông báo", "AND-OR Search không tìm được kế hoạch dự phòng trong giới hạn độ sâu.")
            return
        
        self.log_trace_sync("-" * 30)
        self.log_trace_sync("AND-OR Search tìm được kế hoạch dự phòng!")
        
        self.csp_listbox.delete(0, tk.END)
        items = [
            "═══ KẾ HOẠCH DỰ PHÒNG (AND-OR) ═══",
            "(Contingency Plan - Cây IF-THEN)",
            "-" * 35,
        ]
        
        self._format_andor_plan(plan, items, indent=0)
        
        items.append("-" * 35)
        items.append("Kế hoạch trên là cây quyết định:")
        items.append("  - Thực hiện hành động")
        items.append("  - Quan sát kết quả")  
        items.append("  - Đi theo nhánh tương ứng")
        
        self.csp_listbox.insert(tk.END, *items)
        self.log_tabs.select(self.csp_frame)

    def _format_andor_plan(self, plan, items, indent):
        prefix = "  " * indent
        if plan == LOOP_MARKER:
            items.append(f"{prefix}↻ Quay lại thử lại (bị trượt về trạng thái cũ)")
            return
        
        if isinstance(plan, list):
            if len(plan) == 0:
                items.append(f"{prefix}✓ ĐÃ ĐẠT ĐÍCH!")
                return
            for step in plan:
                if isinstance(step, dict) and "action" in step:
                    action_name = step["action"]
                    sub_plan = step["plan"]
                    items.append(f"{prefix}→ Hành động: {action_name}")
                    if sub_plan == LOOP_MARKER:
                        items.append(f"{prefix}  ↻ Quay lại thử lại")
                    elif isinstance(sub_plan, dict) and "action" not in sub_plan:
                        for result_state, branch_plan in sub_plan.items():
                            state_str = self._format_state_short(result_state)
                            items.append(f"{prefix}  NẾU kết quả = {state_str}:")
                            self._format_andor_plan(branch_plan, items, indent + 2)
                    elif isinstance(sub_plan, list):
                        self._format_andor_plan(sub_plan, items, indent + 1)
                    elif sub_plan is None:
                        items.append(f"{prefix}  ✗ Không tìm được lời giải cho nhánh này")
                else:
                    items.append(f"{prefix}{step}")
        elif isinstance(plan, dict):
            if "action" in plan:
                action_name = plan["action"]
                sub_plan = plan["plan"]
                items.append(f"{prefix}→ Hành động: {action_name}")
                self._format_andor_plan(sub_plan, items, indent + 1)
            else:
                for result_state, branch_plan in plan.items():
                    state_str = self._format_state_short(result_state)
                    items.append(f"{prefix}NẾU kết quả = {state_str}:")
                    self._format_andor_plan(branch_plan, items, indent + 1)
    
    def _format_state_short(self, state_tuple):
        arr = np.array(state_tuple).reshape(3, 3)
        rows = []
        for r in range(3):
            rows.append(",".join(str(arr[r, c]) for c in range(3)))
        return "[" + " | ".join(rows) + "]"

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

        if self.app_mode == "CSPs":
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
            self.is_playing = False; self.btn_play.config(text="▶ Phát")

    def toggle_play(self):
        self.log_tabs.select(self.path_frame)
        if self.is_playing:
            self.is_playing = False; self.btn_play.config(text="▶ Phát")
            self.stop_current_animation()
            if self.path: self.place_tiles_instantly(self.path[self.current_step].state)
        else:
            if self.current_step >= len(self.path) - 1:
                self.current_step = 0
                self.place_tiles_instantly(self.path[self.current_step].state)
            self.is_playing = True; self.btn_play.config(text="⏸ Tạm dừng")
            self.animate_loop()

    def next_step(self):
        self.log_tabs.select(self.path_frame)
        if self.current_step >= len(self.path) - 1: return
        self.is_playing = False; self.btn_play.config(text="▶ Phát"); self.stop_current_animation()
        self.current_step += 1; self.update_view_animate(self.current_step, direction="forward")

    def prev_step(self):
        self.log_tabs.select(self.path_frame)
        if self.current_step <= 0: return
        self.is_playing = False; self.btn_play.config(text="▶ Phát"); self.stop_current_animation()
        self.current_step -= 1; self.update_view_animate(self.current_step, direction="backward")

    def on_history_select(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            idx = selection[0]
            offset = 2
            if idx >= offset:
                step = idx - offset
                if step < len(self.path):
                    self.is_playing = False; self.btn_play.config(text="▶ Phát"); self.stop_current_animation()
                    self.current_step = step
                    self.update_view_animate(self.current_step, direction="jump")

    def disable_anim_controls(self):
        self.btn_prev.config(state=tk.DISABLED); self.btn_play.config(state=tk.DISABLED); self.btn_next.config(state=tk.DISABLED)

    def enable_anim_controls(self):
        self.btn_prev.config(state=tk.NORMAL); self.btn_play.config(state=tk.NORMAL); self.btn_next.config(state=tk.NORMAL)
