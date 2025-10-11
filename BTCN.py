import tkinter as tk
from PIL import Image, ImageTk
import os, random, heapq
from collections import deque
import math

# ===================== KHỞI TẠO GIAO DIỆN =====================
root = tk.Tk()
root.title("8 Queen problem")
root.geometry("1300x800")

canvas = tk.Canvas(root, width=1200, height=650)
canvas.pack(pady=0)

frame = tk.Frame(root)
frame.place(x=0, y=600)

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
    cx = offsetX + x*size + size // 2
    cy = y*size + size // 2
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

# ===================== Hàm heuristic có cost là Khoảng cách Euclid=====================
def heuristic_euclid(state, w_row = 3, w_col = 2, w_diag = 1):
    """
    Hàm heuristic dựa vào khoảng cách Euclid
    w_row, w_col, w_diag: trọng số cho xung đột
    """
    h = 0
    n = len(state)

    for i in range(n):
        r1, c1 = state[i]
        for j in range(i+1, n):
            r2, c2 = state[j]
            dist = math.sqrt((r1 - r2)**2 + (c1 - c2)**2)

            # Cùng hàng/cột/đường chéo => cộng chi phí lớn
            if r1 == r2:
                h += w_row / (dist + 1e-6)
            elif c1 == c2:
                h += w_col / (dist + 1e-6)
            elif abs(r1 - r2) == abs(c1 - c2):
                h += w_diag / (dist + 1e-6)
    return h
# ===================== Greedy STEP =====================
greedy_running = False
greedy_frontier = []
greedy_path = {}

def greedy_step(offsetX):
    global greedy_running, greedy_frontier
    if not greedy_running:
        return
    if not greedy_frontier:
        greedy_running = False
        return
    h, state = heapq.heappop(greedy_frontier)
    
    canvas.delete("queens_right")
    for (r,c) in state:
        ve_queen(c,r,offsetX, tag="queens_right")

    if len(state) == 8 and heuristic_euclid(state) == 0:
        greedy_running = False
        print("Greedy đã tìm thấy lời giải")
        
        path = []
        s = tuple(state)
        while s is not None:
            path.append(list(s))
            s = greedy_path.get(s,None)
        path.reverse()
        print("Đường đi (Greedy): ")
        for p in path:
            print(p)
        return

    # Sinh trạng thái
    used_row = {r for (r,_) in state}
    next_row = next((r for r in range(8) if r not in used_row), None)
    if next_row is None:
        root.after(300, lambda: greedy_step(offsetX))
        return
    
    for col in range(8):
        new_state = state + [(next_row, col)]
        h_new = heuristic_euclid(new_state)
        greedy_path[tuple(new_state)] = state
        heapq.heappush(greedy_frontier, (h_new, new_state))

    if greedy_running:
        root.after(300, lambda: greedy_step(offsetX))
# ===================== A* STEP =====================
astar_running = False
astar_frontier = []
astar_parent = {}


def astar_step(offsetX):
    global astar_running, astar_frontier, astar_parent
    if not astar_running:
        return
    if not astar_frontier:
        astar_running = False
        return
    
    f, g, state = heapq.heappop(astar_frontier)

    canvas.delete("queens_right")
    for(r,c) in state:
        ve_queen(c,r,offsetX, tag ="queens_right")

    if len(state) == 8 and cost_of_state(state) == 0:
        print("Đã tìm thấy lời giải bằng A*!")
        astar_running = False

        path = []
        s = tuple(state)
        while s is not None:
            path.append(s)
            s = astar_parent.get(tuple(s),None)
        
        path.reverse()
        print("Đường đi (A*): ")
        astar_solution_path = path
        for p in path:
            print(p)
        return 

    used_rows = {r for (r,_) in state}
    next_row = next((r for r in range(8) if r not in used_rows), None)
    if next_row is None:
        root.after(500, lambda: astar_step(offsetX))
        return
    
    for col in range(8):
        new_state = state + [(next_row, col)]
        g_new = cost_of_state(new_state)
        h_new = heuristic_euclid(new_state)
        f_new = g_new + h_new

        astar_parent[tuple(new_state)] = state
        heapq.heappush(astar_frontier,(f_new, g_new, new_state))

    if astar_running:
        root.after(300, lambda: astar_step(offsetX))

