import pygame
import sys
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Optional, Tuple
import math

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


S = TypeVar('S')
A = TypeVar('A')

@dataclass
class SearchStats:
    nodes_explored: int = 0
    max_depth_reached: int = 0

class GameState(ABC, Generic[S, A]):
    
    @abstractmethod
    def get_actions(self) -> List[A]:
        pass
 
    @abstractmethod
    def apply_action(self, action: A) -> None:
        pass
    
    @abstractmethod
    def undo_action(self, action: A) -> None:
        pass

    @abstractmethod
    def evaluate(self) -> float:
        pass
    
    @abstractmethod
    def is_terminal(self) -> bool:
        pass



class MinMaxSearcher(Generic[S, A]):
    
    def __init__(self, max_depth: int = 5):
        self.max_depth = max_depth
        self.stats = SearchStats()
            
    
    def find_best_action(self, state: GameState[S, A]) -> Optional[A]:  
        if state.is_terminal():
            return None
            
        actions = state.get_actions()
        if not actions:
            return None
            
        best_action = None
        best_value = -math.inf if state.current_player == 'X' else math.inf
        alpha = -math.inf
        beta = math.inf

        for action in actions:
            state.apply_action(action)
            if state.current_player == 'O':  
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
  
    def min_value(self, state: GameState[S, A], depth: int, alpha: float, beta: float) -> float:
        self.stats.nodes_explored += 1
        self.stats.max_depth_reached = max(self.stats.max_depth_reached, depth)
        
        if state.is_terminal() or depth >= self.max_depth:
            return state.evaluate()
            
        value = math.inf
        actions = state.get_actions()
    
        for action in actions:
            state.apply_action(action)
            value = min(value, self.max_value(state, depth + 1, alpha, beta))
            state.undo_action(action)
            
            beta = min(beta, value)
            if beta <= alpha:
                break
                
        return value
    
    def max_value(self, state: GameState[S, A], depth: int, alpha: float, beta: float) -> float:
        self.stats.nodes_explored += 1
        self.stats.max_depth_reached = max(self.stats.max_depth_reached, depth)
        
        if state.is_terminal() or depth >= self.max_depth:
            return state.evaluate()
            
        value = -math.inf
        actions = state.get_actions()
        
        for action in actions:
            state.apply_action(action)
            value = max(value, self.min_value(state, depth + 1, alpha, beta))
            state.undo_action(action)
            
            alpha = max(alpha, value)
            if beta <= alpha:
                break
                
        return value






@dataclass
class BreakthroughAction:
    row: int
    col: int

