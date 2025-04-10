import pygame
import sys
import random
import math
from dataclasses import dataclass
from typing import List, Optional, Tuple
import random

# ----- Constante pour config -----
BOARD_SIZE = 8
SQUARE_SIZE = 80
WIDTH = BOARD_SIZE * SQUARE_SIZE
HEIGHT = BOARD_SIZE * SQUARE_SIZE

WHITE_COLOR = (240, 240, 240)
BLACK_COLOR = (50, 50, 50)
LIGHT_BROWN = (222, 184, 135)
DARK_BROWN = (139, 69, 19)
BLUE = (50, 50, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

DIFFICULTY = 1

# ----- class pour les explos-----
class Explosion:
    explosion_img_default = None  
    explosion_img_alternative = None  

    def __init__(self, x, y, use_alternative=False):
        self.use_alternative = use_alternative
        if use_alternative:
            if Explosion.explosion_img_alternative is None:
                try:
                    loaded_img = pygame.image.load("explosion2.png").convert_alpha()
                    new_width = loaded_img.get_width() // 6
                    new_height = loaded_img.get_height() // 6
                    Explosion.explosion_img_alternative = pygame.transform.scale(loaded_img, (new_width, new_height))
                except pygame.error:
                    print("Erreur : Impossible de charger 'explosion2.png'.")
                    sys.exit()
        else:
            if Explosion.explosion_img_default is None:
                try:
                    loaded_img = pygame.image.load("explosion.png").convert_alpha()
                    new_width = loaded_img.get_width() // 6
                    new_height = loaded_img.get_height() // 6
                    Explosion.explosion_img_default = pygame.transform.scale(loaded_img, (new_width, new_height))
                except pygame.error:
                    print("Erreur : Impossible de charger 'explosion.png'.")
                    sys.exit()
        self.x = x
        self.y = y
        self.duration = 30 
        self.current_frame = 0

    def update(self):
        self.current_frame += 1

    def draw(self, screen):
        max_scale_factor = 1.6
        scale_factor = 1 + (self.current_frame / self.duration) * (max_scale_factor - 1)
        if self.use_alternative:
            base_img = Explosion.explosion_img_alternative
        else:
            base_img = Explosion.explosion_img_default
        new_width = int(base_img.get_width() * scale_factor)
        new_height = int(base_img.get_height() * scale_factor)
        explosion_surface = pygame.transform.scale(base_img, (new_width, new_height))
        rect = explosion_surface.get_rect(center=(self.x, self.y))
        screen.blit(explosion_surface, rect)

# ----- fonc qui vérifient info de la partie et dessine plateau -----
def init_board():
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for row in range(2):
        for col in range(BOARD_SIZE):
            board[row][col] = "B"
    for row in range(BOARD_SIZE-2, BOARD_SIZE):
        for col in range(BOARD_SIZE):
            board[row][col] = "W"
    return board

def get_valid_moves(board, row, col):
    moves = []
    piece = board[row][col]
    if piece is None:
        return moves

    direction = -1 if piece == "W" else 1
    new_row = row + direction
    if 0 <= new_row < BOARD_SIZE:
        if board[new_row][col] is None:
            moves.append((new_row, col))
        new_col = col - 1
        if new_col >= 0:
            if board[new_row][new_col] is None or board[new_row][new_col] != piece:
                moves.append((new_row, new_col))
        new_col = col + 1
        if new_col < BOARD_SIZE:
            if board[new_row][new_col] is None or board[new_row][new_col] != piece:
                moves.append((new_row, new_col))
    return moves

def draw_board(screen, board, selected, valid_moves, white_img, black_img):
    try:
        texture1 = pygame.image.load("case1.png").convert()
        texture2 = pygame.image.load("case2.png").convert()
    except pygame.error:
        print("Erreur : Impossible de charger 'case1.png' ou 'case2.png'.")
        sys.exit()

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            texture = texture1 if (row + col) % 2 == 0 else texture2
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            screen.blit(pygame.transform.scale(texture, (SQUARE_SIZE, SQUARE_SIZE)), rect)

            # Removed blue and green borders for selected pieces and valid moves
            piece = board[row][col]
            if piece is not None:
                pawn_img = white_img if piece == "W" else black_img
                pawn_rect = pawn_img.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                      row * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(pawn_img, pawn_rect)

def check_win(board):
    for col in range(BOARD_SIZE):
        if board[0][col] == "W":
            return "W"
        if board[BOARD_SIZE-1][col] == "B":
            return "B"
    return None
    
def has_moves(board, player):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == player:
                if get_valid_moves(board, row, col):
                    return True
    return False

# ----- class pour minmax (états du jeu, fonc pour min max, etc ...)-----

@dataclass
class BreakthroughAction:
    src_row: int
    src_col: int
    dst_row: int
    dst_col: int
    captured: Optional[str] = None

class BreakthroughState:
    def __init__(self, board: List[List[Optional[str]]], current_player: str):
        self.board = board
        self.current_player = current_player

    def get_actions(self) -> List[BreakthroughAction]:
        actions = []
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if self.board[row][col] == self.current_player:
                    for move in get_valid_moves(self.board, row, col):
                        is_capture = self.board[move[0]][move[1]] is not None
                        actions.append((is_capture, BreakthroughAction(row, col, move[0], move[1])))

        actions.sort(key=lambda x: x[0], reverse=True)
        return [action for _, action in actions]

    def apply_action(self, action: BreakthroughAction) -> None:
        piece = self.board[action.src_row][action.src_col]
        action.captured = self.board[action.dst_row][action.dst_col]
        self.board[action.dst_row][action.dst_col] = piece
        self.board[action.src_row][action.src_col] = None
        self.current_player = "B" if self.current_player == "W" else "W"

    def undo_action(self, action: BreakthroughAction) -> None:
        piece = self.board[action.dst_row][action.dst_col]
        self.board[action.src_row][action.src_col] = piece
        self.board[action.dst_row][action.dst_col] = action.captured
        self.current_player = "B" if self.current_player == "W" else "W"




# fonction pour evaluer l'état du jeu tiré de https://www.codeproject.com/Articles/37024/Simple-AI-for-the-Game-of-Breakthrough

    def evaluateOld(self) -> float: 
        score = 0
        white_pawns = 0
        black_pawns = 0

        WIN_VALUE = 10000
        PIECE_VALUE = 100
        PIECE_ALMOST_WIN_VALUE = 500
        PIECE_DANGER_VALUE = 10
        PIECE_HIGH_DANGER_VALUE = 50
        PIECE_ATTACK_VALUE = 30
        PIECE_PROTECTION_VALUE = 20
        CONNECTION_HORIZONTAL_VALUE = 15
        CONNECTION_VERTICAL_VALUE = 10
        PIECE_MOBILITY_VALUE = 5
        COLUMN_HOLE_VALUE = 50
        HOME_GROUND_VALUE = 20

        for col in range(BOARD_SIZE):
            if self.board[0][col] == "W":  
                return WIN_VALUE
            if self.board[BOARD_SIZE-1][col] == "B":  
                return -WIN_VALUE

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece is None:
                    continue

                piece_score = PIECE_VALUE

                if piece == "W":
                    piece_score += row * PIECE_DANGER_VALUE
                    if row == BOARD_SIZE - 2:  
                        piece_score += PIECE_HIGH_DANGER_VALUE
                elif piece == "B":
                    piece_score += (BOARD_SIZE - 1 - row) * PIECE_DANGER_VALUE
                    if row == 1: 
                        piece_score += PIECE_HIGH_DANGER_VALUE

                valid_moves = get_valid_moves(self.board, row, col)
                piece_score += len(valid_moves) * PIECE_MOBILITY_VALUE

                for move in valid_moves:
                    target_row, target_col = move
                    target_piece = self.board[target_row][target_col]
                    if target_piece is not None:
                        if target_piece != piece:  
                            piece_score += PIECE_ATTACK_VALUE
                        else:  
                            piece_score += PIECE_PROTECTION_VALUE

                if col > 0 and self.board[row][col - 1] == piece:
                    piece_score += CONNECTION_HORIZONTAL_VALUE
                if row > 0 and self.board[row - 1][col] == piece:
                    piece_score += CONNECTION_VERTICAL_VALUE

                if piece == "W":
                    white_pawns += 1
                    score += piece_score
                elif piece == "B":
                    black_pawns += 1
                    score -= piece_score

        for col in range(BOARD_SIZE):
            white_in_column = any(self.board[row][col] == "W" for row in range(BOARD_SIZE))
            black_in_column = any(self.board[row][col] == "B" for row in range(BOARD_SIZE))
            if not white_in_column:
                score -= COLUMN_HOLE_VALUE
            if not black_in_column:
                score += COLUMN_HOLE_VALUE

        for col in range(BOARD_SIZE):
            if self.board[BOARD_SIZE - 1][col] == "W":
                score += HOME_GROUND_VALUE
            if self.board[0][col] == "B":
                score -= HOME_GROUND_VALUE

        score += (white_pawns - black_pawns) * PIECE_VALUE

        return score


# fonction pour evaluer l'état du jeu tiré de https://www.codeproject.com/Articles/37024/Simple-AI-for-the-Game-of-Breakthrough

    def evaluate(self) -> float:
        score = 0
        white_pawns = 0
        black_pawns = 0
        white_advanced = 0
        black_advanced = 0
        white_protected = 0
        black_protected = 0
        white_mobility = 0
        black_mobility = 0
        white_central = 0
        black_central = 0

        # Constants
        WIN_VALUE = 100000
        PIECE_VALUE = 100
        PIECE_ALMOST_WIN_VALUE = 1000
        ADVANCE_VALUE = 20
        CENTRAL_VALUE = 15
        PROTECTION_VALUE = 25
        MOBILITY_VALUE = 10
        PAIR_VALUE = 30
        COLUMN_CONTROL_VALUE = 40
        DEFENSE_VALUE = 20
        ATTACK_VALUE = 35

        # Check for immediate wins
        for col in range(BOARD_SIZE):
            if self.board[0][col] == "W":
                return WIN_VALUE
            if self.board[BOARD_SIZE-1][col] == "B":
                return -WIN_VALUE

        # Evaluate each piece
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece is None:
                    continue

                # Basic piece value and counting
                if piece == "W":
                    white_pawns += 1
                    # Advancement (closer to promotion is better)
                    advance_score = (BOARD_SIZE - 1 - row) * ADVANCE_VALUE
                    white_advanced += advance_score
                    
                    # Central control (controlling center is better)
                    if 2 <= col <= BOARD_SIZE-3:
                        white_central += CENTRAL_VALUE
                else:
                    black_pawns += 1
                    # Advancement (closer to promotion is better)
                    advance_score = row * ADVANCE_VALUE
                    black_advanced += advance_score
                    
                    # Central control
                    if 2 <= col <= BOARD_SIZE-3:
                        black_central += CENTRAL_VALUE

                # Mobility and protection
                valid_moves = get_valid_moves(self.board, row, col)
                if piece == "W":
                    white_mobility += len(valid_moves) * MOBILITY_VALUE
                else:
                    black_mobility += len(valid_moves) * MOBILITY_VALUE

                # Protection (pawns defended by other pawns)
                protection = 0
                direction = -1 if piece == "W" else 1
                protected_row = row - direction
                if 0 <= protected_row < BOARD_SIZE:
                    for dc in [-1, 1]:
                        protected_col = col + dc
                        if 0 <= protected_col < BOARD_SIZE:
                            if self.board[protected_row][protected_col] == piece:
                                protection += PROTECTION_VALUE
                                if piece == "W":
                                    white_protected += PROTECTION_VALUE
                                else:
                                    black_protected += PROTECTION_VALUE

                # Attack potential (pawns that can capture)
                for move in valid_moves:
                    target_piece = self.board[move[0]][move[1]]
                    if target_piece is not None and target_piece != piece:
                        if piece == "W":
                            score += ATTACK_VALUE
                        else:
                            score -= ATTACK_VALUE

        # Pawn structure evaluation
        for col in range(BOARD_SIZE):
            # Column control (having pawns in each column is good)
            white_in_column = any(self.board[row][col] == "W" for row in range(BOARD_SIZE))
            black_in_column = any(self.board[row][col] == "B" for row in range(BOARD_SIZE))
            
            if white_in_column:
                score += COLUMN_CONTROL_VALUE
            if black_in_column:
                score -= COLUMN_CONTROL_VALUE

            # Pawn pairs (side-by-side pawns are stronger)
            for row in range(BOARD_SIZE):
                if self.board[row][col] == "W" and col > 0 and self.board[row][col-1] == "W":
                    score += PAIR_VALUE
                if self.board[row][col] == "B" and col > 0 and self.board[row][col-1] == "B":
                    score -= PAIR_VALUE

        # Pawns almost promoting
        for col in range(BOARD_SIZE):
            if self.board[1][col] == "W":
                score += PIECE_ALMOST_WIN_VALUE * 0.8
            if self.board[BOARD_SIZE-2][col] == "B":
                score -= PIECE_ALMOST_WIN_VALUE * 0.8

        # Combine all factors
        score += (white_pawns - black_pawns) * PIECE_VALUE
        score += white_advanced - black_advanced
        score += white_protected - black_protected
        score += white_mobility - black_mobility
        score += white_central - black_central

        # Encourage keeping some defensive pieces
        if white_pawns > black_pawns and black_pawns < 4:
            score += DEFENSE_VALUE * (4 - black_pawns)
        elif black_pawns > white_pawns and white_pawns < 4:
            score -= DEFENSE_VALUE * (4 - white_pawns)

        return score


    def is_terminal(self) -> bool:
        for col in range(BOARD_SIZE):
            if self.board[0][col] == "W" or self.board[BOARD_SIZE-1][col] == "B":
                return True
        if not self.get_actions():
            return True
        return False

class BreakthroughMinMaxSearcher:
    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.nodes_explored = 0
        self.max_depth_reached = 0

    def find_best_action(self, state: BreakthroughState) -> Optional[BreakthroughAction]:
        if state.is_terminal():
            return None

        for action in state.get_actions():
            state.apply_action(action)
            if state.is_terminal():  
                state.undo_action(action)
                return action
            state.undo_action(action)

        actions = state.get_actions()
        if not actions:
            return None
        best_action = None
        if state.current_player == "W":
            best_value = -math.inf
        else:
            best_value = math.inf
        alpha = -math.inf
        beta = math.inf

        actions.sort(key=lambda action: self.evaluate_action(state, action), reverse=True)

        for action in actions:
            state.apply_action(action)
            if state.current_player == "B":  
                value = self.min_value(state, 1, alpha, beta)
                if value > best_value:
                    best_value = value
                    best_action = action
                alpha = max(alpha, value)
            else:  
                value = self.max_value(state, 1, alpha, beta)
                if value < best_value:
                    best_value = value
                    best_action = action
                beta = min(beta, value)
            state.undo_action(action)
        return best_action

    def evaluate_action(self, state: BreakthroughState, action: BreakthroughAction) -> float:
        state.apply_action(action)
        value = state.evaluate()
        state.undo_action(action)
        return value

    def min_value(self, state: BreakthroughState, depth: int, alpha: float, beta: float) -> float:
        self.nodes_explored += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        if state.is_terminal() or depth >= self.max_depth:
            return state.evaluate()
        value = math.inf
        for action in state.get_actions():
            state.apply_action(action)
            value = min(value, self.max_value(state, depth + 1, alpha, beta))
            state.undo_action(action)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

    def max_value(self, state: BreakthroughState, depth: int, alpha: float, beta: float) -> float:
        self.nodes_explored += 1
        self.max_depth_reached = max(self.max_depth_reached, depth)
        if state.is_terminal() or depth >= self.max_depth:
            return state.evaluate()
        value = -math.inf
        for action in state.get_actions():
            state.apply_action(action)
            value = max(value, self.min_value(state, depth + 1, alpha, beta))
            state.undo_action(action)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value

# ----- boucle de jeu -----
def main(mode="AI", difficulty="medium"):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Breakthrough avec Minimax")
    clock = pygame.time.Clock()

    board = init_board()
    current_player = "W"  
    selected = None
    valid_moves = []
    game_over = False
    winner = None

    try:
        white_pawn_img = pygame.image.load("white_pawn.png").convert_alpha()
        black_pawn_img = pygame.image.load("black_pawn.png").convert_alpha()
    except pygame.error:
        print("Erreur : Impossible de charger 'white_pawn.png' ou 'black_pawn.png'.")
        sys.exit()
    target_size = (SQUARE_SIZE - 20, SQUARE_SIZE - 20)
    white_pawn_img = pygame.transform.scale(white_pawn_img, target_size)
    black_pawn_img = pygame.transform.scale(black_pawn_img, target_size)

    explosions = []
    cascade_started = False
    explosion_delay = 30  
    explosion_cascade_timer = explosion_delay
    cascade_list = []
    cascade_explosion_alternative = False 

    font = pygame.font.SysFont(None, 48)

    searcher = BreakthroughMinMaxSearcher(max_depth={"easy": 1, "medium": 2, "hard": 4}[difficulty])

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if current_player == "W" and not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = mouse_x // SQUARE_SIZE
                row = mouse_y // SQUARE_SIZE

                if selected is None:
                    if board[row][col] == current_player:
                        selected = (row, col)
                        valid_moves = get_valid_moves(board, row, col)
                else:
                    if (row, col) in valid_moves:
                        src_row, src_col = selected
                        if board[row][col] is not None:
                            explosion_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                            explosion_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                            explosions.append(Explosion(explosion_x, explosion_y, use_alternative=False))
                        board[row][col] = board[src_row][src_col]
                        board[src_row][src_col] = None
                        current_player = "B" if current_player == "W" else "W"
                        selected = None
                        valid_moves = []
                        winner = check_win(board)
                        if winner is not None or not has_moves(board, current_player):
                            game_over = True

                        # Update the display immediately after the player's move
                        draw_board(screen, board, selected, valid_moves, white_pawn_img, black_pawn_img)
                        for explosion in explosions[:]:
                            explosion.update()
                            explosion.draw(screen)
                            if explosion.current_frame > explosion.duration:
                                explosions.remove(explosion)
                        pygame.display.flip()
                    else:
                        if board[row][col] == current_player:
                            selected = (row, col)
                            valid_moves = get_valid_moves(board, row, col)
                        else:
                            selected = None
                            valid_moves = []

        if mode == "AI" and current_player == "B" and not game_over:
            pygame.time.wait(random.randint(1000, 3000))
            state = BreakthroughState(board, current_player)
            best_action = searcher.find_best_action(state)
            if best_action:
                if board[best_action.dst_row][best_action.dst_col] is not None:
                    explosion_x = best_action.dst_col * SQUARE_SIZE + SQUARE_SIZE // 2
                    explosion_y = best_action.dst_row * SQUARE_SIZE + SQUARE_SIZE // 2
                    explosions.append(Explosion(explosion_x, explosion_y, use_alternative=True))
                board[best_action.dst_row][best_action.dst_col] = board[best_action.src_row][best_action.src_col]
                board[best_action.src_row][best_action.src_col] = None
                current_player = "W"
                winner = check_win(board)
                if winner is not None or not has_moves(board, current_player):
                    game_over = True
            else:
                game_over = True
                winner = "W"

        if game_over:
            if not cascade_started:
                cascade_list = []
                if winner == "W":
                    for row in range(BOARD_SIZE):
                        for col in range(BOARD_SIZE):
                            if board[row][col] == "B":
                                cascade_list.append((row, col))
                    cascade_explosion_alternative = False
                elif winner == "B":
                    for row in range(BOARD_SIZE):
                        for col in range(BOARD_SIZE):
                            if board[row][col] == "W":
                                cascade_list.append((row, col))
                    cascade_explosion_alternative = True
                cascade_started = True
                explosion_cascade_timer = explosion_delay
            else:
                explosion_cascade_timer -= 1
                if explosion_cascade_timer <= 0 and cascade_list:
                    row, col = cascade_list.pop(0)
                    explosion_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
                    explosion_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
                    explosions.append(Explosion(explosion_x, explosion_y, use_alternative=cascade_explosion_alternative))
                    board[row][col] = None
                    explosion_cascade_timer = explosion_delay

        draw_board(screen, board, selected, valid_moves, white_pawn_img, black_pawn_img)

        for explosion in explosions[:]:
            explosion.update()
            explosion.draw(screen)
            if explosion.current_frame > explosion.duration:
                explosions.remove(explosion)

        if game_over and not cascade_list:
            msg = f"{winner} gagne!" if winner is not None else "Match nul!"
            text = font.render(msg, True, RED)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
