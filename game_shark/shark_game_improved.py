"""
╔══════════════════════════════════════════════════════════════╗
║   DEEP FURY: SỰ TRỖI DẬY CỦA SÁT THỦ ĐỈNH CAO                ║
║   BẢN ĐẦY ĐỦ - TIẾNG VIỆT - NÂNG CẤP - BOSS                  ║
╚══════════════════════════════════════════════════════════════╝
"""

import pygame
import math
import random
import sys
import json
import os

# ── KHỞI TẠO ──────────────────────────────────────────────────────
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
W, H = 1280, 720
screen = pygame.display.set_mode((W, H), pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("DEEP FURY - Sát Thủ Đại Dương")
clock = pygame.time.Clock()
FPS = 60

# ── MÀU SẮC ───────────────────────────────────────────────────────
class Colors:
    DEEP = (2, 8, 30)
    ABYSS = (5, 15, 50)
    OCEAN = (10, 40, 90)
    MID = (20, 80, 140)
    SURFACE = (30, 120, 200)
    FOAM = (180, 220, 255)
    WHITE = (255, 255, 255)
    GOLD = (255, 210, 50)
    RED = (220, 40, 40)
    ORANGE = (255, 140, 0)
    GREEN = (40, 220, 100)
    PURPLE = (140, 40, 220)
    CYAN = (40, 220, 255)
    DARK_RED = (120, 10, 10)
    GREY = (80, 80, 100)
    HP_GREEN = (0, 200, 80)
    HP_RED = (200, 50, 50)
    XP_BLUE = (50, 150, 255)

C = Colors

# ── QUẢN LÝ ÂM THANH ─────────────────────────────────────────────
class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.load_sounds()

    def load_sounds(self):
        sound_dir = "assets/sounds"
        os.makedirs(sound_dir, exist_ok=True)
        sound_files = {
            "bite": "bite.wav", "dash": "dash.wav", "evolve": "evolve.wav",
            "upgrade": "upgrade.wav", "hit": "hit.wav", "game_over": "game_over.wav",
            "level_up": "level_up.wav", "boss": "boss.wav", "coin": "coin.wav"
        }
        for name, fname in sound_files.items():
            path = os.path.join(sound_dir, fname)
            if os.path.exists(path):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(self.sfx_volume)
                except:
                    pass

    def play(self, name, loop=False, fade_ms=0):
        if name in self.sounds:
            if loop:
                self.sounds[name].play(-1, fade_ms=fade_ms)
            else:
                self.sounds[name].play(fade_ms=fade_ms)

    def stop(self, name):
        if name in self.sounds:
            self.sounds[name].stop()

    def play_music(self, name="bg_music.ogg", loop=True):
        path = os.path.join("assets/sounds", name)
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1 if loop else 0)

    def stop_music(self, fade_ms=500):
        pygame.mixer.music.fadeout(fade_ms)

    def set_sfx_volume(self, vol):
        self.sfx_volume = max(0.0, min(1.0, vol))
        for s in self.sounds.values():
            s.set_volume(self.sfx_volume)

    def set_music_volume(self, vol):
        self.music_volume = max(0.0, min(1.0, vol))
        pygame.mixer.music.set_volume(self.music_volume)

# ── HỆ THỐNG HẠT (PARTICLE) CẢI TIẾN ──────────────────────────────
class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=4, gravity=0, glow=False):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.color = color
        self.life = self.max_life = life
        self.size = size
        self.gravity = gravity
        self.glow = glow

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1
        self.vx *= 0.98
        return self.life > 0

    def draw(self, surf):
        alpha = int(255 * (self.life / self.max_life))
        r = max(1, int(self.size * (self.life / self.max_life)))
        if self.glow:
            glow_r = r * 2
            glow_surf = pygame.Surface((glow_r*2, glow_r*2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color[:3], alpha//2), (glow_r, glow_r), glow_r)
            surf.blit(glow_surf, (int(self.x)-glow_r, int(self.y)-glow_r))
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], alpha), (r, r), r)
        surf.blit(s, (int(self.x)-r, int(self.y)-r))

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def add(self, particle):
        self.particles.append(particle)

    def update(self):
        self.particles = [p for p in self.particles if p.update()]

    def draw(self, surf):
        for p in self.particles:
            p.draw(surf)

    def spawn_blood(self, x, y, count=20):
        for _ in range(count):
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(2, 8)
            self.add(Particle(x, y, math.cos(angle)*speed, math.sin(angle)*speed,
                              (random.randint(180,255), random.randint(0,40), 0),
                              random.randint(20,50), size=random.randint(3,8), gravity=0.1))

    def spawn_bubbles(self, x, y, count=5):
        for _ in range(count):
            self.add(Particle(x+random.randint(-10,10), y,
                              random.uniform(-0.5,0.5), random.uniform(-3,-1),
                              (180,220,255), random.randint(30,60), size=random.randint(2,6), glow=True))

    def spawn_bite_chunks(self, x, y, count=8):
        for _ in range(count):
            angle = random.uniform(-math.pi/2, math.pi/2)
            speed = random.uniform(3,10)
            self.add(Particle(x, y, math.cos(angle)*speed, math.sin(angle)*speed,
                              (random.randint(150,255), random.randint(100,200), 50),
                              random.randint(15,35), size=random.randint(4,10), gravity=0.15))

    def spawn_evolution(self, x, y):
        for _ in range(80):
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(3,12)
            color = random.choice([(255,210,50),(255,150,0),(255,255,100),(200,100,255)])
            self.add(Particle(x, y, math.cos(angle)*speed, math.sin(angle)*speed,
                              color, random.randint(40,80), size=random.randint(4,10), glow=True))

    def spawn_boss_hit(self, x, y):
        for _ in range(20):
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(4,14)
            self.add(Particle(x, y, math.cos(angle)*speed, math.sin(angle)*speed,
                              (255, random.randint(50,200), 0),
                              random.randint(25,55), size=random.randint(5,12), gravity=0.05, glow=True))

