import os
import sys
from typing import Optional

from src.core.context import AppContext
from src.services.automation_core import AutomationCore

class CliHandler:
    @staticmethod
    def get_mode_choice() -> Optional[str]:
        print("\nSelect Mode:")
        print("1. YouTube Upload + LMS Sync")
        print("2. YouTube Upload Only")
        print("3. LMS Sync from YouTube CSV")
        print("Q. Quit")
        
        choice = input("\nEnter choice (1-3 or Q): ").strip().upper()
        if choice in ['1', '2', '3', 'Q']:
            return choice
        return None

    @staticmethod
    def run_automation(ctx: AppContext, choice: str):
        lms_csv = None
        if choice == '3':
            lms_csv = input("Enter path to YouTube CSV report: ").strip()
            if not os.path.exists(lms_csv):
                ctx.logger.error(f"File {lms_csv} does not exist.")
                return

        def cb(msg: str, p: tuple):
            sys.stdout.write(f"\rProgress: [{p[0]}/{p[1]}] {msg} ".ljust(80))
            sys.stdout.flush()
            if p[0] == p[1]:
                print("\n")

        automation = AutomationCore(
            ctx, cb, 
            error_cb=lambda t, m: ctx.logger.error(f"{t}: {m}")
        )
        automation.execute_automation(choice, lms_csv_path=lms_csv)