def heuristic_SA(w_diag = 1, w_col = 2, w_row = 3):
    pass

# ===================== Simulated Annealing STEP =====================


sa_running = False
sa_state = []
sa_temperature = 4.0
sa_cooling_rate = 0.95


def sa_step(offsetX):
    global sa_state, sa_temperature, sa_running
    if not sa_running:
        return


    if sa_temperature < 0.001:
        print("SA dừng do nhiệt độ quá thấp!")
        sa_running = False
        return

# Vẽ trạng thái hiện tại
    canvas.delete("queens_right")
    for (r, c) in sa_state:
        ve_queen(c, r, offsetX, tag="queens_right")

    current_cost = cost_of_state(sa_state)
    if current_cost == 0:
        print("SA đã tìm thấy lời giải!")
        sa_running = False
        return

    # Chọn ngẫu nhiên 1 hàng để thay đổi
    neighbor = sa_state.copy()
    row_to_change = random.randint(0, len(neighbor)-1)
    current_col = neighbor[row_to_change][1]

    # Chọn cột mới khác cột cũ
    new_col = random.choice([c for c in range(8) if c != current_col])
    neighbor[row_to_change] = (neighbor[row_to_change][0], new_col)

    neighbor_cost = cost_of_state(neighbor)

    delta = neighbor_cost - current_cost

    # Quyết định có chấp nhận trạng thái láng giềng hay không

    if delta < 0 or random.random() < math.exp(-delta / sa_temperature):
        sa_state = neighbor

    sa_temperature *= sa_cooling_rate

    if sa_running:
        root.after(500, lambda: sa_step(offsetX))

# ===================== Beam Search =====================
beam_running = False
beam_frontier = []
beam_width = 5

def beam_step(offsetX):
    global beam_running, beam_frontier
    if not beam_running:
        return

    if not beam_frontier:
        print("Beam Search: Không tìm thấy lời giải")
        beam_running = False
        return

    # Lấy tất cả trạng thái ở mức hiện tại
    current_level = beam_frontier

    # Sinh tất cả con từ mỗi trạng thái trong current level
    children = []
    for cost, state in current_level:
        # Nếu là nghiệm thì dừng ngay
        if len(state) == 8 and cost_of_state(state) == 0:
            print("Beam Search: Tìm thấy lời giải")
            beam_running = False
            # Vẽ nghiệm
            canvas.delete("queens_right")
            for (r, c) in state:
                ve_queen(c, r, offsetX, tag="queens_right")
            return

        used_row = {r for (r, _) in state}
        next_row = next((r for r in range(8) if r not in used_row), None)
        if next_row is None:
            continue

        for col in range(8):
            new_state = state + [(next_row, col)]
            new_cost = cost_of_state(new_state)
            children.append((new_cost, new_state))

    if not children:
        print("Beam Search: Không có trạng thái con để mở rộng")
        beam_running = False
        return

    # Chọn beam_width trạng thái tốt nhất làm frontier mới
    children.sort(key=lambda x: x[0])
    beam_frontier = children[:beam_width]

    # Vẽ trạng thái tốt nhất (nhỏ nhất) trong frontier mới
    best_state = beam_frontier[0][1]
    canvas.delete("queens_right")
    for (r, c) in best_state:
        ve_queen(c, r, offsetX, tag="queens_right")

    # Nếu đã tìm thấy nghiệm ở best_state thì dừng
    if len(best_state) == 8 and cost_of_state(best_state) == 0:
        print("Beam Search: Tìm thấy lời giải")
        beam_running = False
        return

    # Tiếp tục sau 300ms nếu vẫn chạy
    if beam_running:
        root.after(300, lambda: beam_step(offsetX))

