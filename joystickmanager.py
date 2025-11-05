import pygame


class JoystickManager:
    """
    Gestor de controles para mando de PS3
    Mapea los botones y joysticks del control
    """

    def __init__(self):
        self.joystick = None
        self.connected = False

        # Inicializar sistema de joystick
        pygame.joystick.init()

        # Intentar conectar el primer mando disponible
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.connected = True
            print(f"✅ Mando conectado: {self.joystick.get_name()}")
            print(f"   Botones: {self.joystick.get_numbuttons()}")
            print(f"   Ejes: {self.joystick.get_numaxes()}")
        else:
            print("⚠️  No se detectó ningún mando")

    # ==================== MAPEO DE BOTONES PS3 ====================
    # Estos valores pueden variar según el driver, pero son estándar para PS3
    BUTTON_X = 0  # X (ataque)
    #BUTTON_CIRCLE = 1  # Círculo
    BUTTON_SQUARE = 2  # Cuadrado
    BUTTON_TRIANGLE = 3  # Triángulo
    BUTTON_L1 = 4  # L1
    BUTTON_R1 = 5  # R1
    BUTTON_L2 = 6  # L2
    BUTTON_R2 = 7  # R2
    BUTTON_SELECT = 8  # Select (volver/ESC)
    BUTTON_START = 1  # Start (confirmar/ENTER)
    BUTTON_L3 = 10  # Joystick izquierdo presionado
    BUTTON_R3 = 11  # Joystick derecho presionado
    BUTTON_PS = 12  # Botón PS (centro)

    # Ejes del joystick
    AXIS_LEFT_X = 0  # Joystick izquierdo horizontal
    AXIS_LEFT_Y = 1  # Joystick izquierdo vertical
    AXIS_RIGHT_X = 2  # Joystick derecho horizontal
    AXIS_RIGHT_Y = 3  # Joystick derecho vertical

    # Zona muerta para evitar drift
    DEADZONE = 0.15

    def get_button(self, button_id):
        """Verifica si un botón está presionado"""
        if not self.connected:
            return False
        try:
            return self.joystick.get_button(button_id)
        except:
            return False

    def get_axis(self, axis_id):
        """Obtiene el valor de un eje (-1.0 a 1.0)"""
        if not self.connected:
            return 0.0
        try:
            value = self.joystick.get_axis(axis_id)
            # Aplicar zona muerta
            if abs(value) < self.DEADZONE:
                return 0.0
            return value
        except:
            return 0.0

    def get_movement(self):
        """
        Obtiene el movimiento del joystick izquierdo
        Retorna: (dx, dy) valores entre -1 y 1
        """
        dx = self.get_axis(self.AXIS_LEFT_X)
        dy = self.get_axis(self.AXIS_LEFT_Y)
        return dx, dy

    def is_attack_pressed(self):
        """Verifica si se presionó el botón de ataque (X)"""
        return self.get_button(self.BUTTON_X)

    def is_back_pressed(self):
        """Verifica si se presionó el botón de volver (SELECT)"""
        return self.get_button(self.BUTTON_SELECT)

    def is_confirm_pressed(self):
        """Verifica si se presionó el botón de confirmar (START)"""
        return self.get_button(self.BUTTON_START)

    def update(self):
        """Actualiza el estado del joystick"""
        if not self.connected:
            # Intentar reconectar si se desconectó
            if pygame.joystick.get_count() > 0:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                self.connected = True
                print("✅ Mando reconectado")

    def disconnect(self):
        """Desconecta el joystick"""
        if self.joystick:
            self.joystick.quit()
            self.connected = False


# Instancia global del gestor de joystick
JOYSTICK = JoystickManager()


# ==================== EVENTOS DE JOYSTICK ====================
def joystick_to_keyboard_event(event):
    """
    Convierte eventos de joystick a eventos de teclado simulados
    para mantener compatibilidad con el código existente

    Retorna un evento de pygame.KEYDOWN o None
    """
    if not JOYSTICK.connected:
        return None

    if event.type == pygame.JOYBUTTONDOWN:
        # Mapear botones a teclas
        button_map = {
            JOYSTICK.BUTTON_X: pygame.K_SPACE,  # X -> ESPACIO (ataque)
            JOYSTICK.BUTTON_SELECT: pygame.K_ESCAPE,  # SELECT -> ESC (volver)
            JOYSTICK.BUTTON_START: pygame.K_RETURN,  # START -> ENTER (confirmar)
        }

        if event.button in button_map:
            # Crear evento de teclado simulado
            return pygame.event.Event(
                pygame.KEYDOWN, key=button_map[event.button], unicode="", mod=0
            )

    return None


# ==================== INSTRUCCIONES DE USO ====================
"""
📋 CÓMO INTEGRAR EN TU JUEGO:

1. En main.py:
   from joystick import JOYSTICK, joystick_to_keyboard_event

2. En el game loop, dentro del manejo de eventos:
   
   for event in pygame.event.get():
       # ... código existente ...
       
       # Convertir eventos de joystick a teclado
       keyboard_event = joystick_to_keyboard_event(event)
       if keyboard_event:
           manager.handle_event(keyboard_event)

3. En player.py, modificar el método update():
   
   def update(self, dt, keys):
       from joystick import JOYSTICK
       
       dx = dy = 0
       
       # TECLADO (código existente)
       if keys[pygame.K_a] or keys[pygame.K_LEFT]:
           dx -= 1
           self.facing = -1
       # ... resto del código ...
       
       # JOYSTICK
       if JOYSTICK.connected:
           joy_dx, joy_dy = JOYSTICK.get_movement()
           dx += joy_dx
           dy += joy_dy
           
           # Actualizar dirección
           if joy_dx > 0.2:
               self.facing = 1
           elif joy_dx < -0.2:
               self.facing = -1

4. En main.py, actualizar el joystick en cada frame:
   
   def main():
       while True:
           JOYSTICK.update()  # Agregar esto al inicio del loop
           # ... resto del código ...

🎮 CONTROLES DEL MANDO PS3:
- Joystick Izquierdo: Movimiento (WASD)
- X: Atacar (ESPACIO)
- START: Confirmar (ENTER)
- SELECT: Volver (ESC)

⚙️ TROUBLESHOOTING:
- Si no detecta el mando, verifica que esté conectado ANTES de iniciar el juego
- En Linux puede requerir permisos: sudo chmod +x /dev/input/js0
- En Windows asegúrate de tener los drivers de DirectInput instalados
"""
