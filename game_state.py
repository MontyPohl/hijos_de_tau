# game_state.py
class GameState:
    def __init__(self):
        self.player = None  # Referencia al jugador
        self.score = 0  # Puntaje acumulado
        self.nickname = "Jugador"  # Nombre del jugador


# Instancia global del estado del juego
GAME = GameState() 