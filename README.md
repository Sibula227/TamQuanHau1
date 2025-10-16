# Dự Án Giải Bài Toán 8 Quân Hậu với Nhiều Thuật Toán AI

## 🎯 Mục tiêu dự án

Dự án mô phỏng bài toán **8 quân hậu (8-Queens Problem)** bằng cách sử dụng nhiều thuật toán tìm kiếm và tối ưu hóa trong trí tuệ nhân tạo. Mỗi thuật toán sẽ được trực quan hóa trên bàn cờ, giúp người học dễ dàng quan sát cách thuật toán hoạt động.

## 🖥️ Giao diện chương trình

- Bàn cờ trái: Trạng thái khởi tạo hoặc trạng thái đang duyệt.
- Bàn cờ phải: Trạng thái mục tiêu hoặc trạng thái hiện tại của thuật toán.
- Các nhóm thuật toán được đặt trong các **ListBox** tiện lợi.
- Các nút điều khiển: **Start – Stop – Continue – Reset**.

## 📌 Các nhóm thuật toán

### **Nhóm 1 – Tìm kiếm không có thông tin (Uninformed Search)**

- BFS (Breadth-First Search)
- DFS (Depth-First Search)
- IDS (Iterative Deepening Search)
- DLS (Depth-Limited Search)

### **Nhóm 2 – Tìm kiếm có thông tin (Informed Search)**

- UCS (Uniform Cost Search)
- Greedy Best-First Search
- A\*

### **Nhóm 3 – Thuật toán Heuristic / Local Search**

- Simulated Annealing (SA)
- Beam Search
- Hill Climbing (HC)
- Genetic Algorithm (GA)

### **Nhóm 4 – Tìm kiếm đặc biệt**

- Belief Search
- AndOr Search
- No Observation Search

### **Nhóm 5 – Ràng buộc (Constraint Satisfaction Problem – CSP)**

- Backtracking
- Forward Checking
- AC-3 (Arc Consistency Algorithm)

---

## 🛠️ Cách sử dụng chương trình

1. Nhấn **Start** để tạo trạng thái ngẫu nhiên.
2. Chọn thuật toán trong ListBox → **Double Click** để chạy.
3. Dùng **Stop – Continue – Reset** để điều khiển.

---

## 📂 Cấu trúc dự án

```
|-- project_8queens
    |-- main.py
    |-- wq.png         # Ảnh quân hậu
    |-- README.md
```

---

## 🚀 Hướng phát triển tương lai

- Thêm so sánh hiệu năng giữa các thuật toán.
- Xuất dữ liệu đường đi và số bước tìm kiếm.
- Thêm animation hoặc âm thanh khi tìm được nghiệm.

---

## 👨‍💻 Tác giả & Đóng góp

- Sinh viên: _Trần Minh Trọng Nhân_
- Môn học: Trí Tuệ Nhân Tạo / Artificial Intelligence
- Mọi đóng góp hoặc thắc mắc: **tranminhtrongnhan22072005@gmail.com**

_Chúc bạn bảo vệ đồ án thật tốt!_ 🇻🇳
