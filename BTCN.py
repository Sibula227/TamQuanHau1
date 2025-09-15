import tkinter as tk
from PIL import Image, ImageTk
import os, random, heapq
from collections import deque

# ===================== KHỞI TẠO GIAO DIỆN =====================
root = tk.Tk()
root.title("8 Queen problem")
root.geometry("1300x800")

canvas = tk.Canvas(root, width=1200, height=650)
canvas.pack(pady=70)

frame = tk.Frame(root)
frame.place(x=0, y=650)

size = 60

# ===================== TẢI ẢNH CON HẬU =====================
current_dir = os.path.dirname(os.path.abspath(__file__))
img_path = os.path.join(current_dir, "wq.png")

queen_img = Image.open(img_path)
queen_img = queen_img.resize((50, 50))  # scale vừa ô
queen_img_tk = ImageTk.PhotoImage(queen_img)

# ===================== VẼ BÀN CỜ =====================
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

def ve_queen(x, y, offsetX, tag=None):
    """Vẽ một quân hậu tại (x,y)"""
    cx = offsetX + x*size + size//2
    cy = y*size + size//2
    if tag:
        canvas.create_image(cx, cy, image=queen_img_tk, tags=tag)
    else:
        canvas.create_image(cx, cy, image=queen_img_tk)

def clear_queens():
    """Xóa toàn bộ quân hậu (giữ nguyên bàn cờ)"""
    canvas.delete("queens_left")
    canvas.delete("queens_right")

# ===================== HÀM HỖ TRỢ =====================
def is_safe_state(state, row, col):
    """Kiểm tra xem đặt hậu tại (row,col) có xung đột với state hay không"""
    for (r, c) in state:
        if c == col:  # cùng cột
            return False
        if abs(c - col) == abs(r - row):  # cùng đường chéo
            return False
    return True
# ===================== THUẬT TOÁN IDS =====================
ids_running = False
ids_depth_limit = 0
ids_frontier = []

# Chạy 1 bước của DLS với giới hạn là ids_depth_limit (dùng cho IDS)
def ids_step_once(offsetX):
    """Phiên bản DLS dùng trong IDS. Mỗi lần gọi sẽ pop 1 trạng thái, mở rộng nếu chưa đạt giới hạn.
    Khi frontier rỗng sẽ tăng giới hạn và khởi tạo lại frontier để lặp lại.
    """
    global ids_frontier, ids_running, ids_depth_limit
    if not ids_running:
        return

    # Nếu frontier rỗng -> tăng giới hạn và khởi tạo lại frontier từ trạng thái bắt đầu
    if not ids_frontier:
        ids_depth_limit += 1
        if ids_depth_limit > 8:
            print("IDS: Không tìm thấy lời giải trong giới hạn tối đa")
            ids_running = False
            return
        # khởi tạo lại stack với trạng thái bắt đầu
        ids_frontier = [(start_state, len(start_state))]
        root.after(300, lambda: ids_step_once(offsetX))
        return

    # Lấy trạng thái cuối (LIFO)
    state, depth = ids_frontier.pop()

    # Vẽ trạng thái hiện tại bên phải
    canvas.delete("queens_right")
    for (r, c) in state:
        ve_queen(c, r, offsetX, tag="queens_right")

    # Nếu tìm thấy lời giải
    if len(state) == 8:
        print("IDS: Tìm thấy lời giải ở độ sâu", len(state))
        ids_running = False
        return

    # Nếu đã đạt giới hạn hiện tại -> không mở rộng
    if depth >= ids_depth_limit:
        if ids_running:
            root.after(300, lambda: ids_step_once(offsetX))
        return
    
    print(f"Độ sâu: {depth} | Đường đi: {state}")

    # Tìm hàng tiếp theo
    used_rows = {r for (r, _) in state}
    next_row = next((r for r in range(8) if r not in used_rows), None)
    if next_row is None:
        if ids_running:
            root.after(300, lambda: ids_step_once(offsetX))
        return

    # Sinh con (duyệt ngược cột để giữ thứ tự giống DFS khi pop
    for col in range(7, -1, -1):
        if is_safe_state(state, next_row, col):
            ids_frontier.append((state + [(next_row, col)], depth + 1))

    if ids_running:
        root.after(300, lambda: ids_step_once(offsetX))

