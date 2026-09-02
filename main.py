import random
import pygame

class AnimatedPiece:
    def __init__(self, color, start_pos, end_pos, duration_frames=12, on_complete=None):
        self.color = color
        self.start_x, self.start_y = start_pos
        self.end_x, self.end_y = end_pos
        self.current_x = float(self.start_x)
        self.current_y = float(self.start_y)
        self.progress = 0.0
        self.step = 1.0 / max(1, duration_frames)
        self.on_complete = on_complete
        self.is_active = True

    def update(self):
        if not self.is_active:
            return

        self.progress += self.step
        if self.progress >= 1.0:
            self.progress = 1.0
            self.current_x = float(self.end_x)
            self.current_y = float(self.end_y)
            self.is_active = False
            if self.on_complete:
                self.on_complete()
        else:
            t = self.progress
            ease_t = 1 - (1 - t) * (1 - t)
            self.current_x = self.start_x + (self.end_x - self.start_x) * ease_t
            self.current_y = self.start_y + (self.end_y - self.start_y) * ease_t

    def draw(self, screen):
        radius = 20
        pos = (int(self.current_x), int(self.current_y))
        pygame.draw.circle(screen, self.color, pos, radius)
        outline_color = (0, 0, 0) if self.color == WHITE else (255, 255, 255)
        pygame.draw.circle(screen, outline_color, pos, radius, 2)


# --- 1. CONSTANTS ---
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 650

NAVY_FELT = (9, 9, 12)
BYU_ROYAL = (0, 102, 204)
WHITE = (240, 240, 240)
WOOD_FRAME = (60, 40, 30)
HIGHLIGHT_GREEN = (0, 255, 128)

BAR_WIDTH = 40
POINT_WIDTH = 50
FRAME_THICKNESS = 12

pygame.mixer.init()

def load_sound_safe(filename):
    try:
        return pygame.mixer.Sound(filename)
    except Exception:
        return None

roll_sound = load_sound_safe("ElevenLabs_Rolling_dice_in_a_tabletop_game,_immersive_ambiance.mp3")
hit_sound = load_sound_safe("ElevenLabs_A_crisp_snap_as_a_piece_is_placed_on_the_board,_followed_by_a_smooth_voice_saying___Strategic_placem.mp3")
turn_sound = load_sound_safe("ElevenLabs_Short_mechanical_switch_click_sound_effect,_realistic_light_switch_toggle,_clean_tactile_snap,_close.mp3")
win_sound = load_sound_safe("ElevenLabs_A_short_victory_sound_for_a_strategic_card_game_using_a_single_muted_trumpet_playing_a_simple_ascend.mp3")

def play_sound(sound, enabled=True):
    if sound and enabled:
        sound.play()


