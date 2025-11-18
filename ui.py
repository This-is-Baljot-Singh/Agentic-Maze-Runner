import pygame
from config import *

# Colors for UI
UI_BG = (44, 62, 80)
UI_ACCENT = (52, 152, 219)
UI_TEXT = (236, 240, 241)
UI_BUTTON = (39, 174, 96)
UI_BUTTON_HOVER = (46, 204, 113)
UI_TOGGLE_ON = (39, 174, 96)
UI_TOGGLE_OFF = (192, 57, 43)

class Button:
    def __init__(self, x, y, w, h, text, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.hovered = False

    def draw(self, screen, font):
        color = UI_BUTTON_HOVER if self.hovered else UI_BUTTON
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=5)
        
        txt_surf = font.render(self.text, True, WHITE)
        text_rect = txt_surf.get_rect(center=self.rect.center)
        screen.blit(txt_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and self.action:
                return self.action 
        return None

class NumberSelector:
    def __init__(self, x, y, label, min_val, max_val, default_val):
        self.x, self.y = x, y
        self.label = label
        self.min = min_val
        self.max = max_val
        self.value = default_val
        
        self.btn_minus = Button(x + 150, y, 30, 30, "-")
        self.btn_plus = Button(x + 220, y, 30, 30, "+")

    def draw(self, screen, font):
        lbl = font.render(f"{self.label}:", True, UI_TEXT)
        screen.blit(lbl, (self.x, self.y + 5))
        
        val_txt = font.render(str(self.value), True, UI_ACCENT)
        screen.blit(val_txt, (self.x + 190, self.y + 5))
        
        self.btn_minus.draw(screen, font)
        self.btn_plus.draw(screen, font)

    def handle_event(self, event):
        if self.btn_minus.handle_event(event) == self.btn_minus.action:
            if event.type == pygame.MOUSEBUTTONDOWN and self.btn_minus.hovered:
                self.value = max(self.min, self.value - 1)
        
        if self.btn_plus.handle_event(event) == self.btn_plus.action:
            if event.type == pygame.MOUSEBUTTONDOWN and self.btn_plus.hovered:
                self.value = min(self.max, self.value + 1)

class ToggleSelector:
    def __init__(self, x, y, label, default_state=False):
        self.x, self.y = x, y
        self.label = label
        self.state = default_state
        self.btn = Button(x + 150, y, 100, 30, "ON" if default_state else "OFF", action="toggle")

    def draw(self, screen, font):
        lbl = font.render(f"{self.label}:", True, UI_TEXT)
        screen.blit(lbl, (self.x, self.y + 5))
        
        # Update button color based on state
        global UI_BUTTON
        original_color = UI_BUTTON
        UI_BUTTON = UI_TOGGLE_ON if self.state else UI_TOGGLE_OFF
        
        self.btn.text = "ON" if self.state else "OFF"
        self.btn.draw(screen, font)
        
        UI_BUTTON = original_color

    def handle_event(self, event):
        if self.btn.handle_event(event) == "toggle":
             if event.type == pygame.MOUSEBUTTONDOWN and self.btn.hovered:
                 self.state = not self.state

class StartMenu:
    def __init__(self):
        self.selectors = [
            NumberSelector(50, 50, "Enemies", 0, 10, 3),
            NumberSelector(50, 100, "Keys", 1, 5, 1),
            NumberSelector(50, 150, "Game Speed", 1, 10, 5),
            NumberSelector(50, 200, "Traps (Diff)", 0, 15, 5),
            NumberSelector(50, 250, "Total Runs", 1, 20, 5),
            ToggleSelector(50, 300, "Show Heatmaps", default_state=True)
        ]
        self.start_btn = Button(250, 380, 200, 50, "START SIMULATION", action="start")
        self.config = {}

    def run(self, screen):
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 32)
        title_font = pygame.font.Font(None, 48)
        
        running = True
        while running:
            screen.fill(UI_BG)
            
            title = title_font.render("Maze Runner Configuration", True, UI_ACCENT)
            screen.blit(title, (200, 10))
            
            for sel in self.selectors:
                sel.draw(screen, font)
            
            self.start_btn.draw(screen, font)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                
                for sel in self.selectors:
                    sel.handle_event(event)
                
                res = self.start_btn.handle_event(event)
                if res == "start":
                    self.config = {
                        "enemies": self.selectors[0].value,
                        "keys": self.selectors[1].value,
                        "speed": self.selectors[2].value,
                        "traps": self.selectors[3].value,
                        "runs": self.selectors[4].value,
                        "heatmaps": self.selectors[5].state
                    }
                    return self.config
            
            pygame.display.flip()
            clock.tick(30)