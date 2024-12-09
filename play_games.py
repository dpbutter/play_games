#!/usr/bin/python


import sys
from board_games import *


game_lst = []

class GameWrapper:
    def __init__(self, n, o):
        self.name = n
        self.obj = o

def load_games():
    # Load all the games
    game_lst.append(GameWrapper('Tic-Tac-Toe', TicTacToe))
    game_lst.append(GameWrapper('Connect4', Connect_X))
    game_lst.append(GameWrapper('Othello', Othello))


def play_game(game, interactive = True):
    game.current_player = 1
    game.interactive = interactive
    
    while (game.condition == -1):
        if interactive:
            game.display_board()

        # Get a move from the player and ensure it is valid
        valid_move = False        
        while (not valid_move):
            move = game.get_move()
            valid_move = game.is_valid(move)

        # Make the move
        game.make_move(move)
        
    if interactive:
        game.display_board()
        if (game.condition != 0):
            print(f'Player {game.condition} is the winner!')
        else:
            print('Game is a draw.')
        sys.stdout.flush()
            
    return game.condition


def play_many_games(num_games, game, interactive = True):
    player1_wins = 0
    player2_wins = 0
    draws = 0
    for counter in range(num_games):
        game.reset()
        result = play_game(game, interactive)
        if result == 1:
            player1_wins += 1
        elif result == 2:
            player2_wins += 1
        else:
            draws += 1
            
        if not interactive:
            print(f'Played {counter} / {num_games} games. Stats: {player1_wins}/{player2_wins}/{draws} ')
            
    print(f'In {num_games} games:')
    print(f'\tPlayer 1: {player1_wins} wins')
    print(f'\tPlayer 2: {player2_wins} wins')
    print(f'\t{draws} draws')




def console_main():
    load_games()    
    game_choice = select_game()
    
    player1 = configure_player(1)
    player2 = configure_player(2)

    num_plays = 1
    if player1[0] != 'h' and player2[0] != 'h':
        num_plays_str = input("You have selected two computers.\nHow many games do you want them to play? [default=1] ").strip()
        if num_plays_str.isdigit():
            num_plays = int(num_plays_str)
                
    # Create a game object
    game = game_choice.obj()
    # Configure the players
    game.configure_player(1, player1)
    game.configure_player(2, player2)

    if num_plays == 1:
        play_game(game, True)
    else:
        play_many_games(num_plays, game, True)


def select_game():
    print("Available games\n")
    
    i=1
    for game in game_lst:
       print(f'\t{i}: {game.name}') 
       i+=1
    print("")
    while (True):
        choice_str = input("Choice: ").strip()
        if choice_str.isdigit():
            choice = int(choice_str)
            if choice > 0 and choice <= len(game_lst):
                return game_lst[choice-1]
    
    
def configure_player(n):
    while (True):
        char = input(f'Player {n}: (H)uman or (C)omputer? ').strip().lower()
        if char == 'h':
            return ['h']
        if char == 'c':
            break
        
    while (True):
        comp = []
        char = input('Algorithm: (R)andom or (M)inimax? ').strip().lower()
        if char == 'r':
            comp.append('r')
            return comp
        if char == 'm':
            comp.append('m')
            break

    print("\nThe Minimax player will play to a certain depth (d), after which " +
          "it will either evaluate the board using (b) a built-in scoring method or " +
          "by randomly sampling (r) the rest of the game tree. For random sampling, " +
          "you can set the number of samples and the depth of the sampling.\n")
    
    print("To change settings, enter e.g. 'd 10', 'b', or 'r 3 4' or press enter to continue.")

    mdepth = 2
    mscoring = 'b'
    mrandom_n = 10
    mrandom_depth = 10

    while (True):
        if mscoring == 'b':
            print(f'\nCurrent minimax settings: Depth = {mdepth}, Scoring = {mscoring}')
        else:
            print(f'\nCurrent minimax settings: Depth = {mdepth}, Scoring = {mscoring} {mrandom_n} {mrandom_depth}')
        input_str = input().strip().lower()
        if len(input_str) == 0:
            break
        if input_str[0] == 'd':
            rest = input_str[1:].strip()
            if rest.isdigit():
                mdepth = int(rest)
        if input_str == 'b':
            mscoring = 'b'
        if input_str[0] == 'r':
            params_str = input_str[1:].split()
            if len(params_str) == 2 and all(list(map(lambda x : x.isdigit(), params_str))):
                params_int = list(map(lambda x: int(x), params_str))
                mscoring = 'r'
                mrandom_n = params_int[0]
                mrandom_depth = params_int[1]

    comp.append(mdepth)
    comp.append(mscoring)
    comp.append(mrandom_n)
    comp.append(mrandom_depth)
    return comp