# --- 2. UI SCREEN DRAWING FUNCTIONS ---
def draw_menu_screen(screen, logo_left=None, logo_right=None):
    screen.fill(NAVY_FELT)

    if logo_left:
        screen.blit(logo_left, (40, 30))
    if logo_right:
        screen.blit(logo_right, (SCREEN_WIDTH - 170, 30))

    font_title = pygame.font.SysFont("Arial", 42, bold=True)
    title_surf = font_title.render("BYU CUSTOM BACKGAMMON", True, WHITE)
    title_rect = title_surf.get_rect(center=(SCREEN_WIDTH // 2, 80))
    screen.blit(title_surf, title_rect)

    mouse_pos = pygame.mouse.get_pos()

    pvp_rect = pygame.Rect(SCREEN_WIDTH // 2 - 175, 200, 350, 65)
    pvp_hover = pvp_rect.collidepoint(mouse_pos)
    pygame.draw.rect(screen, BYU_ROYAL if pvp_hover else WOOD_FRAME, pvp_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, pvp_rect, 3, border_radius=10)

    font_btn = pygame.font.SysFont("Arial", 26, bold=True)
    pvp_text = font_btn.render("Player vs Player (PvP)", True, WHITE)
    screen.blit(pvp_text, pvp_text.get_rect(center=pvp_rect.center))

    pvc_rect = pygame.Rect(SCREEN_WIDTH // 2 - 175, 300, 350, 65)
    pvc_hover = pvc_rect.collidepoint(mouse_pos)
    pygame.draw.rect(screen, BYU_ROYAL if pvc_hover else WOOD_FRAME, pvc_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, pvc_rect, 3, border_radius=10)

    pvc_text = font_btn.render("Player vs Computer (PvC)", True, WHITE)
    screen.blit(pvc_text, pvc_text.get_rect(center=pvc_rect.center))

    font_sub = pygame.font.SysFont("Arial", 18)
    sub_surf = font_sub.render("Click a mode to play | Press 'M' in-game to return here", True, (180, 180, 180))
    screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 430)))

    return pvp_rect, pvc_rect


def draw_difficulty_screen(screen):
    screen.fill(NAVY_FELT)

    font_title = pygame.font.SysFont("Arial", 40, bold=True)
    title_surf = font_title.render("SELECT AI DIFFICULTY", True, WHITE)
    screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 140)))

    mouse_pos = pygame.mouse.get_pos()

    easy_rect = pygame.Rect(SCREEN_WIDTH // 2 - 175, 240, 350, 65)
    e_hover = easy_rect.collidepoint(mouse_pos)
    pygame.draw.rect(screen, BYU_ROYAL if e_hover else WOOD_FRAME, easy_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, easy_rect, 3, border_radius=10)

    font_btn = pygame.font.SysFont("Arial", 24, bold=True)
    e_text = font_btn.render("Easy (Greedy / Casual)", True, WHITE)
    screen.blit(e_text, e_text.get_rect(center=easy_rect.center))

    hard_rect = pygame.Rect(SCREEN_WIDTH // 2 - 175, 340, 350, 65)
    h_hover = hard_rect.collidepoint(mouse_pos)
    pygame.draw.rect(screen, BYU_ROYAL if h_hover else WOOD_FRAME, hard_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, hard_rect, 3, border_radius=10)

    h_text = font_btn.render("Hard (Strategic / Risk-Aware)", True, WHITE)
    screen.blit(h_text, h_text.get_rect(center=hard_rect.center))

    return easy_rect, hard_rect


def draw_color_select_screen(screen):
    screen.fill(NAVY_FELT)

    font_title = pygame.font.SysFont("Arial", 40, bold=True)
    title_surf = font_title.render("CHOOSE YOUR SIDE", True, WHITE)
    screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 140)))

    mouse_pos = pygame.mouse.get_pos()

    white_rect = pygame.Rect(SCREEN_WIDTH // 2 - 175, 240, 350, 65)
    w_hover = white_rect.collidepoint(mouse_pos)
    pygame.draw.rect(screen, (80, 80, 80) if w_hover else (40, 40, 40), white_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, white_rect, 3, border_radius=10)

    font_btn = pygame.font.SysFont("Arial", 26, bold=True)
    w_text = font_btn.render("Play as White (Goes First)", True, WHITE)
    screen.blit(w_text, w_text.get_rect(center=white_rect.center))

    blue_rect = pygame.Rect(SCREEN_WIDTH // 2 - 175, 340, 350, 65)
    b_hover = blue_rect.collidepoint(mouse_pos)
    pygame.draw.rect(screen, BYU_ROYAL if b_hover else WOOD_FRAME, blue_rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, blue_rect, 3, border_radius=10)

    b_text = font_btn.render("Play as BYU Royal (Blue)", True, WHITE)
    screen.blit(b_text, b_text.get_rect(center=blue_rect.center))

    return white_rect, blue_rect


def draw_pause_screen(screen, sound_enabled, show_moves):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    font_title = pygame.font.SysFont("Arial", 48, bold=True)
    title_surf = font_title.render("GAME PAUSED", True, WHITE)
    screen.blit(title_surf, title_surf.get_rect(center=(SCREEN_WIDTH // 2, 140)))

    font_btn = pygame.font.SysFont("Arial", 22, bold=True)
    mouse_pos = pygame.mouse.get_pos()

    sound_rect = pygame.Rect(SCREEN_WIDTH // 2 - 160, 230, 320, 50)
    sound_bg = BYU_ROYAL if sound_rect.collidepoint(mouse_pos) else WOOD_FRAME
    pygame.draw.rect(screen, sound_bg, sound_rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, sound_rect, 2, border_radius=8)
    s_txt = font_btn.render(f"Sound FX: {'ON' if sound_enabled else 'OFF'}", True, WHITE)
    screen.blit(s_txt, s_txt.get_rect(center=sound_rect.center))

    moves_rect = pygame.Rect(SCREEN_WIDTH // 2 - 160, 300, 320, 50)
    moves_bg = BYU_ROYAL if moves_rect.collidepoint(mouse_pos) else WOOD_FRAME
    pygame.draw.rect(screen, moves_bg, moves_rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, moves_rect, 2, border_radius=8)
    m_txt = font_btn.render(f"Show Moves: {'ON' if show_moves else 'OFF'}", True, WHITE)
    screen.blit(m_txt, m_txt.get_rect(center=moves_rect.center))

    font_sub = pygame.font.SysFont("Arial", 20)
    sub_surf = font_sub.render("Press 'P' or 'ESC' to Resume  |  Press 'M' for Main Menu  |  'R' to Reset", True, (200, 200, 200))
    screen.blit(sub_surf, sub_surf.get_rect(center=(SCREEN_WIDTH // 2, 400)))

    return sound_rect, moves_rect


def draw_undo_button(screen, start_x, board_total_width, can_undo):
    rect = pygame.Rect(start_x + board_total_width + 12, 20, 82, 32)
    mouse_pos = pygame.mouse.get_pos()

    if can_undo:
        bg_color = BYU_ROYAL if rect.collidepoint(mouse_pos) else WOOD_FRAME
        text_color = WHITE
    else:
        bg_color = (40, 40, 45)
        text_color = (100, 100, 100)

    pygame.draw.rect(screen, bg_color, rect, border_radius=6)
    pygame.draw.rect(screen, text_color, rect, 2, border_radius=6)

    font = pygame.font.SysFont("Arial", 14, bold=True)
    txt = font.render("UNDO", True, text_color)
    screen.blit(txt, txt.get_rect(center=rect.center))

    return rect


def calculate_pip_counts(board_state, bar_state):
    white_pips = sum(count * (24 - i) for i, count in enumerate(board_state) if count > 0) + (bar_state[0] * 24)
    blue_pips = sum(abs(count) * (i + 1) for i, count in enumerate(board_state) if count < 0) + (bar_state[1] * 24)
    return white_pips, blue_pips


def draw_pip_counter(screen, board_state, bar_state, start_x, board_total_width):
    white_pips, blue_pips = calculate_pip_counts(board_state, bar_state)

    box_x = start_x + board_total_width + 12
    box_y = 65
    box_w = 82
    box_h = 105

    rect = pygame.Rect(box_x, box_y, box_w, box_h)
    pygame.draw.rect(screen, WOOD_FRAME, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)

    font_hdr = pygame.font.SysFont("Arial", 12, bold=True)
    hdr_surf = font_hdr.render("PIPS", True, (200, 200, 200))
    screen.blit(hdr_surf, hdr_surf.get_rect(center=(box_x + box_w // 2, box_y + 16)))

    font_val = pygame.font.SysFont("Arial", 14, bold=True)

    w_label = font_val.render(f"W: {white_pips}", True, WHITE)
    screen.blit(w_label, w_label.get_rect(center=(box_x + box_w // 2, box_y + 45)))

    b_label = font_val.render(f"B: {blue_pips}", True, (100, 180, 255))
    screen.blit(b_label, b_label.get_rect(center=(box_x + box_w // 2, box_y + 75)))


# --- 3. BOARD & GAMEPLAY DRAWING FUNCTIONS ---
def draw_board(screen, logo_left=None, logo_right=None):
    screen.fill((0, 0, 0))

    board_total_width = (POINT_WIDTH * 12) + BAR_WIDTH + (FRAME_THICKNESS * 2)
    start_x = (SCREEN_WIDTH - board_total_width) // 2

    pygame.draw.rect(screen, NAVY_FELT, (start_x, 0, board_total_width, SCREEN_HEIGHT))
    pygame.draw.rect(screen, WOOD_FRAME, (start_x, 0, board_total_width, SCREEN_HEIGHT), FRAME_THICKNESS)

    bar_x = start_x + (POINT_WIDTH * 6) + FRAME_THICKNESS
    pygame.draw.rect(screen, WOOD_FRAME, (bar_x, 0, BAR_WIDTH, SCREEN_HEIGHT))

    for i in range(12):
        x = start_x + FRAME_THICKNESS + (i * POINT_WIDTH)
        if i >= 6:
            x += BAR_WIDTH

        p_bot = [(x, SCREEN_HEIGHT - FRAME_THICKNESS),
                 (x + POINT_WIDTH, SCREEN_HEIGHT - FRAME_THICKNESS),
                 (x + POINT_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)]
        pygame.draw.polygon(screen, BYU_ROYAL if i % 2 == 0 else WHITE, p_bot)

        p_top = [(x, FRAME_THICKNESS),
                 (x + POINT_WIDTH, FRAME_THICKNESS),
                 (x + POINT_WIDTH // 2, SCREEN_HEIGHT // 2 - 60)]
        pygame.draw.polygon(screen, WHITE if i % 2 == 0 else BYU_ROYAL, p_top)

    if logo_left:
        left_quad_center = start_x + (POINT_WIDTH * 3) + FRAME_THICKNESS
        screen.blit(logo_left, logo_left.get_rect(center=(left_quad_center, SCREEN_HEIGHT // 2)))

    if logo_right:
        right_quad_center = bar_x + BAR_WIDTH + (POINT_WIDTH * 3)
        screen.blit(logo_right, logo_right.get_rect(center=(right_quad_center, SCREEN_HEIGHT // 2)))


def draw_checkers(screen, board_state, start_x, selected_point):
    radius = 20
    for i, count in enumerate(board_state):
        if count == 0:
            continue

        color = WHITE if count > 0 else BYU_ROYAL

        if i < 12:
            point_index = i
        else:
            point_index = 23 - i

        x = start_x + FRAME_THICKNESS + (point_index * POINT_WIDTH)
        if point_index >= 6:
            x += BAR_WIDTH
        center_x = x + POINT_WIDTH // 2

        for j in range(abs(count)):
            if i < 12:
                center_y = (SCREEN_HEIGHT - FRAME_THICKNESS) - (radius * 2 * j) - radius
            else:
                center_y = FRAME_THICKNESS + (radius * 2 * j) + radius

            pygame.draw.circle(screen, color, (center_x, center_y), radius)
            pygame.draw.circle(screen, (0, 0, 0), (center_x, center_y), radius, 2)

            if i == selected_point and j == abs(count) - 1:
                pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), radius, 4)


def draw_dice(screen, dice, start_x):
    dice_size = 36
    center_x = (SCREEN_WIDTH // 2) - (dice_size // 2)

    for i, value in enumerate(dice):
        if value == 0:
            continue

        if i == 0:
            y_pos = (SCREEN_HEIGHT // 2) - 100 - dice_size - 10
        else:
            y_pos = (SCREEN_HEIGHT // 2) + 100 + 10

        rect = pygame.Rect(center_x, y_pos, dice_size, dice_size)
        pygame.draw.rect(screen, WHITE, rect, border_radius=5)
        pygame.draw.rect(screen, (0, 0, 0), rect, 2, border_radius=5)

        font = pygame.font.SysFont('Arial', 24, bold=True)
        text = font.render(str(value), True, (0, 0, 0))
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)


def get_point_from_mouse(pos, start_x):
    mouse_x, mouse_y = pos

    board_inner_x = start_x + FRAME_THICKNESS
    board_inner_width = (POINT_WIDTH * 12) + BAR_WIDTH

    if not (board_inner_x <= mouse_x <= board_inner_x + board_inner_width):
        return None

    relative_x = mouse_x - board_inner_x

    if relative_x < (POINT_WIDTH * 6):
        col = int(relative_x // POINT_WIDTH)
    elif relative_x > (POINT_WIDTH * 6) + BAR_WIDTH:
        col = int((relative_x - BAR_WIDTH) // POINT_WIDTH)
    else:
        return None

    if mouse_y > SCREEN_HEIGHT // 2:
        return col
    else:
        return 23 - col


def draw_turn_indicator(screen, turn, game_mode, player_side=1):
    center_x = SCREEN_WIDTH // 2
    y_pos = (SCREEN_HEIGHT // 2) - 195

    font = pygame.font.SysFont('Arial', 18, bold=True)
    text_str = "TURN" if game_mode == "PVP" else ("HUMAN" if turn == player_side else "CPU")
    text = font.render(text_str, True, (200, 200, 200))
    text_rect = text.get_rect(center=(center_x, y_pos))
    screen.blit(text, text_rect)

    box_size = 20
    color = WHITE if turn == 1 else BYU_ROYAL
    box_rect = pygame.Rect(center_x - (box_size // 2), y_pos + 15, box_size, box_size)

    pygame.draw.rect(screen, color, box_rect, border_radius=3)
    pygame.draw.rect(screen, (255, 255, 255) if turn == -1 else (0, 0, 0), box_rect, 1, border_radius=3)


def draw_bar(screen, bar_state, selected_point):
    center_x = SCREEN_WIDTH // 2
    radius = 18

    for i in range(bar_state[0]):
        y = (SCREEN_HEIGHT // 2) - 40 - (i * 10)
        pygame.draw.circle(screen, WHITE, (center_x, y), radius)
        pygame.draw.circle(screen, (0, 0, 0), (center_x, y), radius, 2)

        if selected_point == "BAR" and i == bar_state[0] - 1:
            pygame.draw.circle(screen, (255, 215, 0), (center_x, y), radius + 2, 3)

    for i in range(bar_state[1]):
        y = (SCREEN_HEIGHT // 2) + 40 + (i * 10)
        pygame.draw.circle(screen, BYU_ROYAL, (center_x, y), radius)
        pygame.draw.circle(screen, (255, 255, 255), (center_x, y), radius, 2)

        if selected_point == "BAR" and i == bar_state[1] - 1:
            pygame.draw.circle(screen, (255, 215, 0), (center_x, y), radius + 2, 3)


def draw_home_boxes(screen, home_state):
    box_w, box_h = 60, 200
    x_pos = 20
    white_y = 50
    blue_y = SCREEN_HEIGHT - 250

    pygame.draw.rect(screen, (255, 255, 255), (x_pos, white_y, box_w, box_h), 5)
    pygame.draw.rect(screen, BYU_ROYAL, (x_pos, blue_y, box_w, box_h), 5)

    for i in range(home_state[0]):
        row = i // 2
        col = i % 2
        pos = (x_pos + 18 + col * 24, white_y + 20 + row * 15)
        pygame.draw.circle(screen, WHITE, pos, 10)
        pygame.draw.circle(screen, (0, 0, 0), pos, 10, 1)

    for i in range(home_state[1]):
        row = i // 2
        col = i % 2
        pos = (x_pos + 18 + col * 24, blue_y + 20 + row * 15)
        pygame.draw.circle(screen, BYU_ROYAL, pos, 10)
        pygame.draw.circle(screen, (255, 255, 255), pos, 10, 1)


def can_bear_off(board_state, bar_state, turn):
    if (turn == 1 and bar_state[0] > 0) or (turn == -1 and bar_state[1] > 0):
        return False

    if turn == 1:
        for i in range(18):
            if board_state[i] > 0:
                return False
    else:
        for i in range(6, 24):
            if board_state[i] < 0:
                return False

    return True


def draw_win_screen(screen, winner_text):
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    font = pygame.font.SysFont("Arial", 64, bold=True)
    color = (255, 255, 255) if "White" in winner_text else (0, 46, 93)

    text_surf = font.render(winner_text, True, color)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

    pygame.draw.rect(screen, (255, 255, 255), text_rect.inflate(40, 40), 5)
    screen.blit(text_surf, text_rect)

    sub_font = pygame.font.SysFont("Arial", 24)
    sub_surf = sub_font.render("Press 'R' to Play Again | 'M' for Main Menu", True, (200, 200, 200))
    sub_rect = sub_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    screen.blit(sub_surf, sub_rect)


def is_move_legal(board_state, turn, start_index, die_value):
    target = start_index + (die_value * turn)

    if target < 0 or target > 23:
        return False

    target_count = board_state[target]
    if (turn == 1 and target_count <= -2) or (turn == -1 and target_count >= 2):
        return False

    return True


def has_legal_moves(board_state, bar_state, dice, turn):
    if not dice:
        return False

    my_bar_index = 0 if turn == 1 else 1

    if bar_state[my_bar_index] > 0:
        for d in dice:
            start_pos = -1 if turn == 1 else 24
            if is_move_legal(board_state, turn, start_pos, d):
                return True
        return False

    for i in range(24):
        if (turn == 1 and board_state[i] > 0) or (turn == -1 and board_state[i] < 0):
            for d in dice:
                if is_move_legal(board_state, turn, i, d):
                    return True

    if can_bear_off(board_state, bar_state, turn):
        return True

    return False


# --- 4. COMPUTER AI LOGIC ---
def select_computer_move(board_state, bar_state, home_state, dice, turn):
    if not dice:
        return None

    my_bar_idx = 0 if turn == 1 else 1

    if bar_state[my_bar_idx] > 0:
        for d in dice:
            target = (d - 1) if turn == 1 else (24 - d)
            target_count = board_state[target]
            is_opp = (turn == 1 and target_count == -1) or (turn == -1 and target_count == 1)
            is_open = (turn == 1 and target_count >= 0) or (turn == -1 and target_count <= 0)

            if is_open or is_opp:
                return ("BAR", target, d, is_opp)
        return None

    if can_bear_off(board_state, bar_state, turn):
        home_range = range(18, 24) if turn == 1 else range(5, -1, -1)
        for pt in home_range:
            if (turn == 1 and board_state[pt] > 0) or (turn == -1 and board_state[pt] < 0):
                dist_needed = (24 - pt) if turn == 1 else (pt + 1)
                possible_dice = [d for d in dice if d >= dist_needed]
                if possible_dice:
                    used_die = min(possible_dice)
                    return (pt, "HOME", used_die, False)

    board_range = range(24) if turn == 1 else range(23, -1, -1)
    for pt in board_range:
        if (turn == 1 and board_state[pt] > 0) or (turn == -1 and board_state[pt] < 0):
            for d in dice:
                target = pt + (d * turn)
                if 0 <= target <= 23:
                    target_count = board_state[target]
                    if (turn == 1 and target_count == -1) or (turn == -1 and target_count == 1):
                        return (pt, target, d, True)

    for pt in board_range:
        if (turn == 1 and board_state[pt] > 0) or (turn == -1 and board_state[pt] < 0):
            for d in dice:
                target = pt + (d * turn)
                if 0 <= target <= 23:
                    target_count = board_state[target]
                    is_blocked = (turn == 1 and target_count <= -2) or (turn == -1 and target_count >= 2)
                    if not is_blocked:
                        return (pt, target, d, False)

    return None


def evaluate_board(board, bar, home, ai_turn):
    ai_bar = 0 if ai_turn == 1 else 1
    opp_bar = 1 if ai_turn == 1 else 0
    ai_home = 0 if ai_turn == 1 else 1

    score = 0
    score += home[ai_home] * 100
    score -= bar[ai_bar] * 80
    score += bar[opp_bar] * 60

    for i in range(24):
        count = board[i]
        is_ai = (ai_turn == 1 and count > 0) or (ai_turn == -1 and count < 0)
        is_opp = (ai_turn == 1 and count < 0) or (ai_turn == -1 and count > 0)
        abs_count = abs(count)

        if is_ai:
            if abs_count >= 2:
                score += 20
            elif abs_count == 1:
                score -= 30
        elif is_opp:
            if abs_count == 1:
                score += 15

    return score


def select_hard_computer_move(board_state, bar_state, home_state, dice, turn):
    my_bar_idx = 0 if turn == 1 else 1

    if bar_state[my_bar_idx] > 0:
        return select_computer_move(board_state, bar_state, home_state, dice, turn)

    best_score = -999999
    best_move = None

    board_range = range(24) if turn == 1 else range(23, -1, -1)

    for pt in board_range:
        if (turn == 1 and board_state[pt] > 0) or (turn == -1 and board_state[pt] < 0):
            for d in dice:
                target = pt + (d * turn)

                if can_bear_off(board_state, bar_state, turn):
                    dist_needed = (24 - pt) if turn == 1 else (pt + 1)
                    if d >= dist_needed:
                        temp_board = list(board_state)
                        temp_home = list(home_state)
                        temp_board[pt] -= turn
                        temp_home[0 if turn == 1 else 1] += 1
                        score = evaluate_board(temp_board, bar_state, temp_home, turn)
                        if score > best_score:
                            best_score = score
                            best_move = (pt, "HOME", d, False)

                elif 0 <= target <= 23:
                    target_count = board_state[target]
                    is_blocked = (turn == 1 and target_count <= -2) or (turn == -1 and target_count >= 2)
                    if not is_blocked:
                        temp_board = list(board_state)
                        temp_bar = list(bar_state)
                        temp_home = list(home_state)

                        is_hit = (turn == 1 and target_count == -1) or (turn == -1 and target_count == 1)
                        if is_hit:
                            temp_bar[1 if turn == 1 else 0] += 1
                            temp_board[target] = 0

                        temp_board[pt] -= turn
                        temp_board[target] += turn

                        score = evaluate_board(temp_board, temp_bar, temp_home, turn)
                        if score > best_score:
                            best_score = score
                            best_move = (pt, target, d, is_hit)

    if best_move:
        return best_move

    return select_computer_move(board_state, bar_state, home_state, dice, turn)


def get_checker_center(location, stack_index, turn, start_x):
    radius = 20

    if location == "BAR":
        center_x = SCREEN_WIDTH // 2
        if turn == 1:
            center_y = (SCREEN_HEIGHT // 2) - 40 - (stack_index * 10)
        else:
            center_y = (SCREEN_HEIGHT // 2) + 40 + (stack_index * 10)
        return center_x, center_y

    if location == "HOME":
        x_pos = 20
        y_base = 50 if turn == 1 else SCREEN_HEIGHT - 250
        row = stack_index // 2
        col = stack_index % 2
        return (x_pos + 18 + col * 24, y_base + 20 + row * 15)

    if location < 12:
        point_idx = location
        is_bottom = True
    else:
        point_idx = 23 - location
        is_bottom = False

    x = start_x + FRAME_THICKNESS + (point_idx * POINT_WIDTH)
    if point_idx >= 6:
        x += BAR_WIDTH
    center_x = x + POINT_WIDTH // 2

    if is_bottom:
        center_y = (SCREEN_HEIGHT - FRAME_THICKNESS) - (radius * 2 * stack_index) - radius
    else:
        center_y = FRAME_THICKNESS + (radius * 2 * stack_index) + radius

    return center_x, center_y


def get_legal_moves_for_selected(board_state, bar_state, dice, turn, selected_point):
    legal_targets = []
    if selected_point is None or not dice:
        return legal_targets

    if selected_point == "BAR":
        actual_start = -1 if turn == 1 else 24
        for d in set(dice):
            target = actual_start + (d * turn)
            if 0 <= target <= 23 and is_move_legal(board_state, turn, actual_start, d):
                if target not in legal_targets:
                    legal_targets.append(target)
    else:
        for d in set(dice):
            target = selected_point + (d * turn)
            if 0 <= target <= 23:
                if is_move_legal(board_state, turn, selected_point, d):
                    if target not in legal_targets:
                        legal_targets.append(target)

        if can_bear_off(board_state, bar_state, turn):
            dist_needed = (24 - selected_point) if turn == 1 else (selected_point + 1)
            possible_dice = [d for d in dice if d >= dist_needed]
            if possible_dice:
                legal_targets.append("HOME")

    return legal_targets


def draw_possible_moves(screen, legal_targets, board_state, turn, start_x):
    for target in legal_targets:
        if target == "HOME":
            home_rect = pygame.Rect(20, 50, 60, 200) if turn == 1 else pygame.Rect(20, SCREEN_HEIGHT - 250, 60, 200)
            pygame.draw.rect(screen, HIGHLIGHT_GREEN, home_rect, 4, border_radius=5)
        else:
            stack_idx = abs(board_state[target])
            center_x, center_y = get_checker_center(target, stack_idx, turn, start_x)

            pygame.draw.circle(screen, HIGHLIGHT_GREEN, (center_x, center_y), 20, 3)
            pygame.draw.circle(screen, HIGHLIGHT_GREEN, (center_x, center_y), 6)


# --- 5. MAIN ENGINE ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("BYU Custom Backgammon")

    game_state = "MENU"
    game_mode = "PVP"
    ai_difficulty = "EASY"
    player_side = 1
    sound_enabled = True
    show_moves = True

    bar_state = [0, 0]
    home_state = [0, 0]
    turn_history = []

    try:
        img_l = pygame.image.load("byu_neon1.jpg").convert_alpha()
        img_r = pygame.image.load("byu_neon3.jpg").convert_alpha()
        img_l = pygame.transform.scale(img_l, (130, 100))
        img_r = pygame.transform.scale(img_r, (130, 100))
    except Exception:
        img_l = img_r = None

    clock = pygame.time.Clock()
    running = True

    def reset_game():
        nonlocal board_state, bar_state, home_state, dice, selected_point, turn, winner, active_anim, turn_history
        board_state = [0] * 24
        board_state[0] = 2
        board_state[11] = 5
        board_state[18] = 5
        board_state[16] = 3

        board_state[23] = -2
        board_state[12] = -5
        board_state[5] = -5
        board_state[7] = -3

        bar_state = [0, 0]
        home_state = [0, 0]
        dice = []
        selected_point = None
        turn = 1
        winner = None
        active_anim = None
        turn_history = []

    board_state = [0] * 24
    dice = []
    selected_point = None
    turn = 1
    winner = None
    reset_game()

    ai_timer = 0
    active_anim = None
    sound_rect = None
    moves_rect = None
    undo_rect = None

    def trigger_move_animation(start_loc, end_loc, turn_color, dice_used, hit_occurred=False, is_human_move=True):
        nonlocal active_anim, dice, board_state, bar_state, home_state, turn, turn_history

        if is_human_move:
            turn_history.append({
                'board': list(board_state),
                'bar': list(bar_state),
                'home': list(home_state),
                'dice': list(dice)
            })

        piece_color = WHITE if turn_color == 1 else BYU_ROYAL
        board_total_width = (POINT_WIDTH * 12) + BAR_WIDTH + (FRAME_THICKNESS * 2)
        start_x = (SCREEN_WIDTH - board_total_width) // 2

        if start_loc == "BAR":
            stack_start = bar_state[0 if turn_color == 1 else 1] - 1
        else:
            stack_start = abs(board_state[start_loc]) - 1

        start_pos = get_checker_center(start_loc, stack_start, turn_color, start_x)

        if start_loc == "BAR":
            bar_state[0 if turn_color == 1 else 1] -= 1
        else:
            board_state[start_loc] -= turn_color

        if end_loc == "HOME":
            stack_end = home_state[0 if turn_color == 1 else 1]
        elif end_loc == "BAR":
            stack_end = bar_state[1 if turn_color == 1 else 0]
        else:
            stack_end = abs(board_state[end_loc])

        end_pos = get_checker_center(end_loc, stack_end, turn_color, start_x)

        def finalize_move():
            nonlocal active_anim, turn, dice, board_state, bar_state, home_state, turn_history
            if hit_occurred:
                play_sound(hit_sound, sound_enabled)
                bar_state[1 if turn_color == 1 else 0] += 1
                board_state[end_loc] = 0

            if end_loc == "HOME":
                home_state[0 if turn_color == 1 else 1] += 1
            else:
                board_state[end_loc] += turn_color

            if dice_used in dice:
                dice.remove(dice_used)

            if dice and not has_legal_moves(board_state, bar_state, dice, turn_color):
                dice = []

            if not dice:
                turn *= -1
                turn_history = []
                play_sound(turn_sound, sound_enabled)

            active_anim = None

        active_anim = AnimatedPiece(piece_color, start_pos, end_pos, duration_frames=12, on_complete=finalize_move)

    while running:
        if game_state == "MENU":
            pvp_btn, pvc_btn = draw_menu_screen(screen, img_l, img_r)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if pvp_btn.collidepoint(pos):
                        game_mode = "PVP"
                        player_side = 1
                        reset_game()
                        game_state = "GAME"
                    elif pvc_btn.collidepoint(pos):
                        game_mode = "PVC"
                        game_state = "DIFFICULTY_SELECT"

            pygame.display.flip()
            clock.tick(60)
            continue

        if game_state == "DIFFICULTY_SELECT":
            easy_btn, hard_btn = draw_difficulty_screen(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if easy_btn.collidepoint(pos):
                        ai_difficulty = "EASY"
                        game_state = "COLOR_SELECT"
                    elif hard_btn.collidepoint(pos):
                        ai_difficulty = "HARD"
                        game_state = "COLOR_SELECT"

            pygame.display.flip()
            clock.tick(60)
            continue

        if game_state == "COLOR_SELECT":
            w_btn, b_btn = draw_color_select_screen(screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if w_btn.collidepoint(pos):
                        player_side = 1
                        reset_game()
                        game_state = "GAME"
                    elif b_btn.collidepoint(pos):
                        player_side = -1
                        reset_game()
                        game_state = "GAME"

            pygame.display.flip()
            clock.tick(60)
            continue

        if winner is None:
            if home_state[0] == 15:
                winner = "White Wins!"
                play_sound(win_sound, sound_enabled)
            elif home_state[1] == 15:
                winner = "Blue Wins!" if game_mode == "PVP" else "Computer Wins!"
                play_sound(win_sound, sound_enabled)

        board_total_width = (POINT_WIDTH * 12) + BAR_WIDTH + (FRAME_THICKNESS * 2)
        start_x = (SCREEN_WIDTH - board_total_width) // 2

        if game_state == "GAME" and game_mode == "PVC" and turn != player_side and not winner and active_anim is None:
            ai_timer += 1

            if not dice and ai_timer >= 60:
                ai_timer = 0
                play_sound(roll_sound, sound_enabled)
                dice = [random.randint(1, 6), random.randint(1, 6)]
                if dice[0] == dice[1]:
                    dice = [dice[0]] * 4

                if not has_legal_moves(board_state, bar_state, dice, turn):
                    dice = []
                    turn = player_side
                    turn_history = []
                    play_sound(turn_sound, sound_enabled)

            elif dice and ai_timer >= 40:
                ai_timer = 0
                if ai_difficulty == "HARD":
                    move_tuple = select_hard_computer_move(board_state, bar_state, home_state, dice, turn)
                else:
                    move_tuple = select_computer_move(board_state, bar_state, home_state, dice, turn)

                if move_tuple:
                    start_loc, end_loc, die_used, is_hit = move_tuple
                    trigger_move_animation(start_loc, end_loc, turn, die_used, hit_occurred=is_hit, is_human_move=False)
                else:
                    dice = []
                    turn = player_side
                    turn_history = []
                    play_sound(turn_sound, sound_enabled)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                if game_state == "PAUSED" or winner is not None:
                    reset_game()
                    if game_state == "PAUSED":
                        game_state = "GAME"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                if game_state == "PAUSED":
                    game_state = "MENU"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                turn *= -1
                turn_history = []
                play_sound(turn_sound, sound_enabled)

            if event.type == pygame.KEYDOWN and (event.key == pygame.K_p or event.key == pygame.K_ESCAPE):
                if game_state == "GAME":
                    game_state = "PAUSED"
                elif game_state == "PAUSED":
                    game_state = "GAME"

            if event.type == pygame.MOUSEBUTTONDOWN and game_state == "PAUSED":
                pos = pygame.mouse.get_pos()
                if sound_rect and sound_rect.collidepoint(pos):
                    sound_enabled = not sound_enabled
                elif moves_rect and moves_rect.collidepoint(pos):
                    show_moves = not show_moves

            if game_state == "GAME" and not winner and (game_mode == "PVP" or turn == player_side):
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not dice:
                        play_sound(roll_sound, sound_enabled)
                        dice = [random.randint(1, 6), random.randint(1, 6)]
                        if dice[0] == dice[1]:
                            dice = [dice[0]] * 4

                        if not has_legal_moves(board_state, bar_state, dice, turn):
                            dice = []
                            turn *= -1
                            turn_history = []
                            play_sound(turn_sound, sound_enabled)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if active_anim is not None:
                        continue

                    pos = pygame.mouse.get_pos()

                    can_undo = len(turn_history) > 0 and (game_mode == "PVP" or turn == player_side)
                    if undo_rect and undo_rect.collidepoint(pos) and can_undo:
                        prev_state = turn_history.pop()
                        board_state = prev_state['board']
                        bar_state = prev_state['bar']
                        home_state = prev_state['home']
                        dice = prev_state['dice']
                        selected_point = None
                        continue

                    point = get_point_from_mouse(pos, start_x)

                    white_home_rect = pygame.Rect(20, 50, 60, 200)
                    blue_home_rect = pygame.Rect(20, SCREEN_HEIGHT - 250, 60, 200)
                    clicked_home = (turn == 1 and white_home_rect.collidepoint(pos)) or \
                                   (turn == -1 and blue_home_rect.collidepoint(pos))

                    if selected_point is None:
                        my_bar_index = 0 if turn == 1 else 1
                        bar_rect = pygame.Rect(SCREEN_WIDTH // 2 - 35, 50, 70, SCREEN_HEIGHT - 100)

                        if bar_state[my_bar_index] > 0:
                            if bar_rect.collidepoint(pos):
                                selected_point = "BAR"
                        elif point is not None:
                            count = board_state[point]
                            if (turn == 1 and count > 0) or (turn == -1 and count < 0):
                                if dice:
                                    selected_point = point

                    else:
                        if clicked_home and can_bear_off(board_state, bar_state, turn):
                            dist_needed = (24 - selected_point) if turn == 1 else (selected_point + 1)
                            possible_dice = [d for d in dice if d >= dist_needed]
                            if possible_dice:
                                used_die = min(possible_dice)
                                trigger_move_animation(selected_point, "HOME", turn, used_die, is_human_move=True)

                        elif point is not None and point != selected_point:
                            start_pos_idx = -1 if turn == 1 else 24
                            actual_start = start_pos_idx if selected_point == "BAR" else selected_point
                            distance = (point - actual_start) * turn

                            if distance in dice:
                                target_count = board_state[point]
                                is_blocked = (turn == 1 and target_count <= -2) or (turn == -1 and target_count >= 2)

                                if not is_blocked:
                                    is_hit = (turn == 1 and target_count == -1) or (turn == -1 and target_count == 1)
                                    trigger_move_animation(selected_point, point, turn, distance, hit_occurred=is_hit, is_human_move=True)

                        selected_point = None

        # --- DRAWING ---
        screen.fill((9, 9, 12))
        draw_board(screen, img_l, img_r)
        draw_home_boxes(screen, home_state)
        draw_bar(screen, bar_state, selected_point)
        draw_checkers(screen, board_state, start_x, selected_point)

        can_undo = len(turn_history) > 0 and (game_mode == "PVP" or turn == player_side)
        undo_rect = draw_undo_button(screen, start_x, board_total_width, can_undo)
        draw_pip_counter(screen, board_state, bar_state, start_x, board_total_width)

        if show_moves:
            legal_targets = get_legal_moves_for_selected(board_state, bar_state, dice, turn, selected_point)
            draw_possible_moves(screen, legal_targets, board_state, turn, start_x)

        if active_anim:
            anim = active_anim
            anim.update()
            anim.draw(screen)

        draw_dice(screen, dice, start_x)
        draw_turn_indicator(screen, turn, game_mode, player_side)

        if winner:
            draw_win_screen(screen, winner)

        if game_state == "PAUSED":
            sound_rect, moves_rect = draw_pause_screen(screen, sound_enabled, show_moves)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()