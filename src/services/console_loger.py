class ConsoleLogger:
    def info(self, m: str): 
        print(f"[INFO] {m}")

    def error(self, m: str): 
        print(f"[ERROR] {m}")

    def warning(self, m: str): 
        print(f"[WARN] {m}")