def commandline_main():
    try:
        lst = sys.argv.copy()
        lst.reverse()
        lst.pop()
        
        arg1 = lst.pop()
        if arg1.isdigit():
            num_plays = int(arg1)
            game_name = lst.pop()
        else:
            num_plays = 1
            game_name = arg1

        game = parse_game(game_name)
        player1 = parse_player(lst)
        player2 = parse_player(lst)
        
        if (len(lst) == 0):
            iactive = True
        else:
            arg = lst.pop()
            if arg == 'hide':
                iactive = False
            else:
                raise Exception

        if (len(lst) != 0):
            raise Exception

        game.configure_player(1, player1)
        game.configure_player(2, player2)
    
        if num_plays == 1:
            play_game(game, iactive)
        else:
            play_many_games(num_plays, game, iactive)

    #print(player1)
    except Exception:
        print("Usage: python play_game.py <name> <player1> <player2>")
        print("       python play_game.py <num_plays> <name> <player1> <player2>")
        print("       python play_game.py <num_plays> <name> <player1> <player2> hide")
        print("")
        print("\t <name> = 'Tic-Tac-Toe', 'Connect4', or 'Othello'")
        print("\t <player> = 'h', 'r', 'm 2 b', or 'm 2 r 5 2' (for example)")
    
    
def parse_game(game_name):
    if game_name == 'Tic-Tac-Toe':
        return TicTacToe()
    elif game_name == 'Connect4':
        return Connect_X()
    elif game_name == 'Othello':
        return Othello()
    else:
        raise Exception

    
def parse_player(lst):
    char = lst.pop()
    if char == 'h':
        return ['h']
    elif char == 'r':
        return ['r']
    elif char == 'm':
        comp = ['m']
        mdepth = lst.pop()
        if mdepth.isdigit():
            comp.append(int(mdepth))
        else:
            # exception
            raise Exception
        
        mscoring = lst.pop()
        if mscoring == 'b':
            comp.append('b')
            return comp
        elif mscoring  == 'r':
            comp.append('r')
            mrandom_n = lst.pop()
            if mrandom_n.isdigit():
                comp.append(int(mrandom_n))
            else:
                #exception
                raise Exception
            mrandom_depth = lst.pop()
            if mrandom_depth.isdigit():
                comp.append(int(mrandom_depth))
                return comp
            else:
                #exception
                raise Exception
        else:
            # exception
            raise Exception
    else:
        # exception
        raise Exception


if __name__ == "__main__":
    if len(sys.argv) == 1:
        console_main()
        # play_game(Connect_X(), 'human', 'comp2', True)
        #play_game(TicTacToe(), 'comp2', 'comp2', True)
        #play_many_games(10, TicTacToe(), 'comp3r', 'comp3', False)
        #play_many_games(10, Connect_X(), 'comp2r', 'comp2', True)
        #play_game(Connect_X(), 'comp2', 'comp2', True)
        #play_game_commandline(Connect_X(), 'comp2', 'comp2', True)
        #play_many_games(10, Othello(), 'comp4', 'comp4', True)
    else:
        commandline_main()
        #play_game(Connect_X(), sys.argv[1], sys.argv[2], sys.argv[3] != 'False')
        #play_many_games(int(sys.argv[4]), Connect_X(), sys.argv[1], sys.argv[2], sys.argv[3] != 'False')