# ===================== Hill Climbing =====================
hc_running = False
hc_state = []

def hc_step(offsetX):
    global hc_running, hc_state
    if not hc_running:
        return

    # Vẽ trạng thái hiện tại
    canvas.delete("queens_right")
    for (r, c) in hc_state:
        ve_queen(c, r, offsetX, tag="queens_right")

    current_cost = cost_of_state(hc_state)
    print(f"Hill Climbing: cost hiện tại = {current_cost} | state = {hc_state}")

    if current_cost == 0:
        print("Hill Climbing tìm thấy lời giải!")
        hc_running = False
        return

    # Sinh tất cả neighbor: thay cột từng con hậu trên từng hàng
    neighbors = []  # chứa (cost, state)
    for i in range(len(hc_state)):
        row_idx = hc_state[i][0]
        for col in range(8):
            if col == hc_state[i][1]:
                continue
            neighbor = hc_state.copy()
            # thay cột của hàng i
            neighbor[i] = (row_idx, col)
            neighbors.append((cost_of_state(neighbor), neighbor))

    if not neighbors:
        print("Hill Climbing: Không có neighbor nào")
        hc_running = False
        return

    # Chọn neighbor tốt nhất (cost nhỏ nhất)
    neighbors.sort(key=lambda x: x[0])
    best_cost, best_state = neighbors[0]

    # Nếu best không tốt hơn current -> local minimum
    if best_cost >= current_cost:
        print("Hill Climbing đã đạt local minimum (không cải tiến được).")
        hc_running = False
        return

    # Cập nhật trạng thái và tiếp tục
    hc_state = best_state

    if hc_running:
        root.after(300, lambda: hc_step(offsetX))
# ===================== Genetic Algorithm STEP =====================
ga_running = False
ga_population = []
ga_generation = 0
POP_SIZE = 30
MUTATION_RATE = 0.2

def fitness(state):
    # Giá trị càng nhỏ càng tốt, nên đảo lại
    h = heuristic_euclid(state)
    return 1 / (1 + h)  # chuyển thành fitness để maximize


def crossover(parent1, parent2):
    """Tạo con bằng cách lai chéo"""
    point = random.randint(1,len(parent1)-2)
    child = parent1[:point] + parent2[point:]
    return child

def mutate(state):
    """Đột biến: đổi cột ngẫu nhiên của 1 con hậu"""
    if random.random() < MUTATION_RATE:
        idx = random.randint(0,len(state)-1)
        col_new = random.randint(0,7)
        state[idx] = (state[idx][0], col_new)
    return state

