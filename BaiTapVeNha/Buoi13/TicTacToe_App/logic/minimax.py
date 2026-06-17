import math

def check_winner(board):
    win_states = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8], # Hàng ngang
        [0, 3, 6], [1, 4, 7], [2, 5, 8], # Hàng dọc
        [0, 4, 8], [2, 4, 6]             # Chéo
    ]
    for state in win_states:
        if board[state[0]] == board[state[1]] == board[state[2]] and board[state[0]] != ' ':
            return board[state[0]]
    if ' ' not in board:
        return 'Tie'
    return None

def find_best_move(board, ai_player, human_player, log_callback=None):
    if log_callback:
        log_callback(f"=== AI ({ai_player}) ĐANG SUY NGHĨ ===\n")
        
    best_score = -math.inf
    best_move = -1
    states_evaluated = 0

    def minimax(board, depth, is_maximizing):
        nonlocal states_evaluated
        states_evaluated += 1
        
        result = check_winner(board)
        if result == ai_player:
            return 10 - depth
        elif result == human_player:
            return depth - 10
        elif result == 'Tie':
            return 0

        if is_maximizing:
            best_score = -math.inf
            for i in range(9):
                if board[i] == ' ':
                    board[i] = ai_player
                    score = minimax(board, depth + 1, False)
                    board[i] = ' '
                    best_score = max(score, best_score)
            return best_score
        else:
            best_score = math.inf
            for i in range(9):
                if board[i] == ' ':
                    board[i] = human_player
                    score = minimax(board, depth + 1, True)
                    board[i] = ' '
                    best_score = min(score, best_score)
            return best_score

    for i in range(9):
        if board[i] == ' ':
            board[i] = ai_player
            if log_callback:
                log_callback(f"-> Thử nước đi tại ô ({i//3}, {i%3})")
                
            score = minimax(board, 0, False)
            board[i] = ' '
            
            if log_callback:
                log_callback(f"   Điểm đánh giá (Score): {score}\n")
                
            if score > best_score:
                best_score = score
                best_move = i

    if log_callback:
        log_callback(f"=> Tổng số kịch bản tương lai đã duyệt: {states_evaluated}\n")
        if best_move != -1:
            log_callback(f"=> Quyết định chọn ô ({best_move//3}, {best_move%3}) vì có điểm cao nhất: {best_score}\n")
        log_callback("-" * 40 + "\n")

    return best_move
