import pygame
import random
from config import (
    WIDTH,
    HEIGHT,
    draw_text,
    draw_hud,
    draw_boss_health_bar,
    draw_enemy_health_bar,
    draw_intro_overlay,
)
from enemy import Enemy
from pages import ScreenBase
from powerup import PowerUpManager
from joystickmanager import JOYSTICK


class Level2Screen(ScreenBase):
    def __init__(self, manager):
        from game_state import GAME

        self.manager = manager
        self.GAME = GAME
        self.player = GAME.player

        self.powerup_manager = PowerUpManager()
        self.enemies = []
        self.boss_active = False
        self.game_over = False
        self.victory = False

        # ==================== ENEMIGOS COMUNES (MOÑÁI) ====================
        self.enemy_frames = []
        for i in range(1, 4):
            try:
                img = pygame.image.load(
                    f"imagenes/moñai_anim/frame{i}.png"
                ).convert_alpha()
                img = pygame.transform.scale(img, (150, 150))
                self.enemy_frames.append(img)
            except:
                pass

        for i in range(5):
            e = Enemy(
                random.randint(120, WIDTH - 220),
                random.randint(150, HEIGHT - 150),
                name="Moñái",
                hp=70,
                speed=70,
            )

            e.anim_timer = 0
            e.current_frame = 0
            e.facing_right = False  # <-- NECESARIO PARA EL GIRO

            # Tamaño real del sprite
            e.w = 150
            e.h = 150

            # HITBOX NIVEL 2
            e.hitbox_offset_x = 30
            e.hitbox_offset_y = 25
            e.hitbox_width_reduce = 40
            e.hitbox_height_reduce = 40

            self.enemies.append(e)

        # ==================== JEFE: AO AO ====================
        self.boss = Enemy(
            WIDTH - 160, HEIGHT // 2 - 60, name="Ao Ao", hp=350, speed=80, w=220, h=220
        )
        self.boss.facing_right = False

        # HITBOX JEFE
        self.boss.hitbox_offset_x = 80
        self.boss.hitbox_offset_y = 20
        self.boss.hitbox_width_reduce = 150
        self.boss.hitbox_height_reduce = 30

        self.boss_frames = []
        for i in range(1, 4):
            try:
                img = pygame.image.load(
                    f"imagenes/aoao_anim/frame{i}.png"
                ).convert_alpha()
                img = pygame.transform.scale(img, (220, 220))
                self.boss_frames.append(img)
            except:
                pass

        self.current_frame_boss = 0
        self.frame_timer_boss = 0
        self.frame_speed = 0.15

        # ==================== FONDO ====================
        try:
            self.bg_image = pygame.image.load("imagenes/fondo_aoao.jpg").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        except:
            self.bg_image = None

        # ==================== INTRO ====================
        self.countdown = 10.0
        self.text_alpha = 0
        self.started = False

        # ==================== MÚSICA ====================
        try:
            pygame.mixer.music.load("sonidos/audio_level2.mp3")
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)
        except:
            pass

    # ==================== INPUT ====================
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                self.manager.pop()

            if event.key == pygame.K_p:
                from level3 import Level3Screen

                pygame.mixer.music.stop()
                self.manager.push(Level3Screen(self.manager))
                return

            if not self.started:
                return

            if event.key == pygame.K_SPACE:
                atk = self.player.attack()
                if atk:
                    damage = getattr(self.player, "attack_damage", 30)
                    for e in self.enemies + ([self.boss] if self.boss_active else []):
                        if atk.colliderect(e.rect()):
                            if self.player.sonido_golpe:
                                self.player.sonido_golpe.play()
                            e.take_damage(damage)
                            self.GAME.score += 15

            if event.key == pygame.K_RETURN and self.victory:
                from level3 import Level3Screen

                pygame.mixer.music.stop()
                self.GAME.score += 150
                self.manager.push(Level3Screen(self.manager))

    # ==================== UPDATE ====================
    def update(self, dt):

        if not self.started:
            self.countdown -= dt
            self.text_alpha = min(255, self.text_alpha + dt * 80)
            if self.countdown <= 0:
                self.started = True
            return

        self.powerup_manager.update(dt, self.player)

        if self.game_over or self.victory:
            return

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)
        # === LIMITAR MOVIMIENTO DEL JUGADOR A LA MITAD INFERIOR ===
        if self.player.y < HEIGHT // 2 - 100:
            self.player.y = HEIGHT // 2 - 100
        if self.player.y + self.player.h > HEIGHT:
            self.player.y = HEIGHT - self.player.h

        # ATAQUE JOYSTICK
        if JOYSTICK.connected and JOYSTICK.is_attack_pressed():
            atk = self.player.attack()
            if atk:
                damage = getattr(self.player, "attack_damage", 30)
                for e in self.enemies + ([self.boss] if self.boss_active else []):
                    if atk.colliderect(e.rect()):
                        if self.player.sonido_golpe:
                            self.player.sonido_golpe.play()
                        e.take_damage(damage)
                        self.GAME.score += 15

        vivos = []
        for e in self.enemies:
            e.update(dt, self.player)
            # === LIMITAR ENEMIGOS A LA MITAD INFERIOR ===
            if e.y < HEIGHT // 2 - 110:
                e.y = HEIGHT // 2 - 110
            if e.y + e.h > HEIGHT:
                e.y = HEIGHT - e.h
            # === GIRO HACIA EL JUGADOR ===
            e.facing_right = self.player.x > e.x

            # Animación
            e.anim_timer += dt
            if e.anim_timer >= 0.15:
                e.anim_timer = 0
                e.current_frame = (e.current_frame + 1) % len(self.enemy_frames)

            if e.rect().colliderect(self.player.hurt_rect()):
                self.player.health -= 12 * dt

            if e.hp > 0:
                vivos.append(e)
        self.enemies = vivos

        # Activar jefe
        if not self.enemies and not self.boss_active:
            self.boss_active = True

        # JEFE
        if self.boss_active and self.boss.hp > 0:
            self.boss.update(dt, self.player)
            # === LIMITAR JEFE A LA MITAD INFERIOR ===
            if self.boss.y < HEIGHT // 2 - 110:
                self.boss.y = HEIGHT // 2 - 110
            if self.boss.y + self.boss.h > HEIGHT:
                self.boss.y = HEIGHT - self.boss.h

            # === GIRO DEL JEFE ===
            self.boss.facing_right = self.player.x > self.boss.x

            # Animación
            self.frame_timer_boss += dt
            if self.frame_timer_boss >= self.frame_speed:
                self.frame_timer_boss = 0
                self.current_frame_boss = (self.current_frame_boss + 1) % len(
                    self.boss_frames
                )

            if self.boss.rect().colliderect(self.player.hurt_rect()):
                self.player.health -= 20 * dt

        if self.player.health <= 0:
            self.game_over = True
            pygame.mixer.music.stop()

        if self.boss_active and self.boss.hp <= 0:
            self.victory = True
            pygame.mixer.music.stop()

    # ==================== DRAW ====================
    def draw(self, surf):

        if self.bg_image:
            surf.blit(self.bg_image, (0, 0))
        else:
            surf.fill((22, 25, 38))
            # === LÍNEA DE DELIMITACIÓN (mitad de pantalla) ===
        # pygame.draw.line(
        #    surf, (200, 200, 200), (0, HEIGHT // 2), (WIDTH, HEIGHT //2),2)

        # ENEMIGOS
        for e in self.enemies:
            frame = self.enemy_frames[e.current_frame]
            if e.facing_right:
                frame = pygame.transform.flip(frame, True, False)
            surf.blit(frame, (e.x, e.y))

            bar_x = e.x + (e.w // 2) - 30
            bar_y = e.y - 14
            draw_enemy_health_bar(surf, bar_x, bar_y, 60, 6, e.hp, 45)

        # JEFE
        if self.boss_active and self.boss.hp > 0:
            img = self.boss_frames[self.current_frame_boss]
            if self.boss.facing_right:
                img = pygame.transform.flip(img, True, False)
            surf.blit(img, (self.boss.x, self.boss.y))

            draw_boss_health_bar(surf, "AO AO", self.boss.hp, 240, color=(255, 200, 40))

        # PLAYER + HUD
        self.player.draw(surf)
        self.powerup_manager.draw(surf)
        self.powerup_manager.draw_hud(surf, 12, 120)
        draw_hud(surf, self.GAME.nickname, self.GAME.score, self.player.health)

        # INTRO VISUAL
        if not self.started:
            story_lines = [
                "Las praderas abiertas y los cerros solitarios albergan al Moñái,",
                "serpiente cornuda que se mueve entre los pastizales.",
                "",
                "En lo alto de las montañas aguarda el Ao Ao,",
                "bestia devoradora de hombres.",
                "",
                "Atrévete a sobrevivir.",
            ]
            draw_intro_overlay(
                surf, "NIVEL 2", story_lines, self.countdown, self.text_alpha
            )
            return

        # FIN DEL NIVEL
        if self.game_over:
            draw_text(
                surf,
                "DERROTA - ESC para volver",
                28,
                WIDTH // 2,
                HEIGHT // 2,
                center=True,
            )

        if self.victory:
            draw_text(
                surf,
                "¡VICTORIA! Ao Ao derrotado.",
                28,
                WIDTH // 2,
                HEIGHT // 2,
                center=True,
            )
            draw_text(
                surf,
                "ENTER para continuar",
                20,
                WIDTH // 2,
                HEIGHT // 2 + 40,
                center=True,
            )
