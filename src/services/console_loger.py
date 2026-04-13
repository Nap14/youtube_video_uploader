class ConsoleLogger:
    def info(self, m): 
        print(f"[INFO] {m}")

    def error(self, m): 
        print(f"[ERROR] {m}")

    def warning(self, m): 
        print(f"[WARN] {m}")

