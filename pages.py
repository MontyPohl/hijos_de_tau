import pygame
import random
from config import WIDTH, HEIGHT, draw_text
from player import Player
from base import ScreenBase
from game_state import GAME


# ==================== CLASE BOTÓN ====================
class Button:
    def __init__(self, rect, text, color=(80, 100, 160)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.hover = False

    def draw(self, surf):
        btn_color = (
            tuple(min(255, c + 40) for c in self.color) if self.hover else self.color
        )

        gradient = pygame.Surface(self.rect.size)
        for y in range(self.rect.height):
            factor = y / self.rect.height
            r = int(btn_color[0] * (0.7 + 0.3 * factor))
            g = int(btn_color[1] * (0.7 + 0.3 * factor))
            b = int(btn_color[2] * (0.8 + 0.2 * factor))
            pygame.draw.line(gradient, (r, g, b), (0, y), (self.rect.width, y))
        surf.blit(gradient, self.rect.topleft)

        pygame.draw.rect(surf, (180, 200, 255), self.rect, 3, border_radius=12)

        shadow = pygame.Surface(
            (self.rect.width + 8, self.rect.height + 8), pygame.SRCALPHA
        )
        pygame.draw.rect(shadow, (0, 0, 0, 90), shadow.get_rect(), border_radius=14)
        surf.blit(shadow, (self.rect.x - 4, self.rect.y - 4))

        draw_text(
            surf,
            self.text,
            26,
            self.rect.centerx + 2,
            self.rect.centery + 2,
            color=(0, 0, 0),
            center=True,
        )
        draw_text(
            surf,
            self.text,
            26,
            self.rect.centerx,
            self.rect.centery,
            color=(240, 240, 255),
            center=True,
        )

    def update_hover(self, pos):
        self.hover = self.rect.collidepoint(pos)

    def clicked(self, pos):
        return self.rect.collidepoint(pos)


# ==================== PANTALLA DE PORTADA ====================
class CoverScreen(ScreenBase):
    def __init__(self, manager):
        self.manager = manager

        self.start_btn = Button(
            (WIDTH // 2 - 150, HEIGHT // 2 + 130, 300, 70),
            "COMENZAR AVENTURA",
            color=(70, 80, 130),
        )

        try:
            self.bg_image = pygame.image.load("imagenes/portada.png").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        except:
            self.bg_image = pygame.Surface((WIDTH, HEIGHT))
            self.bg_image.fill((20, 20, 40))

        try:
            pygame.mixer.music.load("sonidos/audio_srpombero.mp3")
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
        except:
            print("No se pudo cargar el audio de fondo")

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.start_btn.clicked(event.pos):
                self.manager.push(CustomizeScreen(self.manager))

    def update(self, dt):
        self.start_btn.update_hover(pygame.mouse.get_pos())

    def draw(self, surf):
        surf.blit(self.bg_image, (0, 0))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(overlay, (0, 0, 40, 100), (0, 0, WIDTH, HEIGHT))
        surf.blit(overlay, (0, 0))

        draw_text(
            surf, "PARAGUAYITO", 84, WIDTH // 2 + 3, 142, color=(0, 0, 0), center=True
        )
        draw_text(
            surf, "PARAGUAYITO", 84, WIDTH // 2, 140, color=(255, 255, 255), center=True
        )

        draw_text(
            surf,
            "Hijos de Tau y Kerana",
            52,
            WIDTH // 2,
            245,
            color=(255, 255, 255),
            center=True,
        )
        draw_text(
            surf,
            "Mitología Paraguaya - Los 7 Hijos",
            40,
            WIDTH // 2,
            305,
            color=(255, 255, 255),
            center=True,
        )

        self.start_btn.draw(surf)
        draw_text(
            surf,
            "Haz clic para comenzar tu aventura",
            30,
            WIDTH // 2,
            HEIGHT - 50,
            color=(230, 230, 255),
            center=True,
        )


# ==================== PANTALLA DE PERSONALIZACIÓN ====================
class CustomizeScreen(ScreenBase):
    def __init__(self, manager):
        self.manager = manager
        self.next_btn = Button(
            (WIDTH - 240, HEIGHT - 90, 200, 60), "SIGUIENTE", color=(90, 100, 180)
        )
        self.back_btn = Button(
            (40, HEIGHT - 90, 200, 60), "VOLVER", color=(100, 80, 80)
        )

        self.input_rect = pygame.Rect(WIDTH // 2 - 200, HEIGHT // 2 - 20, 400, 60)
        self.active = False
        self.text = ""
        self.cursor_visible = True
        self.cursor_timer = 0

        try:
            self.bg_image = pygame.image.load(
                "imagenes/page_personalizacion.jpg"
            ).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        except:
            self.bg_image = None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.next_btn.clicked(event.pos):
                GAME.player = Player(100, 300)
                GAME.nickname = self.text if self.text.strip() != "" else "SIN NOMBRE"
                self.manager.push(
                    SurvivalTipsScreen(self.manager)
                )  # ← NUEVA PANTALLA AQUI

            if self.back_btn.clicked(event.pos):
                self.manager.pop()

            self.active = self.input_rect.collidepoint(event.pos)

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                GAME.player = Player(100, 300)
                GAME.nickname = self.text
                self.manager.push(SurvivalTipsScreen(self.manager))
            elif len(self.text) < 16 and event.unicode.isprintable():
                self.text += event.unicode

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer > 0.5:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

        mouse_pos = pygame.mouse.get_pos()
        self.next_btn.update_hover(mouse_pos)
        self.back_btn.update_hover(mouse_pos)

    def draw(self, surf):
        if self.bg_image:
            surf.blit(self.bg_image, (0, 0))
        else:
            surf.fill((15, 15, 30))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 40))
        surf.blit(overlay, (0, 0))

        draw_text(
            surf,
            "PERSONALIZACIÓN DE PERSONAJE",
            48,
            WIDTH // 2,
            100,
            color=(255, 255, 255),
            center=True,
        )

        border_color = (255, 230, 140) if self.active else (180, 180, 220)
        pygame.draw.rect(surf, (10, 10, 25), self.input_rect, border_radius=10)
        pygame.draw.rect(surf, border_color, self.input_rect, 3, border_radius=10)

        font = pygame.font.SysFont("dejavusans", 26, bold=True)

        if self.text.strip() == "":
            placeholder = font.render("INGRESA TU NOMBRE...", True, (180, 180, 180))
            surf.blit(placeholder, (self.input_rect.x + 15, self.input_rect.y + 14))
        else:
            txt_surface = font.render(self.text.upper(), True, (255, 255, 255))
            surf.blit(txt_surface, (self.input_rect.x + 15, self.input_rect.y + 14))

            if self.active and self.cursor_visible:
                cursor_x = self.input_rect.x + 15 + txt_surface.get_width() + 2
                pygame.draw.line(
                    surf,
                    (255, 255, 255),
                    (cursor_x, self.input_rect.y + 10),
                    (cursor_x, self.input_rect.y + 50),
                    2,
                )

        self.back_btn.draw(surf)
        self.next_btn.draw(surf)


# ============================================================
# ✅ ✅ ✅  NUEVA PANTALLA: TIPS DE SUPERVIVENCIA
# ============================================================
class SurvivalTipsScreen(ScreenBase):
    def __init__(self, manager):
        self.manager = manager
        self.next_btn = Button(
            (WIDTH - 240, HEIGHT - 90, 200, 60), "CONTINUAR", color=(80, 140, 120)
        )
        self.back_btn = Button(
            (40, HEIGHT - 90, 200, 60), "VOLVER", color=(120, 80, 90)
        )

        try:
            self.bg_image = pygame.image.load("imagenes/fondo_control.jpg").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        except:
            self.bg_image = None

        self.tips = [
            '" No se vayan todo"',
            "By Olaf",
            "",
            '" No se regalen"',
            "By Edu",
        ]

        self.controls = [
            "CONTROLES:",
            "W, A, S, D — Movimiento",
            "ENTER — Confirmar",
            "ESPACIO — Atacar",
            "ESC — Volver",
        ]

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.next_btn.clicked(event.pos):
                self.manager.push(IntroScreen(self.manager))
            if self.back_btn.clicked(event.pos):
                self.manager.pop()

    def update(self, dt):
        mouse = pygame.mouse.get_pos()
        self.next_btn.update_hover(mouse)
        self.back_btn.update_hover(mouse)

    def draw(self, surf):
        # Fondo
        if self.bg_image:
            surf.blit(self.bg_image, (0, 0))
        else:
            surf.fill((20, 20, 25))

        # Oscurecer para efecto cinematográfico
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        # ====== TÍTULO ======
        title = "TIPS DE SUPERVIVENCIA"
        # Sombra
        draw_text(surf, title, 68, WIDTH // 2 + 3, 88 + 3, center=True, color=(0, 0, 0))
        # Principal
        draw_text(surf, title, 68, WIDTH // 2, 88, center=True, color=(255, 230, 180))

        # ====== TIPS ======
        y = 210
        for t in self.tips:
            # Sombra
            draw_text(surf, t, 38, WIDTH // 2 + 2, y + 2, center=True, color=(0, 0, 0))
            # Principal
            draw_text(surf, t, 38, WIDTH // 2, y, center=True, color=(255, 255, 230))
            y += 48

        # ====== CONTROLES ======
        y += 40
        for c in self.controls:
            # Sombra
            draw_text(surf, c, 20, WIDTH // 2 + 2, y + 2, center=True, color=(0, 0, 0))
            # Principal
            draw_text(surf, c, 20, WIDTH // 2, y, center=True, color=(210, 225, 255))
            y += 42

        # ====== BOTONES ESTILO VICTORY ======
        self.back_btn.text = "VOLVER"
        self.back_btn.color = (150, 80, 90)

        self.next_btn.text = "CONTINUAR"
        self.next_btn.color = (90, 150, 120)

        self.back_btn.draw(surf)
        self.next_btn.draw(surf)


# ==================== PANTALLA DE INTRODUCCIÓN ====================
class IntroScreen(ScreenBase):
    def __init__(self, manager):
        self.manager = manager
        self.cont_btn = Button(
            (WIDTH - 240, HEIGHT - 90, 200, 60), "¡JUGAR!", color=(100, 100, 170)
        )
        self.back_btn = Button(
            (40, HEIGHT - 90, 200, 60), "VOLVER", color=(120, 80, 90)
        )
        self.lines = [
            "Hace generaciones, los 7 hijos de Tau y Kerana dejaron",
            "su marca sobre la tierra paraguaya.",
            "",
            "Eres Paraguayito, empuñando un machete heredado.",
            "Deberás atravesar el Chaco, enfrentar criaturas del monte",
            "y derrotar al Teju Jagua en su cueva para salvar aldeas.",
            "",
            "Los espíritus del bosque te observan...",
        ]
        self.controls = ["WASD o FLECHAS: Movimiento", "ESPACIO: Atacar", "ESC: Menú"]
        self.text_alpha = 0

        try:
            self.bg_image = pygame.image.load("imagenes/fondo_intro.jpg").convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WIDTH, HEIGHT))
        except:
            self.bg_image = None
        # Detener la música aquí

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.cont_btn.clicked(event.pos):
                pygame.mixer.music.stop()
                from level1 import Level1Screen

                self.manager.push(Level1Screen(self.manager))

            if self.back_btn.clicked(event.pos):
                self.manager.pop()

    def update(self, dt):
        self.text_alpha = min(255, self.text_alpha + dt * 150)
        mouse_pos = pygame.mouse.get_pos()
        self.cont_btn.update_hover(mouse_pos)
        self.back_btn.update_hover(mouse_pos)

    def draw(self, surf):
        if self.bg_image:
            surf.blit(self.bg_image, (0, 0))
        else:
            surf.fill((20, 18, 32))

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 80))
        surf.blit(overlay, (0, 0))

        draw_text(
            surf, "LA LEYENDA", 58, WIDTH // 2, 100, color=(240, 230, 255), center=True
        )

        y = 180
        for i, line in enumerate(self.lines):
            line_alpha = max(0, min(255, self.text_alpha - i * 20))
            if line_alpha > 0:
                txt = pygame.font.SysFont("dejavusans", 28, bold=True).render(
                    line, True, (245, 245, 250)
                )
                txt.set_alpha(line_alpha)
                surf.blit(txt, txt.get_rect(center=(WIDTH // 2, y)))
            y += 38

        self.back_btn.draw(surf)
        self.cont_btn.draw(surf)
