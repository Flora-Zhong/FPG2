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
CLR_GRADIENT_TOP = (40, 35, 90)
CLR_GRADIENT_BOTTOM = (15, 40, 60)
CLR_ACCENT = (120, 180, 255)
CLR_WHITE = (245, 245, 245)
ALPHA_PANEL  = 180
ALPHA_BUTTON = 200
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Weekly Expense Tracker")
CLOCK = pygame.time.Clock()
F_TITLE = ft.SysFont(None, 46)
F_TEXT  = ft.SysFont(None, 24)

def lerp_rgb(color_a: tuple[int, int, int],
             color_b: tuple[int, int, int],
             t: float) -> tuple[int, ...]:
    """
    Linear-interpolate between two RGB tuples.
    """
    return tuple(int(a + (b - a) * t) for a, b in zip(color_a, color_b))

def draw_background_gradient() -> None:
    """
    Paint a vertical gradient across the entire window.
    """
    for y in range(HEIGHT):
        pygame.draw.line(
            WIN,
            lerp_rgb(CLR_GRADIENT_TOP, CLR_GRADIENT_BOTTOM, y / HEIGHT),
            (0, y), (WIDTH, y)
        )

def draw_glass_panel(rect: pygame.Rect) -> None:
    """
    Draw a semi-transparent, rounded glass panel.
    """
    surface = pygame.Surface(rect.size, pygame.SRCALPHA)
    surface.fill((0, 0, 0, ALPHA_PANEL))
    pygame.draw.rect(surface, CLR_WHITE, surface.get_rect(),
                     width=1, border_radius=16)
    WIN.blit(surface, rect.topleft)

def render_centered_text(font: ft.Font,
                         text: str,
                         pos: tuple[int, int],
                         color: tuple[int, int, int] = CLR_WHITE,
                         size: int | None = None) -> None:
    """
    Render *text* centred at *pos* using *font*.
    """
    rect = font.get_rect(text, size=size) if size else font.get_rect(text)
    rect.center = pos

    if size is None:
        font.render_to(WIN, rect.topleft, text, color)  # ← 不传 size
    else:
        font.render_to(WIN, rect.topleft, text, color, size=size)

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
        col   = CLR_ACCENT if hover else CLR_WHITE
        surf  = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        surf.fill((0, 0, 0, ALPHA_BUTTON + (40 if hover else 0)))
        pygame.draw.rect(surf, col, surf.get_rect(), 2, border_radius=14)
        WIN.blit(surf, self.rect.topleft)
        render_centered_text(F_TEXT, self.label, self.rect.center, col, 24)

    def hit(self, pos: tuple[int, int]) -> bool:
        """Return True if *pos* lies inside the button."""
        return self.rect.collidepoint(pos)

class TextInput:
    """
    Single-line text box with prompt and active border.
    """
    COL_ACTIVE  = CLR_ACCENT
    COL_PASSIVE = (160, 160, 160)

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
            elif len(event.unicode) == 1 and event.unicode.isprintable():
                self.text += event.unicode

    def draw(self) -> None:
        """
        Render prompt label and current input text.
        """
        border = self.COL_ACTIVE if self.active else self.COL_PASSIVE
        pygame.draw.rect(WIN, (0, 0, 0, 200), self.rect, border_radius=8)
        pygame.draw.rect(WIN, border, self.rect, 2, border_radius=8)
        render_centered_text(F_TEXT, self.prompt,
                             (self.rect.centerx, self.rect.y - 15))
        F_TEXT.render_to(WIN, (self.rect.x + 10, self.rect.y + 8),
                         self.text or " ", CLR_WHITE)

NOTICE_MSG  = ""
NOTICE_COL  = CLR_WHITE
NOTICE_TIME = 0
NOTICE_MS   = 3000

def banner(msg: str, col: tuple[int, int, int] = CLR_WHITE) -> None:
    """
    Display a transient notice banner (3 seconds).
    """
    global NOTICE_MSG, NOTICE_COL, NOTICE_TIME
    NOTICE_MSG, NOTICE_COL, NOTICE_TIME = msg, col, pygame.time.get_ticks()

def modal_text(prompt: str) -> str:
    """Blocking text prompt; returns user input after pressing Enter."""
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

