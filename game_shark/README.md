# 🦈 APEX PREDATOR — Shark Evolution Game

A full-featured Python game with hand gesture controls.

---

## 📦 Installation

### 1. Install Python 3.9+
https://www.python.org/downloads/

### 2. Install dependencies

```bash
pip install pygame
```

**For hand gesture controls (optional but recommended):**
```bash
pip install mediapipe opencv-python
```

---

## 🎮 Run the game

```bash
python game.py
```

Or open the folder in VS Code, then press **F5** (with Python extension).

---

## ✋ Controls

| Gesture / Key | Action |
|---|---|
| ← Arrow / A | Swim Left |
| → Arrow / D | Swim Right |
| ↑ Arrow / W / SPACE | Burst Jump |
| Z or X | **BITE** |
| ESC | Pause |
| F1 | Activate webcam gesture |

### Hand Gestures (webcam)
| Gesture | Action |
|---|---|
| Hand moved to the left | Move Left |
| Hand moved to the right | Move Right |
| Hand raised up | Jump / Burst |
| Closed fist | **BITE** |

---

## 🦈 Game Structure

### 5 Levels × 5 Bosses

| Level | Zone | Boss |
|---|---|---|
| 1 | Coastal Shallows | EEL KING Zapper |
| 2 | The Reef | SWORDFISH EMPEROR |
| 3 | Open Ocean | TOXIC KRAKEN |
| 4 | Sunken City | LEVIATHAN PRIME |
| 5 | The Abyss | ABYSSAL LEVIATHAN |

### 4 Evolution Stages
Baby Shark → Reef Shark → Great White → Hammerhead → **MEGALODON**

### 8 Upgrades (3 choices after each boss)
- Swift Fins, Steel Jaws, Titanium Scales, Ocean Healing
- Bloodlust, Razor Reach, Frenzy Boost, Deep Sea Armor

---

## 🔊 Adding Sounds (later)

Place `.wav` or `.ogg` files in `assets/sounds/` and load with:
```python
pygame.mixer.Sound("assets/sounds/bite.wav")
pygame.mixer.music.load("assets/sounds/bgm_level1.ogg")
```

## 🖼 Adding Images / Sprites (later)

Place `.png` files in `assets/images/` and load with:
```python
sprite = pygame.image.load("assets/images/shark.png").convert_alpha()
```

---

## 🛠 VS Code Setup (recommended)

1. Install extension: **Python** (Microsoft)
2. Open folder `shark_game/`
3. Select Python interpreter (Ctrl+Shift+P → "Python: Select Interpreter")
4. Press **F5** → select "Python File"

Enjoy ruling the ocean! 🌊
