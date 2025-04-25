"""
interface.py – Pygame front-end for InteractiveExpenseTracker
"""
import sys
import os
import csv
import json
from typing import List, Tuple
from __future__ import annotations
import pygame
import pygame.freetype as ft
import matplotlib.pyplot as plt
import numpy as np
from InteractiveExpenseTracker import InteractiveExpenseTracker

WIDTH, HEIGHT = 900, 620
FPS = 60
GRADIENT_TOP = (40, 35, 90)
GRADIENT_BOTTOM = (15, 40, 60)
ACCENT_COLOR = (120, 180, 255)
WHITE = (245, 245, 245)
PANEL_ALPHA = 180
BUTTON_ALPHA = 200
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Weekly Expense Tracker")
clock = pygame.time.Clock()
FONT_TITLE: ft.Font = ft.SysFont(None, 46)
FONT_TEXT: ft.Font = ft.SysFont(None, 24)

def _lerp(c0: Tuple[int, int, int], c1: Tuple[int, int, int], t: float) -> Tuple[int, int, int]:
    """Return the linear interpolation between two RGB colours *c0* and *c1* at factor *t* (0–1)."""
    return tuple(int(a + (b - a) * t) for a, b in zip(c0, c1))

def draw_gradient() -> None:
    """Fill the entire screen with a vertical gradient background."""
    for y in range(HEIGHT):
        pygame.draw.line(screen, _lerp(GRADIENT_TOP, GRADIENT_BOTTOM, y / HEIGHT),
                         (0, y), (WIDTH, y))

def draw_glass(rect: pygame.Rect) -> None:
    """Draw a rounded, semi-transparent panel (“glass”) inside *rect*."""
    surf = pygame.Surface(rect.size, pygame.SRCALPHA)
    surf.fill((0, 0, 0, PANEL_ALPHA))
    pygame.draw.rect(surf, WHITE, surf.get_rect(), 1, border_radius=16)
    screen.blit(surf, rect.topleft)

def txt_center(font: ft.Font, txt: str, pos: Tuple[int, int],
               color: Tuple[int, int, int] = WHITE, size: int | None = None) -> None:
    """Render *txt* centered at *pos* using *font*."""
    if size is None:
        rect = font.get_rect(txt)
        rect.center = pos
        font.render_to(screen, rect.topleft, txt, color)
    else:
        rect = font.get_rect(txt, size=size)
        rect.center = pos
        font.render_to(screen, rect.topleft, txt, color, size=size)

class Button:
    """A clickable, rounded rectangle button with a hover accent."""

    def __init__(self, label: str, center: Tuple[int, int]) -> None:
        self.label = label
        self.rect = pygame.Rect(0, 0, 240, 56)
        self.rect.center = center

    def draw(self) -> None:
        """Render the button with hover feedback."""
        hover = self.rect.collidepoint(pygame.mouse.get_pos())
        color = ACCENT_COLOR if hover else WHITE

        surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        surf.fill((0, 0, 0, BUTTON_ALPHA + (40 if hover else 0)))
        pygame.draw.rect(surf, color, surf.get_rect(), 2, border_radius=14)
        screen.blit(surf, self.rect.topleft)

        txt_center(FONT_TEXT, self.label, self.rect.center, color, size=24)

    def hit(self, pos: Tuple[int, int]) -> bool:
        """Return *True* if *pos* (mouse coordinate) lies within the button."""
        return self.rect.collidepoint(pos)