def modal_load_or_new(root: str) -> str:
    """
    Offer “Load Existing Data” versus “Create New Account”.
    """
    y0, y1 = 250, 300
    b_load = Button("Load Existing Data", (WIDTH//2, y1 + 60))
    b_new  = Button("Create New Account", (WIDTH//2, y1 + 130))
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if b_load.hit(ev.pos):
                    return "load"
                if b_new.hit(ev.pos):
                    return "new"
        draw_background_gradient()
        draw_glass_panel(pygame.Rect(200, 220, 500, 250))
        render_centered_text(F_TITLE, f"User '{root}' found",
                             (WIDTH//2, y0), CLR_ACCENT, 32)
        render_centered_text(F_TEXT, "Choose an option:",
                             (WIDTH//2, y1))
        b_load.draw(); b_new.draw()
        pygame.display.flip(); CLOCK.tick(FPS)

def split_root_suffix(name: str) -> tuple[str, int]:
    """
    Split *name* into (root, suffix_int).
    """
    i = len(name)
    while i > 0 and name[i-1].isdigit():
        i -= 1
    root = name[:i] if i else name
    suffix = int(name[i:]) if name[i:] else 0
    return root, suffix

def next_unused_suffix(root: str, variants: list[str]) -> int:
    """
    Compute the lowest positive integer suffix not yet used for *root*.
    """
    used = {split_root_suffix(v)[1] for v in variants if split_root_suffix(v)[0] == root}
    n = 1
    while n in used:
        n += 1
    return n

def build_tracker() -> tuple[InteractiveExpenseTracker, list[str]]:
    """
    Handle username logic, then construct & return an uninitialised Tracker instance plus the initial category list.
    """
    raw = modal_text("Enter your username:")
    if raw == "":
        pygame.quit(); sys.exit()
    root, _ = split_root_suffix(raw.capitalize())
    variants = [f[5:-5] for f in os.listdir('.')
                if f.startswith(f"data_{root}") and f.endswith(".json")]
    choice = modal_load_or_new(root) if variants else "new"
    if choice == "load":
        username = raw.capitalize() if raw.capitalize() in variants else root
    else:
        username = (f"{root}{next_unused_suffix(root, variants)}"
                    if root in variants else root)
        if username != root:
            banner(f"Your username is set to {username}!")
    tr = InteractiveExpenseTracker.__new__(InteractiveExpenseTracker)
    tr.username = username
    tr.data_file    = f"data_{username}.json"
    tr.history_file = f"history_{username}.csv"
    tr.weekly_totals, tr.weekly_budgets, tr.history = {}, {}, {}
    tr.current_week, tr.active = 1, 1
    try:
        with open(tr.history_file) as f:
            rows = [r for r in csv.reader(f) if r]
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
                tr.weekly_totals  = d.get("weekly_totals", {})
                tr.weekly_budgets = d.get("weekly_budgets", {})
                tr.current_week   = d.get("current_week", tr.current_week)
        except FileNotFoundError:
            pass
    defaults = ["Food", "Entertainment", "Transport", "School Supplies"]
    cats = list(set(defaults) | set(tr.weekly_totals) | set(tr.weekly_budgets))
    banner(f"Loaded data for {username}" if choice == "load"
           else f"New user: {username}")
    return tr, cats

def modal_pick_category(cats: list[str]) -> str:
    """
    Modal list of categories with “+ New Category”.
    """
    btns = [Button(c, (WIDTH//2, 200+i*60)) for i, c in enumerate(cats)]
    b_new = Button("+ New Category", (WIDTH//2, 200+len(cats)*60))
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if b_new.hit(ev.pos):
                    nm = modal_text("New category name:")
                    if nm:
                        nm = nm.capitalize()
                        cats.append(nm)
                        return nm
                for b in btns:
                    if b.hit(ev.pos):
                        return b.label
        draw_background_gradient()
        draw_glass_panel(pygame.Rect(220, 120, 460, 420))
        render_centered_text(F_TITLE, "Select Category",
                             (WIDTH//2, 150), CLR_ACCENT)
        for b in btns:
            b.draw()
        b_new.draw()
        pygame.display.flip(); CLOCK.tick(FPS)

def prompt_budget(tracker: InteractiveExpenseTracker,
                  cat: str) -> None:
    """
    Prompt the user for a positive numeric budget for *cat*.
    """
    while True:
        inp = modal_text(f"Weekly budget for '{cat}':")
        try:
            val = float(inp)
            assert val > 0
        except ValueError:
            banner("Please enter a number.", (255, 80, 80))
            continue
        except AssertionError:
            banner("Budget must be greater than 0.", (255, 80, 80))
            continue
        tracker.weekly_budgets[cat] = val
        tracker.save_current_data()
        break

def flow_add_expense(tracker: InteractiveExpenseTracker,
                     cats: list[str]) -> None:
    """
    Run the “Add Expense” flow: amount → category → (optional) budget.
    """
    try:
        amt = float(modal_text("Expense amount:"))
        assert amt > 0
    except ValueError:
        banner("Amount must be a number.", (255, 80, 80))
        return
    except AssertionError:
        banner("Amount must be greater than 0.", (255, 80, 80))
        return
    cat = modal_pick_category(cats)
    if cat not in tracker.weekly_totals:
        prompt_budget(tracker, cat)
    tracker.weekly_totals[cat] = tracker.weekly_totals.get(cat, 0.0) + amt
    tracker.save_current_data()

def main():
    """Launch the Pygame UI and run indefinitely."""
    tracker, cats = build_tracker()
    labels = ["Add Expense", "Set Budget", "Show Summary", "Reset Week",
              "Visualize Expenses", "Weekly PDF Report", "Expense Prediction"]
    col = [WIDTH//2 - 160, WIDTH//2 + 160]
    btns = [Button(l, (col[i%2], 190+(i//2)*80)) for i, l in enumerate(labels)]
    exit_btn = Button("Exit", (WIDTH//2, 540))
    p_main  = pygame.Rect(140, 60, 680, 520)
    p_info  = pygame.Rect(140, 40, 680, 540)
    p_chart = pygame.Rect(50,  50, 800, 520)
    mode, back, chart = "home", None, None
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and mode != "home":
                mode, back, chart = "home", None, None
            if mode == "home" and ev.type == pygame.MOUSEBUTTONDOWN:
                if exit_btn.hit(ev.pos):
                    pygame.quit(); sys.exit()
                for b in btns:
                    if b.hit(ev.pos):
                        label = b.label
                        if label == "Add Expense":
                            flow_add_expense(tracker, cats)
                        elif label == "Set Budget":
                            prompt_budget(tracker, modal_pick_category(cats))
                        elif label == "Show Summary":
                            mode, back = "summary", Button("Back", (WIDTH//2, 520))
                        elif label == "Reset Week":
                            tracker.reset_week()
                            tracker.weekly_budgets.clear()
                            tracker.save_current_data()
                            banner("Week reset.")
                        elif label == "Visualize Expenses":
                            fig = tracker.plotting()
                            fig.savefig("tmp.png"); plt.close(fig)
                            chart = pygame.image.load("tmp.png"); os.remove("tmp.png")
                            mode, back = "chart", Button("Back", (WIDTH//2, 520))
                        elif label == "Weekly PDF Report":
                            tracker.creating_report_pdf()
                            banner("PDF saved.")
                        elif label == "Expense Prediction":
                            mode, back = "prediction", Button("Back", (WIDTH//2, 520))
                        break
            if mode in ("summary", "prediction", "chart") and ev.type == pygame.MOUSEBUTTONDOWN:
                if back and back.hit(ev.pos):
                    mode, back, chart = "home", None, None
        draw_background_gradient()
        pane, title = {
            "home"      : (p_main,  "Weekly Expense Tracker"),
            "summary"   : (p_info,  "Weekly Summary"),
            "prediction": (p_info,  "Expense Prediction"),
            "chart"     : (p_chart, "Weekly Expenses Chart")
        }[mode]
        draw_glass_panel(pane)
        render_centered_text(F_TITLE, title, (pane.centerx, pane.y+40), CLR_ACCENT)
        if mode == "home":
            render_centered_text(F_TEXT, f"User: {tracker.username}",
                                 (pane.centerx, pane.y+80))
            for b in btns:
                b.draw()
            exit_btn.draw()
        elif mode == "summary":
            y = pane.y + 100
            all_cats = sorted(set(tracker.weekly_totals) | set(tracker.weekly_budgets))
            if not all_cats:
                render_centered_text(F_TEXT, "No data.", (pane.centerx, y))
            for c in all_cats:
                spent = tracker.weekly_totals.get(c, 0.0)
                bud   = tracker.weekly_budgets.get(c)
                line  = f"{c}: ${spent:.2f}" if bud is None else f"{c}: ${spent:.2f} / ${bud:.2f}"
                F_TEXT.render_to(WIN, (pane.x+30, y), line, CLR_WHITE); y += 30
            back.draw()
        elif mode == "prediction":
            y = pane.y + 100
            if not tracker.history:
                render_centered_text(F_TEXT, "No history.", (pane.centerx, y))
            for c, hist in tracker.history.items():
                arr = np.array(hist)
                mean, std = arr.mean(), arr.std()
                pred_line = f"{c}: ${max(0, mean-std):.2f}-{mean+std:.2f}"
                F_TEXT.render_to(WIN, (pane.x+30, y), pred_line, CLR_WHITE); y += 30
            back.draw()
        elif mode == "chart" and chart:
            WIN.blit(chart, chart.get_rect(center=pane.center))
            back.draw()
        if NOTICE_MSG and pygame.time.get_ticks() - NOTICE_TIME < NOTICE_MS:
            y_banner = back.rect.top-20 if back else exit_btn.rect.top-20 if mode == "home" else pane.bottom-40
            render_centered_text(F_TEXT, NOTICE_MSG, (pane.centerx, y_banner), NOTICE_COL)
        pygame.display.flip()
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()
