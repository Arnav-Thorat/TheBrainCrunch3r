import tkinter as tk
import random
import time
from threading import Thread
import numpy as np

class BrainCruncher:
    def __init__(self, root):
        self.root = root
        self.root.title("The Brain Cruncher")
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg="#f0f4f8")

        self.difficulty_limits = {"Easy": 50, "Medium": 199, "Hard": 499}
        self.difficulty_speeds = {"Easy": 1500, "Medium": 2000, "Hard": 2500}
        self.division_limits = {"Easy": 10, "Medium": 20, "Hard": 40}

        self.start_screen()

    def start_screen(self):
        self.clear()
        frame = tk.Frame(self.root, bg="#f0f4f8")
        frame.pack(expand=True)

        tk.Label(frame, text="The Brain Cruncher", font=("Arial", 36, "bold"), bg="#f0f4f8", fg="#2c3e50").pack(pady=40)
        tk.Label(frame, text="Choose Difficulty:", font=("Arial", 24), bg="#f0f4f8", fg="#34495e").pack(pady=20)

        for level in ["Easy", "Medium", "Hard"]:
            tk.Button(frame, text=level, font=("Arial", 20), width=12, bg="#3498db", fg="white", activebackground="#2980b9",
                      command=lambda l=level: self.start_game(l)).pack(pady=10)

        tk.Button(frame, text="Close", font=("Arial", 14), command=self.root.destroy, bg="#95a5a6", fg="white").pack(pady=20)

    def start_game(self, difficulty):
        self.clear()
        self.difficulty = difficulty
        self.speed = self.difficulty_speeds[difficulty]
        self.limit = self.difficulty_limits[difficulty]
        self.div_limit = self.division_limits[difficulty]
        self.operations = []
        self.current_index = 0

        while True:
            self.start_value = int(np.random.choice(range(1, self.limit + 1), p=self.get_weighted_probs(self.limit)))
            self.result = self.start_value
            self.operations = []
            success = self.generate_operations()
            if success:
                break

        Thread(target=self.run_game).start()

    def get_weighted_probs(self, limit):
        weights = np.exp(-np.linspace(0, 3, limit))
        return weights / weights.sum()

    def generate_operations(self):
        temp_result = self.start_value
        ops = []
        prev_op = None

        for _ in range(random.randint(10, 15)):
            possible_ops = ["+", "-"]
            if prev_op not in ["*", "/"]:
                possible_ops += ["*", "/"]
            op = random.choice(possible_ops)

            if op == "+":
                max_val = self.limit - temp_result
                if max_val <= 0:
                    return False
                num = int(np.random.choice(range(1, max_val + 1), p=self.get_weighted_probs(max_val)))
                temp_result += num
            elif op == "-":
                if temp_result == 0:
                    return False
                num = random.randint(1, temp_result)
                temp_result -= num
            elif op == "*":
                max_val = self.limit // temp_result if temp_result != 0 else 0
                if max_val <= 1:
                    return False
                num = int(np.random.choice(range(2, max_val + 1), p=self.get_weighted_probs(max_val - 1)))
                temp_result *= num
            elif op == "/":
                divisors = [i for i in range(2, min(temp_result + 1, self.div_limit + 1)) if temp_result % i == 0 and temp_result // i <= self.limit]
                if not divisors:
                    return False
                num = random.choice(divisors)
                temp_result //= num

            ops.append((op, num))
            prev_op = op

        self.result = temp_result
        self.operations = ops
        return True

    def run_game(self):
        self.clear()
        frame = tk.Frame(self.root, bg="#f0f4f8")
        frame.pack(expand=True)

        self.display_label = tk.Label(frame, font=("Arial", 32), bg="#f0f4f8", fg="#2c3e50")
        self.display_label.pack(pady=60)

        self.progress = tk.Canvas(frame, width=500, height=30, bg="lightgrey", highlightthickness=0)
        self.progress.pack(pady=20)

        tk.Button(frame, text="Restart", font=("Arial", 14), command=self.start_screen, bg="#e74c3c", fg="white", activebackground="#c0392b").pack(pady=10)

        self.countdown(frame)
        self.update_display(f"Start with {self.start_value}")
        self.animate_progress(self.speed)

        for op, num in self.operations:
            expression = self.word_operation(op, num)
            self.update_display(expression)
            self.animate_progress(self.speed)

        self.ask_user()

    def countdown(self, frame):
        label = tk.Label(frame, font=("Arial", 48, "bold"), bg="#f0f4f8", fg="#e67e22")
        label.pack(pady=10)
        for i in ["Get Ready!", "3", "2", "1"]:
            label.config(text=i)
            label.update()
            time.sleep(1)
        label.destroy()

    def word_operation(self, op, num):
        words = {"+": "Add", "-": "Subtract", "*": "Multiply by", "/": "Divide by"}
        return f"{words[op]} {num}"

    def animate_progress(self, duration_ms):
        self.progress.delete("bar")
        steps = 100
        for i in range(steps):
            width = (i + 1) * 5
            self.progress.create_rectangle(0, 0, width, 30, fill="green", tags="bar")
            self.progress.update()
            time.sleep(duration_ms / 1000 / steps)

    def update_display(self, text):
        self.display_label.config(text=text)
        self.display_label.update_idletasks()

    def ask_user(self):
        self.clear()
        frame = tk.Frame(self.root, bg="#f0f4f8")
        frame.pack(expand=True)

        tk.Label(frame, text="What's your final answer?", font=("Arial", 28), bg="#f0f4f8", fg="#2c3e50").pack(pady=40)
        self.answer_entry = tk.Entry(frame, font=("Arial", 24), justify="center")
        self.answer_entry.pack(pady=20)
        tk.Button(frame, text="Submit", font=("Arial", 18), command=self.check_answer, bg="#27ae60", fg="white", activebackground="#1e8449").pack(pady=10)
        tk.Button(frame, text="Restart", font=("Arial", 14), command=self.start_screen, bg="#e67e22", fg="white").pack(pady=10)

    def check_answer(self):
        try:
            user_ans = int(self.answer_entry.get())
            if user_ans == self.result:
                self.show_result("Correct! 🎉")
            else:
                self.show_result(f"Wrong. 😢 Correct answer was {self.result}")
        except ValueError:
            self.show_result("Please enter a valid number.")

    def show_result(self, msg):
        self.clear()
        frame = tk.Frame(self.root, bg="#f0f4f8")
        frame.pack(expand=True)
        tk.Label(frame, text=msg, font=("Arial", 28), bg="#f0f4f8", fg="#2c3e50").pack(pady=60)
        tk.Button(frame, text="Play Again", font=("Arial", 18), command=self.start_screen, bg="#2980b9", fg="white").pack(pady=20)

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = BrainCruncher(root)
    root.mainloop()