class TextInput:
    """A single-line text-input box with a prompt and active focus border."""

    ACTIVE_COLOR = ACCENT_COLOR
    PASSIVE_COLOR = (160, 160, 160)

    def __init__(self, prompt: str, center: Tuple[int, int]) -> None:
        self.prompt = prompt
        self.text: str = ""
        self.active: bool = False
        self.box = pygame.Rect(0, 0, 340, 40)
        self.box.center = center

    def handle_event(self, ev: pygame.event.Event) -> None:
        """Process mouse/keyboard events to update cursor focus and text."""
        if ev.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.box.collidepoint(ev.pos)
        if ev.type == pygame.KEYDOWN and self.active:
            if ev.key == pygame.K_RETURN:
                self.active = False
            elif ev.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(ev.unicode) == 1 and ev.unicode.isprintable():
                    self.text += ev.unicode

    def draw(self) -> None:
        """Render the prompt and current input inside the box."""
        color = self.ACTIVE_COLOR if self.active else self.PASSIVE_COLOR
        pygame.draw.rect(screen, (0, 0, 0, 200), self.box, border_radius=8)
        pygame.draw.rect(screen, color, self.box, 2, border_radius=8)
        txt_center(FONT_TEXT, self.prompt, (self.box.centerx, self.box.y - 15))
        FONT_TEXT.render_to(screen, (self.box.x + 10, self.box.y + 8),
                            self.text or " ", WHITE)