class BreakthroughState(GameState[List[List[str]], BreakthroughAction]):
    def __init__(self, size: int, alignement: int):
        self.size = size
        self.alignement = alignement
        self.board = [[' ' for _ in range(size)] for _ in range(size)]
        self.current_player = 'X' 
        
    def get_actions(self) -> List[BreakthroughAction]: 
        actions = []
        center = self.size // 2
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == ' ':
                    if (i == center and j == center) or \
                       (i in (0, self.size-1) and j in (0, self.size-1)):
                        actions.insert(0, BreakthroughAction(i, j))
                    else:
                        actions.append(BreakthroughAction(i, j))
        actions.sort(key=lambda a: (a.row == self.size // 2 and a.col == self.size // 2, a.row in (0, self.size-1) and a.col in (0, self.size-1)), reverse=True)
        return actions
    
    def apply_action(self, action: BreakthroughAction) -> None:
        self.board[action.row][action.col] = self.current_player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
    
    def undo_action(self, action: BreakthroughAction) -> None:
        self.board[action.row][action.col] = ' '    
        self.current_player = 'O' if self.current_player == 'X' else 'X'
    
    def evaluate(self) -> float:
        if self._is_winner('X'):
            return 1000
        elif self._is_winner('O'):
            return -1000

        score = 0
        
        for i in range(self.size):
            for j in range(self.size - self.alignement + 1):
                line = [self.board[i][j + k] for k in range(self.alignement)]
                score += self._evaluate_line(line)
                
                if i <= self.size - self.alignement:
                    column = [self.board[i + k][j] for k in range(self.alignement)]
                    score += self._evaluate_line(column)
                
                if i <= self.size - self.alignement:
                    diagonal1 = [self.board[i + k][j + k] for k in range(self.alignement)]
                    score += self._evaluate_line(diagonal1)
                    if j + self.alignement <= self.size:
                        diagonal2 = [self.board[i + k][j + self.alignement - k - 1] for k in range(self.alignement)]
                        score += self._evaluate_line(diagonal2)
        
        return score

    def _evaluate_line(self, line: List[str]) -> int:
        x_count = line.count('X')
        o_count = line.count('O')

        if x_count > 0 and o_count > 0:
            return 0

        if o_count == 0 and x_count > 0:
            return 10 * x_count 

        if x_count == 0 and o_count > 0:
            return -10 * o_count 

        return 0
    
    def is_terminal(self) -> bool:
        if self._is_winner('X') or self._is_winner('O'):
            return True
        return not any(' ' in row for row in self.board)


    
    def _is_winner(self, player: str) -> bool:
        for i in range(self.size):
            for j in range(self.size - self.alignement + 1):
                if all(self.board[i][j + k] == player for k in range(self.alignement)):
                    return True
        
        for i in range(self.size - self.alignement + 1):
            for j in range(self.size):
                if all(self.board[i + k][j] == player for k in range(self.alignement)):
                    return True
        
        for i in range(self.size - self.alignement + 1):
            for j in range(self.size - self.alignement + 1):
                if all(self.board[i + k][j + k] == player for k in range(self.alignement)):
                    return True
                if all(self.board[i + k][j + self.alignement - k - 1] == player for k in range(self.alignement)):
                    return True
        
        return False


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
    """
    Calcule les coups valides pour un pion situé en (row, col).
    Le pion avance d'une case vers l'avant.
    Les déplacements en diagonale (gauche et droite) sont autorisés
    s'ils mènent sur une case vide ou sur une case occupée par un pion adverse.
    """
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
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

            if selected == (row, col):
                pygame.draw.rect(screen, BLUE, rect, 4)
            if (row, col) in valid_moves:
                pygame.draw.rect(screen, GREEN, rect, 4)

            piece = board[row][col]
            if piece is not None:
                pawn_img = white_img if piece == "W" else black_img
                pawn_rect = pawn_img.get_rect(center=(col * SQUARE_SIZE + SQUARE_SIZE // 2,
                                                        row * SQUARE_SIZE + SQUARE_SIZE // 2))
                screen.blit(pawn_img, pawn_rect)

def check_win(board):
    """
    Vérifie si un joueur a gagné.
    - Les blancs gagnent si un pion blanc atteint la première rangée.
    - Les noirs gagnent si un pion noir atteint la dernière rangée.
    """
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

def ai_move(board, player):
    """
    Juste bouge au pif pour l'instant 
    """
    moves = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board[row][col] == player:
                valid = get_valid_moves(board, row, col)
                for move in valid:
                    moves.append(((row, col), move))
    if moves:
        return random.choice(moves)
    return None

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Breakthrough")
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
                        current_player = "B"
                        selected = None
                        valid_moves = []
                        winner = check_win(board)
                        if winner is not None or not has_moves(board, current_player):
                            game_over = True
                    else:
                        if board[row][col] == current_player:
                            selected = (row, col)
                            valid_moves = get_valid_moves(board, row, col)
                        else:
                            selected = None
                            valid_moves = []

        if current_player == "B" and not game_over:
            pygame.time.wait(500)
            move = ai_move(board, "B")
            if move:
                (src_row, src_col), (dest_row, dest_col) = move
                if board[dest_row][dest_col] is not None:
                    explosion_x = dest_col * SQUARE_SIZE + SQUARE_SIZE // 2
                    explosion_y = dest_row * SQUARE_SIZE + SQUARE_SIZE // 2
                    explosions.append(Explosion(explosion_x, explosion_y, use_alternative=True))
                board[dest_row][dest_col] = board[src_row][src_col]
                board[src_row][src_col] = None
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
