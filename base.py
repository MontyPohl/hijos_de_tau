import pygame


class ScreenBase:
    def handle_event(self, event):
        pass

    def update(self, dt): 
        pass

    def draw(self, surf):
        pass