def prompt_text(prompt: str) -> str:
    """Blocking prompt that asks the user for text input."""
    inp = TextInput(prompt, (WIDTH // 2, HEIGHT // 2))
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            inp.handle_event(ev)
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN and not inp.active:
                return inp.text.strip()
        draw_gradient()
        draw_glass(pygame.Rect(200, 200, 500, 200))
        inp.draw()
        pygame.display.flip()
        clock.tick(FPS)
        
def prompt_load_or_new(username: str) -> str:
    """Modal dialog asking whether to **load** existing user data or create a **new** account."""
    title_y, sub_y = 250, 300
    load_btn = Button("Load Existing Data", (WIDTH // 2, sub_y + 60))
    new_btn = Button("Create New Account", (WIDTH // 2, sub_y + 130))
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if load_btn.hit(ev.pos):
                    return "load"
                if new_btn.hit(ev.pos):
                    return "new"
        draw_gradient()
        draw_glass(pygame.Rect(200, 220, 500, 250))
        txt_center(FONT_TITLE, f"User '{username}' found",
                   (WIDTH // 2, title_y), ACCENT_COLOR, size=32)
        txt_center(FONT_TEXT, "Choose an option:", (WIDTH // 2, sub_y), WHITE)
        load_btn.draw()
        new_btn.draw()
        pygame.display.flip()
        clock.tick(FPS)

def init_tracker() -> Tuple[InteractiveExpenseTracker, List[str], str]:
    """Prompt for username, decide whether to load or create a profile, and instantiate `InteractiveExpenseTracker` without triggering its interactive input prompts."""
    raw = prompt_text("Enter your username:")
    if not raw:
        pygame.quit(); sys.exit()
    username = raw.capitalize()
    choice = "load" if os.path.exists(f"data_{username}.json") else "new"
    if choice == "load":
        choice = prompt_load_or_new(username)
    if choice == "new":
        base, n = username, 1
        while os.path.exists(f"data_{base}{n}.json"):
            n += 1
        username = base if n == 1 else f"{base}{n}"
    tr = InteractiveExpenseTracker.__new__(InteractiveExpenseTracker)
    tr.username = username
    tr.data_file = f"data_{username}.json"
    tr.history_file = f"history_{username}.csv"
    tr.weekly_totals, tr.weekly_budgets, tr.history = {}, {}, {}
    tr.current_week, tr.active = 1, 1
    try:
        with open(tr.history_file) as f:
            rows = [r for r in csv.reader(f) if r]
            if rows:
                tr.current_week = int(rows[0][0])
            for row in rows[1:]:
                tr.history[row[0]] = [float(x) for x in row[1:]]
    except Exception:
        with open(tr.history_file, "w", newline="") as f:
            csv.writer(f).writerow([tr.current_week])
    if choice == "load":
        with open(tr.data_file) as f:
            d = json.load(f)
            tr.weekly_totals = d.get("weekly_totals", {})
            tr.weekly_budgets = d.get("weekly_budgets", {})
            tr.current_week = d.get("current_week", tr.current_week)
    cats = ["Food", "Entertainment", "Transport", "School Supplies"]
    for c in list(tr.weekly_totals) + list(tr.weekly_budgets):
        if c not in cats:
            cats.append(c)
    notice = f"Loaded data for {username}" if choice == "load" else f"New user: {username}"
    return tr, cats, notice

def choose_category(cats: List[str]) -> str:
    """Display a modal list of existing categories plus a “+ New Category” button. Allows adding a new category inline."""
    btns = [Button(c, (WIDTH // 2, 200 + i * 60)) for i, c in enumerate(cats)]
    new_btn = Button("+ New Category", (WIDTH // 2, 200 + len(cats) * 60))
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if new_btn.hit(ev.pos):
                    nm = prompt_text("New category name:")
                    if nm:
                        nm = nm.capitalize()
                        cats.append(nm)
                        return nm
                for b in btns:
                    if b.hit(ev.pos):
                        return b.label
        draw_gradient()
        draw_glass(pygame.Rect(220, 120, 460, 420))
        txt_center(FONT_TITLE, "Select Category", (WIDTH // 2, 150), ACCENT_COLOR)
        for b in btns:
            b.draw()
        new_btn.draw()
        pygame.display.flip()
        clock.tick(FPS)
        
def main_gui() -> None:
    """Launch the full Pygame front-end and handle every interaction loop."""
    tr, cats, notice = init_tracker()
    labels = [
        "Add Expense", "Set Budget", "Show Summary", "Reset Week",
        "Visualize Expenses", "Weekly PDF Report", "Expense Prediction"
    ]
    col_x = [WIDTH // 2 - 160, WIDTH // 2 + 160]
    buttons = [Button(lbl, (col_x[i % 2], 190 + (i // 2) * 80))
               for i, lbl in enumerate(labels)]
    exit_btn = Button("Exit", (WIDTH // 2, 540))
    pane_main = pygame.Rect(140, 60, 680, 520)
    pane_info = pygame.Rect(140, 40, 680, 540)
    pane_chart = pygame.Rect(50, 50, 800, 520)
    mode = "home"
    inputs: List[TextInput] = []
    chart_surf = None
    back_btn = None
    note, note_time, note_color = notice, pygame.time.get_ticks(), WHITE
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE and mode != "home":
                mode, inputs, chart_surf, back_btn = "home", [], None, None
            if mode == "home" and ev.type == pygame.MOUSEBUTTONDOWN:
                if exit_btn.hit(ev.pos):
                    pygame.quit(); sys.exit()
                for b in buttons:
                    if b.hit(ev.pos):
                        sel = b.label
                        if sel == "Add Expense":
                            mode = "add"
                            inputs = [
                                TextInput("Amount (number)", (WIDTH // 2, 380)),
                                TextInput("Notes (optional)", (WIDTH // 2, 460))
                            ]
                        elif sel == "Set Budget":
                            mode = "budget"
                            inputs = [TextInput("Budget Amount", (WIDTH // 2, 380))]
                        elif sel == "Show Summary":
                            mode, back_btn = "summary", Button("Back", (WIDTH // 2, 520))
                        elif sel == "Reset Week":
                            if tr.weekly_totals:
                                tr.reset_week()
                                note = f"Week {tr.current_week - 1} cleared."
                            else:
                                note = "Weekly totals already empty."
                            note_color, note_time = WHITE, pygame.time.get_ticks()
                        elif sel == "Visualize Expenses":
                            fig = tr.plotting()
                            fig.savefig("tmp.png")
                            plt.close(fig)
                            chart_surf = pygame.image.load("tmp.png")
                            os.remove("tmp.png")
                            mode, back_btn = "chart", Button("Back", (WIDTH // 2, 520))
                        elif sel == "Weekly PDF Report":
                            tr.creating_report_pdf()
                            note = f"Saved weekly_report_{tr.username}.pdf"
                            note_color, note_time = WHITE, pygame.time.get_ticks()
                        elif sel == "Expense Prediction":
                            mode, back_btn = "prediction", Button("Back", (WIDTH // 2, 520))
                        break
            if mode in ("add", "budget"):
                for box in inputs:
                    box.handle_event(ev)
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_RETURN and not any(b.active for b in inputs):
                    if mode == "add":
                        try:
                            amount = float(inputs[0].text)
                        except ValueError:
                            note = "Invalid amount!"
                            note_color, note_time = (255, 80, 80), pygame.time.get_ticks()
                            mode, inputs = "home", []
                            continue
                        category = choose_category(cats)
                        _ = inputs[1].text
                        tr.add_expense(amount, category)
                        if category not in cats:
                            cats.append(category)
                    else:
                        category = choose_category(cats)
                        try:
                            val = float(inputs[0].text)
                            if val > 0:
                                tr.weekly_budgets[category] = val
                                tr.save_current_data()
                        except ValueError:
                            pass
                    mode, inputs = "home", []
            if mode in ("summary", "prediction", "chart") and ev.type == pygame.MOUSEBUTTONDOWN:
                if back_btn and back_btn.hit(ev.pos):
                    mode, back_btn, chart_surf = "home", None, None
        draw_gradient()
        pane, title = {
            "home": (pane_main, "Weekly Expense Tracker"),
            "add": (pane_main, "Add Expense"),
            "budget": (pane_main, "Set Budget"),
            "summary": (pane_info, "Weekly Summary"),
            "prediction": (pane_info, "Expense Prediction"),
            "chart": (pane_chart, "Weekly Expenses Chart"),
        }[mode]
        draw_glass(pane)
        txt_center(FONT_TITLE, title, (pane.centerx, pane.y + 40), ACCENT_COLOR)
        if mode == "home":
            txt_center(FONT_TEXT, f"User: {tr.username}", (pane.centerx, pane.y + 80))
            for b in buttons:
                b.draw()
            exit_btn.draw()
        elif mode in ("add", "budget"):
            for box in inputs:
                box.draw()
            txt_center(FONT_TEXT, "Press Enter to confirm", (pane.centerx, pane.bottom - 40))
        elif mode == "summary":
            y = pane.y + 100
            cats_sorted = sorted(set(tr.weekly_totals) | set(tr.weekly_budgets))
            if not cats_sorted:
                txt_center(FONT_TEXT, "No data this week.", (pane.centerx, y))
            for cat in cats_sorted:
                spent = tr.weekly_totals.get(cat, 0.0)
                bud = tr.weekly_budgets.get(cat)
                line = f"{cat}: ${spent:.2f}" if bud is None else f"{cat}: ${spent:.2f} / ${bud:.2f}"
                FONT_TEXT.render_to(screen, (pane.x + 30, y), line, WHITE)
                y += 30
            back_btn.draw()
        elif mode == "prediction":
            y = pane.y + 100
            if not tr.history:
                txt_center(FONT_TEXT, "No history available.", (pane.centerx, y))
            for cat, hist in tr.history.items():
                arr = np.array(hist)
                mean, std = arr.mean(), arr.std()
                line = f"{cat}: ${max(0, mean - std):.2f} – ${mean + std:.2f}"
                FONT_TEXT.render_to(screen, (pane.x + 30, y), line, WHITE)
                y += 30
            back_btn.draw()
        elif mode == "chart" and chart_surf:
            screen.blit(chart_surf, chart_surf.get_rect(center=pane.center))
            back_btn.draw()
        if note and pygame.time.get_ticks() - note_time < 3000:
            if back_btn:
                notice_y = back_btn.rect.top - 20
            elif mode == "home":
                notice_y = exit_btn.rect.top - 20
            else:
                notice_y = pane.bottom - 40
            txt_center(FONT_TEXT, note, (pane.centerx, notice_y), note_color)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main_gui()
