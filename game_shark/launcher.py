"""
DEEP FURY — MAIN LAUNCHER
━━━━━━━━━━━━━━━━━━━━━━━━━
Chạy file này để khởi động game.

INSTALL (lần đầu):
  pip install pygame opencv-python mediapipe numpy

CHẠY GAME (keyboard only):
  python launcher.py

CHẠY GAME + ĐIỀU KHIỂN CỬ CHỈ TAY:
  python launcher.py --gesture
"""

import sys
import os

# Gesture mode flag
USE_GESTURE = "--gesture" in sys.argv or "-g" in sys.argv

# Ensure working directory is correct
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import core game - try improved version first, fallback to original
try:
    from shark_game_improved import Game, GameState
    print("[Launcher] Loaded shark_game_improved.py")
except ModuleNotFoundError:
    try:
        from shark_game import Game, GameState
        print("[Launcher] Loaded shark_game.py")
    except ModuleNotFoundError:
        print("[Launcher] ERROR: Cannot find shark_game.py or shark_game_improved.py")
        sys.exit(1)

def main():
    game = Game()

    gesture_ctrl = None
    if USE_GESTURE:
        try:
            from gesture_control import GestureController
            gesture_ctrl = GestureController(game)
            gesture_ctrl.start()
            game.hud.add_notif("🖐 Gesture Control ACTIVE!", (0,255,180), 200)
            print("[Launcher] Gesture control ON.")
        except ImportError as e:
            print(f"[Launcher] Cannot load gesture module: {e}")
            print("  → Install: pip install opencv-python mediapipe")
            print("  → Falling back to keyboard control.")
        except Exception as e:
            print(f"[Launcher] Error: {e}")
            print("  → Falling back to keyboard control.")
    else:
        print("[Launcher] Keyboard mode. Run with --gesture for hand control.")

    # Patch game loop to inject gesture each frame
    original_update = game.update

    def patched_update():
        if gesture_ctrl and gesture_ctrl.running:
            gesture_ctrl.apply_to_game(game)
        original_update()

    game.update = patched_update

    try:
        game.run()
    finally:
        if gesture_ctrl:
            gesture_ctrl.stop()

if __name__ == "__main__":
    main()