import pygame
import random
from config import WIDTH, HEIGHT, draw_text


# ==================== CLASE POWER-UP ====================
class PowerUp:
    """
    Clase que representa ítems coleccionables que dan beneficios temporales
    - Guampa de Tereré: Recupera vida
    - Carrulim: Aumenta velocidad y fuerza por 3 segundos
    """

    def __init__(self, x, y, tipo):
        """
        Constructor del power-up

        Parámetros:
        - x, y: Posición en el mapa
        - tipo: "terere" o "carrulim"
        """
        self.x = x
        self.y = y
        self.w = 50  # Ancho (aumentado para las imágenes)
        self.h = 50  # Alto (aumentado para las imágenes)
        self.tipo = tipo
        self.active = True  # Si está disponible para recoger

        # Animación de flotación
        self.float_offset = 0
        self.float_speed = 2

        # Animación de brillo
        self.glow = 0
        self.glow_dir = 1

        # Cargar imagen según el tipo
        self.image = None
        self.use_image = False

        if tipo == "terere":
            self.color = (100, 200, 120)  # Verde (tereré) - fallback
            self.glow_color = (150, 255, 170)
            try:
                self.image = pygame.image.load(
                    "imagenes/guampa_terere.png"
                ).convert_alpha()
                # Escalar la imagen al tamaño deseado
                self.image = pygame.transform.scale(self.image, (self.w, self.h))
                self.use_image = True
                print("✅ Imagen de guampa de tereré cargada")
            except Exception as e:
                print(f"⚠ No se pudo cargar guampa_terere.png: {e}")
                self.use_image = False

        else:  # carrulim
            self.color = (220, 180, 80)  # Dorado (carrulim) - fallback
            self.glow_color = (255, 220, 120)
            try:
                self.image = pygame.image.load("imagenes/Carrulin.png").convert_alpha()
                # Escalar la imagen al tamaño deseado
                self.image = pygame.transform.scale(self.image, (self.w, self.h))
                self.use_image = True
                print("✅ Imagen de carrulim cargada")
            except Exception as e:
                print(f"⚠ No se pudo cargar carrulim.png: {e}")
                self.use_image = False

    def rect(self):
        """Devuelve el rectángulo de colisión"""
        return pygame.Rect(self.x, self.y + self.float_offset, self.w, self.h)

    def update(self, dt):
        """Actualiza animaciones"""
        # Efecto de flotación
        self.float_offset = pygame.math.Vector2(0, self.float_offset).y
        self.float_offset += self.float_speed * 15 * dt
        if abs(self.float_offset) > 5:
            self.float_speed *= -1

        # Efecto de brillo pulsante
        self.glow += self.glow_dir * 100 * dt
        if self.glow > 40 or self.glow < 0:
            self.glow_dir *= -1

    def draw(self, surf):
        """Dibuja el power-up"""
        if not self.active:
            return

        y_pos = self.y + self.float_offset

        # Brillo exterior (aura)
        glow_size = int(self.w + self.glow / 2)
        glow_rect = pygame.Rect(
            self.x - (glow_size - self.w) // 2,
            y_pos - (glow_size - self.h) // 2,
            glow_size,
            glow_size,
        )
        glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pygame.draw.circle(
            glow_surf,
            (*self.glow_color, 60),  # Semi-transparente
            (glow_size // 2, glow_size // 2),
            glow_size // 2,
        )
        surf.blit(glow_surf, glow_rect.topleft)

        # Dibujar imagen o fallback
        if self.use_image and self.image:
            # Dibujar la imagen PNG
            surf.blit(self.image, (self.x, y_pos))
        else:
            # Fallback: dibujar con formas si no hay imagen
            if self.tipo == "terere":
                # Dibujar guampa de tereré (versión simple)
                pygame.draw.ellipse(surf, (80, 60, 40), (self.x, y_pos, self.w, 8))
                pygame.draw.rect(
                    surf, (100, 80, 60), (self.x, y_pos + 4, self.w, self.h - 8)
                )
                pygame.draw.ellipse(
                    surf, (120, 100, 80), (self.x, y_pos + self.h - 8, self.w, 8)
                )
                pygame.draw.rect(
                    surf, (180, 180, 180), (self.x + self.w // 2 - 1, y_pos - 6, 2, 10)
                )
                pygame.draw.circle(
                    surf, (200, 200, 200), (self.x + self.w // 2, y_pos - 6), 2
                )
                pygame.draw.circle(
                    surf, (80, 160, 90), (self.x + self.w // 2, y_pos + 8), 6
                )

            else:  # carrulim
                # Dibujar carrulim (versión simple)
                pygame.draw.rect(
                    surf, (240, 230, 220), (self.x + 2, y_pos + 6, self.w - 4, 12)
                )
                pygame.draw.circle(surf, (140, 100, 60), (self.x + 4, y_pos + 12), 4)
                pygame.draw.circle(
                    surf, (140, 100, 60), (self.x + self.w - 4, y_pos + 12), 4
                )
                for i in range(3):
                    x_line = self.x + 6 + i * 4
                    pygame.draw.line(
                        surf,
                        (200, 190, 180),
                        (x_line, y_pos + 6),
                        (x_line, y_pos + 18),
                        1,
                    )
                pygame.draw.circle(
                    surf, (255, 100, 50), (self.x + self.w - 4, y_pos + 12), 3
                )
                pygame.draw.circle(
                    surf, (255, 200, 100), (self.x + self.w - 4, y_pos + 12), 2
                )

        # Texto del nombre (debajo del ítem)
        nombre = "TERERÉ" if self.tipo == "terere" else "CARRULIM"
        draw_text(
            surf, nombre, 10, self.x + self.w // 2, y_pos + self.h + 8, center=True
        )


# ==================== GESTOR DE POWER-UPS ====================
class PowerUpManager:
    """
    Administra la aparición y efectos de los power-ups
    """

    def __init__(self):
        self.powerups = []  # Lista de power-ups activos en el mapa
        self.spawn_timer = 10.0  # Aparece cada 10 segundos

        # Efectos activos en el jugador
        self.carrulim_active = False
        self.carrulim_timer = 0.0
        self.carrulim_duration = 5.0  # 5 segundos de duración

    def update(self, dt, player):
        """
        Actualiza power-ups y efectos

        Parámetros:
        - dt: Delta time
        - player: Referencia al jugador
        """
        # Actualizar temporizador de aparición
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_powerup()
            self.spawn_timer = 10.0  # Reinicia a 10 segundos

        # Actualizar cada power-up
        for powerup in self.powerups[:]:
            powerup.update(dt)

            # Verificar colisión con el jugador
            if powerup.active and powerup.rect().colliderect(player.rect()):
                self.collect_powerup(powerup, player)

        # Actualizar efecto de carrulim
        if self.carrulim_active:
            self.carrulim_timer -= dt
            if self.carrulim_timer <= 0:
                self.deactivate_carrulim(player)

        # Limpiar power-ups inactivos (ya recogidos)
        self.powerups = [p for p in self.powerups if p.active]

    def spawn_powerup(self):
        """Genera un nuevo power-up en posición aleatoria"""
        # Elige tipo aleatorio
        tipo = random.choice(["terere", "carrulim"])

        # Posición aleatoria (evita bordes)
        x = random.randint(50, WIDTH - 80)
        y = random.randint(50, HEIGHT - 180)

        powerup = PowerUp(x, y, tipo)
        self.powerups.append(powerup)

        print(f"✨ Apareció un {tipo.upper()} en ({x}, {y})")

    def collect_powerup(self, powerup, player):
        """
        Aplica el efecto del power-up al jugador

        Parámetros:
        - powerup: El power-up recogido
        - player: El jugador
        """
        if powerup.tipo == "terere":
            # Guampa de tereré: Recupera vida
            old_health = player.health
            player.health = min(100, player.health + 40)  # +40 HP (máximo 100)
            healed = player.health - old_health
            print(f"💚 ¡Tereré recogido! +{int(healed)} HP")

        elif powerup.tipo == "carrulim":
            # Carrulim: Aumenta velocidad y fuerza por 3 segundos
            if not self.carrulim_active:
                # Guardar valores originales
                player.original_speed = player.speed
                player.original_attack_damage = 30  # Daño base normal

                # Aplicar buffs
                player.speed *= 1.5  # +50% velocidad
                player.attack_damage = 50  # +66% daño (de 30 a 50)

                self.carrulim_active = True
                self.carrulim_timer = self.carrulim_duration

                print(
                    f"⚡ ¡Carrulim activado! Velocidad y fuerza aumentadas por {self.carrulim_duration}s"
                )
            else:
                # Si ya está activo, reinicia el timer
                self.carrulim_timer = self.carrulim_duration
                print(f"⚡ ¡Carrulim renovado! Timer reiniciado")

        # Desactiva el power-up
        powerup.active = False

    def deactivate_carrulim(self, player):
        """Desactiva el efecto del carrulim"""
        # Restaurar valores originales
        if hasattr(player, "original_speed"):
            player.speed = player.original_speed
            player.attack_damage = 30  # Volver al daño normal

        self.carrulim_active = False
        print("⏱ Efecto del Carrulim terminado")

    def draw(self, surf):
        """Dibuja todos los power-ups activos"""
        for powerup in self.powerups:
            powerup.draw(surf)

    def draw_hud(self, surf, x, y):
        """
        Dibuja el HUD de efectos activos

        Parámetros:
        - surf: Superficie donde dibujar
        - x, y: Posición del HUD
        """
        if self.carrulim_active:
            # Panel semi-transparente
            panel = pygame.Surface((220, 50), pygame.SRCALPHA)
            panel.fill((40, 40, 40, 180))
            surf.blit(panel, (x, y))

            # Borde brillante
            pygame.draw.rect(surf, (255, 200, 100), (x, y, 220, 50), 2)

            # Ícono del carrulim pequeño
            icon_x = x + 10
            icon_y = y + 15
            pygame.draw.rect(surf, (240, 230, 220), (icon_x, icon_y, 16, 8))
            pygame.draw.circle(surf, (255, 100, 50), (icon_x + 14, icon_y + 4), 3)

            # Texto del efecto
            draw_text(surf, "CARRULIM ACTIVO", 16, x + 35, y + 10)

            # Barra de tiempo restante
            time_pct = self.carrulim_timer / self.carrulim_duration
            bar_width = 180
            pygame.draw.rect(surf, (60, 60, 60), (x + 30, y + 30, bar_width, 8))
            pygame.draw.rect(
                surf, (255, 200, 100), (x + 30, y + 30, int(bar_width * time_pct), 8)
            )

            # Tiempo restante en texto
            draw_text(surf, f"{self.carrulim_timer:.1f}s", 14, x + 120, y + 28)


# ==================== INSTRUCCIONES DE USO ====================
"""
📁 ESTRUCTURA DE CARPETAS REQUERIDA:

proyecto/
├── imagenes/
│   ├── guampa_terere.png  ← Imagen del tereré
│   └── carrulim.png       ← Imagen del carrulim
├── powerup.py
└── ... (otros archivos)

🎨 RECOMENDACIONES PARA LAS IMÁGENES:
- Tamaño sugerido: 32x32 píxeles (o más grande, se escalará automáticamente)
- Formato: PNG con fondo transparente
- Estilo: Iconos o sprites pixelados tipo retro

⚙ CÓMO FUNCIONA:
1. Intenta cargar las imágenes desde la carpeta "imagenes/"
2. Si la imagen existe: La muestra con efecto de brillo y flotación
3. Si NO existe: Dibuja el ítem con formas geométricas (fallback)
4. En la consola verás mensajes confirmando si cargó o no

✅ INTEGRACIÓN EN TUS NIVELES (igual que antes):

En level1.py, level2.py, level3.py:

1. Al inicio:
   from powerup import PowerUpManager

2. En _init_:
   self.powerup_manager = PowerUpManager()

3. En update():
   self.powerup_manager.update(dt, self.player)

4. En draw():
   self.powerup_manager.draw(surf)
   self.powerup_manager.draw_hud(surf, 12, 90)

5. En handle_event() (ataque):
   damage = getattr(self.player, 'attack_damage', 30)
   e.take_damage(damage)
"""