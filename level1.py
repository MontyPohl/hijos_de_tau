import pygame
import random
from config import WIDTH, HEIGHT, draw_text
from enemy import Enemy
from pages import ScreenBase
from game_state import GAME
from powerup import PowerUpManager


class Level1Screen(ScreenBase):
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

        # ==================== FONDO ====================
        try:
            self.bg_image = pygame.image.load("imagenes/level1.jpg").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        except:
            self.bg_image = None

        # ==================== MÚSICA ====================
        try:
            pygame.mixer.music.load("sonidos/audio_level1.mp3")
            pygame.mixer.music.set_volume(0.8)
            pygame.mixer.music.play(-1)
        except:
            pass

        # ==================== ANIMACIÓN MBÓI TÚ'Ï ====================
        self.mboi_frames = []
        for i in range(1, 4):
            img = pygame.image.load(f"imagenes/mboi_anim/frame{i}.png").convert_alpha()
            img = pygame.transform.scale(img, (150, 150))
            self.mboi_frames.append(img)

        # ==================== ENEMIGOS ====================
        for i in range(5):
            e = Enemy(
                WIDTH // 2 + i * 60,
                HEIGHT // 2 + random.randint(-100, 100),
                name="Mbói Tu'ï",
                hp=60,
                speed=50,
            )
            e.anim_timer = 0
            e.current_frame = 0
            e.facing_right = False  # ✅ Inicializar dirección
            self.enemies.append(e)

        # ==================== JEFE (Teju Jagua) ====================
        self.boss = Enemy(
            WIDTH - 140,
            HEIGHT // 2 - 40,
            name="Teju Jagua",
            hp=300,
            speed=60,
            w=80,
            h=80,
        )
        self.boss.facing_right = False

        self.boss_frames = []
        for i in range(1, 4):
            img = pygame.image.load(
                f"imagenes/teju_jagua_anim/frame{i}.png"
            ).convert_alpha()
            img = pygame.transform.scale(img, (230, 230))
            self.boss_frames.append(img)

        self.current_frame_boss = 0
        self.boss_frame_timer = 0
        self.boss_frame_speed = 0.15

        # ==================== INTRO ====================
        self.countdown = 10.0
        self.text_alpha = 0
        self.started = False

    # ==================== EVENTOS ====================
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                self.manager.pop()

            # DEBUG saltar nivel
            if event.key == pygame.K_p:
                from level2 import Level2Screen

                self.manager.push(Level2Screen(self.manager))
                return

            if not self.started:
                return

            # ATAQUE
            if event.key == pygame.K_SPACE:
                atk = self.player.attack()
                if atk:
                    damage = getattr(self.player, "attack_damage", 30)

                    for e in self.enemies + ([self.boss] if self.boss_active else []):
                        if atk.colliderect(e.rect()):
                            if self.player.sonido_golpe:
                                self.player.sonido_golpe.play()
                            e.take_damage(damage)
                            self.GAME.score += 12

            # Pasar nivel
            if event.key == pygame.K_RETURN and self.victory:
                from level2 import Level2Screen

                self.GAME.score += 150
                self.manager.push(Level2Screen(self.manager))

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
        if self.player.y < HEIGHT // 2 - 110:
            self.player.y = HEIGHT // 2 - 110
        if self.player.y + self.player.h > HEIGHT:
            self.player.y = HEIGHT - self.player.h

        vivos = []
        for e in self.enemies:
            e.update(dt, self.player)
            # === LIMITAR ENEMIGOS A LA MITAD INFERIOR ===
            if e.y < HEIGHT // 2 - 130:
                e.y = HEIGHT // 2 - 130
            if e.y + e.h > HEIGHT:
                e.y = HEIGHT - e.h
            # ✅ ACTUALIZAR DIRECCIÓN DEL ENEMIGO
            e.facing_right = self.player.x > e.x

            e.anim_timer += dt
            if e.anim_timer >= 0.15:
                e.anim_timer = 0
                e.current_frame = (e.current_frame + 1) % len(self.mboi_frames)

            if e.rect().colliderect(self.player.hurt_rect()):
                self.player.health -= 10 * dt

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
            if self.boss.y < HEIGHT // 2 - 130:
                self.boss.y = HEIGHT // 2 - 130
            if self.boss.y + self.boss.h > HEIGHT:
                self.boss.y = HEIGHT - self.boss.h
            # ✅ ACTUALIZAR DIRECCIÓN DEL JEFE
            self.boss.facing_right = self.player.x > self.boss.x

            self.boss_frame_timer += dt
            if self.boss_frame_timer >= self.boss_frame_speed:
                self.boss_frame_timer = 0
                self.current_frame_boss = (self.current_frame_boss + 1) % len(
                    self.boss_frames
                )

            if self.boss.rect().colliderect(self.player.hurt_rect()):
                self.player.health -= 15 * dt

        if self.player.health <= 0:
            self.game_over = True

        if self.boss_active and self.boss.hp <= 0:
            self.victory = True

    # ==================== DRAW ====================
    def draw(self, surf):
        if self.bg_image:
            surf.blit(self.bg_image, (0, 0))
        else:
            surf.fill((20, 32, 24))
            # LÍNEA DIVISORIA (opcional, para marcar la mitad)
        # pygame.draw.line(
        #    surf, (200, 200, 200), (0, HEIGHT // 2), (WIDTH, HEIGHT //2),2)
        # ENEMIGOS + BARRA DE VIDA (Mbói Tu'ï)
        for e in self.enemies:
            frame = self.mboi_frames[e.current_frame]

            # ✅ VOLTEAR SPRITE SEGÚN DIRECCIÓN
            if e.facing_right:
                frame = pygame.transform.flip(frame, True, False)

            surf.blit(frame, (e.x, e.y))

            # Barra de vida
            max_hp = 40
            hp_ratio = max(0, min(1, e.hp / max_hp))
            bar_width = 60
            bar_height = 6
            bar_x = e.x + (150 // 2) - (bar_width // 2)  # centrado al sprite
            bar_y = e.y - 12

            pygame.draw.rect(
                surf, (60, 0, 0), (bar_x, bar_y, bar_width, bar_height)
            )  # fondo
            pygame.draw.rect(
                surf, (255, 60, 60), (bar_x, bar_y, bar_width * hp_ratio, bar_height)
            )  # vida actual
            pygame.draw.rect(
                surf, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 1
            )  # borde

        # JEFE + BARRA ÉPICA
        if self.boss_active and self.boss.hp > 0:
            boss_frame = self.boss_frames[self.current_frame_boss]

            # ✅ VOLTEAR SPRITE DEL JEFE SEGÚN DIRECCIÓN
            if self.boss.facing_right:
                boss_frame = pygame.transform.flip(boss_frame, True, False)

            surf.blit(boss_frame, (self.boss.x, self.boss.y))
            # self.boss.draw_debug(surf)

            # ===== BARRA DE VIDA ÉPICA =====
            max_hp = 200
            hp_ratio = max(0, min(1, self.boss.hp / max_hp))
            bar_width = 330
            bar_height = 26
            bar_x = WIDTH // 2 - bar_width // 2
            bar_y = 50

            pygame.draw.rect(
                surf, (50, 0, 0), (bar_x, bar_y, bar_width, bar_height)
            )  # fondo oscuro
            pygame.draw.rect(
                surf, (255, 140, 40), (bar_x, bar_y, bar_width * hp_ratio, bar_height)
            )  # vida
            pygame.draw.rect(
                surf, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 3
            )  # borde
            draw_text(
                surf,
                "TEJU JAGUA",
                28,
                WIDTH // 2,
                bar_y - 28,
                center=True,
                color=(255, 230, 120),
            )

        # JUGADOR
        self.player.draw(surf)
        self.powerup_manager.draw(surf)
        self.powerup_manager.draw_hud(surf, 12, 120)

        # HUD
        font_hud = pygame.font.SysFont("dejavusans", 26, bold=True)
        surf.blit(
            font_hud.render(f"Jugador: {self.GAME.nickname}", True, (255, 255, 255)),
            (12, 12),
        )
        surf.blit(
            font_hud.render(f"Puntaje: {self.GAME.score}", True, (255, 255, 200)),
            (12, 48),
        )

        # BARRA DE VIDA DEL JUGADOR
        max_hp = 100
        hp_ratio = max(0, min(1, self.player.health / max_hp))
        pygame.draw.rect(surf, (60, 0, 0), (12, 80, 200, 20))
        pygame.draw.rect(surf, (80, 255, 80), (12, 80, 200 * hp_ratio, 20))
        pygame.draw.rect(surf, (255, 255, 255), (12, 80, 200, 20), 2)

        # INTRO VISUAL
        if not self.started:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            surf.blit(overlay, (0, 0))

            texto_intro = [
                "NIVEL 1",
                "",
                "En los humedales al borde del río yace el dominio del Mbói Tu'ï,",
                "la serpiente-loro que vela por los anfibios y flores acuáticas.",
                "",
                "Desde las cuevas profundas surge el temido Tejú Jagua,",
                "lagarto con cabeza de perro y ojos de fuego,",
                "guardián de las riquezas de la tierra.",
                "",
                "Demuestra respeto o paga el precio.",
            ]

            y = HEIGHT // 2 - len(texto_intro) * 22
            for i, linea in enumerate(texto_intro):
                alpha_line = max(0, min(255, self.text_alpha - i * 12))
                if alpha_line > 0:
                    # sombra
                    txt_shadow = pygame.font.SysFont(
                        "dejavusans", 30, bold=True
                    ).render(linea, True, (0, 0, 0))
                    txt_shadow.set_alpha(alpha_line)
                    surf.blit(
                        txt_shadow, txt_shadow.get_rect(center=(WIDTH // 2 + 2, y + 2))
                    )

                    # texto principal
                    txt = pygame.font.SysFont("dejavusans", 30, bold=True).render(
                        linea, True, (255, 255, 230)
                    )
                    txt.set_alpha(alpha_line)
                    surf.blit(txt, txt.get_rect(center=(WIDTH // 2, y)))

                y += 48

            # Contador más abajo y mismo color que el texto
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

        # ==================== FIN DEL NIVEL ====================
        if self.game_over:
            draw_text(surf, "DERROTA", 40, WIDTH // 2, HEIGHT // 2, center=True)

        if self.victory:
            draw_text(surf, "¡VICTORIA!", 40, WIDTH // 2, HEIGHT // 2, center=True)
            draw_text(
                surf,
                "ENTER para continuar",
                22,
                WIDTH // 2,
                HEIGHT // 2 + 40,
                center=True,
            )
