#!/usr/bin/env python3
import sys
import platform
import subprocess
from pathlib import Path
from datetime import datetime

def is_wsl():
    """WSL 환경인지 확인"""
    try:
        with open('/proc/version', 'r') as f:
            return 'microsoft' in f.read().lower() or 'wsl' in f.read().lower()
    except:
        return False

def notify(message):
    """크로스 플랫폼 알림 함수"""
    # 현재 폴더 이름 가져오기
    folder_name = Path.cwd().name
    full_message = f"{folder_name}: {message}"

    # 타임스탬프 출력
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Hook triggered at: {timestamp}")

    system = platform.system()

    try:
        if system == "Windows" or is_wsl():
            # Windows/WSL: PowerShell TTS 사용
            powershell_cmd = "powershell.exe" if is_wsl() else "powershell"
            ps_command = f"Add-Type -AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('{full_message}')"
            subprocess.run([powershell_cmd, "-Command", ps_command],
                         capture_output=True, check=False)
            print(f"Notification: {full_message}")

        elif system == "Darwin":  # macOS
            # macOS: say 명령어 사용
            subprocess.run(["say", full_message],
                         capture_output=True, check=False)

        elif system == "Linux":
            # Linux: espeak 또는 spd-say 시도
            # espeak 먼저 시도
            result = subprocess.run(["which", "espeak"],
                                  capture_output=True, check=False)
            if result.returncode == 0:
                subprocess.run(["espeak", full_message],
                             capture_output=True, check=False)
            else:
                # spd-say 시도
                result = subprocess.run(["which", "spd-say"],
                                      capture_output=True, check=False)
                if result.returncode == 0:
                    subprocess.run(["spd-say", full_message],
                                 capture_output=True, check=False)
                else:
                    # TTS 없으면 콘솔 출력만
                    print(f"Notification: {full_message}")
                    print("(TTS not available - install espeak or speech-dispatcher)")

        else:
            # 기타 시스템: 콘솔 출력만
            print(f"Notification: {full_message}")

    except Exception as e:
        print(f"Notification (fallback): {full_message}")
        print(f"Error: {e}")

if __name__ == "__main__":
    message = sys.argv[1] if len(sys.argv) > 1 else "작업 완료"
    notify(message)
