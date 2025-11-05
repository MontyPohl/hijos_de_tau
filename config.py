import pygame
import sys

# ==================== CONFIGURACIÓN GENERAL ====================
WIDTH, HEIGHT = 1200, 720
FPS = 60
BG_COLOR = (18, 18, 24)

# ==================== PALETA DE COLORES ====================
# Colores básicos
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)

# Colores para barras de vida
COLOR_HP_BG = (60, 0, 0)  # Fondo de barra de vida (rojo oscuro)
COLOR_HP_GREEN = (80, 255, 80)  # Vida del jugador (verde)
COLOR_HP_RED = (255, 60, 60)  # Vida de enemigos (rojo)
COLOR_HP_ORANGE = (255, 140, 40)  # Vida de jefes (naranja)
COLOR_HP_YELLOW = (255, 200, 40)  # Vida de jefes alternativo (amarillo)

# Colores de texto
COLOR_TEXT_DEFAULT = (230, 230, 230)
COLOR_TEXT_YELLOW = (255, 255, 200)
COLOR_TEXT_GOLD = (255, 215, 100)
COLOR_TEXT_TITLE = (255, 230, 120)

# Colores de interfaz
COLOR_SHADOW = (0, 0, 0)
COLOR_INTRO_TEXT = (255, 255, 230)

# ==================== INICIALIZACIÓN DE PYGAME ====================
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Paraguayito: Hijos de Tau y Kerana")
clock = pygame.time.Clock()

# ==================== FUENTES GLOBALES ====================
# Fuentes base
FONT = pygame.font.SysFont("dejavusans", 20)
BIGFONT = pygame.font.SysFont("dejavusans", 40)
SMALL = pygame.font.SysFont("dejavusans", 16)

# Fuentes especializadas (para evitar recrearlas constantemente)
HUD_FONT = pygame.font.SysFont("dejavusans", 26, bold=True)
TITLE_FONT = pygame.font.SysFont("dejavusans", 110, bold=True)
BODY_FONT = pygame.font.SysFont("dejavusans", 30, bold=True)
SUBTITLE_FONT = pygame.font.SysFont("dejavusans", 32, bold=True)
BOSS_NAME_FONT = pygame.font.SysFont("dejavusans", 28, bold=True)

# ==================== CONSTANTES DE JUEGO ====================
# Vida
PLAYER_MAX_HP = 100
PLAYER_START_HP = 100

# Daño
PLAYER_BASE_DAMAGE = 35
POWERUP_DAMAGE_BOOST = 50

# Velocidad
PLAYER_BASE_SPEED = 180
POWERUP_SPEED_MULTIPLIER = 1.5

# Tiempos
POWERUP_SPAWN_INTERVAL = 5.0  # Segundos entre power-ups
POWERUP_DURATION = 5.0  # Duración del carrulim en segundos


# ==================== FUNCIONES HELPER ====================
def draw_text(surf, text, size, x, y, color=COLOR_TEXT_DEFAULT, center=False):
    """
    Dibuja texto en pantalla con tamaño adaptable y color opcional.

    Args:
        surf: Superficie donde dibujar
        text: Texto a mostrar
        size: Tamaño del texto
        x, y: Coordenadas
        color: Color del texto (tupla RGB)
        center: Si True, centra el texto en (x, y)
    """
    if size >= 32:
        f = BIGFONT
    elif size <= 14:
        f = SMALL
    else:
        f = FONT

    txt = f.render(text, True, color)
    rect = txt.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surf.blit(txt, rect)


def draw_health_bar(
    surf, x, y, width, height, current_hp, max_hp, color=COLOR_HP_GREEN
):
    """
    Dibuja una barra de vida estándar.

    Args:
        surf: Superficie donde dibujar
        x, y: Coordenadas de la esquina superior izquierda
        width, height: Dimensiones de la barra
        current_hp: Vida actual
        max_hp: Vida máxima
        color: Color de la barra de vida
    """
    ratio = max(0, min(1, current_hp / max_hp))

    # Fondo oscuro
    pygame.draw.rect(surf, COLOR_HP_BG, (x, y, width, height))

    # Vida actual
    pygame.draw.rect(surf, color, (x, y, width * ratio, height))

    # Borde blanco
    pygame.draw.rect(surf, COLOR_WHITE, (x, y, width, height), 2)


def draw_boss_health_bar(surf, boss_name, current_hp, max_hp, color=COLOR_HP_ORANGE):
    """
    Dibuja la barra de vida épica de un jefe en la parte superior de la pantalla.

    Args:
        surf: Superficie donde dibujar
        boss_name: Nombre del jefe
        current_hp: Vida actual del jefe
        max_hp: Vida máxima del jefe
        color: Color de la barra
    """
    bar_width = 330
    bar_height = 26
    bar_x = WIDTH // 2 - bar_width // 2
    bar_y = 50

    ratio = max(0, min(1, current_hp / max_hp))

    # Fondo
    pygame.draw.rect(surf, (50, 0, 0), (bar_x, bar_y, bar_width, bar_height))

    # Vida
    pygame.draw.rect(surf, color, (bar_x, bar_y, bar_width * ratio, bar_height))

    # Borde
    pygame.draw.rect(surf, COLOR_WHITE, (bar_x, bar_y, bar_width, bar_height), 3)

    # Nombre del jefe
    draw_text(
        surf, boss_name, 28, WIDTH // 2, bar_y - 28, center=True, color=COLOR_TEXT_TITLE
    )