# Hàm khởi chạy IDS
def run_ids():
    global ids_running, ids_frontier, ids_depth_limit
    if not start_state:
        print("Chưa có trạng thái bắt đầu. Nhấn Start trước.")
        return
    ids_depth_limit = len(start_state)
    ids_frontier = [(start_state, ids_depth_limit)]
    ids_running = True
    ids_step_once(580)

# ===================== THUẬT TOÁN DLS=====================
dls_running = False
# dls_frontier là stack các cặp (state, depth)
dls_frontier = []
dls_limited = 8

def dls_step(offsetX):
    """Thực hiện một bước của DLS. Visualize trạng thái hiện tại ở bên phải (offsetX).
    dls_frontier chứa các tuple (state, depth).
    """
    global dls_running, dls_frontier, dls_limited
    if not dls_running:
        return

    if not dls_frontier:
        dls_running = False
        print("DLS: Không tìm thấy lời giải trong giới hạn độ sâu")
        return

    # Lấy trạng thái cuối cùng (LIFO)
    state, depth = dls_frontier.pop()

    
    print(f"Độ sâu: {depth} | Đường đi: {state}")
    # Vẽ trạng thái hiện tại bên phải
    canvas.delete("queens_right")
    for (r, c) in state:
        ve_queen(c, r, offsetX, tag="queens_right")

    # Nếu tìm thấy lời giải:
    if len(state) == 8:
        print("DLS: Tìm thấy lời giải ở độ sâu", len(state))
        dls_running = False
        return

    # Nếu đã đạt giới hạn độ sâu, không mở rộng nữa
    if depth >= dls_limited:
        # Chỉ chờ 300ms rồi tiếp tục với trạng thái tiếp theo trong stack
        if dls_running:
            root.after(300, lambda: dls_step(offsetX))
        return

    # Tìm hàng tiếp theo cần đặt hậu (hàng nhỏ nhất chưa dùng)
    used_rows = {r for (r, _) in state}
    next_row = next((r for r in range(8) if r not in used_rows), None)
    if next_row is None:
        if dls_running:
            root.after(300, lambda: dls_step(offsetX))
        return

    # Sinh các trạng thái con: duyệt ngược cột để khi push vào stack rồi pop sẽ xét cột 0 trước
    for col in range(7, -1, -1):
        if is_safe_state(state, next_row, col):
            new_state = state + [(next_row, col)]
            dls_frontier.append((new_state, depth + 1))

    # Tiếp tục sau 300ms nếu vẫn đang chạy
    if dls_running:
        root.after(300, lambda: dls_step(offsetX))

# ===================== THUẬT TOÁN BFS =====================
running = False
queue = deque()
start_state = []

def bfs_step(offsetX):
    global running, queue
    if not running: # Nếu người dùng bấm Stop, biến running = FALSE --> Dừng
        return
    if not queue:
        running = False # Queue rỗng tức là đã chạy xong thuật toán
        return

    state = queue.popleft() # Kiểm tra trạng thái đầu tiên trong queue

    print(f"BFS - Độ sâu: {len(state)} | Đường đi: {state}")

    # Vẽ trạng thái hiện tại bên phải
    canvas.delete("queens_right")
    for (r, c) in state: # Vẽ các trạng thái có trong queue hiện tại
        ve_queen(c, r, offsetX, tag="queens_right")

    # Đủ 8 hậu → tìm thấy nghiệm
    if len(state) == 8: # Do có hàm kiểm tra is_safe_step nên đảm bảo không có xung đột
        running = False
        return
    
    # Tìm hàng tiếp theo
    # Lấy hàng nhỏ nhất tiếp theo để đặt hậu
    # --> giảm việc duyệt lung tung
    used_rows = {r for (r, _) in state} 
    next_row = next((r for r in range(8) if r not in used_rows), None) 
    if next_row is None:
        root.after(500, lambda: bfs_step(offsetX))
        return

    # Hàm sinh trạng thái
    for col in range(8):
        if is_safe_state(state, next_row, col):
            queue.append(state + [(next_row, col)])
    # Với mỗi cột ở next_row, kiểm tra nếu đặt hậu vào (next_row, col) không xung đột → thêm vào hàng đợi.
    if running:
        root.after(300, lambda: bfs_step(offsetX)) # Gọi đệ quy không đồng bộ để chạy thuật toán BFS

