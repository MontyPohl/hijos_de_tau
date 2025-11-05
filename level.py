import pygame
import random
from config import WIDTH, HEIGHT, draw_text
from enemy import Enemy
from pages import ScreenBase
from game_state import GAME


# ==================== PANTALLA DE VICTORIA FINAL ====================
class VictoryScreen(ScreenBase):
    """Pantalla que aparece al completar todos los niveles"""
    def __init__(self, manager):
        # Importación tardía para evitar ciclos
        from game_state import GAME
        
        self.manager = manager
        self.GAME = GAME  # Guardamos referencia local
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # Reiniciar el juego
            if event.key == pygame.K_r:
                self.GAME.score = 0
                self.GAME.player.health = 100
                # Volver al inicio
                while len(self.manager.screens) > 1:
                    self.manager.pop()
            
            # Volver al menú principal
            if event.key == pygame.K_ESCAPE:
                self.GAME.score = 0
                while len(self.manager.screens) > 1:
                    self.manager.pop()
    
    def update(self, dt):
        pass
    
    def draw(self, surf):
        # ===== FONDO CON IMAGEN =====
        try:
            bg = pygame.image.load("imagenes/victoryscreen.jpg").convert()
            bg = pygame.transform.scale(bg, (WIDTH, HEIGHT))
            surf.blit(bg, (0, 0))
        except:
            surf.fill((5, 5, 30))

        # Oscurecido cinematográfico
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surf.blit(overlay, (0, 0))

        # Fuentes MAS GRANDES y NEGRITA
        font_title = pygame.font.SysFont("dejavusans", 110, bold=True)  # SE MANTIENE IGUAL
        font_sub = pygame.font.SysFont("dejavusans", 32, bold=True)     # Bajado
        font_body = pygame.font.SysFont("dejavusans", 26, bold=True)    # Bajado
        font_small = pygame.font.SysFont("dejavusans", 22, bold=True)   # Bajado

        # ===== TÍTULO ÉPICO =====
        txt = font_title.render("¡VICTORIA!", True, (255, 215, 100))  
        surf.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 220)))

        # ===== TEXTO NARRATIVO =====
        texto = [
            "El ciclo de los mitos ha sido roto.",
            "El Luisón yace derrotado en lo profundo del monte.",
            "Pero su leyenda permanecerá… en tu nombre."
        ]

        y = HEIGHT // 2 - 80
        for linea in texto:
            line = font_body.render(linea, True, (240, 240, 240))
            surf.blit(line, line.get_rect(center=(WIDTH // 2, y)))
            y += 38

        # ===== PUNTAJE FINAL =====
        puntos = font_sub.render(f"PUNTAJE FINAL: {self.GAME.score}", True, (255, 255, 255))
        surf.blit(puntos, puntos.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50)))

        # ===== OPCIONES =====
        op1 = font_small.render("Presiona R para Reiniciar", True, (230, 230, 230))
        surf.blit(op1, op1.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120)))

        op2 = font_small.render("Presiona ESC para Volver al Inicio", True, (230, 230, 230))
        surf.blit(op2, op2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 155)))



