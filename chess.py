import pygame
import sys
import random

# Dimensions de la fenêtre et de l’échiquier
BOARD_SIZE = 8
SQUARE_SIZE = 80
WIDTH = BOARD_SIZE * SQUARE_SIZE
HEIGHT = BOARD_SIZE * SQUARE_SIZE

# Couleurs
WHITE = (240, 240, 240)
BLACK = (50, 50, 50)
LIGHT_BROWN = (222, 184, 135)
DARK_BROWN = (139, 69, 19)
BLUE = (50, 50, 255)
GREEN = (0, 200, 0)
RED = (200, 0, 0)

def init_board():
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    # Les noirs occupent les deux premières rangées (0 et 1)
    for row in range(2):
        for col in range(BOARD_SIZE):
            board[row][col] = "B"
    # Les blancs occupent les deux dernières rangées (6 et 7)
    for row in range(BOARD_SIZE-2, BOARD_SIZE):
        for col in range(BOARD_SIZE):
            board[row][col] = "W"
    return board

def get_valid_moves(board, row, col):
    """
    Calcule les coups valides pour un pion situé en (row, col).
    Le pion avance d’une case vers l’avant.
    - Le déplacement en avant est autorisé si la case est vide.
    - Les déplacements en diagonale (gauche et droite) sont autorisés s'ils mènent sur une case vide
      ou si celle-ci contient un pion adverse.
    """
    moves = []
    piece = board[row][col]
    if piece is None:
        return moves

    direction = -1 if piece == "W" else 1
    new_row = row + direction
    if 0 <= new_row < BOARD_SIZE:
        # Déplacement en avant (seulement si la case est vide)
        if board[new_row][col] is None:
            moves.append((new_row, col))
        # Déplacement en diagonale gauche
        new_col = col - 1
        if new_col >= 0:
            if board[new_row][new_col] is None or board[new_row][new_col] != piece:
                moves.append((new_row, new_col))
        # Déplacement en diagonale droite
        new_col = col + 1
        if new_col < BOARD_SIZE:
            if board[new_row][new_col] is None or board[new_row][new_col] != piece:
                moves.append((new_row, new_col))
    return moves

def draw_board(screen, board, selected, valid_moves):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            # Alternance des couleurs pour les cases
            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            rect = pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, rect)

            # Met en surbrillance la case sélectionnée
            if selected == (row, col):
                pygame.draw.rect(screen, BLUE, rect, 4)
            # Met en évidence les coups possibles
            if (row, col) in valid_moves:
                pygame.draw.rect(screen, GREEN, rect, 4)

            # Dessine le pion s'il existe
            piece = board[row][col]
            if piece is not None:
                center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                radius = SQUARE_SIZE // 2 - 10
                if piece == "W":
                    pygame.draw.circle(screen, WHITE, center, radius)
                    pygame.draw.circle(screen, BLACK, center, radius, 2)
                else:
                    pygame.draw.circle(screen, BLACK, center, radius)
                    pygame.draw.circle(screen, WHITE, center, radius, 2)

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
    IA très simple qui retourne aléatoirement un coup parmi ceux possibles pour le joueur donné.
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
    current_player = "W"  # Joueur humain : blanc, IA : noir
    selected = None
    valid_moves = []
    game_over = False
    winner = None

    font = pygame.font.SysFont(None, 48)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Tour du joueur humain
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
                        board[row][col] = board[src_row][src_col]
                        board[src_row][src_col] = None
                        current_player = "B"
                        selected = None
                        valid_moves = []
                        winner = check_win(board)
                        if winner is not None:
                            game_over = True
                        elif not has_moves(board, current_player):
                            game_over = True
                            winner = "W"
                    else:
                        if board[row][col] == current_player:
                            selected = (row, col)
                            valid_moves = get_valid_moves(board, row, col)
                        else:
                            selected = None
                            valid_moves = []

        # Tour de l'IA (joueur noir)
        if current_player == "B" and not game_over:
            pygame.time.wait(500)  # Pause pour voir le déroulé
            move = ai_move(board, "B")
            if move:
                (src_row, src_col), (dest_row, dest_col) = move
                board[dest_row][dest_col] = board[src_row][src_col]
                board[src_row][src_col] = None
                current_player = "W"
                winner = check_win(board)
                if winner is not None:
                    game_over = True
                elif not has_moves(board, current_player):
                    game_over = True
                    winner = "B"
            else:
                game_over = True
                winner = "W"

        draw_board(screen, board, selected, valid_moves)

        # Affichage du message de fin de partie
        if game_over:
            msg = f"{winner} gagne!" if winner is not None else "Match nul!"
            text = font.render(msg, True, RED)
            text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2))
            screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
