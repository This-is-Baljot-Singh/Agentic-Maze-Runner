import pygame
from config import *

# --- MODERN COLOR PALETTE ---
COLOR_BG_TOP = (20, 30, 48)       
COLOR_BG_BOTTOM = (36, 59, 85)    
COLOR_ACCENT = (0, 255, 213)      
COLOR_TEXT = (255, 255, 255)      
COLOR_TEXT_SHADOW = (0, 0, 0)     
COLOR_PANEL = (0, 0, 0, 100)      
COLOR_BTN_DEFAULT = (52, 73, 94)
COLOR_BTN_HOVER = (41, 128, 185)
COLOR_BTN_START = (46, 204, 113)  
COLOR_BTN_START_HOVER = (39, 174, 96)
COLOR_DANGER = (231, 76, 60)
COLOR_SUCCESS = (46, 204, 113)

def draw_text_aligned(screen, font, text, anchor_point, align="left", color=COLOR_TEXT, shadow=True):
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect()
    
    if align == "left": rect.midleft = anchor_point
    elif align == "right": rect.midright = anchor_point
    elif align == "center": rect.center = anchor_point

    if shadow:
        shadow_surf = font.render(text, True, COLOR_TEXT_SHADOW)
        shadow_rect = rect.copy(); shadow_rect.x += 2; shadow_rect.y += 2
        screen.blit(shadow_surf, shadow_rect)
    screen.blit(text_surf, rect)

def draw_rounded_rect(surface, rect, color, corner_radius, alpha=None):
    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    if alpha is not None:
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, (*color[:3], alpha), shape_surf.get_rect(), border_radius=corner_radius)
        surface.blit(shape_surf, rect)
    else:
        pygame.draw.rect(surface, color, rect, border_radius=corner_radius)

class Button:
    def __init__(self, x, y, w, h, text, action=None, color_scheme="default"):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action
        self.hovered = False
        self.color_scheme = color_scheme

    def draw(self, screen, font):
        if self.color_scheme == "start": base_color = COLOR_BTN_START_HOVER if self.hovered else COLOR_BTN_START
        elif self.color_scheme == "toggle_on": base_color = COLOR_SUCCESS
        elif self.color_scheme == "toggle_off": base_color = COLOR_DANGER
        else: base_color = COLOR_BTN_HOVER if self.hovered else COLOR_BTN_DEFAULT

        shadow_rect = self.rect.copy(); shadow_rect.y += 4
        draw_rounded_rect(screen, shadow_rect, (0, 0, 0), 8, alpha=50)
        draw_rounded_rect(screen, self.rect, base_color, 8)
        
        if self.hovered: pygame.draw.rect(screen, COLOR_ACCENT, self.rect, 2, border_radius=8)
        
        text_surf = font.render(self.text, True, COLOR_TEXT)
        text_rect = text_surf.get_rect(center=self.rect.center)
        if self.hovered: text_rect.y += 1 
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION: self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered and self.action: return self.action 
        return None

class NumberSelector:
    def __init__(self, y, label, min_val, max_val, default_val, left_align_x, right_align_x):
        self.y = y; self.label = label; self.min = min_val; self.max = max_val; self.value = default_val
        self.left_x = left_align_x
        
        control_width = 140
        start_x = right_align_x - control_width
        
        self.btn_minus = Button(start_x, y - 10, 40, 35, "◄")
        self.val_rect = pygame.Rect(start_x + 45, y - 10, 50, 35)
        self.btn_plus = Button(start_x + 100, y - 10, 40, 35, "►")

    def draw(self, screen, font):
        draw_text_aligned(screen, font, f"{self.label}:", (self.left_x, self.y + 7), align="left")
        draw_rounded_rect(screen, self.val_rect, (20, 20, 20), 5)
        pygame.draw.rect(screen, (60, 60, 60), self.val_rect, 1, border_radius=5)
        
        val_surf = font.render(str(self.value), True, COLOR_ACCENT)
        val_rect = val_surf.get_rect(center=self.val_rect.center)
        screen.blit(val_surf, val_rect)
        self.btn_minus.draw(screen, font); self.btn_plus.draw(screen, font)

    def handle_event(self, event):
        if self.btn_minus.handle_event(event) == self.btn_minus.action:
            if event.type == pygame.MOUSEBUTTONDOWN and self.btn_minus.hovered: self.value = max(self.min, self.value - 1)
        if self.btn_plus.handle_event(event) == self.btn_plus.action:
            if event.type == pygame.MOUSEBUTTONDOWN and self.btn_plus.hovered: self.value = min(self.max, self.value + 1)

