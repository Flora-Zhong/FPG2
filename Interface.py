import sys
from datetime import datetime
import pygame
import pygame.freetype as ft
from InteractiveExpenseTracker import InteractiveExpenseTracker

SCREEN_WIDTH, SCREEN_HEIGHT = 900, 620
FPS = 60
GRADIENT_TOP = (40, 35, 90)
GRADIENT_BOTTOM = (15, 40, 60)
ACCENT_COLOR = (120, 180, 255)
WHITE = (245, 245, 245)
PANEL_ALPHA = 180
BUTTON_ALPHA = 200
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Weekly Expense Tracker")
clock = pygame.time.Clock()
TITLE_FONT = ft.SysFont(None, 46)
TEXT_FONT = ft.SysFont(None, 24)

def lerp(color_start: tuple, color_end: tuple, t: float):
    """
    Linearly interpolate between two RGB colors.
    """
    return tuple(
        int(a + (b - a) * t)
        for a, b in zip(color_start, color_end)
    )

def draw_gradient_background():
    """
    Draw a vertical gradient over the entire screen from GRADIENT_TOP to GRADIENT_BOTTOM.
    """
    for y in range(SCREEN_HEIGHT):
        t = y / SCREEN_HEIGHT
        color = lerp(GRADIENT_TOP, GRADIENT_BOTTOM, t)
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))

def draw_glass_panel(rect):
    """
    Draw a semi‑transparent "glass" panel with a white border.
    """
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    panel.fill((0, 0, 0, PANEL_ALPHA))
    pygame.draw.rect(panel, WHITE, panel.get_rect(), 1, border_radius=16)
    screen.blit(panel, rect.topleft)

def render_center(font, text, position, color=WHITE, size=None):
    """
    Render text centered at a given position.
    """
    if size is None:
        rect = font.get_rect(text)
        rect.center = position
        font.render_to(screen, rect.topleft, text, color)
    else:
        rect = font.get_rect(text, size=size)
        rect.center = position
        font.render_to(screen, rect.topleft, text, color, size=size)

class Button:
    def __init__(self, text, center):
        self.text = text
        self.rect = pygame.Rect(0, 0, 240, 56)
        self.rect.center = center
    def draw(self):
        """
        Draw the button on screen.
        """
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        color = ACCENT_COLOR if hover else WHITE
        alpha = BUTTON_ALPHA + (40 if hover else 0)
        surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        surf.fill((0, 0, 0, alpha))
        pygame.draw.rect(surf, color, surf.get_rect(), 2, border_radius=14)
        screen.blit(surf, self.rect.topleft)
        render_center(TEXT_FONT, self.text, self.rect.center, color, size=24)
    def hit(self, pos):
        """
        Check if a position collides with the button.
        """
        return self.rect.collidepoint(pos)

class TextInput:
    """
    Single‑line text input box.
    """
    ACTIVE_COLOR = ACCENT_COLOR
    PASSIVE_COLOR = (160, 160, 160)
    def __init__(self, prompt, center):
        self.prompt = prompt
        self.text = ""
        self.active = False
        self.box = pygame.Rect(0, 0, 340, 40)
        self.box.center = center
    def handle_event(self, event):
        """
        Handle mouse and keyboard events for typing.
        """
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.box.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
    def draw(self):
        """
        Draw the input box and its current text.
        """
        color = self.ACTIVE_COLOR if self.active else self.PASSIVE_COLOR
        pygame.draw.rect(screen, (0, 0, 0, 200), self.box, border_radius=8)
        pygame.draw.rect(screen, color, self.box, 2, border_radius=8)
        render_center(TEXT_FONT, self.prompt, (self.box.centerx, self.box.y - 15))
        TEXT_FONT.render_to(screen, (self.box.x + 10, self.box.y + 8), self.text or " ", WHITE)

