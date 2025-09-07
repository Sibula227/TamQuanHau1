import tkinter as tk
from PIL import Image, ImageTk
import os, random
from collections import deque

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

# Đặt con hậu (hỗ trợ tag để có thể xóa riêng)
def ve_queen(x, y, offsetX, tag=None):
    cx = offsetX + x*size + size//2
    cy = y*size + size//2
    if tag:
        canvas.create_image(cx, cy, image=queen_img_tk, tags=tag)
    else:
        canvas.create_image(cx, cy, image=queen_img_tk)

# Xóa tất cả quân hậu (giữ bàn cờ)
def clear_queens():
    canvas.delete("queens_left")
    canvas.delete("queens_right")

# -------- BFS 8 QUEENS với state là list[(row,col)] --------
running = False   # trạng thái thuật toán
queue = deque()
start_state = []  # dạng [(row,col), ...]

def is_safe_state(state, row, col):
    # kiểm tra (row,col) có xung đột với các (r,c) trong state không
    for (r, c) in state:
        if c == col:
            return False
        if abs(c - col) == abs(r - row):
            return False
    return True

def bfs_step(offsetX):
    """Thực hiện 1 bước BFS (được gọi lặp lại bằng after khi running=True)."""
    global running, queue

    if not running:
        return

    if not queue:
        running = False
        return  # không tìm thấy lời giải

    state = queue.popleft()  # state là list các (row,col)

    # Vẽ trạng thái hiện tại lên bàn phải
    canvas.delete("queens_right")
    for (r, c) in state:
        ve_queen(c, r, offsetX, tag="queens_right")

    # Nếu đủ 8 hậu → tìm được nghiệm
    if len(state) == 8:
        running = False
        return

    # Tìm hàng nhỏ nhất chưa có hậu
    used_rows = {r for (r, _) in state}
    next_row = None
    for r in range(8):
        if r not in used_rows:
            next_row = r
            break
    if next_row is None:
        # không còn hàng nào (vô lý nếu chưa len==8), skip
        root.after(50, lambda: bfs_step(offsetX))
        return

    # Sinh trạng thái con: thử tất cả cột ở next_row
    for col in range(8):
        if is_safe_state(state, next_row, col):
            new_state = state + [(next_row, col)]
            queue.append(new_state)

    # Lặp lại sau 300ms nếu còn chạy
    if running:
        root.after(300, lambda: bfs_step(offsetX))

# --- Start: vẽ board và đặt 1 hậu random ở bên trái ---
def start_game():
    global start_state, queue, running
    running = False
    queue.clear()
    clear_queens()

    # Vẽ lại bàn cờ (không cần xóa toàn bộ canvas)
    # (bàn cờ được vẽ lần đầu ở init; nếu muốn vẽ lại, ta vẽ lại)
    canvas.delete("board")   # nếu dùng tag board, nhưng ta chưa, nên dùng clear_queens suffices
    ve_banco_daydu(40, side="left")
    ve_banco_daydu(580, side="right")

    # Đặt 1 hậu random bên trái ở hàng y, cột x
    x = random.randint(0, 7)  # cột
    y = random.randint(0, 7)  # hàng
    ve_queen(x, y, 40, tag="queens_left")

    # Khởi tạo start_state là 1 tuple (row=y, col=x)
    start_state = [(y, x)]
    queue = deque([start_state])

# Run BFS từ trạng thái hiện có trong queue
def run_bfs():
    global running
    if not queue:
        # chưa có start_state — cảnh báo nhẹ
        print("Chưa có trạng thái bắt đầu. Nhấn Start trước.")
        return
    if not running:
        running = True
        bfs_step(580)

def stop_game():
    global running
    running = False

def continue_game():
    global running
    if not running and queue:
        running = True
        bfs_step(580)

# Buttons
btn_Start = tk.Button(frame, text="Start (tạo 1 hậu bên trái)", width=25, command=start_game)
btn_Start.pack(side="left", padx=10)

btn_Run = tk.Button(frame, text="Run BFS", width=15, command=run_bfs)
btn_Run.pack(side="left", padx=10)

btn_Stop = tk.Button(frame, text="Stop", width=15, command=stop_game)
btn_Stop.pack(side="left", padx=10)

btn_Continue = tk.Button(frame, text="Continue", width=15, command=continue_game)
btn_Continue.pack(side="left", padx=10)

btn_Reset = tk.Button(frame, text="Reset (Xóa hậu)", width=15, command=clear_queens)
btn_Reset.pack(side="right", padx=20)

# Labels
lbl_left = tk.Label(root, text="Trạng thái bắt đầu", font=("Arial", 12))
lbl_left.place(x=200, y=570)

lbl_right = tk.Label(root, text="Trạng thái BFS", font=("Arial", 12))
lbl_right.place(x=700, y=570)

# Khởi tạo bàn cờ ban đầu (vẽ 2 bàn cờ)
ve_banco_daydu(40, side="left")
ve_banco_daydu(580, side="right")

root.mainloop()