class ToggleSelector:
    def __init__(self, y, label, default_state, left_align_x, right_align_x):
        self.y = y; self.label = label; self.state = default_state; self.left_x = left_align_x
        btn_width = 140; start_x = right_align_x - btn_width
        
        self.btn = Button(start_x, y - 10, btn_width, 35, "ENABLED" if default_state else "DISABLED", action="toggle")
        if self.state: self.btn.color_scheme = "toggle_on"
        else: self.btn.color_scheme = "toggle_off"

    def draw(self, screen, font):
        draw_text_aligned(screen, font, f"{self.label}:", (self.left_x, self.y + 7), align="left")
        self.btn.draw(screen, font)

    def handle_event(self, event):
        if self.btn.handle_event(event) == "toggle":
             if event.type == pygame.MOUSEBUTTONDOWN and self.btn.hovered:
                 self.state = not self.state
                 self.btn.text = "ENABLED" if self.state else "DISABLED"
                 self.btn.color_scheme = "toggle_on" if self.state else "toggle_off"

class StartMenu:
    def __init__(self):
        # --- COMPACT LAYOUT ADJUSTMENTS ---
        panel_w = 600
        panel_h = 380  # Reduced height
        
        # Move panel closer to top to fit button below
        self.panel_rect = pygame.Rect((WINDOW_WIDTH - panel_w)//2, 80, panel_w, panel_h)
        
        padding_x = 50 
        label_x_anchor = self.panel_rect.left + padding_x
        control_x_anchor = self.panel_rect.right - padding_x
        
        start_y = self.panel_rect.top + 40
        spacing = 50 # Reduced spacing
        
        self.selectors = [
            NumberSelector(start_y, "Enemy Count", 0, 10, 3, label_x_anchor, control_x_anchor),
            NumberSelector(start_y + spacing, "Keys to Find", 1, 5, 1, label_x_anchor, control_x_anchor),
            NumberSelector(start_y + spacing*2, "Game Speed", 1, 10, 5, label_x_anchor, control_x_anchor),
            NumberSelector(start_y + spacing*3, "Trap Count", 0, 15, 5, label_x_anchor, control_x_anchor),
            NumberSelector(start_y + spacing*4, "Total Runs", 1, 20, 5, label_x_anchor, control_x_anchor),
            ToggleSelector(start_y + spacing*5, "Heatmap Analytics", True, label_x_anchor, control_x_anchor)
        ]
        
        # Start Button - Positioned tightly below panel
        btn_width = 350
        self.start_btn = Button(
            (WINDOW_WIDTH - btn_width)//2, 
            self.panel_rect.bottom + 15, # Only 15px gap
            btn_width, 
            50, # Slightly shorter button
            "INITIATE SIMULATION", 
            action="start", 
            color_scheme="start"
        )
        self.config = {}

    def draw_background(self, screen):
        height = WINDOW_HEIGHT
        for y in range(height):
            alpha = y / height
            r = int(COLOR_BG_TOP[0] * (1 - alpha) + COLOR_BG_BOTTOM[0] * alpha)
            g = int(COLOR_BG_TOP[1] * (1 - alpha) + COLOR_BG_BOTTOM[1] * alpha)
            b = int(COLOR_BG_TOP[2] * (1 - alpha) + COLOR_BG_BOTTOM[2] * alpha)
            pygame.draw.line(screen, (r, g, b), (0, y), (WINDOW_WIDTH, y))
            
        draw_rounded_rect(screen, self.panel_rect, (0,0,0), 20, alpha=80)
        pygame.draw.rect(screen, COLOR_ACCENT, self.panel_rect, 2, border_radius=20)

    def run(self, screen):
        clock = pygame.time.Clock()
        try:
            title_font = pygame.font.SysFont("impact", 60) # Slightly smaller title
            ui_font = pygame.font.SysFont("segoeui", 26, bold=True)
        except:
            title_font = pygame.font.Font(None, 60)
            ui_font = pygame.font.Font(None, 30)
        
        running = True
        while running:
            self.draw_background(screen)
            
            title_text = "MAZE RUNNER // AI CONFIG"
            title_pos = (WINDOW_WIDTH//2, 30) # Higher up
            
            for offset in range(4, 0, -1):
                alpha = 50 - (offset * 10)
                glow_surf = title_font.render(title_text, True, (*COLOR_ACCENT, alpha))
                glow_rect = glow_surf.get_rect(center=title_pos)
                screen.blit(glow_surf, (glow_rect.x-offset, glow_rect.y-offset))
                screen.blit(glow_surf, (glow_rect.x+offset, glow_rect.y+offset))
            
            draw_text_aligned(screen, title_font, title_text, title_pos, align="center", color=COLOR_TEXT)
            
            for sel in self.selectors: sel.draw(screen, ui_font)
            self.start_btn.draw(screen, ui_font)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return None
                for sel in self.selectors: sel.handle_event(event)
                res = self.start_btn.handle_event(event)
                if res == "start":
                    self.config = {
                        "enemies": self.selectors[0].value, "keys": self.selectors[1].value,
                        "speed": self.selectors[2].value, "traps": self.selectors[3].value,
                        "runs": self.selectors[4].value, "heatmaps": self.selectors[5].state
                    }
                    return self.config
            
            pygame.display.flip(); clock.tick(30)