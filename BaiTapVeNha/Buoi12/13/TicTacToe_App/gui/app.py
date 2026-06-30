import tkinter as tk
from tkinter import messagebox
import tkinter.scrolledtext as st
from logic.minimax import check_winner, find_best_move

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - Minimax AI")
        self.root.configure(bg="#2c3e50")
        # Bỏ fix cứng kích thước để giao diện tự động co giãn theo DPI màn hình
        self.root.minsize(850, 550)

        self.human_player = 'X'
        self.ai_player = 'O'
        self.current_player = self.human_player
        self.board = [' ' for _ in range(9)]
        
        self.human_score = 0
        self.ai_score = 0
        self.tie_score = 0
        
        self.buttons = []
        self.create_widgets()
        
    def create_widgets(self):
        # Frame chính chia đôi màn hình
        main_frame = tk.Frame(self.root, bg="#2c3e50")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- LEFT PANEL: Game Board ---
        left_panel = tk.Frame(main_frame, bg="#2c3e50")
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        
        title_label = tk.Label(left_panel, text="Tic Tac Toe vs AI", font=("Arial", 24, "bold"), bg="#2c3e50", fg="#ecf0f1")
        title_label.pack(pady=10)
        
        # Điểm số
        self.score_frame = tk.Frame(left_panel, bg="#2c3e50")
        self.score_frame.pack(pady=5)
        
        self.human_score_label = tk.Label(self.score_frame, text=f"Bạn (X): {self.human_score}", font=("Arial", 12, "bold"), bg="#2c3e50", fg="#3498db", width=12)
        self.human_score_label.grid(row=0, column=0, padx=5)
        
        self.tie_score_label = tk.Label(self.score_frame, text=f"Hòa: {self.tie_score}", font=("Arial", 12, "bold"), bg="#2c3e50", fg="#ecf0f1", width=10)
        self.tie_score_label.grid(row=0, column=1, padx=5)
        
        self.ai_score_label = tk.Label(self.score_frame, text=f"AI (O): {self.ai_score}", font=("Arial", 12, "bold"), bg="#2c3e50", fg="#e74c3c", width=12)
        self.ai_score_label.grid(row=0, column=2, padx=5)
        
        # Bàn cờ
        board_frame = tk.Frame(left_panel, bg="#34495e", bd=5, relief=tk.RIDGE)
        board_frame.pack(pady=15)
        
        for i in range(3):
            row_buttons = []
            for j in range(3):
                btn = tk.Button(board_frame, text=' ', font=("Arial", 36, "bold"), width=3, height=1,
                                command=lambda idx=i*3+j: self.on_click(idx), bg="#ecf0f1", fg="#2c3e50",
                                activebackground="#bdc3c7", relief=tk.RAISED, bd=3)
                btn.grid(row=i, column=j, padx=5, pady=5)
                row_buttons.append(btn)
            self.buttons.extend(row_buttons)
            
        # Điều khiển
        control_frame = tk.Frame(left_panel, bg="#2c3e50")
        control_frame.pack(pady=10)
        
        new_game_btn = tk.Button(control_frame, text="Ván mới (Giữ tỉ số)", font=("Arial", 12, "bold"), command=self.reset_game, 
                              bg="#27ae60", fg="white", activebackground="#2ecc71", relief=tk.RAISED, bd=3, width=16)
        new_game_btn.grid(row=0, column=0, padx=5)
        
        reset_score_btn = tk.Button(control_frame, text="Xóa toàn bộ tỉ số", font=("Arial", 12, "bold"), command=self.reset_score, 
                              bg="#e74c3c", fg="white", activebackground="#c0392b", relief=tk.RAISED, bd=3, width=16)
        reset_score_btn.grid(row=0, column=1, padx=5)
        
        # --- RIGHT PANEL: AI LOG ---
        right_panel = tk.Frame(main_frame, bg="#34495e", bd=2, relief=tk.SUNKEN)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        log_title = tk.Label(right_panel, text="Nhật ký thuật toán Minimax", font=("Arial", 14, "bold"), bg="#34495e", fg="#f1c40f")
        log_title.pack(pady=5)
        
        self.log_text = st.ScrolledText(right_panel, font=("Consolas", 10), bg="#1e272e", fg="#00d2d3", wrap=tk.WORD, width=45, height=25)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.write_log("Chào mừng! Hệ thống đã sẵn sàng.\n")
        
    def write_log(self, text):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def on_click(self, idx):
        if self.board[idx] == ' ' and check_winner(self.board) is None:
            self.board[idx] = self.human_player
            self.buttons[idx].config(text=self.human_player, fg="#3498db")
            
            self.write_log(f"\n[Người chơi] Bạn đánh vào ô ({idx//3}, {idx%3})")
            
            if self.check_game_over():
                return
                
            # Cập nhật UI trước khi AI tính toán
            self.root.update()
            
            # AI move sau một khoảng delay nhỏ để người dùng thấy nước đi của mình
            self.root.after(100, self.ai_move)
            
    def ai_move(self):
        # Truyền write_log vào find_best_move
        best_move = find_best_move(self.board, self.ai_player, self.human_player, log_callback=self.write_log)
        if best_move != -1:
            self.board[best_move] = self.ai_player
            self.buttons[best_move].config(text=self.ai_player, fg="#e74c3c")
            self.check_game_over()
            
    def check_game_over(self):
        winner = check_winner(self.board)
        if winner:
            if winner == 'Tie':
                self.tie_score += 1
                self.update_score_labels()
                self.write_log(">> TRÒ CHƠI KẾT THÚC: HÒA!\n")
                messagebox.showinfo("Kết thúc", "Hòa!")
            else:
                if winner == self.ai_player:
                    self.ai_score += 1
                    msg = "AI thắng!"
                    self.write_log(">> TRÒ CHƠI KẾT THÚC: AI THẮNG!\n")
                else:
                    self.human_score += 1
                    msg = "Bạn thắng!"
                    self.write_log(">> TRÒ CHƠI KẾT THÚC: BẠN THẮNG!\n")
                self.update_score_labels()
                messagebox.showinfo("Kết thúc", f"Kết quả: {msg}")
            return True
        return False
        
    def update_score_labels(self):
        self.human_score_label.config(text=f"Bạn (X): {self.human_score}")
        self.tie_score_label.config(text=f"Hòa: {self.tie_score}")
        self.ai_score_label.config(text=f"AI (O): {self.ai_score}")

    def reset_score(self):
        self.human_score = 0
        self.ai_score = 0
        self.tie_score = 0
        self.update_score_labels()
        self.write_log("\n--- ĐÃ XÓA TOÀN BỘ TỈ SỐ ---")
        self.reset_game()
        
    def reset_game(self):
        self.board = [' ' for _ in range(9)]
        for btn in self.buttons:
            btn.config(text=' ', fg="#2c3e50")
        self.write_log("\n--- BẮT ĐẦU VÁN MỚI ---")
