import tkinter as tk
from PIL import Image, ImageTk
import os, random

root = tk.Tk()
root.title("8 Queen problem")
root.geometry("1300x800")

canvas = tk.Canvas(root, width=1200, height=650)
canvas.pack(pady=70)

frame = tk.Frame(root)
frame.place(x=0, y=650)

size = 60

# Lấy hình con hậu
current_dir = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(current_dir, "wq.png")

queen_img = Image.open(img_path)
queen_img = queen_img.resize((50, 50))  # scale vừa ô
queen_img_tk = ImageTk.PhotoImage(queen_img)

# Vẽ ô bàn cờ
def ve_o(offsetX):
    for i in range(8):
        for j in range(8):
            x1 = j * size + offsetX
            y1 = i * size
            x2 = x1 + size
            y2 = y1 + size
            color = "white" if (i + j) % 2 == 0 else "#67A767"
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, width=0)

def ve_nhan(offsetX, side="left"):

    for j in range(8):
        x = j * size + size/2 + offsetX
        canvas.create_text(x, -10, text=chr(ord("A")+j), font=("Arial", 12))
        canvas.create_text(x, 8*size+10, text=chr(ord("A")+j), font=("Arial", 12))
    
    for i in range(8):
        y = i * size + size/2
        if side == "left":
            canvas.create_text(offsetX-10, y, text=str(i+1), font=("Arial", 12))
        else:
            canvas.create_text(offsetX+8*size+10, y, text=str(i+1), font=("Arial", 12))

def ve_banco_daydu(offsetX, side="left"):
    ve_o(offsetX)
    ve_nhan(offsetX, side)

# Đặt con hậu lên bàn cờ bên trái
def ve_queen(x, y, offsetX):
    cx = offsetX + x*size + size//2
    cy = y*size + size//2
    canvas.create_image(cx, cy, image=queen_img_tk)

# Random vị trí xuất hiện
def queens_random(offsetX):
    positions = []
    for _ in range(8):
        x = random.randint(0, 7)
        y = random.randint(0, 7)
        positions.append((x,y))
        ve_queen(x, y, offsetX)
    return positions

# Vị trí đã giải xong 
def queens_solution(offsetX):
    # Vị trí mẫu đã được giải của 8 con hậu
    solution = [0, 4, 7, 5, 2, 6, 1, 3]  
    
    for row, col in enumerate(solution):
        ve_queen(col, row, offsetX)

# Buttons
btn_Start = tk.Button(frame, text="Bắt đầu", width=25)
btn_Start.pack(side="left", padx=50)

btn_Stop = tk.Button(frame, text="Reset", width=25)
btn_Stop.pack(side="right", padx=570)

# Labels
lbl_left = tk.Label(root, text="Trạng thái bắt đầu", font=("Arial", 12))
lbl_left.place(x=200, y=570)

lbl_right = tk.Label(root, text="Trạng thái kết thúc", font=("Arial", 12))
lbl_right.place(x=700, y=570)

# Vẽ bàn cờ và queens
ve_banco_daydu(40, side="left")   # bàn cờ trái
queens_random(40)

ve_banco_daydu(580, side="right") # bàn cờ phải
queens_solution(580)

root.mainloop()
