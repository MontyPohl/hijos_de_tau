import pygame
import random
from config import WIDTH, HEIGHT, draw_text
from enemy import Enemy
from pages import ScreenBase
from game_state import GAME
from powerup import PowerUpManager


class Level4Screen(ScreenBase):
    def __init__(self, manager):
        self.manager = manager
        self.GAME = GAME
        self.player = GAME.player

        self.enemies = []
        self.boss_active = False
        self.game_over = False
        self.victory = False
        self.victory_timer = 0

        self.powerup_manager = PowerUpManager()

        # SOMBRAS ANIMADAS
        self.shadow_frames = []
        for i in range(1, 4):
            try:
                img = pygame.image.load(
                    f"imagenes/sombras_anim/frame{i}.png"
                ).convert_alpha()
                img = pygame.transform.scale(img, (110, 110))
                self.shadow_frames.append(img)
            except:
                pass

        self.current_shadow_frame = 0
        self.shadow_frame_timer = 0
        self.shadow_frame_speed = 0.12

        # ENEMIGOS COMUNES (Sombras Malditas)
        for i in range(5):
            e = Enemy(
                random.randint(200, WIDTH - 200),
                random.randint(180, HEIGHT - 180),
                name="Sombras Malditas",
                hp=90,
                speed=95,
                w=110,
                h=110,
            )
            e.facing_right = False
            e.hitbox_offset_x = 22
            e.hitbox_offset_y = 18
            e.hitbox_width_reduce = 40
            e.hitbox_height_reduce = 45
            self.enemies.append(e)

        # JEFE: LUISÓN
        self.boss = Enemy(
            WIDTH - 140,
            HEIGHT // 2 - 40,
            name="Luison",
            hp=100,
            speed=110,
            w=230,
            h=230,
        )
        self.boss.facing_right = False

        self.boss.hitbox_offset_x = 60
        self.boss.hitbox_offset_y = 60
        self.boss.hitbox_width_reduce = 90
        self.boss.hitbox_height_reduce = 90

        self.boss_frames = []
        for i in range(1, 14):
            try:
                img = pygame.image.load(
                    f"imagenes/luison_anim/frame{i}.png"
                ).convert_alpha()
                img = pygame.transform.scale(img, (230, 230))
                self.boss_frames.append(img)
            except:
                pass

        self.current_frame = 0
        self.frame_timer = 0
        self.frame_speed = 0.15

        # FONDO
        try:
            self.bg_image = pygame.image.load("imagenes/level4.png").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        except:
            self.bg_image = None

        # INTRO
        self.countdown = 10.0
        self.text_alpha = 0
        self.started = False

        # MÚSICA
        try:
            pygame.mixer.music.load("sonidos/audio_luison1.mp3")
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)
        except:
            pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                pygame.mixer.music.stop()
                self.manager.pop()

            if not self.started:
                return

            if event.key == pygame.K_SPACE and not self.victory:
                atk = self.player.attack()
                if atk:
                    dmg = getattr(self.player, "attack_damage", 30)

                    for e in self.enemies + ([self.boss] if self.boss_active else []):
                        if atk.colliderect(e.rect()):
                            if getattr(self.player, "sonido_golpe", None):
                                self.player.sonido_golpe.play()
                            e.take_damage(dmg)
                            self.GAME.score += 25

            if event.key == pygame.K_RETURN and self.victory:
                from level import VictoryScreen

                pygame.mixer.music.stop()
                self.manager.push(VictoryScreen(self.manager))

    def update(self, dt):
        self.powerup_manager.update(dt, self.player)

        if not self.started:
            self.countdown -= dt
            self.text_alpha = min(255, self.text_alpha + dt * 80)
            if self.countdown <= 0:
                self.started = True
            return

        if self.game_over:
            pygame.mixer.music.stop()
            return

        if self.victory:
            self.victory_timer += dt
            if self.victory_timer >= 5:
                from level import VictoryScreen

                self.manager.push(VictoryScreen(self.manager))
            return

        # PLAYER
        keys = pygame.key.get_pressed()
        self.player.update(dt, keys)

        # ANIMACIÓN SOMBRAS
        self.shadow_frame_timer += dt
        if self.shadow_frame_timer >= self.shadow_frame_speed:
            self.shadow_frame_timer = 0
            self.current_shadow_frame = (self.current_shadow_frame + 1) % len(
                self.shadow_frames
            )

        vivos = []
        for e in self.enemies:
            e.update(dt, self.player)

            # <-- GIRO
            e.facing_right = self.player.x > e.x

            if e.rect().colliderect(self.player.hurt_rect()):
                self.player.health -= 12 * dt

            if e.hp > 0:
                vivos.append(e)
        self.enemies = vivos

        # ACTIVAR JEFE
        if not self.enemies and not self.boss_active:
            self.boss_active = True

        # JEFE
        if self.boss_active and self.boss.hp > 0:
            self.boss.update(dt, self.player)

            # <-- GIRO DEL JEFE
            self.boss.facing_right = self.player.x > self.boss.x

            self.frame_timer += dt
            if self.frame_timer >= self.frame_speed:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.boss_frames)

            if self.boss.rect().colliderect(self.player.hurt_rect()):
                self.player.health -= 25 * dt

        if self.player.health <= 0:
            self.game_over = True
            pygame.mixer.music.stop()

        if self.boss_active and self.boss.hp <= 0:
            self.victory = True
            self.victory_timer = 0
            pygame.mixer.music.stop()

    def draw(self, surf):
        if self.bg_image:
            surf.blit(self.bg_image, (0, 0))
        else:
            surf.fill((10, 10, 25))

        # ENEMIGOS
        for e in self.enemies:
            img = self.shadow_frames[self.current_shadow_frame]
            if e.facing_right:
                img = pygame.transform.flip(img, True, False)
            surf.blit(img, (e.x, e.y))

            max_hp = 70
            ratio = max(0, min(1, e.hp / max_hp))
            pygame.draw.rect(surf, (70, 0, 0), (e.x + 25, e.y - 12, 60, 6))
            pygame.draw.rect(surf, (180, 60, 250), (e.x + 25, e.y - 12, 60 * ratio, 6))
            pygame.draw.rect(surf, (255, 255, 255), (e.x + 25, e.y - 12, 60, 6), 1)

        # JEFE
        if self.boss_active and self.boss.hp > 0:
            img = self.boss_frames[self.current_frame]
            if self.boss.facing_right:
                img = pygame.transform.flip(img, True, False)

            surf.blit(img, (self.boss.x, self.boss.y))

            # pygame.draw.rect(surf, (255, 0, 0), self.boss.rect(), 2)# esta linea dibuja la hitbox debe estar aca para funcionar

            max_hp = 380
            ratio = max(0, min(1, self.boss.hp / max_hp))
            pygame.draw.rect(surf, (60, 0, 0), (WIDTH // 2 - 170, 50, 340, 24))
            pygame.draw.rect(
                surf, (255, 180, 60), (WIDTH // 2 - 170, 50, 340 * ratio, 24)
            )
            pygame.draw.rect(surf, (255, 255, 255), (WIDTH // 2 - 170, 50, 340, 24), 2)
            draw_text(
                surf, "LUISÓN", 28, WIDTH // 2, 25, center=True, color=(255, 230, 120)
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
            overlay.fill((0, 0, 0, 150))
            surf.blit(overlay, (0, 0))

            texto_intro = [
                "NIVEL 4 – JEFE FINAL",
                "",
                "Cuando la noche se cierra y los vientos cuentan historias de muerte,",
                "surge el Luisón, séptimo y más maldito de los hijos del caos.",
                "",
                "Guarda la frontera entre lo vivo y lo muerto.",
                "Su ladrido anuncia el fin... o el renacer.",
                "",
                "Atrévete a terminar la leyenda.",
            ]

            y = HEIGHT // 2 - len(texto_intro) * 22
            for i, linea in enumerate(texto_intro):
                alpha_line = max(0, min(255, self.text_alpha - i * 12))
                if alpha_line > 0:
                    txt_shadow = pygame.font.SysFont(
                        "dejavusans", 30, bold=True
                    ).render(linea, True, (0, 0, 0))
                    txt_shadow.set_alpha(alpha_line)
                    surf.blit(
                        txt_shadow, txt_shadow.get_rect(center=(WIDTH // 2 + 2, y + 2))
                    )

                    txt = pygame.font.SysFont("dejavusans", 30, bold=True).render(
                        linea, True, (255, 255, 230)
                    )
                    txt.set_alpha(alpha_line)
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

        # DERROTA
        if self.game_over:
            draw_text(
                surf,
                "DERROTA - ESC para volver",
                32,
                WIDTH // 2,
                HEIGHT // 2,
                center=True,
            )
            return

        # VICTORIA
        if self.victory:
            draw_text(
                surf,
                "¡¡HAS VENCIDO AL LUISÓN!!",
                40,
                WIDTH // 2,
                HEIGHT // 2 - 40,
                center=True,
            )
            draw_text(
                surf,
                "ENTER para continuar",
                24,
                WIDTH // 2,
                HEIGHT // 2 + 10,
                center=True,
            )
            return
