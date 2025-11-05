import pygame
import random
from config import WIDTH, HEIGHT, draw_text


class Enemy:
    def __init__(self, x, y, name="enemy", hp=30, speed=60, w=36, h=36):
        self.whip_active = False
        self.whip_start = 0
        self.whip_duration = 2
        self.whip_rect = None
        self.whip_hit = False

        self.x = x
        self.y = y
        self.w = w
        self.h = h

        # 🔥 Fix: ahora todos los enemigos tienen dirección visual
        self.facing_right = False

        self.hitbox_offset_x = 0
        self.hitbox_offset_y = 0
        self.hitbox_width_reduce = 0
        self.hitbox_height_reduce = 0

        self.hp = hp
        self.max_hp = hp
        self.speed = speed
        self.name = name
        self.color = (140, 180, 120)

        self.state = "idle"
        self.dir = random.choice([-1, 1])
        self.timer = 0

    # HITBOX donde recibe daño y hace daño por contacto
    def rect(self):
        # Aplicar offsets y asegurar que la caja nunca tenga tamaño negativo
        x = self.x + self.hitbox_offset_x
        y = self.y + self.hitbox_offset_y
        w = max(1, self.w - self.hitbox_width_reduce)
        h = max(1, self.h - self.hitbox_height_reduce)
        return pygame.Rect(x, y, w, h)

    def update(self, dt, player):
        distx = player.x - self.x
        disty = player.y - self.y
        dist = (distx**2 + disty**2) ** 0.5

        if dist < 500:
            if distx > 2:
                self.x += self.speed * dt * 0.9
            if distx < -2:
                self.x -= self.speed * dt * 0.9
            if disty > 2:
                self.y += self.speed * dt * 0.9
            if disty < -2:
                self.y -= self.speed * dt * 0.9
        else:
            self.timer -= dt
            if self.timer <= 0:
                self.dir = random.choice([-1, 0, 1])
                self.timer = random.uniform(1.0, 3.0)
            self.x += self.dir * self.speed * dt * 0.5

        self.x = max(0, min(WIDTH - self.w, self.x))
        self.y = max(0, min(HEIGHT - self.h, self.y))

    #        if self.name == "Kurupí":
    #            if not self.whip_active and dist < 120:
    #                self.whip_active = True
    #                self.whip_start = pygame.time.get_ticks()
    #                self.whip_hit = False
    #
    #                facing = 1 if distx > 0 else -1
    #                if facing == 1:
    #                    self.whip_rect = pygame.Rect(self.x + self.w, self.y + 10, 80, 12)
    #                else:
    #                    self.whip_rect = pygame.Rect(self.x - 40, self.y + 10, 40, 12)
    #
    #                if self.whip_rect and self.whip_rect.colliderect(player.hurt_rect()) and not self.whip_hit:
    #                    player.health -= 15
    #                    self.whip_hit = True
    #                    self.whip_active = False
    #                    self.whip_rect = None

    #                elapsed = (pygame.time.get_ticks() - self.whip_start) / 1000
    #                if elapsed > 0.20:
    #                    self.whip_active = False
    #                    self.whip_rect = None
    #
    def take_damage(self, d):
        self.hp -= d

    def draw(self, surf):
        pygame.draw.rect(surf, self.color, (self.x, self.y, self.w, self.h))

    def draw_debug(self, surf):
        pygame.draw.rect(surf, (0, 255, 0), self.rect(), 2)
        pygame.draw.rect(surf, (255, 0, 0), self.rect(), 1)

        if self.name == "Kurupí" and self.whip_active and self.whip_rect:
            pygame.draw.rect(surf, (255, 255, 0), self.whip_rect, 2)


# ==================== EXPLICACIÓN DEL FLUJO ====================
"""
CICLO DE VIDA DE UN ENEMIGO:

1. CREACIÓN (Constructor):
   - Se inicializa con posición, nombre, vida y velocidad

2. ACTUALIZACIÓN (update):
   a. Calcula distancia al jugador
   b. Decide comportamiento:
      - Si está cerca: PERSIGUE al jugador
      - Si está lejos: PATRULLA aleatoriamente
   c. Ejecuta ataques especiales (látigo del Kurupí)
   d. Mantiene al enemigo dentro de la pantalla

3. RECIBIR DAÑO (take_damage):
   - Reduce vida cuando el jugador ataca
   - El nivel verifica si hp <= 0 para eliminarlo

4. DIBUJO (draw):
   - Dibuja el cuerpo del enemigo
   - Muestra barra de vida si está dañado
   - Muestra el nombre
   - Dibuja ataques activos (látigo)

ENEMIGOS ESPECIALES:
- Kurupí: Tiene ataque de látigo de 40 píxeles de alcance
- Otros enemigos: Solo persiguen y hacen daño por contacto
- Jefes: Usan esta misma clase pero con más HP y velocidad
"""
