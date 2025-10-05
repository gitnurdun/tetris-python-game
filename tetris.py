import tkinter as tk
import random
import time
import json
import os
from tkinter import messagebox

class Tetris:
    def __init__(self, master):
        self.width = 10
        self.height = 20
        self.cell_size = 30
        self.colors = ["black", "red", "blue", "green", "yellow", "purple", "cyan", "orange"]
        
        self.shapes = [
            [[1, 1, 1, 1]],               # I
            [[1, 1, 1], [0, 1, 0]],        # T
            [[1, 1, 1], [1, 0, 0]],        # L
            [[1, 1, 1], [0, 0, 1]],        # J
            [[1, 1], [1, 1]],              # O
            [[0, 1, 1], [1, 1, 0]],        # S
            [[1, 1, 0], [0, 1, 1]]         # Z
        ]
        
        self.init_game()
        
        self.master = master
        self.master.title("俄罗斯方块")
        self.master.geometry("650x650")
        
        # 确保游戏有初始的next_piece
        if self.next_piece is None:
            self.get_next_piece()
            
        self.show_menu()

    def init_game(self):
        """初始化游戏状态"""
        self.board = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.current_piece = None
        self.next_piece = None  # 确保初始化后不为None
        self.current_x = 0
        self.current_y = 0
        self.score = 0
        self.level = 1
        self.game_over = False
        self.paused = False
        self.start_time = 0
        self.elapsed_time = 0
        self.get_next_piece()  # 确保初始化时有next_piece
        
    def show_menu(self):
        """显示主菜单界面"""
        for widget in self.master.winfo_children():
            widget.destroy()
            
        menu_frame = tk.Frame(self.master)
        menu_frame.pack(expand=True, fill="both")
        
        tk.Label(menu_frame, text="俄罗斯方块", font=("Arial", 32)).pack(pady=30)
        
        tk.Button(menu_frame, text="开始新游戏", font=("Arial", 18), height=2, 
                 command=self.start_new_game).pack(fill="x", padx=80, pady=10)
        
        if self.save_exists():
            tk.Button(menu_frame, text="继续游戏", font=("Arial", 18), height=2, 
                     command=self.resume_game).pack(fill="x", padx=80, pady=10)
        
        tk.Button(menu_frame, text="历史榜单", font=("Arial", 18), height=2, 
                 command=self.show_highscores).pack(fill="x", padx=80, pady=10)
        
        tk.Button(menu_frame, text="玩法说明", font=("Arial", 18), height=2, 
                 command=self.show_instructions).pack(fill="x", padx=80, pady=10)

    def save_exists(self):
        """检查存档文件是否存在"""
        return os.path.exists("tetris_save.json")
    
    def show_instructions(self):
        """修复1: 使用正确的messagebox调用方式"""
        instructions = (
            "游戏控制:\n\n"
            "← 或 A: 向左移动\n"
            "→ 或 D: 向右移动\n"
            "↑ 或 W: 旋转方块\n"
            "↓ 或 S: 加速下落\n\n"
            "空格键: 暂停/继续游戏\n"
            "ESC键: 返回主菜单\n\n"
            "目标: 尽可能多地消除完整的行来获得高分!"
        )
        messagebox.showinfo("玩法说明", instructions)
    
    def show_highscores(self):
        """显示历史榜单"""
        try:
            with open("tetris_highscores.json", "r") as f:
                highscores = json.load(f)
        except:
            highscores = []
            
        top = tk.Toplevel(self.master)
        top.title("历史榜单")
        top.geometry("400x400")
        
        tk.Label(top, text="历史最高分", font=("Arial", 20)).pack(pady=10)
        
        highscores.sort(key=lambda x: x["score"], reverse=True)
        
        for i, record in enumerate(highscores[:10], 1):
            time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(record["timestamp"]))
            text = f"{i}. 分数: {record['score']} | 时间: {time_str}"
            tk.Label(top, text=text, font=("Arial", 12)).pack(anchor="w", padx=20, pady=2)
    
    def save_highscore(self):
        """保存当前分数到历史榜单"""
        try:
            with open("tetris_highscores.json", "r") as f:
                highscores = json.load(f)
        except:
            highscores = []
            
        new_record = {
            "score": self.score,
            "timestamp": time.time()
        }
        highscores.append(new_record)
        
        with open("tetris_highscores.json", "w") as f:
            json.dump(highscores, f)
    
    def save_game(self):
        """保存当前游戏状态"""
        game_state = {
            "board": self.board,
            "current_piece": self.current_piece,
            "next_piece": self.next_piece,
            "current_x": self.current_x,
            "current_y": self.current_y,
            "score": self.score,
            "level": self.level,
            "elapsed_time": time.time() - self.start_time
        }
        
        with open("tetris_save.json", "w") as f:
            json.dump(game_state, f)
    
    def load_game(self):
        """从存档加载游戏状态"""
        try:
            with open("tetris_save.json", "r") as f:
                game_state = json.load(f)
            
            self.board = game_state["board"]
            self.current_piece = game_state["current_piece"]
            self.next_piece = game_state["next_piece"]
            self.current_x = game_state["current_x"]
            self.current_y = game_state["current_y"]
            self.score = game_state["score"]
            self.level = game_state["level"]
            self.elapsed_time = game_state["elapsed_time"]
            self.start_time = time.time() - self.elapsed_time
            
            # 确保不为None
            if self.next_piece is None:
                self.get_next_piece()
                
            return True
        except:
            return False
    
    def resume_game(self):
        """继续上次存档的游戏"""
        if not self.load_game():
            messagebox.showerror("错误", "无法加载存档")
            return
        
        self.create_game_ui()
        
        if not self.paused:
            self.master.after(500, self.game_loop)
    
    def start_new_game(self):
        """开始新游戏"""
        self.init_game()
        self.get_next_piece()
        self.get_new_piece()
        self.create_game_ui()
        self.start_time = time.time()
        
        self.master.after(500, self.game_loop)
    
    def create_game_ui(self):
        """修复2: 确保在绘制前next_piece已初始化"""
        for widget in self.master.winfo_children():
            widget.destroy()
        
        main_frame = tk.Frame(self.master)
        main_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(
            main_frame,
            width=self.width * self.cell_size,
            height=self.height * self.cell_size,
            bg="white"
        )
        self.canvas.grid(row=0, column=0, rowspan=2, padx=10, pady=10)
        
        side_panel = tk.Frame(main_frame)
        side_panel.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        
        tk.Label(side_panel, text="下一个形状:", font=("Arial", 14)).pack(anchor="w")
        self.next_canvas = tk.Canvas(side_panel, width=120, height=120, bg="lightgray")
        self.next_canvas.pack(pady=5)
        
        self.score_label = tk.Label(side_panel, text=f"分数: {self.score}", font=("Arial", 14))
        self.score_label.pack(anchor="w", pady=10)
        
        self.time_label = tk.Label(side_panel, text="时间: 00:00", font=("Arial", 14))
        self.time_label.pack(anchor="w")
        
        tk.Button(side_panel, text="返回菜单", command=self.show_menu, 
                 font=("Arial", 12)).pack(side="bottom", pady=10)
        
        self.master.bind("<Left>", lambda e: self.move(-1))
        self.master.bind("<Right>", lambda e: self.move(1))
        self.master.bind("<Up>", lambda e: self.rotate())
        self.master.bind("<Down>", lambda e: self.drop())
        self.master.bind("a", lambda e: self.move(-1))
        self.master.bind("d", lambda e: self.move(1))
        self.master.bind("w", lambda e: self.rotate())
        self.master.bind("s", lambda e: self.drop())
        self.master.bind("<space>", lambda e: self.toggle_pause())
        self.master.bind("<Escape>", lambda e: self.show_menu())
        
        # 确保在绘制前已初始化
        self.draw_board()
    
    def get_next_piece(self):
        """获取下一个方块"""
        self.next_piece = {
            "shape": random.randint(0, len(self.shapes) - 1),
            "color": random.randint(1, len(self.colors) - 1),
            "rotation": 0
        }
    
    def get_new_piece(self):
        """获取新方块并放置到顶部"""
        if self.next_piece:
            self.current_piece = self.next_piece
            self.get_next_piece()
        else:
            self.get_next_piece()  # 确保next_piece不为None
            self.current_piece = self.next_piece.copy()
            self.get_next_piece()
        
        self.current_x = self.width // 2 - 1
        self.current_y = 0
        
        if self.check_collision():
            self.game_over = True
            self.save_highscore()
            os.remove("tetris_save.json")
            messagebox.showinfo("游戏结束", f"游戏结束! 最终分数: {self.score}")
            self.show_menu()
    
    def draw_next_piece(self):
        """绘制下一个方块预览"""
        self.next_canvas.delete("all")
        
        # 确保next_piece有效
        if self.next_piece is None:
            return
            
        shape = self.shapes[self.next_piece["shape"]]
        color_idx = self.next_piece["color"]
        
        center_x = 60
        center_y = 60
        
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    cx = center_x + (x - len(row)/2) * self.cell_size * 0.7
                    cy = center_y + (y - len(shape)/2) * self.cell_size * 0.7
                    self.next_canvas.create_rectangle(
                        cx - self.cell_size * 0.6/2,
                        cy - self.cell_size * 0.6/2,
                        cx + self.cell_size * 0.6/2,
                        cy + self.cell_size * 0.6/2,
                        fill=self.colors[color_idx],
                        outline="black"
                    )
    
    def draw_board(self):
        """绘制整个游戏板和当前方块"""
        self.canvas.delete("all")
        
        # 绘制网格线
        for i in range(self.width + 1):
            self.canvas.create_line(
                i * self.cell_size, 0,
                i * self.cell_size, self.height * self.cell_size
            )
            
        for i in range(self.height + 1):
            self.canvas.create_line(
                0, i * self.cell_size,
                self.width * self.cell_size, i * self.cell_size
            )
        
        # 绘制已经落下的方块
        for y in range(self.height):
            for x in range(self.width):
                if self.board[y][x]:
                    color_idx = self.board[y][x]
                    self.draw_cell(x, y, color_idx)
        
        # 绘制当前正在下落的方块
        if self.current_piece:
            shape = self.shapes[self.current_piece["shape"]]
            color_idx = self.current_piece["color"]
            
            rotation = self.current_piece["rotation"]
            rotated_shape = self.rotate_shape(shape, rotation)
            
            for y, row in enumerate(rotated_shape):
                for x, cell in enumerate(row):
                    if cell:
                        self.draw_cell(
                            self.current_x + x, 
                            self.current_y + y,
                            color_idx
                        )
        
        # 确保有next_piece才绘制预览
        if self.next_piece:
            self.draw_next_piece()
        
        elapsed = int(time.time() - self.start_time)
        minutes, seconds = divmod(elapsed, 60)
        self.time_label.config(text=f"时间: {minutes:02d}:{seconds:02d}")
        self.score_label.config(text=f"分数: {self.score}")
    
    def draw_cell(self, x, y, color_idx):
        """在指定位置绘制一个方块单元"""
        self.canvas.create_rectangle(
            x * self.cell_size + 1,
            y * self.cell_size + 1,
            (x + 1) * self.cell_size - 1,
            (y + 1) * self.cell_size - 1,
            fill=self.colors[color_idx],
            outline=""
        )
    
    def rotate_shape(self, shape, rotation):
        """旋转方块形状"""
        rotated = shape
        for _ in range(rotation):
            rotated = list(zip(*rotated[::-1]))
            rotated = [list(row) for row in rotated]
        return rotated
    
    def rotate(self):
        """旋转当前方块"""
        if not self.current_piece or self.paused:
            return
            
        self.current_piece["rotation"] = (self.current_piece["rotation"] + 1) % 4
        
        shape = self.shapes[self.current_piece["shape"]]
        rotated_shape = self.rotate_shape(shape, self.current_piece["rotation"])
        
        if self.check_collision(shape=rotated_shape):
            self.current_piece["rotation"] = (self.current_piece["rotation"] - 1) % 4
        
        self.draw_board()
    
    def move(self, dx):
        """水平移动当前方块"""
        if not self.current_piece or self.paused:
            return
            
        self.current_x += dx
        
        if self.check_collision():
            self.current_x -= dx
        
        self.draw_board()
    
    def drop(self):
        """加速下落"""
        if not self.current_piece or self.paused:
            return
        self.current_y+=2  
        #self.game_loop()
    
    def toggle_pause(self):
        """暂停/继续游戏"""
        self.paused = not self.paused
        if not self.paused:
            self.master.after(500, self.game_loop)
        
    def check_collision(self, x=None, y=None, shape=None):
        """检查当前方块位置是否有效"""
        if not self.current_piece:
            return True
            
        if x is None:
            x = self.current_x
            
        if y is None:
            y = self.current_y
            
        if shape is None:
            shape = self.shapes[self.current_piece["shape"]]
            rotated = self.rotate_shape(shape, self.current_piece["rotation"])
        else:
            rotated = shape
        
        for py, row in enumerate(rotated):
            for px, cell in enumerate(row):
                if cell:
                    try:
                        if (
                            (y + py) >= self.height or 
                            (x + px) < 0 or 
                            (x + px) >= self.width or 
                            (y + py) >= 0 and self.board[y + py][x + px]
                        ):
                            return True
                    except IndexError:
                        return True
        return False
    
    def merge_piece(self):
        """将当前方块合并到游戏板上"""
        if not self.current_piece:
            return
            
        shape = self.shapes[self.current_piece["shape"]]
        rotated = self.rotate_shape(shape, self.current_piece["rotation"])
        color_idx = self.current_piece["color"]
        
        for py, row in enumerate(rotated):
            for px, cell in enumerate(row):
                if cell and 0 <= (self.current_y + py) < self.height:
                    try:
                        self.board[self.current_y + py][self.current_x + px] = color_idx
                    except:
                        pass
    
    def check_lines(self):
        """检查并清除完整的行"""
        lines_cleared = 0
        new_board = []
        
        for y in range(self.height - 1, -1, -1):
            if all(cell != 0 for cell in self.board[y]):
                lines_cleared += 1
            else:
                new_board.append(self.board[y])
        
        for _ in range(lines_cleared):
            new_board.insert(0, [0] * self.width)
        
        self.board = new_board[::-1]
        
        if lines_cleared > 0:
            self.score += [100, 300, 500, 800][min(lines_cleared - 1, 3)] * self.level
            self.level = min(10, self.score // 2000 + 1)
    
    def game_loop(self):
        """游戏主循环"""
        if self.paused or self.game_over:
            return
            
        if self.current_piece:
            self.current_y += 1
            
            if self.check_collision():
                self.current_y -= 1
                self.merge_piece()
                self.check_lines()
                self.get_new_piece()
        else:
            self.get_new_piece()
        
        self.draw_board()
        self.save_game()
        
        if not self.paused and not self.game_over:
            speed = max(100, 500 - (self.level - 1) * 50)
            self.master.after(speed, self.game_loop)

if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
