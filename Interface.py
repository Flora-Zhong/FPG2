"""
interface.py – Pygame front-end for InteractiveExpenseTracker
"""
import sys
import os
import csv
import json
import pygame
import pygame.freetype as ft
import matplotlib.pyplot as plt
import numpy as np
from InteractiveExpenseTracker import InteractiveExpenseTracker

WIDTH, HEIGHT = 900, 620
FPS = 60
TOP_COLOR = (40, 35, 90)
BOTTOM_COLOR = (15, 40, 60)
ACCENT_COLOR = (120, 180, 255)
WHITE = (245, 245, 245)
PANEL_ALPHA = 180
BUTTON_ALPHA = 200
pygame.init()
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Weekly Expense Tracker")
clock = pygame.time.Clock()
font_title = pygame.freetype.SysFont(None, 46)
font_text = pygame.freetype.SysFont(None, 24)

def lerp_rgb(color_a: tuple[int, int, int], 
             color_b: tuple[int, int, int], 
             t: float) -> tuple[int, ...]:
    """
    Mix two colors by t (0.0 to 1.0).
    """
    return tuple(int(a + (b - a) * t) for a, b in zip(color_a, color_b))

def draw_background_gradient() -> None:
    """
    Paint a vertical gradient across the entire window.
    """
    for y in range(HEIGHT):
        col = lerp_rgb(TOP_COLOR, BOTTOM_COLOR, y / HEIGHT)
        pygame.draw.line(win, col, (0, y), (WIDTH, y))

def draw_glass_panel(rect: pygame.Rect) -> None:
    """
    Draw a translucent panel with rounded corners.
    """
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    surf.fill((0, 0, 0, PANEL_ALPHA))
    pygame.draw.rect(surf, WHITE, surf.get_rect(), 1, border_radius=16)
    win.blit(surf, rect.topleft)

def render_centered_text(font: ft.Font, 
                         text: str, 
                         pos: tuple[int, int], 
                         color: tuple[int, int, int] = WHITE, 
                         size = None) -> None:
    """
    Render text centered at pos.
    """
    if size:
        rect = font.get_rect(text, size=size)
    else:
        rect = font.get_rect(text)
    rect.center = pos
    if size:
        font.render_to(win, rect.topleft, text, color, size=size)
    else:
        font.render_to(win, rect.topleft, text, color)

class Button:
    """
    A simple rounded-rectangle button with hover outline.
    """
    def __init__(self, label: str, center: tuple[int, int]) -> None:
        self.label = label
        self.rect  = pygame.Rect(0, 0, 240, 56)
        self.rect.center = center

    def draw(self) -> None:
        """
        Render the button.
        """
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        col = ACCENT_COLOR if hover else WHITE
        surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        surf.fill((0, 0, 0, BUTTON_ALPHA + (40 if hover else 0)))
        pygame.draw.rect(surf, col, surf.get_rect(), 2, border_radius=14)
        win.blit(surf, self.rect.topleft)
        render_centered_text(font_text, self.label, self.rect.center, col, 24)

    def hit(self, pos: tuple[int, int]) -> bool:
        """Return True if pos lies inside the button."""
        return self.rect.collidepoint(pos)

