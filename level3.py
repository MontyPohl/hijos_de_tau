import pygame
import random
from config import WIDTH, HEIGHT, draw_text
from enemy import Enemy
from pages import ScreenBase
from powerup import PowerUpManager


class Level3Screen(ScreenBase):
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

        # === ENEMIGOS: Kurupí (comunes) ===
        self.enemy_frames = []
        for i in range(1, 4):
            try:
                img = pygame.image.load(
                    f"imagenes/kurupi_anim/frame{i}.png"
                ).convert_alpha()
                img = pygame.transform.scale(img, (110, 110))
                self.enemy_frames.append(img)
            except:
                pass

        for i in range(4):
            e = Enemy(
                random.randint(150, WIDTH - 150),
                random.randint(150, HEIGHT - 150),
                name="Kurupí",
                hp=80,
                speed=80,
            )

            e.w, e.h = 110, 110
            e.hitbox_offset_x = 20
            e.hitbox_offset_y = 18
            e.hitbox_width_reduce = 70
            e.hitbox_height_reduce = 20

            e.anim_timer = 0
            e.current_frame = 0
            e.facing_right = False
            self.enemies.append(e)

        # === JEFE: Jasy Jatere ===
        self.boss = Enemy(
            WIDTH - 140,
            HEIGHT // 2 - 40,
            name="Jasy Jatere",
            hp=480,
            speed=95,
            w=220,
            h=220,
        )
        self.boss.facing_right = False

        self.boss_frames = []
        for i in range(1, 4):
            try:
                img = pygame.image.load(
                    f"imagenes/jasy_anim/frame{i}.png"
                ).convert_alpha()
                img = pygame.transform.scale(img, (220, 220))
                self.boss_frames.append(img)
            except:
                pass

        self.current_frame_boss = 0
        self.frame_timer_boss = 0
        self.frame_speed = 0.15

        # === Fondo ===
        try:
            self.bg_image = pygame.image.load("imagenes/level3.png").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        except:
            self.bg_image = None

        # === Intro visual ===
        self.countdown = 10.0
        self.text_alpha = 0
        self.started = False

        # === Música ===
        try:
            pygame.mixer.music.load("sonidos/audio_jasy.mp3")
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)
        except:
            pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                self.manager.pop()

            if event.key == pygame.K_p:
                from level4 import Level4Screen

                pygame.mixer.music.stop()
                self.manager.push(Level4Screen(self.manager))
                return

            if not self.started or self.game_over:
                return

            if event.key == pygame.K_SPACE and not self.victory:
                atk = self.player.attack()
                if atk:
                    damage = getattr(self.player, "attack_damage", 30)
                    targets = self.enemies + ([self.boss] if self.boss_active else [])
                    for e in targets:
                        if atk.colliderect(e.rect()):
                            if getattr(self.player, "sonido_golpe", None):
                                self.player.sonido_golpe.play()
                            e.take_damage(damage)
                            self.GAME.score += 20

            if event.key == pygame.K_RETURN and self.victory:
                from level4 import Level4Screen

                pygame.mixer.music.stop()
                self.GAME.score += 200
                self.manager.push(Level4Screen(self.manager))

    def update(self, dt):
        if not self.started:
            self.countdown -= dt
            self.text_alpha = min(255, self.text_alpha + dt * 80)
            if self.countdown <= 0:
                self.started = True
            return

        if self.game_over or self.victory:
            return

        self.powerup_manager.update(dt, self.player)

        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)

        vivos = []
        for e in self.enemies:
            e.update(dt, self.player)

            # <-- GIRO DEL ENEMIGO
            e.facing_right = self.player.x > e.x

            if self.enemy_frames:
                e.anim_timer += dt
                if e.anim_timer >= 0.15:
                    e.anim_timer = 0
                    e.current_frame = (e.current_frame + 1) % len(self.enemy_frames)

            if e.rect().colliderect(self.player.hurt_rect()):
                self.player.health -= 10 * dt

            if e.hp > 0:
                vivos.append(e)
        self.enemies = vivos

        if not self.enemies and not self.boss_active:
            self.boss_active = True

        if self.boss_active and self.boss.hp > 0:
            self.boss.update(dt, self.player)

            # <-- GIRO DEL JEFE
            self.boss.facing_right = self.player.x > self.boss.x

            if self.boss_frames:
                self.frame_timer_boss += dt
                if self.frame_timer_boss >= self.frame_speed:
                    self.frame_timer_boss = 0
                    self.current_frame_boss = (self.current_frame_boss + 1) % len(
                        self.boss_frames
                    )

            if self.boss.rect().colliderect(self.player.hurt_rect()):
                self.player.health -= 18 * dt

        if self.player.health <= 0:
            self.game_over = True

        if self.boss_active and self.boss.hp <= 0:
            self.victory = True

    def draw(self, surf):
        if self.bg_image:
            surf.blit(self.bg_image, (0, 0))
        else:
            surf.fill((25, 25, 40))

        # === Enemigos Kurupí ===
        for e in self.enemies:
            frame = self.enemy_frames[e.current_frame]
            if e.facing_right:
                frame = pygame.transform.flip(frame, True, False)
            surf.blit(frame, (e.x, e.y))

            max_hp = 60
            ratio = max(0, min(1, e.hp / max_hp))
            bar_x = e.x + (110 // 2) - 30
            bar_y = e.y - 12

            pygame.draw.rect(surf, (60, 0, 0), (bar_x, bar_y, 60, 6))
            pygame.draw.rect(surf, (255, 100, 100), (bar_x, bar_y, 60 * ratio, 6))
            pygame.draw.rect(surf, (255, 255, 255), (bar_x, bar_y, 60, 6), 1)

        # === Jefe: Jasy Jatere ===
        if self.boss_active and self.boss.hp > 0:
            img = self.boss_frames[self.current_frame_boss]
            if self.boss.facing_right:
                img = pygame.transform.flip(img, True, False)
            surf.blit(img, (self.boss.x, self.boss.y))

            max_hp = 280
            ratio = max(0, min(1, self.boss.hp / max_hp))
            pygame.draw.rect(surf, (50, 0, 0), (WIDTH // 2 - 165, 50, 330, 26))
            pygame.draw.rect(
                surf, (255, 200, 80), (WIDTH // 2 - 165, 50, 330 * ratio, 26)
            )
            pygame.draw.rect(surf, (255, 255, 255), (WIDTH // 2 - 165, 50, 330, 26), 3)
            draw_text(
                surf,
                "JASY JATERE",
                28,
                WIDTH // 2,
                20,
                center=True,
                color=(255, 230, 120),
            )

        # PLAYER + HUD
        self.player.draw(surf)
        self.powerup_manager.draw(surf)
        self.powerup_manager.draw_hud(surf, 12, 120)

        font = pygame.font.SysFont("dejavusans", 26, bold=True)
        surf.blit(
            font.render(f"Jugador: {self.GAME.nickname}", True, (255, 255, 255)),
            (12, 12),
        )
        surf.blit(
            font.render(f"Puntaje: {self.GAME.score}", True, (255, 255, 200)), (12, 48)
        )

        max_hp = 100
        ratio = max(0, min(1, self.player.health / max_hp))
        pygame.draw.rect(surf, (60, 0, 0), (12, 80, 200, 20))
        pygame.draw.rect(surf, (80, 255, 80), (12, 80, 200 * ratio, 20))
        pygame.draw.rect(surf, (255, 255, 255), (12, 80, 200, 20), 2)

        # INTRO
        if not self.started:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surf.blit(overlay, (0, 0))

            texto_intro = [
                "NIVEL 3",
                "",
                "En lo profundo del bosque acechan secretos antiguos.",
                "Donde la luz se filtra entre hojas eternas,",
                "Kurupí y Jasy Jatere reclaman el territorio.",
                "",
                "Equilibrio y respeto serán tu única defensa.",
            ]

            y = HEIGHT // 2 - len(texto_intro) * 22
            for i, linea in enumerate(texto_intro):
                alpha = max(0, min(255, self.text_alpha - i * 12))
                if alpha > 0:
                    txt = pygame.font.SysFont("dejavusans", 33, bold=True).render(
                        linea, True, (255, 255, 230)
                    )
                    txt.set_alpha(alpha)
                    surf.blit(txt, txt.get_rect(center=(WIDTH // 2, y)))
                y += 48

            if self.text_alpha >= 240:
                draw_text(
                    surf,
                    f"COMIENZA EN {int(self.countdown)+1}",
                    60,
                    WIDTH // 2,
                    HEIGHT - 60,
                    center=True,
                    color=(255, 255, 230),
                )

            return

        if self.game_over:
            draw_text(
                surf,
                "DERROTA - ESC para volver",
                24,
                WIDTH // 2,
                HEIGHT // 2,
                center=True,
            )

        if self.victory:
            draw_text(
                surf,
                "¡VICTORIA! Jasy Jatere derrotado.",
                28,
                WIDTH // 2,
                HEIGHT // 2 - 20,
                center=True,
            )
            draw_text(
                surf,
                "ENTER para continuar",
                20,
                WIDTH // 2,
                HEIGHT // 2 + 20,
                center=True,
            )