# ── TẠO HÌNH CÁ MẬP ───────────────────────────────────────────────
def make_shark_surface(stage=0, w=120, h=60, mouth_open=0.0, angle=0, color_override=None):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    palettes = [
        {"body": (100,140,160), "belly": (220,230,240), "fin": (80,110,130), "eye": (20,20,20), "glow": None},
        {"body": (60,110,140),  "belly": (200,220,235), "fin": (50,90,120),  "eye": (20,20,20), "glow": None},
        {"body": (40,80,120),   "belly": (180,210,230), "fin": (30,60,100),  "eye": (255,50,50), "glow": None},
        {"body": (20,40,80),    "belly": (100,150,200), "fin": (10,30,70),   "eye": (255,100,0), "glow": (255,150,0,60)},
        {"body": (60,0,80),     "belly": (140,0,160),   "fin": (100,0,120),  "eye": (255,0,255), "glow": (200,0,255,80)},
    ]
    p = palettes[min(stage,4)]
    if color_override:
        p["body"] = color_override
    cx, cy = w//2, h//2

    if p["glow"] and stage>=3:
        for r in range(12,0,-3):
            alpha = 20 + r*3
            glow_col = (*p["glow"][:3], alpha)
            pygame.draw.ellipse(surf, glow_col, (cx-w//2+r, cy-h//2+r//2, w-r*2, h-r//2))

    pygame.draw.ellipse(surf, p["body"], (cx-w//2+4, cy-h//3, w-8, h*2//3))
    pygame.draw.ellipse(surf, p["belly"], (cx-w//3, cy, w*2//3, h//4))
    tail_pts = [(cx+w//2-8, cy), (cx+w//2+20, cy-h//3), (cx+w//2+12, cy), (cx+w//2+20, cy+h//3)]
    pygame.draw.polygon(surf, p["fin"], tail_pts)
    dorsal = [(cx-w//8, cy-h//3), (cx+w//8, cy-h//3), (cx, cy-h//2-(stage*4))]
    pygame.draw.polygon(surf, p["fin"], dorsal)
    pygame.draw.polygon(surf, p["fin"], [(cx-w//6, cy+2), (cx-w//4, cy+h//3), (cx, cy+4)])
    pygame.draw.polygon(surf, p["fin"], [(cx+w//6, cy+2), (cx+w//4, cy+h//3), (cx, cy+4)])
    pygame.draw.polygon(surf, p["body"], [(cx-w//2+4, cy-h//6), (cx-w//2-16, cy), (cx-w//2+4, cy+h//6)])

    if mouth_open > 0:
        mouth_y_top = cy - int(h//4 * mouth_open)
        mouth_y_bot = cy + int(h//4 * mouth_open)
        mx = cx - w//2 - 14
        pygame.draw.polygon(surf, C.DARK_RED, [(mx, mouth_y_top), (mx+18, cy-2), (mx+18, cy+2), (mx, mouth_y_bot)])
        teeth_col = (240,240,200)
        num_teeth = 4 + stage
        for i in range(num_teeth):
            tx = mx + 2 + i*(14//max(num_teeth,1))
            th = 6 + stage
            pygame.draw.polygon(surf, teeth_col, [(tx, mouth_y_top+2), (tx+3, mouth_y_top+2+th), (tx-1, mouth_y_top+2)])

    eye_x, eye_y = cx-w//3, cy-h//6
    pygame.draw.circle(surf, C.WHITE, (eye_x, eye_y), 6+stage)
    pygame.draw.circle(surf, p["eye"], (eye_x, eye_y), 3+stage//2)
    pygame.draw.line(surf, (0,0,0), (eye_x, eye_y-3), (eye_x, eye_y+3), 2)
    if stage>=2:
        for i in range(3):
            sx = cx + i*(w//8)
            pygame.draw.line(surf, p["fin"], (sx, cy-h//4), (sx+6, cy+h//4), 2)
    if angle != 0:
        surf = pygame.transform.rotate(surf, math.degrees(angle))
    return surf

def make_fish(size=20, color=None):
    if color is None:
        color = random.choice([(255,165,0),(255,80,80),(80,200,255),(255,220,80),(180,80,255)])
    s = pygame.Surface((size*2, size), pygame.SRCALPHA)
    pygame.draw.ellipse(s, color, (0, size//4, size*3//2, size//2))
    tail = [(size*3//2, size//4), (size*2, 0), (size*2, size), (size*3//2, size*3//4)]
    pygame.draw.polygon(s, color, tail)
    pygame.draw.circle(s, (20,20,20), (size//3, size//2), 2)
    return s

# ── KẺ ĐỊCH ───────────────────────────────────────────────────────
class Enemy:
    def __init__(self, x, y, etype="fish", level=1):
        self.x, self.y = float(x), float(y)
        self.etype = etype
        self.level = level
        self.alive = True
        self.flash_timer = 0

        cfg = {
            "fish":    {"hp": 10*level, "speed": 2+level*0.3, "dmg": 5,  "score": 10*level,  "size": 20},
            "squid":   {"hp": 20*level, "speed": 3+level*0.2, "dmg": 10, "score": 20*level,  "size": 28},
            "turtle":  {"hp": 40*level, "speed": 1+level*0.1, "dmg": 15, "score": 30*level,  "size": 36},
            "whale":   {"hp": 80*level, "speed": 1.5,          "dmg": 25, "score": 60*level,  "size": 70},
        }
        c = cfg.get(etype, cfg["fish"])
        self.max_hp = self.hp = c["hp"]
        self.speed  = c["speed"]
        self.dmg    = c["dmg"]
        self.score  = c["score"]
        self.size   = c["size"]

        colors = {"fish":(255,165,0),"squid":(200,50,200),"turtle":(50,180,80),"whale":(60,100,180)}
        self.surf = make_fish(self.size, colors.get(etype,(200,200,100)))
        self.vx = random.choice([-1,1]) * self.speed
        self.vy = random.uniform(-0.5, 0.5)
        self.phase_y = random.uniform(0, math.pi*2)
        self.rect = pygame.Rect(self.x, self.y, self.size*2, self.size)

    def update(self, shark_x, shark_y, dt):
        self.phase_y += 0.03
        dx = shark_x - self.x
        dist = math.hypot(dx, shark_y - self.y)
        if dist < 200:
            self.vx += (dx / dist) * (0.05 if self.etype == "whale" else -0.05)
        self.vx = max(-self.speed, min(self.speed, self.vx + random.uniform(-0.1,0.1)))
        self.vy = math.sin(self.phase_y) * 0.8
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.x = self.x % W
        self.y = max(60, min(H - 80, self.y))
        self.rect.topleft = (int(self.x), int(self.y))
        if self.flash_timer > 0:
            self.flash_timer -= 1

    def take_damage(self, dmg):
        self.hp -= dmg
        self.flash_timer = 8
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surf):
        draw_surf = self.surf
        if self.flash_timer > 0 and self.flash_timer % 3 < 2:
            flash = self.surf.copy()
            flash.fill((255, 50, 50, 120), special_flags=pygame.BLEND_RGBA_ADD)
            draw_surf = flash
        if self.vx > 0:
            draw_surf = pygame.transform.flip(draw_surf, True, False)
        surf.blit(draw_surf, (int(self.x), int(self.y)))
        bar_w = self.size * 2
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(surf, C.DARK_RED, (int(self.x), int(self.y)-10, bar_w, 5))
        pygame.draw.rect(surf, C.HP_GREEN, (int(self.x), int(self.y)-10, int(bar_w*hp_ratio), 5))

# ── BOSS ──────────────────────────────────────────────────────────
class Boss:
    TYPES = [
        {"name": "LEVIATHAN", "color": (100,200,255), "hp": 500, "size": 140, "speed": 2.5, "phase_count": 2},
        {"name": "KRAKEN",    "color": (160,0,200),   "hp": 800, "size": 160, "speed": 3,   "phase_count": 3},
        {"name": "VOLCANIC",  "color": (255,100,0),   "hp": 1200,"size": 180, "speed": 3.5, "phase_count": 3},
        {"name": "TITAN RAY", "color": (0,180,200),   "hp": 1600,"size": 200, "speed": 4,   "phase_count": 4},
        {"name": "ABYSS GOD", "color": (80,0,100),    "hp": 2500,"size": 220, "speed": 4.5, "phase_count": 4},
    ]

    def __init__(self, level):
        cfg = self.TYPES[min(level, len(self.TYPES)-1)]
        self.name = cfg["name"]
        self.color = cfg["color"]
        self.max_hp = self.hp = cfg["hp"]
        self.size = cfg["size"]
        self.speed = cfg["speed"]
        self.phase_count = cfg["phase_count"]
        self.phase = 1
        self.x, self.y = float(W-200), float(H//2)
        self.vx, self.vy = -self.speed, 0
        self.alive = True
        self.angle = 0
        self.flash_timer = 0
        self.attack_timer = 0
        self.projectiles = []
        self.enrage_timer = 0
        self.level = level
        self.surf = make_shark_surface(stage=min(level+1,4), w=self.size, h=self.size//2, color_override=self.color)

    def update(self, shark_x, shark_y, dt):
        self.angle = math.sin(pygame.time.get_ticks() * 0.002) * 0.15
        hp_ratio = self.hp / self.max_hp

        thresholds = [0.7, 0.4, 0.2]
        for i, t in enumerate(thresholds[:self.phase_count-1]):
            if hp_ratio < t and self.phase == i+1:
                self.phase = i+2
                self.speed *= 1.3
                self.enrage_timer = 60

        dx = shark_x - self.x
        dy = shark_y - self.y
        dist = math.hypot(dx, dy) or 1
        target_vx = (dx/dist)*self.speed
        target_vy = (dy/dist)*self.speed
        self.vx += (target_vx - self.vx)*0.05
        self.vy += (target_vy - self.vy)*0.05
        self.x += self.vx*dt
        self.y += self.vy*dt
        self.x = max(self.size, min(W-self.size, self.x))
        self.y = max(80, min(H-80, self.y))

        self.attack_timer += 1
        if self.phase >= 2 and self.attack_timer > max(40, 80 - self.level*10):
            self.attack_timer = 0
            ang = math.atan2(shark_y-self.y, shark_x-self.x)
            spread = self.phase - 1
            for s in range(-spread, spread+1):
                a = ang + s*0.25
                self.projectiles.append({
                    "x": self.x, "y": self.y,
                    "vx": math.cos(a)*6, "vy": math.sin(a)*6,
                    "life": 80
                })

        new_proj = []
        for p in self.projectiles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"]>0 and 0<p["x"]<W and 0<p["y"]<H:
                new_proj.append(p)
        self.projectiles = new_proj

        if self.flash_timer > 0:
            self.flash_timer -= 1
        if self.enrage_timer > 0:
            self.enrage_timer -= 1

    def take_damage(self, dmg):
        self.hp -= dmg
        self.flash_timer = 10
        if self.hp <= 0:
            self.alive = False
            return True
        return False

    def draw(self, surf):
        if self.enrage_timer > 0:
            s = pygame.Surface((W,H), pygame.SRCALPHA)
            alpha = int(80 * (self.enrage_timer/60))
            s.fill((255,0,0,alpha))
            surf.blit(s, (0,0))

        draw_surf = self.surf
        if self.flash_timer>0 and self.flash_timer%3<2:
            flash = self.surf.copy()
            flash.fill((255,100,100,150), special_flags=pygame.BLEND_RGBA_ADD)
            draw_surf = flash

        rotated = pygame.transform.rotate(draw_surf, math.degrees(self.angle))
        rect = rotated.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rotated, rect)

        for p in self.projectiles:
            ps = pygame.Surface((16,16), pygame.SRCALPHA)
            pygame.draw.circle(ps, (*self.color,200), (8,8), 6)
            pygame.draw.circle(ps, (255,255,255,150), (8,8), 3)
            surf.blit(ps, (int(p["x"])-8, int(p["y"])-8))

        bar_w, bar_x, bar_y = 400, W//2 - 200, 20
        hp_ratio = max(0, self.hp/self.max_hp)
        pygame.draw.rect(surf, (40,40,40), (bar_x-2, bar_y-2, bar_w+4, 22))
        pygame.draw.rect(surf, C.HP_RED, (bar_x, bar_y, bar_w, 18))
        bar_color = (255, int(200*hp_ratio), 0)
        pygame.draw.rect(surf, bar_color, (bar_x, bar_y, int(bar_w*hp_ratio), 18))
        font_sm = pygame.font.SysFont("consolas", 14, bold=True)
        lbl = font_sm.render(f"⚡ {self.name}  [PHA {self.phase}]  {self.hp}/{self.max_hp}", True, C.WHITE)
        surf.blit(lbl, (bar_x, bar_y+22))

# ── NỀN ĐẠI DƯƠNG ─────────────────────────────────────────────────
class OceanBackground:
    def __init__(self, depth_level=0):
        self.depth = depth_level
        self.scroll_x = 0
        self.bubbles = [(random.randint(0,W), random.randint(0,H), random.uniform(0.3,1.5), random.randint(2,8)) for _ in range(60)]
        self.rays = [(random.randint(0,W), random.uniform(0.2,0.8)) for _ in range(8)]
        self.corals = self._gen_corals()
        self.weed_phase = 0
        self.caustic_phase = 0

    def _gen_corals(self):
        corals = []
        for _ in range(20):
            x = random.randint(0, W*2)
            h = random.randint(30,120)
            color = random.choice([(220,80,80),(80,220,180),(255,180,80),(180,80,220),(80,180,255)])
            corals.append((x, H-40, h, color, random.randint(3,8)))
        return corals

    def _get_sky_colors(self):
        depths = [
            [(20,100,180), (5,50,120)],
            [(10,70,150), (3,35,100)],
            [(5,40,100), (2,20,70)],
            [(3,20,60), (1,10,40)],
            [(5,0,30), (2,0,15)],
        ]
        return depths[min(self.depth,4)]

    def update(self, dt):
        self.scroll_x += 0.2*dt
        self.weed_phase += 0.03
        self.caustic_phase += 0.02
        new_bubbles = []
        for bx,by,spd,r in self.bubbles:
            by -= spd*dt
            if by < -20:
                by = H+10
                bx = random.randint(0,W)
            new_bubbles.append((bx,by,spd,r))
        self.bubbles = new_bubbles

    def draw(self, surf):
        top_c, bot_c = self._get_sky_colors()
        for y in range(H):
            t = y/H
            r = int(top_c[0] + (bot_c[0]-top_c[0])*t)
            g = int(top_c[1] + (bot_c[1]-top_c[1])*t)
            b = int(top_c[2] + (bot_c[2]-top_c[2])*t)
            pygame.draw.line(surf, (r,g,b), (0,y), (W,y))

        if self.depth < 3:
            for i, (rx, intensity) in enumerate(self.rays):
                phase = math.sin(self.caustic_phase + i*0.7)
                alpha = int(20 * intensity * (1+phase) * (1-self.depth/3))
                ray_surf = pygame.Surface((80,H), pygame.SRCALPHA)
                pts = [(0,0), (80,0), (100+int(20*phase), H), (-20+int(20*phase), H)]
                pygame.draw.polygon(ray_surf, (180,220,255,alpha), pts)
                surf.blit(ray_surf, (int(rx+math.sin(self.caustic_phase*0.5+i)*40)-40, 0))

        if self.depth < 2:
            for i in range(12):
                cx = (i*140 + int(self.scroll_x*0.5)) % W
                cy = H-70 + int(math.sin(self.caustic_phase+i)*12)
                cs = pygame.Surface((100,30), pygame.SRCALPHA)
                pygame.draw.ellipse(cs, (150,200,255,40), (0,0,100,30))
                surf.blit(cs, (cx, cy))

        bed_color = [(20,60,40),(15,50,35),(10,35,25),(8,20,15),(5,5,10)][min(self.depth,4)]
        pygame.draw.rect(surf, bed_color, (0, H-60, W, 60))

        for i in range(30):
            wx = (i*60 + self.scroll_x) % W
            wh = random.Random(i).randint(40,120)
            wc = (20+i*5%60, 100+i*3%80, 40)
            for seg in range(wh//10):
                sway = math.sin(self.weed_phase + i*0.4 + seg*0.2) * (seg*2)
                sx = wx + sway
                sy = H-60 - seg*10
                pygame.draw.line(surf, wc, (sx, sy), (sx+sway*0.5, sy-10), 4)

        for cx, cy, ch, cc, cw in self.corals:
            rx = (cx - int(self.scroll_x*0.3)) % (W+200) - 100
            sway = math.sin(self.weed_phase + cx*0.01) * 6
            for i in range(ch):
                t = i/ch
                col = (min(255,cc[0]+i), min(255,cc[1]+i//2), cc[2])
                pygame.draw.circle(surf, col, (int(rx+sway*t), cy-i), max(1, cw - i*cw//ch//2))

        for bx,by,spd,r in self.bubbles:
            bs = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(bs, (180,220,255,120), (r,r), r)
            pygame.draw.circle(bs, (220,240,255,200), (r,r), r, 1)
            surf.blit(bs, (int(bx), int(by)))

        if self.depth >= 2:
            fog = pygame.Surface((W,H), pygame.SRCALPHA)
            fog_alpha = min(120, self.depth*25)
            fog.fill((*bot_c, fog_alpha))
            surf.blit(fog, (0,0))

# ── CÁ MẬP NGƯỜI CHƠI (ĐẦY ĐỦ XP, NÂNG CẤP) ──────────────────────
EVOLUTIONS = [
    {"name": "Cá Mập Sơ Sinh",   "xp_needed": 0,    "speed": 4,   "bite_dmg": 20,  "hp": 100, "size": (90,45)},
    {"name": "Thợ Săn Trẻ",      "xp_needed": 200,  "speed": 5,   "bite_dmg": 35,  "hp": 160, "size": (110,55)},
    {"name": "Cá Mập Trắng",     "xp_needed": 600,  "speed": 6,   "bite_dmg": 60,  "hp": 240, "size": (130,65)},
    {"name": "Cá Mập Khổng Lồ",  "xp_needed": 1400, "speed": 7,   "bite_dmg": 100, "hp": 360, "size": (150,75)},
    {"name": "Thần Cá Mập",      "xp_needed": 3000, "speed": 8.5, "bite_dmg": 180, "hp": 500, "size": (170,85)},
]

UPGRADES = {
    "speed_boost": {"name": "Gia Tăng Tốc", "cost": 100, "max": 5, "desc": "+1 tốc độ mỗi cấp"},
    "damage_up":   {"name": "Sức Mạnh Cắn", "cost": 150, "max": 5, "desc": "+20 sát thương cắn"},
    "hp_up":       {"name": "Da Cứng",      "cost": 120, "max": 5, "desc": "+50 máu tối đa"},
    "regen":       {"name": "Tái Tạo",      "cost": 200, "max": 3, "desc": "Hồi máu theo thời gian"},
    "dash":        {"name": "Phóng Nhanh",  "cost": 250, "max": 3, "desc": "Giảm thời gian hồi phóng"},
}

class Shark:
    def __init__(self):
        self.stage = 0
        self.xp = 0
        self.score = 0
        self.coins = 0
        self.upgrades = {k:0 for k in UPGRADES}
        self.reset_stats()
        self.x, self.y = float(W//4), float(H//2)
        self.vx, self.vy = 0.0, 0.0
        self.facing = 1

        self.swim_phase = 0.0
        self.mouth_open = 0.0
        self.is_biting = False
        self.bite_timer = 0
        self.dash_timer = 0
        self.dash_cooldown = 0
        self.hurt_timer = 0
        self.evolve_anim = 0
        self.tail_wag = 0.0
        self.alive = True
        self.surf_cache = {}

    def reset_stats(self):
        ev = EVOLUTIONS[self.stage]
        hp_up = self.upgrades.get("hp_up", 0)
        speed_up = self.upgrades.get("speed_boost", 0)
        damage_up = self.upgrades.get("damage_up", 0)
        self.max_hp = ev["hp"] + hp_up*50
        self.hp = self.max_hp
        self.speed = ev["speed"] + speed_up
        self.bite_dmg = ev["bite_dmg"] + damage_up*20
        self.w, self.h = ev["size"]

    def get_surf(self):
        key = (self.stage, round(self.mouth_open,1), self.hurt_timer>0)
        if key not in self.surf_cache:
            s = make_shark_surface(self.stage, self.w, self.h, mouth_open=self.mouth_open)
            if self.hurt_timer>0:
                s2 = s.copy()
                s2.fill((255,80,80,100), special_flags=pygame.BLEND_RGBA_ADD)
                s = s2
            self.surf_cache[key] = s
        return self.surf_cache[key]

    def try_evolve(self):
        next_stage = self.stage+1
        if next_stage >= len(EVOLUTIONS):
            return False
        if self.xp >= EVOLUTIONS[next_stage]["xp_needed"]:
            self.stage = next_stage
            self.surf_cache.clear()
            self.evolve_anim = 90
            self.reset_stats()
            self.hp = self.max_hp
            return True
        return False

    def apply_upgrade(self, key):
        upg = UPGRADES[key]
        if self.upgrades[key] < upg["max"] and self.coins >= upg["cost"]:
            self.coins -= upg["cost"]
            self.upgrades[key] += 1
            if key == "hp_up":
                self.max_hp += 50
                self.hp = min(self.hp+50, self.max_hp)
            elif key == "speed_boost":
                self.speed += 1
            elif key == "damage_up":
                self.bite_dmg += 20
            return True
        return False

    def bite(self):
        if not self.is_biting:
            self.is_biting = True
            self.bite_timer = 20
            return True
        return False

    def dash(self):
        if self.dash_cooldown <= 0:
            dash_frames = max(8, 18 - self.upgrades.get("dash",0)*3)
            self.dash_timer = dash_frames
            self.dash_cooldown = 60 - self.upgrades.get("dash",0)*10
            return True
        return False

    def take_damage(self, dmg):
        if self.hurt_timer > 0:
            return
        self.hp -= dmg
        self.hurt_timer = 45
        self.surf_cache.clear()
        if self.hp <= 0:
            self.alive = False

    def update(self, keys, gesture=None, dt=1):
        ax, ay = 0, 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:  ax -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: ax += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:    ay -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:  ay += 1
        if gesture:
            gx, gy = gesture
            ax, ay = gx, gy

        spd = self.speed * (2.5 if self.dash_timer>0 else 1.0)
        self.vx += ax*0.8
        self.vy += ay*0.8
        self.vx *= 0.85
        self.vy *= 0.85
        mag = math.hypot(self.vx, self.vy)
        if mag > spd:
            self.vx = self.vx/mag * spd
            self.vy = self.vy/mag * spd

        self.x += self.vx*dt
        self.y += self.vy*dt
        self.x = max(0, min(W-self.w, self.x))
        self.y = max(50, min(H-self.h-50, self.y))

        if abs(self.vx) > 0.2:
            self.facing = 1 if self.vx>0 else -1

        self.swim_phase += 0.1 + abs(self.vx+self.vy)*0.02
        self.tail_wag = math.sin(self.swim_phase)*8

        if self.is_biting:
            progress = 1 - self.bite_timer/20
            self.mouth_open = math.sin(progress*math.pi)
            self.bite_timer -= 1
            if self.bite_timer <= 0:
                self.is_biting = False
                self.mouth_open = 0.0
                self.surf_cache.clear()
        else:
            if self.mouth_open > 0:
                self.mouth_open = max(0, self.mouth_open-0.1)
                self.surf_cache.clear()

        if self.dash_timer > 0: self.dash_timer -= 1
        if self.dash_cooldown > 0: self.dash_cooldown -= 1
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            if self.hurt_timer == 0:
                self.surf_cache.clear()
        if self.evolve_anim > 0: self.evolve_anim -= 1

        regen_level = self.upgrades.get("regen",0)
        if regen_level>0 and self.hp<self.max_hp:
            self.hp = min(self.max_hp, self.hp + 0.03*regen_level)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.w-10, self.h)

    def draw(self, surf, particles):
        if self.evolve_anim > 0:
            alpha = int(200 * min(1, self.evolve_anim/30))
            es = pygame.Surface((W,H), pygame.SRCALPHA)
            es.fill((255,220,50,alpha//2))
            surf.blit(es, (0,0))

        draw_surf = self.get_surf()
        if abs(self.vx)>3 or self.dash_timer>0:
            trail = draw_surf.copy()
            trail.set_alpha(60)
            flipped_trail = trail if self.facing==1 else pygame.transform.flip(trail, True, False)
            surf.blit(flipped_trail, (int(self.x - self.vx*3), int(self.y - self.vy*3)))
            surf.blit(flipped_trail, (int(self.x - self.vx*6), int(self.y - self.vy*6)))

        draw_x, draw_y = int(self.x), int(self.y + self.tail_wag*0.3)
        if self.facing == -1:
            draw_surf = pygame.transform.flip(draw_surf, True, False)
        surf.blit(draw_surf, (draw_x, draw_y))

        if (abs(self.vx)>2 or abs(self.vy)>2) and random.random()<0.2:
            particles.spawn_bubbles(self.x + (self.w if self.facing==1 else 0), self.y+self.h//2, 1)

# ── GIAO DIỆN HUD (TIẾNG VIỆT) ───────────────────────────────────
class HUD:
    def __init__(self):
        # Dùng font có sẵn hỗ trợ tiếng Việt
        self.font_big = pygame.font.SysFont("consolas", 22, bold=True)
        self.font_med = pygame.font.SysFont("consolas", 16, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 13)
        self.font_title = pygame.font.SysFont("consolas", 48, bold=True)
        self.notifs = []

    def add_notif(self, text, color=C.GOLD, duration=120):
        self.notifs.append([text, duration, color])

    def draw(self, surf, shark, level_num, level_name, wave, total_waves, boss=None):
        hp_ratio = shark.hp/shark.max_hp
        hp_col = C.HP_GREEN if hp_ratio>0.5 else C.ORANGE if hp_ratio>0.25 else C.HP_RED
        pygame.draw.rect(surf, (30,30,30), (20, H-50, 200, 18))
        pygame.draw.rect(surf, hp_col, (20, H-50, int(200*hp_ratio), 18))
        pygame.draw.rect(surf, C.WHITE, (20, H-50, 200, 18), 1)
        hp_lbl = self.font_sm.render(f"HP {int(shark.hp)}/{shark.max_hp}", True, C.WHITE)
        surf.blit(hp_lbl, (22, H-49))

        ev = EVOLUTIONS[shark.stage]
        next_ev = EVOLUTIONS[min(shark.stage+1, len(EVOLUTIONS)-1)]
        xp_start = ev["xp_needed"]
        xp_end = next_ev["xp_needed"]
        xp_ratio = (shark.xp - xp_start)/(xp_end - xp_start) if xp_end>xp_start else 1.0
        pygame.draw.rect(surf, (30,30,30), (20, H-28, 200, 12))
        pygame.draw.rect(surf, C.XP_BLUE, (20, H-28, int(200*xp_ratio), 12))
        pygame.draw.rect(surf, C.WHITE, (20, H-28, 200, 12), 1)
        xp_lbl = self.font_sm.render(f"XP {shark.xp}/{next_ev['xp_needed']}", True, C.WHITE)
        surf.blit(xp_lbl, (22, H-27))

        stage_txt = self.font_med.render(f"◆ {EVOLUTIONS[shark.stage]['name']}", True, C.CYAN)
        surf.blit(stage_txt, (20, H-72))

        score_txt = self.font_med.render(f"⚡ {shark.score}  💎 {shark.coins}", True, C.GOLD)
        surf.blit(score_txt, (W-220, 10))

        lv_txt = self.font_med.render(f"CẤP {level_num}: {level_name}", True, C.WHITE)
        surf.blit(lv_txt, (W//2 - lv_txt.get_width()//2, 10))

        wave_txt = self.font_sm.render(f"Làn {wave}/{total_waves}", True, C.FOAM)
        surf.blit(wave_txt, (W//2 - wave_txt.get_width()//2, 34))

        if shark.dash_cooldown > 0:
            dc = 1 - shark.dash_cooldown/60
            pygame.draw.rect(surf, (30,30,30), (230, H-50, 80, 12))
            pygame.draw.rect(surf, C.CYAN, (230, H-50, int(80*dc), 12))
            dash_lbl = self.font_sm.render("PHÓNG", True, C.CYAN)
            surf.blit(dash_lbl, (230, H-35))

        ctrl = self.font_sm.render("SPACE=Cắn  SHIFT=Phóng  E=Tiến hóa  U=Nâng cấp", True, (150,170,200))
        surf.blit(ctrl, (W//2 - ctrl.get_width()//2, H-18))

        new_notifs = []
        for i, (txt, timer, col) in enumerate(self.notifs):
            alpha = min(255, timer*5)
            ntxt = self.font_big.render(txt, True, col)
            ntxt.set_alpha(alpha)
            surf.blit(ntxt, (W//2 - ntxt.get_width()//2, H//2 - 80 - i*40))
            timer -= 1
            if timer > 0:
                new_notifs.append([txt, timer, col])
        self.notifs = new_notifs

# ── MENU NÂNG CẤP ────────────────────────────────────────────────
class UpgradeMenu:
    def __init__(self):
        self.active = False
        self.font = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_sm = pygame.font.SysFont("consolas", 14)
        self.selected = 0
        self.keys_list = list(UPGRADES.keys())

    def toggle(self):
        self.active = not self.active
        self.selected = 0

    def handle_key(self, key, shark, hud):
        if key == pygame.K_ESCAPE or key == pygame.K_u:
            self.active = False
        elif key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.keys_list)
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.keys_list)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            k = self.keys_list[self.selected]
            if shark.apply_upgrade(k):
                hud.add_notif(f"⬆ Nâng cấp {UPGRADES[k]['name']} thành công!", C.GREEN)
            else:
                hud.add_notif("Không đủ xu hoặc đã đạt cấp tối đa!", C.RED)

    def draw(self, surf, shark):
        if not self.active:
            return
        overlay = pygame.Surface((W,H), pygame.SRCALPHA)
        overlay.fill((0,10,30,200))
        surf.blit(overlay, (0,0))
        title = self.font.render("⚙  CỬA HÀNG NÂNG CẤP", True, C.GOLD)
        surf.blit(title, (W//2 - title.get_width()//2, 80))
        coins_txt = self.font.render(f"💎 Xu: {shark.coins}", True, C.CYAN)
        surf.blit(coins_txt, (W//2 - coins_txt.get_width()//2, 110))

        for i, k in enumerate(self.keys_list):
            upg = UPGRADES[k]
            level = shark.upgrades[k]
            y = 160 + i*70
            bg_col = (0,50,100,180) if i==self.selected else (0,20,50,150)
            bg = pygame.Surface((600,60), pygame.SRCALPHA)
            bg.fill(bg_col)
            surf.blit(bg, (W//2-300, y))
            if i==self.selected:
                pygame.draw.rect(surf, C.CYAN, (W//2-300, y, 600,60), 2)
            name_t = self.font.render(f"{upg['name']}  [{level}/{upg['max']}]", True, C.WHITE)
            surf.blit(name_t, (W//2-290, y+5))
            desc_t = self.font_sm.render(f"{upg['desc']}  |  Giá: 💎{upg['cost']}", True, C.FOAM)
            surf.blit(desc_t, (W//2-290, y+30))
            dots = "●"*level + "○"*(upg["max"]-level)
            dot_t = self.font_sm.render(dots, True, C.GOLD)
            surf.blit(dot_t, (W//2+200, y+10))

        hint = self.font_sm.render("↑↓ Di chuyển  |  ENTER=Mua  |  U/ESC=Đóng", True, C.GREY)
        surf.blit(hint, (W//2 - hint.get_width()//2, H-40))

# ── DỮ LIỆU CÁC MÀN CHƠI (TIẾNG VIỆT) ───────────────────────────
LEVELS = [
    {"id": 1, "name": "Vùng Nước Nông Ánh Nắng",
     "story": "Bạn vừa nở ra từ quả trứng ở vùng nước nông ấm áp.\nNhỏ bé và đói, hãy học cách săn mồi.",
     "depth": 0, "waves": 4, "enemies": [("fish",1), ("fish",1), ("fish",2)], "boss_type": 0, "reward_coins": 80},
    {"id": 2, "name": "Rạn San Hô Chết Chóc",
     "story": "Lớn lên, bạn dấn thân vào rạn san hô.\nNhững kẻ săn mồi ẩn nấp giữa các rạn.",
     "depth": 1, "waves": 5, "enemies": [("fish",2),("squid",1),("fish",3),("turtle",1)], "boss_type": 1, "reward_coins": 140},
    {"id": 3, "name": "Vùng Hoàng Hôn",
     "story": "Sâu hơn bây giờ. Ánh sáng nhạt dần.\nNhững sinh vật cổ đại thức giấc trong bóng tối.",
     "depth": 2, "waves": 6, "enemies": [("squid",2),("turtle",2),("squid",3),("whale",1)], "boss_type": 2, "reward_coins": 200},
    {"id": 4, "name": "Miệng Phun Núi Lửa",
     "story": "Bạn lặn xuống vùng nước núi lửa.\nSinh vật sinh ra từ lửa và áp lực thách thức bạn.",
     "depth": 3, "waves": 7, "enemies": [("turtle",3),("whale",2),("whale",3)], "boss_type": 3, "reward_coins": 300},
    {"id": 5, "name": "Vực Thẳm Vĩnh Cửu",
     "story": "Đáy đại dương sâu nhất. Bóng tối thuần khiết.\nBạn đối mặt với Chúa Tể Vực Thẳm.",
     "depth": 4, "waves": 8, "enemies": [("whale",3),("whale",4),("whale",5)], "boss_type": 4, "reward_coins": 500},
]

class GameState:
    MENU = "menu"
    STORY = "story"
    PLAYING = "playing"
    BOSS = "boss_fight"
    UPGRADE = "upgrade"
    WIN_LEVEL = "win_level"
    GAME_OVER = "game_over"
    WIN_GAME = "win_game"
    PAUSE = "pause"

# ── LỚP GAME CHÍNH ───────────────────────────────────────────────
class Game:
    def __init__(self):
        self.sound = SoundManager()
        self.state = GameState.MENU
        self.shark = Shark()
        self.bg = OceanBackground(0)
        self.particles = ParticleSystem()
        self.hud = HUD()
        self.upgrade_menu = UpgradeMenu()
        self.enemies = []
        self.current_level_idx = 0
        self.current_wave = 0
        self.wave_timer = 0
        self.boss = None
        self.story_timer = 0
        self.story_text = ""
        self.menu_phase = 0.0
        self.font_title = pygame.font.SysFont("consolas", 52, bold=True)
        self.font_big   = pygame.font.SysFont("consolas", 26, bold=True)
        self.font_med   = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_sm    = pygame.font.SysFont("consolas", 14)
        self.win_timer  = 0
        self.gesture_dir = None
        self.menu_shark_x = 0.0
        self.menu_shark_y = H//2
        self.menu_fish = [Enemy(random.randint(200,W), random.randint(100,H-100), "fish", 1) for _ in range(8)]

    def start_level(self, idx):
        self.current_level_idx = idx
        self.current_wave = 0
        lvl = LEVELS[idx]
        self.bg = OceanBackground(lvl["depth"])
        self.enemies = []
        self.boss = None
        self.state = GameState.STORY
        self.story_text = lvl["story"]
        self.story_timer = 180

    def spawn_wave(self):
        lvl = LEVELS[self.current_level_idx]
        self.enemies = []
        wave_idx = self.current_wave % len(lvl["enemies"])
        etype, el = lvl["enemies"][wave_idx]
        count = 4 + self.current_wave
        for _ in range(count):
            x = random.choice([random.randint(W+50, W+200), random.randint(-200, -50)])
            y = random.randint(80, H-100)
            self.enemies.append(Enemy(x, y, etype, el))

    def start_boss(self):
        lvl = LEVELS[self.current_level_idx]
        self.boss = Boss(lvl["boss_type"])
        self.enemies = []
        self.state = GameState.BOSS
        self.hud.add_notif(f"⚠ TRÙM: {self.boss.name} XUẤT HIỆN!", C.RED, 180)
        self.sound.play("boss")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.start_level(0)
                    elif event.key == pygame.K_l:
                        self._load()
                elif self.state == GameState.STORY:
                    self.story_timer = 0
                elif self.state in (GameState.PLAYING, GameState.BOSS):
                    if event.key == pygame.K_SPACE:
                        if self.shark.bite():
                            self._check_bite()
                            self.sound.play("bite")
                    elif event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                        if self.shark.dash():
                            self.sound.play("dash")
                    elif event.key == pygame.K_e:
                        if self.shark.try_evolve():
                            self.particles.spawn_evolution(self.shark.x+self.shark.w//2, self.shark.y+self.shark.h//2)
                            self.hud.add_notif(f"★ TIẾN HÓA THÀNH {EVOLUTIONS[self.shark.stage]['name']}!", C.GOLD, 150)
                            self.sound.play("evolve")
                    elif event.key == pygame.K_u:
                        self.upgrade_menu.toggle()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSE
                elif self.state == GameState.PAUSE:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_s:
                        self._save()
                        self.hud.add_notif("Đã lưu trò chơi!", C.GREEN)
                        self.state = GameState.PLAYING
                elif self.state == GameState.UPGRADE:
                    self.upgrade_menu.handle_key(event.key, self.shark, self.hud)
                    if event.key == pygame.K_RETURN and not self.upgrade_menu.active:
                        self._next_level()
                elif self.state == GameState.WIN_LEVEL:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.UPGRADE
                        self.upgrade_menu.active = True
                elif self.state in (GameState.GAME_OVER, GameState.WIN_GAME):
                    if event.key == pygame.K_RETURN:
                        self._restart()

                if self.upgrade_menu.active and self.state not in (GameState.WIN_LEVEL, GameState.UPGRADE):
                    self.upgrade_menu.handle_key(event.key, self.shark, self.hud)

    def _check_bite(self):
        bite_rect = pygame.Rect(
            self.shark.x - 30 if self.shark.facing == -1 else self.shark.x + self.shark.w - 10,
            self.shark.y, 60, self.shark.h
        )
        for e in self.enemies[:]:
            if bite_rect.colliderect(e.rect):
                dmg = self.shark.bite_dmg
                killed = e.take_damage(dmg)
                self.particles.spawn_blood(e.x+e.size, e.y+e.size//2, 15)
                self.particles.spawn_bite_chunks(e.x+e.size, e.y+e.size//2, 5)
                if killed:
                    self.shark.xp += e.score//5
                    self.shark.score += e.score
                    self.shark.coins += random.randint(3,10)
                    self.sound.play("coin")
        if self.boss and self.boss.alive:
            if bite_rect.colliderect(pygame.Rect(self.boss.x-self.boss.size//2,
                                                   self.boss.y-self.boss.size//4,
                                                   self.boss.size, self.boss.size//2)):
                dmg = self.shark.bite_dmg
                killed = self.boss.take_damage(dmg)
                self.particles.spawn_boss_hit(self.boss.x, self.boss.y)
                if killed:
                    self.particles.spawn_evolution(self.boss.x, self.boss.y)
                    self.hud.add_notif(f"★ HẠ TRÙM THÀNH CÔNG!", C.GOLD, 180)
                    self.shark.score += 500 * (self.current_level_idx+1)
                    self.shark.coins += LEVELS[self.current_level_idx]["reward_coins"]
                    self.win_timer = 120
                    self.state = GameState.WIN_LEVEL
                    self.sound.play("level_up")

    def _next_level(self):
        self.upgrade_menu.active = False
        next_idx = self.current_level_idx + 1
        if next_idx >= len(LEVELS):
            self.state = GameState.WIN_GAME
        else:
            self.start_level(next_idx)

    def _save(self):
        data = {
            "stage": self.shark.stage,
            "xp": self.shark.xp,
            "score": self.shark.score,
            "coins": self.shark.coins,
            "upgrades": self.shark.upgrades,
            "level": self.current_level_idx,
        }
        with open("savegame.json", "w") as f:
            json.dump(data, f)

    def _load(self):
        if os.path.exists("savegame.json"):
            with open("savegame.json") as f:
                data = json.load(f)
            self.shark.stage = data.get("stage", 0)
            self.shark.xp    = data.get("xp", 0)
            self.shark.score = data.get("score", 0)
            self.shark.coins = data.get("coins", 0)
            self.shark.upgrades = data.get("upgrades", {k:0 for k in UPGRADES})
            self.shark.reset_stats()
            self.start_level(data.get("level", 0))
            self.hud.add_notif("Đã tải dữ liệu!", C.GREEN)

    def _restart(self):
        self.__init__()

    def update(self):
        dt = 1
        keys = pygame.key.get_pressed()

        if self.state == GameState.MENU:
            self.bg.update(dt)
            self.menu_phase += 0.02
            self.menu_shark_x = (self.menu_shark_x + 2) % (W+200)
            self.menu_shark_y = H//2 + math.sin(self.menu_phase)*60
            for mf in self.menu_fish:
                mf.update(self.menu_shark_x, self.menu_shark_y, dt)

        elif self.state == GameState.STORY:
            self.bg.update(dt)
            self.story_timer -= 1
            if self.story_timer <= 0:
                self.state = GameState.PLAYING
                self.spawn_wave()

        elif self.state in (GameState.PLAYING, GameState.BOSS):
            if self.upgrade_menu.active:
                return
            self.bg.update(dt)
            self.shark.update(keys, self.gesture_dir, dt)
            self.particles.update()

            dead = []
            for e in self.enemies:
                e.update(self.shark.x, self.shark.y, dt)
                if self.boss:
                    for proj in self.boss.projectiles[:]:
                        if pygame.Rect(proj["x"]-8, proj["y"]-8, 16, 16).colliderect(self.shark.get_rect()):
                            self.shark.take_damage(15 * self.boss.phase)
                            self.boss.projectiles.remove(proj)
                            self.particles.spawn_blood(self.shark.x+self.shark.w//2, self.shark.y+self.shark.h//2, 8)
                            self.sound.play("hit")
                            break
                if e.rect.colliderect(self.shark.get_rect()):
                    self.shark.take_damage(e.dmg//10)
                    self.sound.play("hit")
                if not e.alive:
                    dead.append(e)
            for e in dead:
                self.enemies.remove(e)

            if self.boss and self.boss.alive:
                self.boss.update(self.shark.x, self.shark.y, dt)
                bd = math.hypot(self.boss.x - self.shark.x, self.boss.y - self.shark.y)
                if bd < self.boss.size//2 + 30:
                    self.shark.take_damage(self.boss.phase*2)
                    self.sound.play("hit")

            if self.state == GameState.PLAYING and len(self.enemies) == 0:
                self.current_wave += 1
                lvl = LEVELS[self.current_level_idx]
                if self.current_wave >= lvl["waves"]:
                    self.start_boss()
                else:
                    self.wave_timer = 60
                    self.hud.add_notif(f"Làn {self.current_wave+1}!", C.CYAN)
                    self.spawn_wave()

            if self.wave_timer > 0:
                self.wave_timer -= 1

            if not self.shark.alive:
                self.state = GameState.GAME_OVER
                self.sound.play("game_over")

        elif self.state == GameState.WIN_LEVEL:
            self.win_timer -= 1
            self.bg.update(dt)
            self.shark.update(keys, None, dt)

    def draw(self):
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.STORY:
            self._draw_story()
        elif self.state in (GameState.PLAYING, GameState.BOSS):
            self._draw_game()
        elif self.state == GameState.WIN_LEVEL:
            self._draw_win_level()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()
        elif self.state == GameState.WIN_GAME:
            self._draw_win_game()
        elif self.state == GameState.PAUSE:
            self._draw_pause()
        elif self.state == GameState.UPGRADE:
            self._draw_game()
            self.upgrade_menu.draw(screen, self.shark)
        pygame.display.flip()

    def _draw_menu(self):
        self.bg.draw(screen)
        for mf in self.menu_fish:
            mf.draw(screen)
        ms = make_shark_surface(0, 100, 50, mouth_open=abs(math.sin(self.menu_phase*3))*0.4)
        screen.blit(ms, (int(self.menu_shark_x-200)%W, int(self.menu_shark_y)))
        glow_s = pygame.Surface((W,200), pygame.SRCALPHA)
        pygame.draw.rect(glow_s, (0,30,80,120), (0,0,W,200))
        screen.blit(glow_s, (0, H//2-160))
        title1 = self.font_title.render("DEEP FURY", True, C.CYAN)
        title2 = self.font_title.render("Sự Trỗi Dậy Của Sát Thủ Đỉnh Cao", True, C.GOLD)
        screen.blit(title1, (W//2 - title1.get_width()//2, H//2-140))
        screen.blit(title2, (W//2 - title2.get_width()//2, H//2-85))
        blink = abs(math.sin(self.menu_phase*3))
        col = (int(200*blink+55), int(220*blink+35), 255)
        start_t = self.font_big.render("[ ENTER ] Bắt Đầu Game Mới", True, col)
        screen.blit(start_t, (W//2 - start_t.get_width()//2, H//2))
        load_t = self.font_med.render("[ L ] Tải Game", True, C.FOAM)
        screen.blit(load_t, (W//2 - load_t.get_width()//2, H//2+45))
        for i, ev in enumerate(EVOLUTIONS):
            sx = 80 + i*(W-160)//len(EVOLUTIONS)
            ss = make_shark_surface(i, 80, 40)
            screen.blit(ss, (sx, H-120))
            lbl = self.font_sm.render(ev["name"], True, C.FOAM)
            screen.blit(lbl, (sx - lbl.get_width()//4, H-75))
        ver = self.font_sm.render("DEEP FURY v2.0 | Python + Pygame | Hỗ trợ cử chỉ tay", True, C.GREY)
        screen.blit(ver, (W//2 - ver.get_width()//2, H-30))

    def _draw_story(self):
        self.bg.draw(screen)
        overlay = pygame.Surface((W,H), pygame.SRCALPHA)
        overlay.fill((0,5,20,160))
        screen.blit(overlay, (0,0))
        lvl = LEVELS[self.current_level_idx]
        title = self.font_big.render(f"— Cấp {lvl['id']}: {lvl['name']} —", True, C.GOLD)
        screen.blit(title, (W//2 - title.get_width()//2, H//2-80))
        for i, line in enumerate(self.story_text.split("\n")):
            lt = self.font_med.render(line, True, C.FOAM)
            screen.blit(lt, (W//2 - lt.get_width()//2, H//2-20 + i*32))
        hint = self.font_sm.render("(Nhấn phím bất kỳ để bỏ qua)", True, C.GREY)
        screen.blit(hint, (W//2 - hint.get_width()//2, H-40))

    def _draw_game(self):
        self.bg.draw(screen)
        for e in self.enemies:
            e.draw(screen)
        if self.boss and self.boss.alive:
            self.boss.draw(screen)
        self.particles.draw(screen)
        self.shark.draw(screen, self.particles)
        lvl = LEVELS[self.current_level_idx]
        self.hud.draw(screen, self.shark, lvl["id"], lvl["name"],
                      self.current_wave+1, lvl["waves"], self.boss)
        if self.upgrade_menu.active:
            self.upgrade_menu.draw(screen, self.shark)

    def _draw_win_level(self):
        self._draw_game()
        overlay = pygame.Surface((W,H), pygame.SRCALPHA)
        overlay.fill((0,30,10,180))
        screen.blit(overlay, (0,0))
        wt = self.font_title.render("HOÀN THÀNH CẤP!", True, C.GOLD)
        screen.blit(wt, (W//2 - wt.get_width()//2, H//2-80))
        lvl = LEVELS[self.current_level_idx]
        coins_t = self.font_big.render(f"+ 💎 {lvl['reward_coins']} xu nhận được", True, C.CYAN)
        screen.blit(coins_t, (W//2 - coins_t.get_width()//2, H//2))
        cont = self.font_med.render("[ ENTER ] Tiếp tục đến cửa hàng nâng cấp", True, C.FOAM)
        screen.blit(cont, (W//2 - cont.get_width()//2, H//2+60))

    def _draw_game_over(self):
        self.bg.draw(screen)
        overlay = pygame.Surface((W,H), pygame.SRCALPHA)
        overlay.fill((40,0,0,200))
        screen.blit(overlay, (0,0))
        got = self.font_title.render("BẠN ĐÃ TỬ TRẬN", True, C.RED)
        screen.blit(got, (W//2 - got.get_width()//2, H//2-100))
        sc = self.font_big.render(f"Điểm số cuối: {self.shark.score}", True, C.GOLD)
        screen.blit(sc, (W//2 - sc.get_width()//2, H//2))
        hint = self.font_med.render("[ ENTER ] Chơi lại", True, C.FOAM)
        screen.blit(hint, (W//2 - hint.get_width()//2, H//2+60))

    def _draw_win_game(self):
        screen.fill(C.DEEP)
        overlay = pygame.Surface((W,H), pygame.SRCALPHA)
        overlay.fill((0,0,60,180))
        screen.blit(overlay, (0,0))
        wt = self.font_title.render("★ SÁT THỦ ĐỈNH CAO ★", True, C.GOLD)
        screen.blit(wt, (W//2 - wt.get_width()//2, H//2-120))
        sub = self.font_big.render("Bạn đã chinh phục đại dương sâu thẳm!", True, C.CYAN)
        screen.blit(sub, (W//2 - sub.get_width()//2, H//2-50))
        sc = self.font_big.render(f"Điểm số cuối: {self.shark.score}", True, C.WHITE)
        screen.blit(sc, (W//2 - sc.get_width()//2, H//2+10))
        godshark = make_shark_surface(4, 200, 100, mouth_open=0.5)
        screen.blit(godshark, (W//2-100, H//2+60))
        hint = self.font_med.render("[ ENTER ] Chơi lại", True, C.FOAM)
        screen.blit(hint, (W//2 - hint.get_width()//2, H-60))

    def _draw_pause(self):
        self._draw_game()
        overlay = pygame.Surface((W,H), pygame.SRCALPHA)
        overlay.fill((0,10,30,180))
        screen.blit(overlay, (0,0))
        pt = self.font_title.render("TẠM DỪNG", True, C.CYAN)
        screen.blit(pt, (W//2 - pt.get_width()//2, H//2-80))
        for i, txt in enumerate(["[ ESC ] Tiếp tục", "[ S ] Lưu game", "[ ENTER ] Menu chính"]):
            t = self.font_big.render(txt, True, C.WHITE)
            screen.blit(t, (W//2 - t.get_width()//2, H//2 + i*50))

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)

# ── ĐIỂM BẮT ĐẦU ─────────────────────────────────────────────────
if __name__ == "__main__":
    game = Game()
    game.run()