# ===================== THUẬT TOÁN UCS =====================
ucs_running = False
ucs_frontier = []

def cost_of_state(state, w_row=3, w_col=2, w_diag=1):
    """Tính chi phí cho một trạng thái"""
    cost = 0
    n = len(state)
    for i in range(n):
        r1, c1 = state[i]
        for j in range(i+1, n):
            r2, c2 = state[j]
            if r1 == r2:
                cost += w_row
            if c1 == c2:
                cost += w_col
            if abs(r1 - r2) == abs(c1 - c2):
                cost += w_diag
    return cost

def ucs_step(offsetX):
    global ucs_running, ucs_frontier
    if not ucs_running:
        return
    if not ucs_frontier:
        ucs_running = False
        return

    cost, state = heapq.heappop(ucs_frontier)

    print(f"UCS - Độ sâu: {len(state)} | Chi phí: {cost} | Đường đi: {state}")

    # Vẽ trạng thái hiện tại bên phải
    canvas.delete("queens_right")
    for (r, c) in state:
        ve_queen(c, r, offsetX, tag="queens_right")

    if len(state) == 8 and cost == 0:
        ucs_running = False
        return

    # Tìm hàng tiếp theo
    used_rows = {r for (r, _) in state}
    next_row = next((r for r in range(8) if r not in used_rows), None)
    if next_row is None:
        root.after(500, lambda: ucs_step(offsetX))
        return

    # Sinh trạng thái con
    for col in range(8):
        new_state = state + [(next_row, col)]
        new_cost = cost_of_state(new_state)
        heapq.heappush(ucs_frontier, (new_cost, new_state))

    if ucs_running:
        root.after(300, lambda: ucs_step(offsetX))
# ===================== DFS STEP =====================
dfs_running = False
dfs_frontier = []   # stack: list, dùng append/pop
dfs_explored = []   # lưu số trạng thái đã xét

def dfs_step(offsetX):
    global dfs_running, dfs_frontier, dfs_explored
    if not dfs_running:
        return
    if not dfs_frontier:
        dfs_running = False
        return  # không còn trạng thái nào để xét

    # Lấy trạng thái cuối cùng trong stack (LIFO)
    state = dfs_frontier.pop()
    dfs_explored.append(state)

    print(f"DFS: Đang xét trạng thái (số hậu = {len(state)}): {state}")
    
    # Vẽ trạng thái hiện tại
    canvas.delete("queens_right")
    for (r, c) in state:
        ve_queen(c, r, offsetX, tag="queens_right")

    # Nếu tìm được lời giải
    if len(state) == 8:
        dfs_running = False
        return

    # Tìm hàng tiếp theo cần đặt hậu
    used_rows = {r for (r, _) in state}
    next_row = None
    for r in range(8):
        if r not in used_rows:
            next_row = r
            break
    if next_row is None:
        root.after(500, lambda: dfs_step(offsetX))
        return

    # Sinh các trạng thái con theo thứ tự cột → append vào stack
    for col in range(7, -1, -1):  
        # Duyệt ngược từ cột 7 → 0 để khi pop ra sẽ xét cột 0 trước
        if is_safe_state(state, next_row, col):
            new_state = state + [(next_row, col)]
            dfs_frontier.append(new_state)

    # Gọi lại sau 300ms nếu còn chạy
    if dfs_running:
        root.after(300, lambda: dfs_step(offsetX))

# ===================== HÀM ĐIỀU KHIỂN =====================
def start_game():
    global start_state, queue, running, ucs_frontier, ucs_running
    running = False
    ucs_running = False
    queue.clear()
    ucs_frontier.clear()
    clear_queens()

    # Vẽ lại bàn cờ
    ve_banco_daydu(40, side="left")
    ve_banco_daydu(580, side="right")

    # Đặt 1 hậu ngẫu nhiên bên trái
    x = random.randint(0, 7)
    y = random.randint(0, 7)
    ve_queen(x, y, 40, tag="queens_left")

    start_state = [(y, x)]
    queue = deque([start_state])
    ucs_frontier = [(cost_of_state(start_state), start_state)]
    heapq.heapify(ucs_frontier)

