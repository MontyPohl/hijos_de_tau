import pygame
import sys
from config import screen, clock, FPS
from pages import CoverScreen, SurvivalTipsScreen
from joystickmanager import JOYSTICK, joystick_to_keyboard_event


# ==================== GESTOR DE PANTALLAS ====================
class ScreenManager:
    """
    Clase que administra las diferentes pantallas del juego (menú, juego, etc.)
    Funciona como una pila (stack): la pantalla en la cima es la activa
    """

    def __init__(self):
        self.screens = []  # Lista que almacena todas las pantallas activas

    def push(self, screen):
        """
        Añade una nueva pantalla a la pila
        La nueva pantalla se convierte en la activa
        Ejemplo: push(Level1Screen) muestra el nivel 1
        """
        self.screens.append(screen)

    def pop(self):
        """
        Elimina la pantalla actual de la pila
        Vuelve a la pantalla anterior
        Ejemplo: cuando presionas ESC en un nivel, haces pop() para volver al menú
        """
        if self.screens:
            self.screens.pop()

    def current(self):
        """
        Obtiene la pantalla actual (la última de la lista)
        Retorna None si no hay pantallas activas
        """
        return self.screens[-1] if self.screens else None

    def handle_event(self, event):
        """
        Pasa los eventos (clicks, teclas) a la pantalla actual
        Solo la pantalla activa recibe y procesa los eventos
        """
        cur = self.current()
        if cur:
            cur.handle_event(event)

    def update(self, dt):
        """
        Actualiza la lógica de la pantalla actual
        dt = delta time (tiempo transcurrido desde el último frame)
        Aquí se actualizan animaciones, movimientos, física, etc.
        """
        cur = self.current()
        if cur:
            cur.update(dt)

    def draw(self, surf):
        """
        Dibuja la pantalla actual en la superficie proporcionada
        surf = surface (la ventana del juego)
        Aquí se dibujan todos los elementos visuales
        """
        cur = self.current()
        if cur:
            cur.draw(surf)


# ==================== INICIALIZACIÓN ====================
# Crea el gestor de pantallas (una sola instancia para todo el juego)
manager = ScreenManager()

# Añade la pantalla de portada como primera pantalla
# Esta será la pantalla que se muestra al iniciar el juego
manager.push(CoverScreen(manager))


# ==================== FUNCIÓN PRINCIPAL ====================
def main():
    """
    Función principal del juego - El game loop (bucle principal)
    Se ejecuta continuamente mientras el juego está corriendo
    """

    # Variable para controlar el estado de pantalla completa
    fullscreen = False

    # BUCLE PRINCIPAL DEL JUEGO (se repite ~60 veces por segundo)
    while True:
        # ===== ACTUALIZAR JOYSTICK =====
        JOYSTICK.update()

        # ===== CONTROL DE TIEMPO =====
        # clock.tick(FPS) limita el juego a 60 FPS y devuelve milisegundos transcurridos
        # Dividimos entre 1000 para convertir a segundos (dt = delta time)
        dt = clock.tick(FPS) / 1000.0

        # ===== MANEJO DE EVENTOS =====
        # Procesa todos los eventos que ocurrieron (clicks, teclas, etc.)
        for event in pygame.event.get():

            # Si el usuario cierra la ventana (X)
            if event.type == pygame.QUIT:
                JOYSTICK.disconnect()  # Desconectar joystick antes de salir
                pygame.quit()
                sys.exit()

            # Si se presiona una tecla
            if event.type == pygame.KEYDOWN:

                # F11: Alterna entre pantalla completa y ventana
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        from config import WIDTH, HEIGHT

                        pygame.display.set_mode((WIDTH, HEIGHT))

            # Pasa el evento a la pantalla actual
            manager.handle_event(event)

            # ===== CONVERTIR EVENTOS DE JOYSTICK =====
            keyboard_event = joystick_to_keyboard_event(event)
            if keyboard_event:
                # Simular que se presionó una tecla
                manager.handle_event(keyboard_event)

        # ===== ACTUALIZACIÓN =====
        # Actualiza la lógica del juego (movimientos, colisiones, animaciones)
        manager.update(dt)

        # ===== RENDERIZADO =====
        # Dibuja todo en la pantalla
        manager.draw(screen)

        # ===== ACTUALIZACIÓN DE PANTALLA =====
        # Muestra lo que acabamos de dibujar
        pygame.display.flip()


# ==================== PUNTO DE ENTRADA ====================
if __name__ == "__main__":
    main()
