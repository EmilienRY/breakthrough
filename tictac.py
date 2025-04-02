
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar, Generic, List, Optional, Tuple
import math

S = TypeVar('S')
A = TypeVar('A')

# classes abstraictes pour le états du jeu.

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
    

#version générique de min max

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
    

#instanciation de searchstate pour tic tac toe

@dataclass
class TicTacToeAction:
    row: int
    col: int

class TicTacToeState(GameState[List[List[str]], TicTacToeAction]):
    def __init__(self, size: int, alignement: int):
        self.size = size
        self.alignement = alignement
        self.board = [[' ' for _ in range(size)] for _ in range(size)]
        self.current_player = 'X' 
        
    def get_actions(self) -> List[TicTacToeAction]:  #recup de toutes les actions possibles
        actions = []
        center = self.size // 2
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == ' ':
                    if (i == center and j == center) or \
                       (i in (0, self.size-1) and j in (0, self.size-1)):
                        actions.insert(0, TicTacToeAction(i, j))
                    else:
                        actions.append(TicTacToeAction(i, j))
        actions.sort(key=lambda a: (a.row == self.size // 2 and a.col == self.size // 2, a.row in (0, self.size-1) and a.col in (0, self.size-1)), reverse=True)
        return actions
    
    def apply_action(self, action: TicTacToeAction) -> None:
        self.board[action.row][action.col] = self.current_player
        self.current_player = 'O' if self.current_player == 'X' else 'X'
    
    def undo_action(self, action: TicTacToeAction) -> None:
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
    

# boucle de jeu

def afficher_grille(state: TicTacToeState):
    for row in state.board:
        print(" | ".join(row))
        print("-" * (4 * len(row) - 1))

def jouer_coup_humain(state: TicTacToeState, taille: int) -> None:
    while True:
        try:
            x, y = map(int, input("Entrez votre coup (ligne colonne) : ").split())
            if 0 <= x < taille and 0 <= y < taille and state.board[x][y] == ' ':
                state.apply_action(TicTacToeAction(x, y))
                break
            else:
                print("Case invalide ! Réessayez.")
        except ValueError:
            print("Format invalide. Entrez deux nombres (ex: 1 2).")

def jouer_coup_ia(state: TicTacToeState, searcher: MinMaxSearcher, nom_ia: str = "IA") -> None:
    print(f"\nTour de {nom_ia}...")
    action = searcher.find_best_action(state)
    if action:
        state.apply_action(action)
        print(f"{nom_ia} joue en position ({action.row}, {action.col})")

def verifier_fin_partie(state: TicTacToeState, mode_ia_vs_ia: bool = False) -> bool:
    if state._is_winner('X'):
        afficher_grille(state)
        print("Le joueur X a gagné !" if mode_ia_vs_ia else "Vous avez gagné !")
        return True
    elif state._is_winner('O'):
        afficher_grille(state)
        print("Le joueur O a gagné !" if mode_ia_vs_ia else "L'IA a gagné !")
        return True
    elif state.is_terminal():
        afficher_grille(state)
        print("Match nul !")
        return True
    return False



def jouer():
    taille = int(input("Entrez la taille de la grille (ex: 3 pour 3x3) : "))
    alignement = taille
    
    print("\nChoisissez le mode de jeu:")
    print("1. Humain vs IA")
    print("2. IA vs IA")
    mode = int(input("Votre choix (1 ou 2) : "))
    
    mode_ia_vs_ia = mode == 2
    joueur_commence = True 
    
    if not mode_ia_vs_ia:
        premier_joueur = input("\nVoulez-vous jouer en premier ? (o/n) : ").lower()
        joueur_commence = premier_joueur.startswith('o')
    
    print(f"\nBienvenue dans Tic-Tac-Toe {taille}x{taille} ! Vous devez aligner {alignement} symboles.")

    state = TicTacToeState(taille, alignement)

    searcher1 = MinMaxSearcher(max_depth=5) #ia min
    searcher2 = MinMaxSearcher(max_depth=5) # ia max


    if not mode_ia_vs_ia and not joueur_commence:
        state.current_player = 'O'
    


    while True:
        afficher_grille(state)
        
        if mode_ia_vs_ia:
            if state.current_player == 'X':
                jouer_coup_ia(state, searcher1, "IA 1")
            else:
                jouer_coup_ia(state, searcher2, "IA 2")
        else:
            if joueur_commence:
                if state.current_player == 'X':
                    jouer_coup_humain(state, taille)
                else:
                    jouer_coup_ia(state, searcher1)
            else:
                if state.current_player == 'O':
                    jouer_coup_ia(state, searcher1)
                else:
                    jouer_coup_humain(state, taille)


                
        if verifier_fin_partie(state, mode_ia_vs_ia):
            break
    
    print(f"\nNombre total de nœuds explorés par IA 1 : {searcher1.stats.nodes_explored}")
    print(f"Profondeur maximale atteinte par IA 1 : {searcher1.stats.max_depth_reached}")
    
    if mode_ia_vs_ia:
        print(f"\nNombre total de nœuds explorés par IA 2 : {searcher2.stats.nodes_explored}")
        print(f"Profondeur maximale atteinte par IA 2 : {searcher2.stats.max_depth_reached}")

if __name__ == "__main__":
    jouer()   
