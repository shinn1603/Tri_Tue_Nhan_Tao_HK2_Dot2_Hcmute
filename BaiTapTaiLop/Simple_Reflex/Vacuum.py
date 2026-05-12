import numpy as np
import random
def RandomInput():
    floor = np.random.randint(0,2,(4,4))
    return floor 


def findVacuum():
    row = random.randint(0,3)
    col = random.randint(0,3)
    return row,col


def get_moves(row,col):
    moves = []
    if row < 3:
        moves.append("DOWN")
    if row > 0:
        moves.append("UP")
    if col < 3:
        moves.append("RIGHT")
    if col > 0:
        moves.append("LEFT")
    return moves


def move(row,col,move_random):
    if(move_random=="DOWN"):
        row += 1
    if(move_random=="UP"):
        row -= 1
    if(move_random=="LEFT"):
        col -= 1
    if(move_random=="RIGHT"):
        col += 1
    return row, col



def main():
    floor = RandomInput()
    row, col = findVacuum()
    steps = 0
    print("Sàn nhà ban đầu là: \n",floor)
    while not np.array_equal(floor, np.zeros((4,4), dtype=int)):
        steps +=1
        # print(f"Sàn nhà hiện tại: ", floor)
        if floor[row][col]==1:
            floor[row][col]=0
            print(f"Đã hút bụi tại vị trí [{row};{col}]")
        if floor[row][col]==0:
            valid_moves = get_moves(row,col)
            action = random.choice(valid_moves)
            row, col = move(row,col,action)
            
    print(f"Đã hút sạch bụi sau {steps}")
    print(floor)
    
main()