def run_ids():
    global ids_running, ids_frontier, ids_depth_limit
    ids_depth_limit = len(start_state)
    ids_frontier =[(start_state, ids_depth_limit)]
    ids_running = True
    ids_step_once(580)

def run_bfs():
    global running
    if not queue:
        print("Chưa có trạng thái bắt đầu. Nhấn Start trước.")
        return
    running = True
    bfs_step(580)

def run_ucs():
    global ucs_running
    if not ucs_frontier:
        print("Chưa có trạng thái bắt đầu!!")
        return
    ucs_running = True
    ucs_step(580)

def run_dfs():
    global dfs_running, dfs_frontier, dfs_explored
    dfs_explored.clear()
    dfs_frontier.clear()

    if not start_state:
        print("Chưa có trạng thái bắt đầu. Nhấn Start trước.")
        return

    dfs_frontier.append(start_state)
    dfs_running = True
    dfs_step(580)

def run_dls():
    """Khởi chạy DLS: đặt stack ban đầu và bắt đầu dls_step."""
    global dls_running, dls_frontier
    dls_frontier.clear()

    if not start_state:
        print("Chưa có trạng thái bắt đầu. Nhấn Start trước.")
        return

    # Độ sâu ban đầu = số hậu trong trạng thái bắt đầu
    initial_depth = len(start_state)
    dls_frontier.append((start_state, initial_depth))
    dls_running = True
    dls_step(580)

def stop_game():
    global running, ucs_running, dls_running, ids_running
    running = False
    ucs_running = False
    dls_running = False
    ids_running = False

def continue_game():
    global running, ucs_running, dls_running, ids_running
    if not running and queue:
        running = True
        bfs_step(580)
    if not ucs_running and ucs_frontier:
        ucs_running = True
        ucs_step(580)
    if not dls_running and dls_frontier:
        dls_running = True
        dls_step(580)
    if not ids_running and ids_frontier:
        ids_running = True
        ids_step_once(580)


# ===================== GIAO DIỆN NÚT BẤM =====================
btn_Start = tk.Button(frame, text="Start (tạo 1 hậu bên trái)", width=25, command=start_game)
btn_Start.pack(side="left", padx=10)

btn_Run = tk.Button(frame, text="Run BFS", width=15, command=run_bfs)
btn_Run.pack(side="left", padx=10)
btn_RunIDS = tk.Button(frame, text="Run IDS", width = 15, command=run_ids)
btn_RunIDS.pack(side = "left", padx = 10)

btn_RunUCS = tk.Button(frame, text="Run UCS", width=15, command=run_ucs)
btn_RunUCS.pack(side="left", padx=10)

btn_RunDFS = tk.Button(frame, text="Run DFS", width=15, command=run_dfs)
btn_RunDFS.pack(side="left", padx=10)

btn_RunDLS = tk.Button(frame, text="Run DLS", width = 15, command=run_dls)
btn_RunDLS.pack(side="left", padx = 10)
btn_Stop = tk.Button(frame, text="Stop", width=15, command=stop_game)
btn_Stop.pack(side="left", padx=10)

btn_Continue = tk.Button(frame, text="Continue", width=15, command=continue_game)
btn_Continue.pack(side="left", padx=10)

btn_Reset = tk.Button(frame, text="Reset (Xóa hậu)", width=15, command=clear_queens)
btn_Reset.pack(side="right", padx=20)

# ===================== LABELS =====================
lbl_left = tk.Label(root, text="Trạng thái bắt đầu", font=("Arial", 12))
lbl_left.place(x=200, y=570)

lbl_right = tk.Label(root, text="Trạng thái mục tiêu", font=("Arial", 12))
lbl_right.place(x=700, y=570)

# Khởi tạo bàn cờ ban đầu
ve_banco_daydu(40, side="left")
ve_banco_daydu(580, side="right")

# ===================== CHẠY GIAO DIỆN =====================
root.mainloop()

# Không in ra tất cả các lựa chọn, chỉ in ra lựa chọn trong hàng đợi ưu tiên của UCS
# In ra mảng truy xuất các đường 
