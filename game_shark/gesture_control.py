"""
GESTURE CONTROL MODULE
━━━━━━━━━━━━━━━━━━━━━
Điều khiển cá mập bằng cử chỉ tay qua webcam.
"""

import cv2
import mediapipe as mp
import numpy as np
import threading
import math

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

class GestureController:
    def __init__(self, game_ref):
        self.game = game_ref
        self.running = False
        self.thread = None
        self.cap = None
        self.mirror = True

        self.direction = (0, 0)
        self.action = None
        self.gesture_name = "None"
        self.palm_history = []
        self.SMOOTH = 6

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[GestureControl] Started.")

    def stop(self):
        self.running = False
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()
        print("[GestureControl] Stopped.")

    def _fingers_up(self, hand_landmarks):
        lm = hand_landmarks.landmark
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]
        up = []
        up.append(lm[tips[0]].x < lm[pips[0]].x)
        for i in range(1, 5):
            up.append(lm[tips[i]].y < lm[pips[i]].y)
        return up

    def _palm_center(self, hand_landmarks):
        lm = hand_landmarks.landmark
        wrist = lm[0]
        mid_mcp = lm[9]
        cx = (wrist.x + mid_mcp.x) / 2
        cy = (wrist.y + mid_mcp.y) / 2
        return cx, cy

    def _classify_gesture(self, fingers, hand_landmarks):
        thumb, index, middle, ring, pinky = fingers
        if sum(fingers) >= 4:
            return "move"
        if sum(fingers) == 0:
            return "bite"
        if index and not middle and not ring and not pinky:
            return "dash"
        if index and middle and not ring and not pinky:
            return "upgrade"
        if thumb and pinky and not index and not middle and not ring:
            return "evolve"
        return "move"

    def _loop(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("[GestureControl] Cannot open webcam.")
            return

        W_cam = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        H_cam = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cx_base, cy_base = 0.5, 0.5
        DEAD_ZONE = 0.1
        MAX_RANGE = 0.35

        with mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.6,
            max_num_hands=1
        ) as hands:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                if self.mirror:
                    frame = cv2.flip(frame, 1)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(rgb)

                ax, ay = 0.0, 0.0
                gesture = "None"

                if results.multi_hand_landmarks:
                    hl = results.multi_hand_landmarks[0]
                    fingers = self._fingers_up(hl)
                    g = self._classify_gesture(fingers, hl)
                    gesture = g

                    mp_drawing.draw_landmarks(frame, hl, mp_hands.HAND_CONNECTIONS)

                    pcx, pcy = self._palm_center(hl)
                    self.palm_history.append((pcx, pcy))
                    if len(self.palm_history) > self.SMOOTH:
                        self.palm_history.pop(0)
                    smooth_cx = sum(p[0] for p in self.palm_history) / len(self.palm_history)
                    smooth_cy = sum(p[1] for p in self.palm_history) / len(self.palm_history)

                    if g == "move":
                        dx = smooth_cx - cx_base
                        dy = smooth_cy - cy_base
                        dist = math.hypot(dx, dy)
                        if dist > DEAD_ZONE:
                            strength = min(1.0, (dist - DEAD_ZONE) / (MAX_RANGE - DEAD_ZONE))
                            ax = (dx / dist) * strength * 3
                            ay = (dy / dist) * strength * 3
                        self.action = None
                    elif g == "bite":
                        self.action = "bite"
                    elif g == "dash":
                        self.action = "dash"
                    elif g == "evolve":
                        self.action = "evolve"
                    elif g == "upgrade":
                        self.action = "upgrade"
                else:
                    self.palm_history.clear()
                    self.action = None

                self.direction = (ax, ay)
                self.gesture_name = gesture

                cv2.putText(frame, f"Gesture: {gesture}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 200), 2)
                cv2.putText(frame, f"Dir: {ax:.2f}, {ay:.2f}", (10, 60),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,0), 2)

                cxpx, cypx = int(cx_base * W_cam), int(cy_base * H_cam)
                cv2.circle(frame, (cxpx, cypx), int(DEAD_ZONE * W_cam), (80,80,80), 1)
                cv2.circle(frame, (cxpx, cypx), int(MAX_RANGE * W_cam), (80,80,80), 1)

                legends = ["✋ Open=Move", "✊ Fist=Bite", "☝ Index=Dash", "✌ V=Upgrade", "🤙 ThumbPinky=Evolve"]
                for i, leg in enumerate(legends):
                    cv2.putText(frame, leg, (W_cam - 200, 30 + i*22),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200,200,255), 1)

                cv2.imshow("DEEP FURY - Gesture Control", frame)
                key = cv2.waitKey(1)
                if key == 27:
                    self.running = False

        self.cap.release()
        cv2.destroyAllWindows()

    def apply_to_game(self, game):
        if not self.running:
            return
        game.shark_game_ref = self
        game.gesture_dir = self.direction if any(abs(v) > 0.05 for v in self.direction) else None

        if self.action == "bite":
            if game.shark.bite():
                game._check_bite()
            self.action = None
        elif self.action == "dash":
            game.shark.dash()
            self.action = None
        elif self.action == "evolve":
            if game.shark.try_evolve():
                game.particles.spawn_evolution(
                    game.shark.x + game.shark.w // 2,
                    game.shark.y + game.shark.h // 2
                )
                game.hud.add_notif(f"★ TIẾN HÓA THÀNH {game.shark.evo['name']}!", (255,210,50), 150)
            self.action = None
        elif self.action == "upgrade":
            game.upgrade_menu.toggle()
            self.action = None