class TextInput:
    """
    Simple single-line text input box.
    """
    ACTIVE_COLOR = ACCENT_COLOR
    PASSIVE_COLOR = (160, 160, 160)
    
    def __init__(self, prompt: str, center: tuple[int, int]) -> None:
        self.prompt = prompt
        self.text   = ""
        self.active = False
        self.rect   = pygame.Rect(0, 0, 340, 40)
        self.rect.center = center
        
    def handle_event(self, event: pygame.event.Event) -> None:
        """Update focus / text according to the event given."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode.isprintable():
                self.text += event.unicode

    def draw(self) -> None:
        """
        Draw the input box and text.
        """
        border = self.ACTIVE_COLOR if self.active else self.PASSIVE_COLOR
        pygame.draw.rect(win, (0, 0, 0, 200), self.rect, border_radius=8)
        pygame.draw.rect(win, border, self.rect, 2, border_radius=8)
        render_centered_text(font_text, self.prompt,
                             (self.rect.centerx, self.rect.y - 15))
        font_text.render_to(win, (self.rect.x + 10, self.rect.y + 8),
                            self.text or " ", WHITE)

notice_msg = ""
notice_color = WHITE
notice_time = 0
notice_duration = 3000

def banner(msg: str, col: tuple[int, int, int] = WHITE) -> None:
    """
    Display a transient notice banner (3 seconds).
    """
    global notice_msg, notice_color, notice_time
    notice_msg = text
    notice_color = color
    notice_time = pygame.time.get_ticks()

def modal_text(prompt: str) -> str:
    """
    Prompt user for text and wait for Enter.
    """
    inp = TextInput(prompt, (WIDTH//2, HEIGHT//2))
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            inp.handle_event(ev)
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN and not inp.active:
                return inp.text.strip()
        draw_background_gradient()
        draw_glass_panel(pygame.Rect(200, 200, 500, 200))
        inp.draw()
        pygame.display.flip(); CLOCK.tick(FPS)
        clock.tick(FPS)

def modal_load_or_new(root):
    """
    Ask whether to load existing data or start fresh.
    """
    load_btn = Button("Load Existing Data", (WIDTH//2, 320))
    new_btn  = Button("Create New Account", (WIDTH//2, 380))
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if load_btn.hit(ev.pos):
                    return "load"
                if new_btn.hit(ev.pos):
                    return "new"
        draw_background_gradient()
        draw_glass_panel(pygame.Rect(200, 220, 500, 250))
        render_centered_text(font_title, f"User '{root}' found", (WIDTH//2, 260), ACCENT_COLOR, 32)
        render_centered_text(font_text, "Pick an option:", (WIDTH//2, 300))
        load_btn.draw()
        new_btn.draw()
        pygame.display.flip()
        clock.tick(FPS)

def split_root_suffix(name):
    """
    Separate trailing digits from a username base.
    """
    i = len(name)
    while i and name[i-1].isdigit():
        i -= 1
    root = name[:i]
    suffix = int(name[i:]) if name[i:] else 0
    return root, suffix

def next_unused_suffix(root, variants):
    """
    Find the smallest integer suffix not yet in use.
    """
    used = {split_root_suffix(v)[1] for v in variants}
    n = 1
    while n in used:
        n += 1
    return n

def build_tracker():
    """
    Get or create a username, then set up the tracker instance.
    """
    raw = modal_text("Enter your username:")
    if not raw:
        pygame.quit(); sys.exit()
    root, _ = split_root_suffix(raw.capitalize())
    files = [f for f in os.listdir('.') if f.startswith(f"data_{root}") and f.endswith(".json")]
    choice = modal_load_or_new(root) if files else "new"
    if choice == "load":
        username = raw.capitalize() if raw.capitalize() in [f[5:-5] for f in files] else root
    else:
        username = root + str(next_unused_suffix(root, [f[5:-5] for f in files])) if root in [f[5:-5] for f in files] else root
        if username != root:
            banner(f"Username set to {username}!")
    tr = InteractiveExpenseTracker.__new__(InteractiveExpenseTracker)
    tr.username = username
    tr.data_file = f"data_{username}.json"
    tr.history_file = f"history_{username}.csv"
    tr.weekly_totals = {}
    tr.weekly_budgets = {}
    tr.history = {}
    tr.current_week = 1
    tr.active = True
    try:
        with open(tr.history_file) as f:
            rows = list(csv.reader(f))
            if rows:
                tr.current_week = int(rows[0][0])
                for r in rows[1:]:
                    tr.history[r[0]] = [float(x) for x in r[1:]]
    except FileNotFoundError:
        with open(tr.history_file, "w", newline="") as f:
            csv.writer(f).writerow([tr.current_week])
    if choice == "load":
        try:
            with open(tr.data_file) as f:
                d = json.load(f)
                tr.weekly_totals = d.get("weekly_totals", {})
                tr.weekly_budgets = d.get("weekly_budgets", {})
                tr.current_week = d.get("current_week", tr.current_week)
        except FileNotFoundError:
            pass
    cats = list(set(["Food", "Entertainment", "Transport", "School Supplies"]) |
                set(tr.weekly_totals) | set(tr.weekly_budgets))
    banner(f"{'Loaded' if choice=='load' else 'New'} user: {username}")
    return tr, cats

def modal_pick_category(cats):
    """
    Let the user pick an existing category or add a new one.
    """
    btns = [Button(c, (WIDTH//2, 180 + i*60)) for i, c in enumerate(cats)]
    add_btn = Button("+ New Category", (WIDTH//2, 180 + len(cats)*60))
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if add_btn.hit(ev.pos):
                    nm = modal_text("New category name:")
                    if nm:
                        nm = nm.capitalize()
                        cats.append(nm)
                        return nm
                for b in btns:
                    if b.hit(ev.pos):
                        return b.label
        draw_background_gradient()
        draw_glass_panel(pygame.Rect(220, 120, 460, 440))
        render_centered_text(font_title, "Select Category", (WIDTH//2, 160), ACCENT_COLOR, 32)
        for b in btns:
            b.draw()
        add_btn.draw()
        pygame.display.flip()
        clock.tick(FPS)

def prompt_budget(tracker, cat):
    """
    Ask for a positive weekly budget for a category.
    """
    while True:
        resp = modal_text(f"Weekly budget for '{cat}':")
        try:
            val = float(resp)
            assert val > 0
        except:
            banner("Enter a positive number", (255, 80, 80))
            continue
        tracker.weekly_budgets[cat] = val
        tracker.save_current_data()
        break

def flow_add_expense(tracker, cats):
    """
    Full flow: ask amount → category → (if needed) budget.
    """
    amt_s = modal_text("Expense amount:")
    try:
        amt = float(amt_s)
        assert amt > 0
    except:
        banner("Amount must be > 0", (255, 80, 80))
        return
    cat = modal_pick_category(cats)
    if cat not in tracker.weekly_totals:
        prompt_budget(tracker, cat)
    tracker.weekly_totals[cat] = tracker.weekly_totals.get(cat, 0) + amt
    tracker.save_current_data()
  
def main():
    """
    App entry point: build UI state and enter the loop.
    """
    tracker, cats = build_tracker()
    labels = [
        "Add Expense", "Set Budget", "Show Summary", "Reset Week",
        "Visualize Expenses", "Weekly PDF Report", "Expense Prediction"
    ]
    btn_positions = [
        (WIDTH//2 - 160 + (i % 2) * 320, 190 + (i // 2) * 80)
        for i in range(len(labels))
    ]
    buttons = [Button(lbl, pos) for lbl, pos in zip(labels, btn_positions)]
    exit_btn = Button("Exit", (WIDTH//2, 540))
    mode = "home"
    back_btn = None
    chart_img = None
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if mode == "home" and ev.type == pygame.MOUSEBUTTONDOWN:
                if exit_btn.hit(ev.pos):
                    pygame.quit()
                    sys.exit()
                for b in buttons:
                    if b.hit(ev.pos):
                        lbl = b.label
                        if lbl == "Add Expense":
                            flow_add_expense(tracker, cats)
                        elif lbl == "Set Budget":
                            prompt_budget(tracker, modal_pick_category(cats))
                        elif lbl == "Show Summary":
                            mode, back_btn = "summary", Button("Back", (WIDTH//2, 520))
                        elif lbl == "Reset Week":
                            tracker.reset_week()
                            tracker.weekly_budgets.clear()
                            tracker.save_current_data()
                            banner("Week reset.")
                        elif lbl == "Visualize Expenses":
                            fig = tracker.plotting()
                            fig.savefig("tmp.png")
                            plt.close(fig)
                            chart_img = pygame.image.load("tmp.png")
                            os.remove("tmp.png")
                            mode, back_btn = "chart", Button("Back", (WIDTH//2, 520))
                        elif lbl == "Weekly PDF Report":
                            tracker.creating_report_pdf()
                            banner("PDF saved.")
                        elif lbl == "Expense Prediction":
                            mode, back_btn = "prediction", Button("Back", (WIDTH//2, 520))
                        break
            if mode in ("summary", "chart", "prediction") and ev.type == pygame.MOUSEBUTTONDOWN:
                if back_btn and back_btn.hit(ev.pos):
                    mode, back_btn, chart_img = "home", None, None
        draw_background_gradient()
        pane, title = {
            "home":      ((140, 60, 680, 520),  "Weekly Expense Tracker"),
            "summary":   ((140, 40, 680, 540),  "Weekly Summary"),
            "chart":     ((50,  50, 800, 520),  "Weekly Expenses Chart"),
            "prediction":((140, 40, 680, 540),  "Expense Prediction")
        }[mode]
        rect = pygame.Rect(*pane)
        draw_glass_panel(rect)
        render_centered_text(font_title, title, (rect.centerx, rect.y + 40), ACCENT_COLOR)
        if mode == "home":
            render_centered_text(font_text, f"User: {tracker.username}", (rect.centerx, rect.y + 80))
            for b in buttons:
                b.draw()
            exit_btn.draw()
        elif mode == "summary":
            y = rect.y + 100
            cats_set = sorted(set(tracker.weekly_totals) | set(tracker.weekly_budgets))
            if not cats_set:
                render_centered_text(font_text, "No data.", (rect.centerx, y))
            for c in cats_set:
                spent = tracker.weekly_totals.get(c, 0.0)
                bud   = tracker.weekly_budgets.get(c)
                line = f"{c}: ${spent:.2f}" + (f" / ${bud:.2f}" if bud else "")
                font_text.render_to(win, (rect.x+30, y), line, WHITE)
                y += 30
            back_btn.draw()
        elif mode == "prediction":
            y = rect.y + 100
            if not tracker.history:
                render_centered_text(font_text, "No history.", (rect.centerx, y))
            for c, hist in tracker.history.items():
                arr = np.array(hist)
                low = max(0, arr.mean() - arr.std())
                high = arr.mean() + arr.std()
                line = f"{c}: ${low:.2f} - ${high:.2f}"
                font_text.render_to(win, (rect.x+30, y), line, WHITE)
                y += 30
            back_btn.draw()
        elif mode == "chart" and chart_img:
            win.blit(chart_img, chart_img.get_rect(center=rect.center))
            back_btn.draw()
        if notice_msg and pygame.time.get_ticks() - notice_time < notice_duration:
            y_banner = back_btn.rect.top - 20 if back_btn else exit_btn.rect.top - 20
            render_centered_text(font_text, notice_msg, (rect.centerx, y_banner), notice_color)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