def prompt_text(prompt):
    """
    Block until the user enters a line of text and presses Enter.
    """
    input_box = TextInput(prompt, (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            input_box.handle_event(event)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and not input_box.active:
                return input_box.text.strip()
        draw_gradient_background()
        draw_glass_panel(pygame.Rect(200, 200, 500, 200))
        input_box.draw()
        pygame.display.flip()
        clock.tick(FPS)

def choose_category(categories):
    """
    Let the user pick an existing category or add a new one.
    """
    buttons = [
        Button(name, (SCREEN_WIDTH // 2, 200 + i * 60))
        for i, name in enumerate(categories)
    ]
    new_btn = Button("+ New Category", (SCREEN_WIDTH // 2, 200 + len(categories) * 60))
    while True:
        draw_gradient_background()
        draw_glass_panel(pygame.Rect(220, 120, 460, 420))
        render_center(TITLE_FONT, "Select Category", (SCREEN_WIDTH // 2, 150), ACCENT_COLOR)
        for btn in buttons:
            btn.draw()
        new_btn.draw()
        pygame.display.flip()
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if new_btn.hit(event.pos):
                    new_name = prompt_text("New category name:")
                    if new_name:
                        cat = new_name.strip().capitalize()
                        categories.append(cat)
                        return cat
                for btn in buttons:
                    if btn.hit(event.pos):
                        return btn.text

def main_gui():
    """
    Main entry point for the Pygame UI.
    """
    tracker = InteractiveExpenseTracker()
    categories = ["Food", "Entertainment", "Transport", "School Supplies"]

    menu_items = ["Add Expense", "Set Budget", "Show Summary", "Reset Week", "Exit"]
    menu_buttons = [
        Button(label, (SCREEN_WIDTH // 2, 300 + idx * 70))
        for idx, label in enumerate(menu_items)
    ]
    mode = "home"
    inputs = []
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if mode == "home" and event.type == pygame.MOUSEBUTTONDOWN:
                for button in menu_buttons:
                    if button.hit(event.pos):
                        label = button.text
                        if label == "Add Expense":
                            mode = "add"
                            inputs = [
                                TextInput("Date DD/MM/YYYY", (SCREEN_WIDTH // 2, 330)),
                                TextInput("Amount (number)", (SCREEN_WIDTH // 2, 390)),
                                TextInput("Notes (optional)", (SCREEN_WIDTH // 2, 450)),
                            ]
                        elif label == "Set Budget":
                            mode = "budget"
                            inputs = [
                                TextInput("Budget Amount (number)", (SCREEN_WIDTH // 2, 400)),
                            ]
                        elif label == "Show Summary":
                            tracker.show_summary()
                        elif label == "Reset Week":
                            tracker.reset_week()
                        elif label == "Exit":
                            pygame.quit(); sys.exit()
            if mode in ("add", "budget"):
                for inp in inputs:
                    inp.handle_event(event)
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN
                        and not any(inp.active for inp in inputs)):
                    if mode == "add":
                        try:
                            date_str = datetime.strptime(inputs[0].text, "%d/%m/%Y")\
                                                    .strftime("%d/%m/%Y")
                            amount = float(inputs[1].text)
                        except ValueError:
                            mode = "home"
                            break
                        category = choose_category(categories)
                        notes = inputs[2].text
                        tracker.add_expense(amount, category)
                    else:
                        category = choose_category(categories)
                        try:
                            budget_value = float(inputs[0].text)
                            tracker.weekly_budgets[category] = budget_value
                        except ValueError:
                            pass
                    mode = "home"
        draw_gradient_background()
        draw_glass_panel(pygame.Rect(150, 70, 600, 480))
        render_center(TITLE_FONT, "Weekly Expense Tracker", (SCREEN_WIDTH // 2, 110), ACCENT_COLOR)
        if mode == "home":
            for btn in menu_buttons:
                btn.draw()
        else:
            for inp in inputs:
                inp.draw()
            render_center(TEXT_FONT, "Press Enter to confirm", (SCREEN_WIDTH // 2, 520), WHITE)
        pygame.display.flip()
        clock.tick(FPS)
if __name__ == "__main__":
    main_gui()