def draw_enemy_health_bar(surf, x, y, width, height, current_hp, max_hp):
    """
    Dibuja una pequeña barra de vida sobre un enemigo común.

    Args:
        surf: Superficie donde dibujar
        x, y: Coordenadas (usualmente arriba del enemigo)
        width, height: Dimensiones de la barra
        current_hp: Vida actual
        max_hp: Vida máxima
    """
    ratio = max(0, min(1, current_hp / max_hp))

    # Fondo
    pygame.draw.rect(surf, COLOR_HP_BG, (x, y, width, height))

    # Vida
    pygame.draw.rect(surf, COLOR_HP_RED, (x, y, width * ratio, height))

    # Borde
    pygame.draw.rect(surf, COLOR_WHITE, (x, y, width, height), 1)


def draw_hud(surf, nickname, score, health):
    """
    Dibuja el HUD estándar del juego (nombre, puntaje, vida).

    Args:
        surf: Superficie donde dibujar
        nickname: Nombre del jugador
        score: Puntaje actual
        health: Vida actual del jugador
    """
    # Texto del jugador
    txt_jugador = HUD_FONT.render(f"Jugador: {nickname}", True, COLOR_WHITE)
    surf.blit(txt_jugador, (12, 12))

    # Texto del puntaje
    txt_puntaje = HUD_FONT.render(f"Puntaje: {score}", True, COLOR_TEXT_YELLOW)
    surf.blit(txt_puntaje, (12, 48))

    # Barra de vida
    draw_health_bar(surf, 12, 80, 200, 20, health, PLAYER_MAX_HP, COLOR_HP_GREEN)


def draw_intro_overlay(surf, title, story_lines, countdown, text_alpha):
    """
    Dibuja la pantalla de introducción de un nivel.

    Args:
        surf: Superficie donde dibujar
        title: Título del nivel (ej: "NIVEL 1")
        story_lines: Lista de líneas de historia
        countdown: Tiempo restante para comenzar
        text_alpha: Transparencia del texto (0-255)
    """
    # Overlay oscuro
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 120))
    surf.blit(overlay, (0, 0))

    # Calcular posición inicial
    y = HEIGHT // 2 - len(story_lines) * 22

    # Dibujar cada línea con fade-in progresivo
    for i, linea in enumerate(story_lines):
        alpha_line = max(0, min(255, text_alpha - i * 12))
        if alpha_line > 0:
            # Sombra
            txt_shadow = BODY_FONT.render(linea, True, COLOR_BLACK)
            txt_shadow.set_alpha(alpha_line)
            surf.blit(txt_shadow, txt_shadow.get_rect(center=(WIDTH // 2 + 2, y + 2)))

            # Texto principal
            txt = BODY_FONT.render(linea, True, COLOR_INTRO_TEXT)
            txt.set_alpha(alpha_line)
            surf.blit(txt, txt.get_rect(center=(WIDTH // 2, y)))

        y += 48

    # Contador de inicio (solo cuando el texto está completamente visible)
    if text_alpha >= 240:
        draw_text(
            surf,
            f"COMIENZA EN {int(countdown) + 1}",
            56,
            WIDTH // 2,
            HEIGHT - 60,
            center=True,
            color=COLOR_INTRO_TEXT,
        )


# ==================== FUNCIÓN DE DEBUG ====================
def draw_debug_info(surf, fps, player_pos, enemies_count):
    """
    Dibuja información de debug en la esquina superior derecha.

    Args:
        surf: Superficie donde dibujar
        fps: FPS actuales
        player_pos: Posición del jugador (x, y)
        enemies_count: Número de enemigos vivos
    """
    debug_font = pygame.font.SysFont("monospace", 14)
    debug_lines = [
        f"FPS: {int(fps)}",
        f"Pos: ({int(player_pos[0])}, {int(player_pos[1])})",
        f"Enemigos: {enemies_count}",
    ]

    y = 10
    for line in debug_lines:
        txt = debug_font.render(line, True, (0, 255, 0))
        surf.blit(txt, (WIDTH - 150, y))
        y += 20


# ==================== NOTAS DE USO ====================
"""
CÓMO USAR ESTE ARCHIVO OPTIMIZADO:

1. REEMPLAZA TU config.py ACTUAL con este archivo

2. EN TUS NIVELES, usa las funciones helper:
   
   # En lugar de:
   font_hud = pygame.font.SysFont("dejavusans", 26, bold=True)
   surf.blit(font_hud.render(f"Jugador: {nickname}", True, (255, 255, 255)), (12, 12))
   
   # Usa:
   from config import draw_hud
   draw_hud(surf, self.GAME.nickname, self.GAME.score, self.player.health)

3. USA LAS CONSTANTES DE COLOR:
   
   # En lugar de:
   pygame.draw.rect(surf, (60, 0, 0), ...)
   
   # Usa:
   from config import COLOR_HP_BG
   pygame.draw.rect(surf, COLOR_HP_BG, ...)

4. BARRAS DE VIDA:
   
   # Para enemigos comunes:
   from config import draw_enemy_health_bar
   draw_enemy_health_bar(surf, bar_x, bar_y, 60, 6, e.hp, e.max_hp)
   
   # Para jefes:
   from config import draw_boss_health_bar
   draw_boss_health_bar(surf, "TEJU JAGUA", self.boss.hp, 200)

BENEFICIOS:
✅ Menos código duplicado
✅ Más fácil de mantener
✅ Colores consistentes en todo el juego
✅ Fuentes creadas una sola vez (mejor rendimiento)
✅ Código más limpio y legible
"""
