import pygame
import math
from config import WIDTH, HEIGHT


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 180
        self.health = 100

        # 1 = mirando derecha, -1 = mirando izquierda
        self.facing = 1

        # Control del ataque del machete
        self.attacking = False
        self.attack_timer = 0.0
        self.attack_duration = 0.2

        # Sprite principal
        self.image = pygame.image.load("imagenes/paraguayito.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (180, 210))
        self.w = self.image.get_width()
        self.h = self.image.get_height()

        # ===== ANIMACIÓN DE CAMINAR (4 FRAMES) =====
        self.walk_frames = []
        for i in range(1, 5):

            try:
                img = pygame.image.load(
                    f"imagenes/paraguayito_anim/frame{i}.png"
                ).convert_alpha()
                img = pygame.transform.scale(img, (180, 210))
                self.walk_frames.append(img)
            except:
                break

        self.walk_frame = 0
        self.walk_speed = 0.10
        self.walk_timer = 0

        # ===== ANIMACIÓN DEL MACHETE =====
        self.machete_frames = []
        for i in range(1, 5):
            try:
                img = pygame.image.load(
                    f"imagenes/machete_anim/frame{i}.png"
                ).convert_alpha()
                img = pygame.transform.scale(img, (120, 120))
                self.machete_frames.append(img)
            except:
                break

        if len(self.machete_frames) == 0:
            self.machete_frames = [pygame.Surface((0, 0), pygame.SRCALPHA)]

        self.machete_frame = 0
        self.machete_speed = 0.04
        self.machete_timer = 0

        # ==== SONIDOS ====
        try:
            self.sonido_machete = pygame.mixer.Sound("sonidos/espada.mp3")
        except:
            self.sonido_machete = None

        try:
            self.sonido_golpe = pygame.mixer.Sound("sonidos/efecto_golpe.mp3")
        except:
            self.sonido_golpe = None

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def hurt_rect(self):
        return pygame.Rect(self.x + 70, self.y + 40, self.w - 140, self.h - 80)

    def attack_rect(self):
        offset_y = 80
        offset_x = 120
        w = 50
        h = 50

        if self.facing == 1:
            x = self.x + offset_x
        else:
            x = self.x + self.w - offset_x - w

        y = self.y + offset_y
        return pygame.Rect(x, y, w, h)

    def update(self, dt, keys):
        from joystickmanager import JOYSTICK

        dx = dy = 0

        # ==================== CONTROL TECLADO ====================
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= 1
            self.facing = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += 1
            self.facing = 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += 1

        # ==================== CONTROL JOYSTICK ====================
        if JOYSTICK.connected:
            joy_dx, joy_dy = JOYSTICK.get_movement()

            dx += joy_dx
            dy += joy_dy

            if joy_dx > 0.2:
                self.facing = 1
            elif joy_dx < -0.2:
                self.facing = -1

        # Normalizar movimiento diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        moving = dx != 0 or dy != 0

        # ==================== ANIMACIÓN CAMINAR ====================
        if moving:
            self.walk_timer += dt
            if self.walk_timer >= self.walk_speed:
                self.walk_timer = 0
                self.walk_frame = (self.walk_frame + 1) % len(self.walk_frames)
        else:
            self.walk_frame = 0  # quieto

        # Aplicar movimiento
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt

        # Mantener dentro de la pantalla
        self.x = max(0, min(WIDTH - self.w, self.x))
        self.y = max(0, min(HEIGHT - self.h, self.y))

        # ==================== ANIMACIÓN ATAQUE ====================
        if self.attacking:
            self.attack_timer += dt
            self.machete_timer += dt

            if self.machete_timer >= self.machete_speed:
                self.machete_timer = 0
                self.machete_frame = (self.machete_frame + 1) % len(self.machete_frames)

            if self.attack_timer >= self.attack_duration:
                self.attacking = False
                self.attack_timer = 0
                self.machete_frame = 0

    def attack(self):
        if not self.attacking:
            if self.sonido_machete:
                self.sonido_machete.play()
            self.attacking = True
            self.attack_timer = 0
            self.machete_frame = 0
            return self.attack_rect()
        return None

    def draw(self, surf):

        # ========= SPRITE DEL JUGADOR (animación caminar) =========
        if hasattr(self, "walk_frames") and len(self.walk_frames) > 0:
            sprite = self.walk_frames[self.walk_frame]
        else:
            sprite = self.image

        if self.facing == -1:
            sprite = pygame.transform.flip(sprite, True, False)

        surf.blit(sprite, (self.x, self.y))

        # ========= DIBUJAR MACHETE =========
        machete = self.machete_frames[self.machete_frame]
        angle = 0

        if self.attacking:
            swing = math.sin(self.attack_timer * 12) * 25
            angle = -swing if self.facing == 1 else swing

        machete_offset_x = 120
        machete_offset_y = 100

        if self.facing == 1:
            mx = self.x + machete_offset_x
            my = self.y + machete_offset_y
        else:
            machete = pygame.transform.flip(machete, True, False)
            mx = self.x + (self.w - machete_offset_x - 15)
            my = self.y + machete_offset_y

        if angle != 0:
            machete = pygame.transform.rotate(machete, angle)

        machete_rect = machete.get_rect(center=(mx, my))
        surf.blit(machete, machete_rect)