def ga_step(offsetX):
    global ga_population, ga_generation, ga_running
    if not ga_running:
        return

    ga_generation += 1

    # Đánh giá fitness
    scored_pop = [(fitness(ind), ind) for ind in ga_population]
    scored_pop.sort(reverse=True, key=lambda x: x[0])

    best_fit, best_state = scored_pop[0]

    # Xóa toàn bộ quân cũ trước khi vẽ
    canvas.delete("queens_right")
    for (r, c) in best_state[:8]:  # chỉ vẽ đúng 8 hậu
        ve_queen(c, r, offsetX, tag="queens_right")

    print(f"GA - Thế hệ {ga_generation}, fitness tốt nhất: {best_fit}")

    if cost_of_state(best_state) == 0:
        print("GA đã tìm thấy lời giải tối ưu!")
        ga_running = False
        return

    # Chọn lọc: lấy top 50% tốt nhất để lai
    parents = [ind for _, ind in scored_pop[:POP_SIZE // 2]]

    new_population = []
    while len(new_population) < POP_SIZE:
        p1, p2 = random.sample(parents, 2)
        child = crossover(p1.copy(), p2.copy())
        child = mutate(child)
        child.sort(key=lambda x: x[0])  # đảm bảo sắp xếp theo hàng
        new_population.append(child)

    ga_population = new_population

    if ga_running:
        root.after(200, lambda: ga_step(offsetX))


# ===================== AND - OR SEARCH =====================

andor_running = False
andor_stack = []

def expand_andor(state):
    """Sinh các trạng thái con cho AND-OR search"""
    children = []
    used_rows = {r for (r, _) in state}
    next_row = next((r for r in range(8) if r not in used_rows), None)
    if next_row is None:
        return []
    for col in range(8):
        if is_safe_state(state, next_row, col):
            children.append(state + [(next_row, col)])
    return children

def andor_step(offsetX):
    global andor_running, andor_stack
    if not andor_running:
        return
    if not andor_stack:
        print("AND-OR Search: Hết trạng thái, không tìm thấy lời giải.")
        andor_running = False
        return

    state = andor_stack.pop() 

    # Vẽ trạng thái hiện tại
    canvas.delete("queens_right")
    for (r, c) in state:
        ve_queen(c, r, offsetX, tag="queens_right")

    print(f"AND-OR Search: đang xét state = {state}")

    if len(state) == 8 and cost_of_state(state) == 0:
        print("AND-OR Search:  Tìm thấy lời giải!")
        andor_running = False
        return

    # Sinh các trạng thái con
    children = expand_andor(state)

    # Thêm vào stack (LIFO) => duyệt chiều sâu trước
    for child in reversed(children):
        andor_stack.append(child)

    if andor_running:
        root.after(300, lambda: andor_step(offsetX))

# =============== Belief Search ===============
def expand_belief_state(belief):
    """Sinh belief state mới: mở rộng mỗi state trong belief bằng cách đặt hậu vào hàng tiếp theo"""
    next_belief = []
    for state in belief:
        used_rows = {r for (r, _) in state}
        next_row = next((r for r in range(8) if r not in used_rows), None)
        if next_row is None:
            continue

        for col in range(8):
            new_state = state + [(next_row, col)]
            next_belief.append(new_state)  
    return next_belief

def belief_step(offsetX):
    global belief_running, belief_frontier
    if not belief_running:
        return
    if not belief_frontier:
        print("Belief Search: Không còn belief state nào, dừng!")
        belief_running = False
        return

    current_belief = belief_frontier.pop(0)
    print(f"Belief Search: Đang xét belief có {len(current_belief)} trạng thái.")
    
    # Vẽ 1 trạng thái đại diện
    if current_belief:
        rep_state = current_belief[0]
        canvas.delete("queens_right")
        for (r, c) in rep_state:
            ve_queen(c, r, offsetX, tag="queens_right")

    # Kiểm tra nếu tất cả trạng thái trong belief đều là nghiệm
    if current_belief and all(len(state) == 8 and cost_of_state(state) == 0 for state in current_belief):
        print("Belief Search: Toàn bộ belief state là nghiệm hợp lệ!")
        belief_running = False
        return

    next_belief = expand_belief_state(current_belief)

    if next_belief:
        next_belief.sort(key=lambda s: cost_of_state(s))
        next_belief = next_belief[:10]  # Giữ top 10 trạng thái tốt nhất
        belief_frontier.append(next_belief)

    if belief_running:
        root.after(300, lambda: belief_step(offsetX))

#=============== No observation ======================
no_obs_running = False
no_obs_belief = []

def no_obs_step(offsetX):
    global no_obs_running, no_obs_belief
    if not no_obs_running:
        return
    if not no_obs_belief:
        print("Không còn trạng thái nào trong belief!")
        no_obs_running = False
        return

    state = no_obs_belief.pop(0)  # lấy 1 trạng thái bất kỳ trong belief

    # Vẽ trạng thái hiện tại bên phải
    canvas.delete("queens_right")
    for (r, c) in state:
        ve_queen(c, r, offsetX, tag="queens_right")

    if len(state) == 8:
        print("Đã tìm thấy lời giải bằng Searching with No Observation!")
        no_obs_running = False
        return

    # Xác định hàng tiếp theo (chưa được dùng)
    used_rows = {r for (r, _) in state}
    next_row = next((r for r in range(8) if r not in used_rows), None)
    if next_row is None:
        root.after(500, lambda: no_obs_step(offsetX))
        return

    # Sinh trạng thái mới cho belief
    for col in range(8):
        if is_safe_state(state, next_row, col):
            no_obs_belief.append(state + [(next_row, col)])

    if no_obs_running:
        root.after(300, lambda: no_obs_step(offsetX))


# =================Backtracking =========================
bt_running = True
bt_solution = []
bt_found = False

def backtracking_step(row, state, offsetX):
    global bt_running, bt_solution, bt_found
    if not bt_running or bt_found:
        return
    
    if row == 8:
        print("Backtracking đã tìm thấy lời giải!!")
        bt_solution = state.copy()
        bt_found = True
        bt_running = False

        canvas.delete("queens_right")
        for (r, c) in bt_solution:
            ve_queen(c, r, offsetX, tag="queens_right")
        return
    
    for col in range(8):
        if is_safe_state(state,row,col):
            new_state = state + [(row, col)]

            canvas.delete("queens_right")
            for (r, c) in new_state:
                ve_queen(c, r, offsetX, tag = "queens_right")
            
            root.after(300, lambda r = row + 1, s = new_state: backtracking_step(r, s, offsetX))
    
    return


# ==================== Forward Checking ====================
fc_running = False
fc_solution = []
fc_found = False

def init_domains():

    return {r: list(range(8)) for r in range (8)}

def forward_checking_step(row, state, domains, offsetX):
    global fc_running, fc_solution, fc_found
    if not fc_running and fc_found:
        return
    
    if len(state) == 8:
        print("Forward Checking đã tìm thấy lời giải")
        fc_solution = state.copy()
        fc_found = True
        fc_running = False

        canvas.delete("queens_right")
        for (r, c) in fc_solution:
            ve_queen(r, c, offsetX, tag = "queens_right")
        return
    
    for col in domains[row]:
        if is_safe_state(state, row, col):
            new_state = state + [(row, col)]

            new_domains = {r: list(cols) for r, cols in domains.items()}
            for r in range (row+1, 8):
                if col in new_domains[r]:
                    new_domains[r].remove(col)
                diag1 = col + (r - row) # Đường chéo phải
                diag2 = col - (r - row) # Đường chéo trái

                if diag1 in new_domains[r]:
                    new_domains[r].remove(diag1)
                if diag2 in new_domains[r]:
                    new_domains[r].remove(diag2)

            if any(len(new_domains[r]) == 0 for r in range( row+1, 8)):
                continue

            canvas.delete("queens_right")
            for (r, c ) in new_state:
                ve_queen(c, r, offsetX, tag = "queens_right")

            root.after(300, lambda r = row + 1, s = new_state, d = new_domains: forward_checking_step(r, s, d, offsetX))
    return

ac3_running = False
ac3_domains = {}
ac3_queue = []

def ac3_revise(i, j):
    global ac3_domains 
    removed = False
    di = ac3_domains[i]
    dj = ac3_domains[j]

    to_remove = []
    for ci in list(di):
        satisf = False
        for cj in dj:
            if ci != cj and abs(ci - cj) != abs(i - j):
                satisf = True
                break
        if not satisf:
            to_remove.append(ci)
    if to_remove:
        for v in to_remove:
            if v in ac3_domains[i]:
                ac3_domains[i].remove(v)
                removed = True
    return removed

def ac3_step(offsetX):
    global ac3_running, ac3_queue, ac3_domains
    if not ac3_running:
        return
    if ac3_queue:
        for r, d in ac3_domains.items():
            if not d:
                print("AC3: Domain rỗng tại hàng", r, "=> Không có nghiệm")
                ac3_running = False
                return
        if all(len(d) == 1 for d in ac3_domains.values()):
            solution = [(r, ac3_domains[r][0]) for r in range(8)]

            canvas.delete("queens_right")
            for(r, c) in solution:
                ve_queen(c, r, offsetX, tag ="queens_right")
            print("AC: Tìm thấy nghiệm: ", solution)
            ac3_running = False
            return
        else:
            print("AC3: Lọc hoàn tất nhưng không tạo được nghiệm (domains vẫn > 1)")
            ac3_running = False
            return
    i, j = ac3_queue.pop(0)
    revised = ac3_revise(i, j)

    if revised:
        if not ac3_domains[i]:
            print("AC: Domains rỗng tại hàng," ,i, "=> Thất bại")
            ac3_running = False
            return
        for k in range(8):
            if k!= i and k != j:
                ac3_queue.append((k,i))
    
    if ac3_running:
        root.after(200, lambda: ac3_step(offsetX))
    

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

def run_astar():
    global astar_running, astar_frontier, astar_parent
    astar_frontier.clear()
    astar_parent.clear()

    if not start_state:
        print("Chưa có trạng thái bắt đầu. Nhấn start trước")
        return

    start_cost = cost_of_state(start_state)
    start_h = heuristic_euclid(start_state)
    heapq.heappush(astar_frontier, (start_cost+ start_h, start_cost, start_state))
    astar_parent[tuple(start_state)] = None

    astar_running = True
    astar_step(580)

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

def run_greedy():
    global greedy_running, greedy_frontier
    greedy_frontier.clear()

    if not start_state:
        print("Chưa có trạng thái ban đầu. Nhấn start trước.")
        return
    
    h_start = heuristic_euclid(start_state)
    heapq.heappush(greedy_frontier,(h_start, start_state))
    greedy_running = True
    print(f"Greedy bắt đầu từ trạng thái: {start_state} | h = {h_start:.3f}")
    greedy_step(580)

def run_sa(offsetX = 580):
    global sa_state, sa_running, sa_temperature
    clear_queens()
    ve_banco_daydu(40, side="left")
    ve_banco_daydu(offsetX, side="right")

    # Khởi tạo: mỗi hàng một con hậu, cột ngẫu nhiên
    sa_state = [(r, random.randint(0, 7)) for r in range(8)]
    sa_temperature = 8.0
    sa_running = True
    print(f"SA bắt đầu với cost = {cost_of_state(sa_state)}")
    sa_step(580)

def run_beam():
    global beam_running, beam_frontier
    if not start_state:
        print("Chưa có trạng thái băt đầu. Nhấn start trước")
        return
    beam_frontier = [(cost_of_state(start_state), start_state)]
    beam_running = True
    print(f"Beam Search bắt đầu với beam_width = {beam_width} | start = {start_state}")
    beam_step(580)

def run_hc():
    global hc_running, hc_state
    if not start_state:
        print("Chưa có trạng thái bắt đầu!")
        return

    # Nếu start_state chưa đủ 8 hậu, bổ sung random cho các hàng còn thiếu
    hc_state = start_state.copy()
    used_rows = {r for (r, _) in hc_state}
    for r in range(8):
        if r not in used_rows:
            hc_state.append((r, random.randint(0, 7)))

    # Sắp xếp hc_state theo hàng (không bắt buộc nhưng dễ quản lý)
    hc_state.sort(key=lambda x: x[0])

    print("Hill Climbing bắt đầu với state:", hc_state, "cost =", cost_of_state(hc_state))
    hc_running = True
    hc_step(580)

def run_ga():
    global ga_population, ga_running, ga_generation

    if not start_state:
        print("Chưa có trạng thái bắt đầu! Nhấn start")
        return

    ga_population = []
    used_rows = {r for (r, _) in start_state}

    for _ in range(POP_SIZE):
        # Dùng list mới hoàn toàn cho mỗi cá thể
        state = list(start_state)  # copy an toàn, tránh tham chiếu chung
        for r in range(8):
            if r not in used_rows:
                state.append((r, random.randint(0, 7)))
        # Đảm bảo state luôn có đúng 8 hậu và không trùng hàng
        state.sort(key=lambda x: x[0])
        ga_population.append(state.copy())

    ga_generation = 0
    ga_running = True
    print("GA bắt đầu với quần thể kích thước:", POP_SIZE)
    ga_step(580)

def run_andor():
    global andor_running, andor_stack
    if not start_state:
        print("Chưa có trạng thái bắt đầu! Nhấn Start trước.")
        return
    andor_stack.clear()
    andor_stack.append(start_state)
    andor_running = True
    print("AND-OR Search bắt đầu với trạng thái:", start_state)
    andor_step(580)

def run_belief():
    global belief_running, belief_frontier
    if not start_state:
        print("Chưa có trạng thái ban đầu, nhấn start trước")
        return
    
    belief_frontier = [[start_state]]
    belief_running = True
    print("Belief Search bắt đầu với 1 belief state")
    belief_step(580)

def run_backtracking():
    global bt_running, bt_solution, bt_found
    bt_solution.clear()
    bt_found = False
    bt_running = True

    print("Backtracking bắt đầu!")
    backtracking_step(0, [], 580)

def run_fc():
    global fc_running, fc_solution, fc_found
    
    fc_solution.clear()
    fc_found = False
    fc_running = True

    domains = init_domains()

    print("Forward Checking bắt đầu")

    forward_checking_step(0, [], domains,580)

def run_no_obs():
    global no_obs_running, no_obs_belief
    no_obs_belief = [[]]   # khởi đầu không có thông tin, chỉ biết trạng thái rỗng
    no_obs_running = True
    no_obs_step(580)

def run_ac3(offsetX = 580):
    global ac3_running, ac3_domains, ac3_queue
    clear_queens()
    ve_banco_daydu(40, side = "left")
    ve_banco_daydu(offsetX, side = "right")

    ac3_domains={r: list(range(8)) for r in range(8)}

    ac3_queue = [(i, j) for i in range(8) for j in range(8) if i != j]

    ac3_running = True
    ac3_step(offsetX)
def stop_game():
    global running, ucs_running, dfs_running, greedy_running
    global sa_running, beam_running, hc_running, ga_running
    global andor_running, belief_running, bt_running, fc_running, ac3_running

    running = False
    ucs_running = False
    dfs_running = False
    greedy_running = False
    sa_running = False
    beam_running = False
    hc_running = False
    ga_running = False
    andor_running = False
    belief_running = False
    bt_running = False
    ac3_running = False
    fc_running = False
    

def continue_game():
    global running, ucs_running, dls_running, ids_running
    global hc_running, sa_running, greedy_running, astar_running
    global ga_running, andor_running, belief_running
    global bt_running, fc_running, ac3_running
    
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
    if not greedy_running and greedy_frontier:
        greedy_running = True
        greedy_step(580)
    if not astar_running and astar_frontier:
        astar_running = True
        astar_step(580)
    if not sa_running:
        sa_running = True
        sa_step(580)
    if not beam_running and beam_frontier:
        beam_running = True
        beam_step(580)
    if not hc_running:
        hc_running = True
        hc_step(580)
    if not ga_running:
        ga_running = True
        ga_step(580)
    if not andor_running:
        andor_running = True
        andor_step(580)
    if not belief_running:
        belief_running = True
        belief_step(580)
    if not bt_running:
        bt_running = True
        backtracking_step(580)
    if not fc_running:
        fc_running = True
        forward_checking_step(580)
    if not ac3_running:
        ac3_running = True
        ac3_step(580)

# ===================== GIAO DIỆN NÚT BẤM =====================
# ===== Frame chứa thuật toán (trái) =====
algo_frame = tk.Frame(frame)
algo_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nw")  # trái trên cùng

# ===== Nhóm 1: BFS, DFS, IDS, DLS =====
listbox1 = tk.Listbox(algo_frame, height=6, width=20)
listbox1.grid(row=0, column=0, padx=10, pady=5)
algos_group1 = [
    ("Run BFS", run_bfs),
    ("Run DFS", run_dfs),
    ("Run IDS", run_ids),
    ("Run DLS", run_dls)
]
for text, _ in algos_group1:
    listbox1.insert(tk.END, text)

# ===== Nhóm 2: UCS, Greedy, A* =====
listbox2 = tk.Listbox(algo_frame, height=6, width=20)
listbox2.grid(row=0, column=1, padx=10, pady=5)
algos_group2 = [
    ("Run UCS", run_ucs),
    ("Run Greedy", run_greedy),
    ("Run A*", run_astar)
]
for text, _ in algos_group2:
    listbox2.insert(tk.END, text)

# ===== Nhóm 3: SA + Beam Search =====
listbox3 = tk.Listbox(algo_frame, height=6, width=20)
listbox3.grid(row=0, column=2, padx=10, pady=5)
algos_group3 = [
    ("Run SA", run_sa),
    ("Run Beam Search", run_beam), 
    ("Run Hill Climbing", run_hc),
    ("Run Genetic Algorithm", run_ga)
]
for text, _ in algos_group3:
    listbox3.insert(tk.END, text)

# ==== Nhóm 4 ====
listbox4 = tk.Listbox(algo_frame, height=6, width=20)
listbox4.grid(row=0, column=3, padx=10, pady=5)

algos_group4 = [
    ("Run AND-OR search", run_andor),
    ("Run Belief Search", run_belief),
    ("Run SNO", run_no_obs)
]
for text,_ in algos_group4:
    listbox4.insert(tk.END, text)

listbox4.bind("<Double-Button-1>", lambda e: on_listbox_select(e, algos_group4))
# ===== Nhóm 5 =======
listbox5 = tk.Listbox(algo_frame, height=6, width=20)
listbox5.grid(row=0, column=4, padx=10, pady=5)
algos_group5 = [
    ("Run Backtracking", run_backtracking),
    ("Run Forward Checking", run_fc),
    ("Run Arc Consistency 3", run_ac3)
]
for text, _ in algos_group5:
    listbox5.insert(tk.END, text)

listbox5.bind("<Double-Button-1>", lambda e: on_listbox_select(e, algos_group5))


# Hàm xử lý double click
def on_listbox_select(event, actions):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        _, func = actions[index]
        func()

listbox1.bind("<Double-Button-1>", lambda e: on_listbox_select(e, algos_group1))
listbox2.bind("<Double-Button-1>", lambda e: on_listbox_select(e, algos_group2))
listbox3.bind("<Double-Button-1>", lambda e: on_listbox_select(e, algos_group3))

# Label hướng dẫn
lbl_hint = tk.Label(algo_frame, text="Nhấp đúp để chạy thuật toán", font=("Arial", 10), fg="gray")
lbl_hint.grid(row=1, column=0, columnspan=3, pady=5)

# ===== Frame chứa 4 nút cố định (phải) =====
control_frame = tk.Frame(frame)
control_frame.grid(row=0, column=1, padx=350, pady=(0, 1000), sticky="n")  

btn_Start = tk.Button(control_frame, text="Start", width=15, command=start_game)
btn_Start.pack(pady=5)

btn_Stop = tk.Button(control_frame, text="Stop", width=15, command=stop_game)
btn_Stop.pack(pady=5)

btn_Continue = tk.Button(control_frame, text="Continue", width=15, command=continue_game)
btn_Continue.pack(pady=5)

btn_Reset = tk.Button(control_frame, text="Reset", width=15, command=clear_queens)
btn_Reset.pack(pady=5)


# ===================== LABELS =====================
lbl_left = tk.Label(root, text="Trạng thái bắt đầu", font=("Arial", 12))
lbl_left.place(x=250, y=500)

lbl_right = tk.Label(root, text="Trạng thái mục tiêu", font=("Arial", 12))
lbl_right.place(x=750, y=500)

# Khởi tạo bàn cờ ban đầu
ve_banco_daydu(40, side="left")
ve_banco_daydu(580, side="right")

# ===================== CHẠY GIAO DIỆN =====================
root.mainloop()


