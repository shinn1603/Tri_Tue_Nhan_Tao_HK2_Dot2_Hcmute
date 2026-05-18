# DFS
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

class AnimatePuzzleGUI_DFS:
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle DFS Solver")
        self.root.geometry("800x550")
        self.root.configure(padx=20, pady=20)

        self.TILE_SIZE = 100
        self.PAD = 5
        self.GRID_SIZE = (self.TILE_SIZE + self.PAD) * 3 + self.PAD

        self.target_puzzle = np.array([[1, 2, 3],
                                       [4, 5, 6],
                                       [7, 8, 0]])
        self.puzzle = None
        self.path = []
        self.current_step = 0
        self.is_playing = False
        self.is_sliding = False
        self.current_after_job = None 

        self.setup_ui()
        self.generate_new_puzzle()

    def setup_ui(self):
        self.left_frame = tk.Frame(self.root)
        self.left_frame.pack(side=tk.LEFT, padx=20, fill=tk.BOTH)
        
        tk.Label(self.left_frame, text="Mô phỏng Trực quan (DFS)", font=("Helvetica", 14, "bold")).pack(pady=5)

        self.canvas_bg = tk.Frame(self.left_frame, bg="#d3d3d3", width=self.GRID_SIZE, height=self.GRID_SIZE)
        self.canvas_bg.pack(pady=10)
        
        self.tile_widgets = {}
        for val in range(1, 9):
            lbl = tk.Label(self.canvas_bg, text=str(val), font=("Helvetica", 36, "bold"), 
                           width=4, height=2, bg="white", relief="raised", borderwidth=3)
            lbl.place(width=self.TILE_SIZE, height=self.TILE_SIZE) 
            self.tile_widgets[val] = lbl
            
        self.status_lbl = tk.Label(self.left_frame, text="Trạng thái: Đang chờ...", font=("Helvetica", 12), fg="blue")
        self.status_lbl.pack(pady=15)

        self.right_frame = tk.Frame(self.root)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        top_ctrl_frame = tk.LabelFrame(self.right_frame, text="Thiết lập", padx=10, pady=10)
        top_ctrl_frame.pack(fill=tk.X, pady=5)
        
        self.btn_gen = tk.Button(top_ctrl_frame, text="Sinh Puzzle Mới", command=self.generate_new_puzzle, font=("Helvetica", 10))
        self.btn_gen.pack(side=tk.LEFT, padx=5)
        
        self.btn_solve = tk.Button(top_ctrl_frame, text="Giải (DFS)", command=self.start_solve, bg="#FF5722", fg="white", font=("Helvetica", 10, "bold"))
        self.btn_solve.pack(side=tk.LEFT, padx=5)

        anim_ctrl_frame = tk.LabelFrame(self.right_frame, text="Điều khiển Xem", padx=10, pady=10)
        anim_ctrl_frame.pack(fill=tk.X, pady=5)
        
        self.btn_prev = tk.Button(anim_ctrl_frame, text="|< Trước", command=self.prev_step, state=tk.DISABLED)
        self.btn_prev.pack(side=tk.LEFT, padx=2)
        
        self.btn_play = tk.Button(anim_ctrl_frame, text="Phát", command=self.toggle_play, state=tk.DISABLED)
        self.btn_play.pack(side=tk.LEFT, padx=2)
        
        self.btn_next = tk.Button(anim_ctrl_frame, text="Sau >|", command=self.next_step, state=tk.DISABLED)
        self.btn_next.pack(side=tk.LEFT, padx=2)

        speed_frame = tk.Frame(self.right_frame)
        speed_frame.pack(fill=tk.X, pady=5)
        tk.Label(speed_frame, text="Tốc độ (ms):").pack(side=tk.LEFT)
        self.speed_scale = tk.Scale(speed_frame, from_=10, to=1000, resolution=10, orient=tk.HORIZONTAL, length=180)
        self.speed_scale.set(300) 
        self.speed_scale.pack(side=tk.LEFT, padx=5)

        hist_frame = tk.LabelFrame(self.right_frame, text="Lịch sử các bước chạy", padx=10, pady=10)
        hist_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.scrollbar = tk.Scrollbar(hist_frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.history_listbox = tk.Listbox(hist_frame, yscrollcommand=self.scrollbar.set, font=("Consolas", 10))
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
                    x, y = self.get_coords(r, c)
                    tile.place(x=x, y=y)
                    tile.tkraise()

    def slide_tile(self, tile_widget, start_coords, end_coords, callback):
        self.is_sliding = True
        
        total_duration_ms = self.speed_scale.get()
        animation_time = total_duration_ms * 0.8
        
        step_delay_ms = 20 
        num_steps = max(1, int(animation_time / step_delay_ms))
        
        dx = (end_coords[0] - start_coords[0]) / num_steps
        dy = (end_coords[1] - start_coords[1]) / num_steps
        
        current_step = 0
        current_x, current_y = start_coords

        def animate_step():
            nonlocal current_step, current_x, current_y
            if current_step < num_steps:
                current_x += dx
                current_y += dy
                tile_widget.place(x=int(current_x), y=int(current_y))
                tile_widget.tkraise()
                current_step += 1
                self.current_after_job = self.root.after(step_delay_ms, animate_step)
            else:
                tile_widget.place(x=end_coords[0], y=end_coords[1])
                self.is_sliding = False
                callback()

        self.current_after_job = self.root.after(step_delay_ms, animate_step)

    def generate_new_puzzle(self):
        self.is_playing = False
        self.btn_play.config(text="▶ Phát")
        self.stop_current_animation()
        
        self.puzzle = Inputpuzzle()
        self.path = []
        self.current_step = 0
        
        self.place_tiles_instantly(self.puzzle)
        
        self.history_listbox.delete(0, tk.END)
        self.status_lbl.config(text="Đã tạo puzzle mới. Sẵn sàng giải DFS", fg="black")
        self.disable_anim_controls()
        self.btn_solve.config(state=tk.NORMAL)

    def start_solve(self):
        self.btn_gen.config(state=tk.DISABLED)
        self.btn_solve.config(state=tk.DISABLED)
        self.disable_anim_controls()
        self.stop_current_animation()
        self.status_lbl.config(text="Đang tìm kiếm bằng DFS...", fg="red")
        self.history_listbox.delete(0, tk.END)
        
        threading.Thread(target=self.dfs_worker, daemon=True).start()

    def dfs_worker(self):
        blank = Find_blank(self.puzzle)
        row, col = blank
        explored_puzzles = set()
        explored_puzzles.add(tuple(self.puzzle.flatten()))
        start_node = NODE(state=self.puzzle, parent=None, move_action=None, col=col, row=row)
        
        stack = [start_node] 
        steps_searched = 0
        solution_node = None
        
        start_time = time.time()
        while stack:
            # Lấy phần tử ở CUỐI mảng (pop) thay vì ĐẦU mảng (popleft)
            cur_node = stack.pop() 
            steps_searched += 1
            
            if np.array_equal(cur_node.state, self.target_puzzle):
                solution_node = cur_node
                break
                
            valid_moves = get_move(cur_node.row, cur_node.col)
            valid_moves.reverse() 
            
            for move in valid_moves:
                new_puzzle, new_row, new_col = action(cur_node.state, move, cur_node.row, cur_node.col)
                state_tuple = tuple(new_puzzle.flatten())
                if state_tuple not in explored_puzzles:
                    explored_puzzles.add(state_tuple)
                    child_node = NODE(state=new_puzzle, parent=cur_node, move_action=move, col=new_col, row=new_row)
                    stack.append(child_node)

        end_time = time.time()
        search_duration = end_time - start_time
        
        # Do Listbox của Tkinter có thể bị đơ nếu insert 40,000 dòng liên tục, 
        # nên việc cập nhật giao diện được đẩy sang luồng chính.
        self.root.after(0, self.on_solve_complete, solution_node, steps_searched, search_duration)

    def on_solve_complete(self, solution_node, steps_searched, duration):
        self.btn_gen.config(state=tk.NORMAL)
        self.btn_solve.config(state=tk.NORMAL)
        
        if solution_node:
            self.path = []
            current = solution_node
            while current is not None:
                self.path.append(current)
                current = current.parent
            self.path = self.path[::-1]
            
            self.status_lbl.config(text=f"DFS xong ({duration:.2f}s) - Duyệt {steps_searched} nút.", fg="#FF5722")
            self.populate_history()
            self.enable_anim_controls()
            self.current_step = 0
            self.update_listbox_selection()
        else:
            self.status_lbl.config(text=f"DFS xong ({duration:.2f}s). Duyệt {steps_searched} trạng thái.\nKhông tìm thấy đường đi", fg="red")
            messagebox.showerror("Lỗi", "Không tìm thấy cách giải!")

    def populate_history(self):
        self.history_listbox.delete(0, tk.END)
        # Tối ưu hóa việc chèn hàng chục ngàn dòng vào Listbox
        items = ["[0] Bắt đầu"]
        for i in range(1, len(self.path)):
            items.append(f"[{i}] Di chuyển ô vào ô trống: {self.path[i].move_action}")
        self.history_listbox.insert(tk.END, *items)

    def update_listbox_selection(self):
        self.history_listbox.selection_clear(0, tk.END)
        self.history_listbox.selection_set(self.current_step)
        self.history_listbox.see(self.current_step)
        self.btn_prev.config(state=tk.NORMAL if self.current_step > 0 else tk.DISABLED)
        self.btn_next.config(state=tk.NORMAL if self.current_step < len(self.path) - 1 else tk.DISABLED)

    def update_view_animate(self, step_index, direction="forward"):
        if not self.path or self.is_sliding: return
        
        current_node = self.path[step_index]
        self.update_listbox_selection()

        if step_index == 0 or direction == "jump":
            self.place_tiles_instantly(current_node.state)
            if self.is_playing: 
                self.current_after_job = self.root.after(self.speed_scale.get(), self.animate_loop)
            return

        if direction == "forward":
            parent_node = self.path[step_index - 1]
            child_node = current_node
            blank_old_rc = (parent_node.row, parent_node.col)
            blank_new_rc = (child_node.row, child_node.col)
            tile_value = parent_node.state[blank_new_rc[0], blank_new_rc[1]]
            
        elif direction == "backward":
            child_node = self.path[step_index + 1]
            parent_node = current_node
            blank_old_rc = (child_node.row, child_node.col)
            blank_new_rc = (parent_node.row, parent_node.col)
            tile_value = parent_node.state[blank_old_rc[0], blank_old_rc[1]]

        if tile_value == 0:
            self.place_tiles_instantly(current_node.state)
            if self.is_playing: 
                self.current_after_job = self.root.after(self.speed_scale.get(), self.animate_loop)
            return

        tile_widget = self.tile_widgets[tile_value]
        start_coords = self.get_coords(blank_new_rc[0], blank_new_rc[1])
        end_coords = self.get_coords(blank_old_rc[0], blank_old_rc[1])

        self.slide_tile(tile_widget, start_coords, end_coords, self.on_slide_complete_callback)

    def on_slide_complete_callback(self):
        if self.is_playing:
            rest_delay = int(self.speed_scale.get() * 0.2) 
            self.current_after_job = self.root.after(rest_delay, self.animate_loop)

    def toggle_play(self):
        if self.is_playing:
            self.is_playing = False
            self.btn_play.config(text="Phát")
            self.stop_current_animation()
            if self.path:
                self.place_tiles_instantly(self.path[self.current_step].state)
        else:
            if self.current_step >= len(self.path) - 1:
                self.current_step = 0
                self.place_tiles_instantly(self.path[self.current_step].state)
            self.is_playing = True
            self.btn_play.config(text="Tạm dừng")
            self.animate_loop()

    def animate_loop(self):
        if not self.is_playing or self.is_sliding: return
        
        if self.current_step < len(self.path) - 1:
            self.current_step += 1
            self.update_view_animate(self.current_step, direction="forward")
        else:
            self.is_playing = False
            self.btn_play.config(text="Phát")
            self.update_listbox_selection()

    def next_step(self):
        if self.current_step >= len(self.path) - 1: return
        self.is_playing = False
        self.btn_play.config(text="Phát")
        self.stop_current_animation()
        
        self.current_step += 1
        self.update_view_animate(self.current_step, direction="forward")

    def prev_step(self):
        if self.current_step <= 0: return
        self.is_playing = False
        self.btn_play.config(text="Phát")
        self.stop_current_animation()
        
        self.current_step -= 1
        self.update_view_animate(self.current_step, direction="backward")

    def on_history_select(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            self.is_playing = False
            self.btn_play.config(text="Phát")
            self.stop_current_animation()
            
            self.current_step = selection[0]
            self.update_view_animate(self.current_step, direction="jump")

    def disable_anim_controls(self):
        self.btn_prev.config(state=tk.DISABLED)
        self.btn_play.config(state=tk.DISABLED)
        self.btn_next.config(state=tk.DISABLED)

    def enable_anim_controls(self):
        self.btn_prev.config(state=tk.NORMAL)
        self.btn_play.config(state=tk.NORMAL)
        self.btn_next.config(state=tk.NORMAL)


if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.tk.call('tk', 'scaling', 1.5)
    except:
        pass
    app = AnimatePuzzleGUI_DFS(root)
    root.mainloop()
