import random
import numpy as np
import queue
from statistics import mean

INFINITY = 10000

class BoardGame:

    # values of board
    XPIECE = 1
    OPIECE = -1
    EMPTY = 0

    def __init__(self, n_rows, n_cols, iactive=True):
        # instantiate the board
        self.num_rows = n_rows
        self.num_cols = n_cols
        self.board = np.zeros((self.num_rows, self.num_cols), dtype=np.int8)
        # set the move counter to zero
        self.counter = 0
                
        # conditions:
        #   -1     ongoing
        #    0     draw
        #    1     player 1 wins
        #    2     player 2 wins
        
        self.condition = -1
        
        self.last_move = None
        # queue should contain all the moves prior to last_move
        self.queue = queue.LifoQueue()

        self.current_player = 1
        self.interactive = iactive
        
        # Default to human players
        self.players = [self.get_move_human, self.get_move_human]


    def change_player(self):
        if self.current_player == 1:
            self.current_player = 2
        else:
            self.current_player = 1

    def configure_player(self, n, options):
        if options[0] == 'h':
            self.players[n-1] = self.get_move_human
        elif options[0] == 'r':
            self.players[n-1] = self.get_move_random
        elif options[0] == 'm':
            if options[2] == 'b':
                self.players[n-1] = lambda:self.get_move_minimax(options[1])
            if options[2] == 'r':
                self.players[n-1] = lambda:self.get_move_minimax(options[1], True, options[3], options[4])
                

    def get_move(self):
        return self.players[self.current_player-1]()


    def __get_move_old(self):
        # Get a move from the current player
        if self.players[self.current_player-1] == 'human':
            return self.get_move_human()
        elif self.players[self.current_player-1] == 'random':
            return self.get_move_random()
        elif self.players[self.current_player-1] == 'comp0':
            return self.get_move_minimax(0)
        elif self.players[self.current_player-1] == 'comp1':
            return self.get_move_minimax(1)
        elif self.players[self.current_player-1] == 'comp1r':
            return self.get_move_minimax(1, random_score=True)
        elif self.players[self.current_player-1] == 'comp2':
            return self.get_move_minimax(2)
        elif self.players[self.current_player-1] == 'comp2r':
            return self.get_move_minimax(2, random_score=True)
        elif self.players[self.current_player-1] == 'comp3':
            return self.get_move_minimax(3)
        elif self.players[self.current_player-1] == 'comp3r':
            return self.get_move_minimax(3, random_score=True)
        elif self.players[self.current_player-1] == 'comp4':
            return self.get_move_minimax(4)
        elif self.players[self.current_player-1] == 'comp4r':
            return self.get_move_minimax(4, random_score=True)
        elif self.players[self.current_player-1] == 'comp5':
            return self.get_move_minimax(5)
        elif self.players[self.current_player-1] == 'comp5r':
            return self.get_move_minimax(5, random_score=True)
   

    def get_move_minimax(self, depth, random_score=False, random_nums=1, random_depth=0):
        # get a list of valid moves
        moves = self.valid_moves()
        # if just one valid move, play that one
        if len(moves) == 1:
            return moves[0]
        
        # randomly shuffle them
        random.shuffle(moves)
        # pick the move that gives the biggest board score
        player = self.current_player
        scores = []
        for move in moves:
            self.make_move(move)
            score = self.minimax(0, depth, player, random_score, random_nums, random_depth)
            scores.append(score)
            self.undo_move()
        #print(f'{moves} and {scores}')
        return moves[ scores.index(max(scores)) ]        


    def get_move_random(self):
        return random.choice(self.valid_moves())


    def get_piece(self, player = None):
        if player == None:
            player = self.current_player
        if player == 1:
            return self.XPIECE
        else:
            return self.OPIECE


    # Implement a minimax-like scoring of the game tree
    def minimax(self, depth_counter, depth, player, random_score, random_nums, random_depth):
        # Handle an end condition immediately
        if self.condition > 0:
            if self.condition == player:
                # we need to penalize a win if it takes too long to happen
                # this ensures that the algorithm tries to win more quickly
                return INFINITY - depth_counter
            else:
                # conversely, a delayed loss is better
                return -INFINITY + depth_counter
        if self.condition == 0:
            return 0

        # at depth == 0, just score the board
        if depth == 0:
            # Note that score_board includes checks for winning,
            # but these should never be encountered
            if random_score:
                return self.score_board_random(player, random_nums, random_depth)
            else:
                return self.score_board(player)
        else:
            # get a list of possible moves
            moves = self.valid_moves()            
            # play each move and score the board
            scores = []
            for move in moves:
                #print(f'Minimax (depth {depth}): Considering {move}')
                self.make_move(move)
                #self.display_board()
                score = self.minimax(depth_counter+1, depth-1, player, random_score, random_nums, random_depth)
                #print(f'Minimax (depth {depth}): Score {score}')
                scores.append(score)
                self.undo_move()

            #print(f'Depth {depth}: {moves} and {scores}')
            #print(f'Player {player} for {self.current_player}\n')
                
            # return the max or min score
            if player == self.current_player:
                return max(scores)
            else:
                return min(scores)


    def random_recursive_play(self, player, depth, max_depth):
        # Check game condition
        if self.condition == -1 and depth < max_depth:
            move = random.choice(self.valid_moves())
            self.make_move(move)
            score = self.random_recursive_play(player, depth+1, max_depth)
            self.undo_move()
            return score
        elif self.condition == 0 or depth >= max_depth:
            return 0
        elif self.condition == player:
            # The importance of the win/loss is weighted by the depth
            # Additionally, weigh the value less because we're randomly sampling
            return INFINITY/depth/10
        else:
            return -INFINITY/depth/10


    # Reset the game board
    def reset(self):
        self.board = np.zeros((self.num_rows, self.num_cols), dtype=np.int8)
        self.counter = 0
        self.condition = -1
        self.last_move = None
        self.queue = queue.LifoQueue()
        self.current_player = 1


    # universal scoring algorithm using dumb Monte Carlo sampling
    def score_board_random(self, player, num_samples, max_depth):
        # score the board by randomly recursively playing it to completion (or max_depth)
        scores = []
        for _ in range(num_samples):
            scores.append(self.random_recursive_play(player, 1, max_depth))
        return mean(scores)


    def undo_move(self):
        self.board[self.last_move[0]][self.last_move[1]] = self.EMPTY
        self.last_move = self.queue.get()
        self.condition = -1
        self.counter -= 1
        self.change_player()



    # Routines to be implemented by child classes
        
    def display_board(self):
        # Display the board
        pass
    
    
    def get_move_human(self):
        # Get a move from a human
        pass


    def is_valid(self, move):
        # Is the move valid?
        return True


    def make_move(self, move):
        # update the board        
        # update the game metadata, e.g. as follows
        self.queue.put(self.last_move)
        self.last_move = move
        self.counter += 1
        self.update_condition()
        self.change_player()


    def score_board(self, player):
        # Heuristically score the board
        return 0

    def update_condition(self):
        # Update the condition of the board
        pass

    def valid_moves(self):
        # Return list of possible moves
        return []

    

class TicTacToe(BoardGame):

    def __init__(self, n_rows=3, n_cols=3, x=3):
        super().__init__(n_rows, n_cols)
        # number of pieces in a row to win
        self.connect_x = x


    def check_draw(self):
        if self.counter >= self.num_rows * self.num_cols:
            return True
        else:
            return False
        

    def check_win(self):
        # To check for a win, we just need to look at the 
        # nearest neighbors of the move that was just made
    
        current_piece = self.get_piece()

        # check column
        if self.__check_in_a_row(self.last_move, current_piece, [1,0]):
            return True
    
        # check row
        if self.__check_in_a_row(self.last_move, current_piece, [0,1]):
            return True
    
        # check upper diagonal
        if self.__check_in_a_row(self.last_move, current_piece, [1,1]):
            return True
    
        # check lower diagonal
        if self.__check_in_a_row(self.last_move, current_piece, [1,-1]):
            return True

        return False


    def display_board(self):
        # Display the current board
        print("")
        row_label = 'a'
        for row in self.board:
            print(row_label+' ', end="")
            for element in row:
                if element == self.EMPTY:
                    print("_", end = " ")
                elif element == self.XPIECE:
                    print("X", end = " ")
                elif element == self.OPIECE:    
                    print("O", end = " ")
            print("")
            row_label = chr(ord(row_label)+1)
            
        print("  ", end="")
        for i in range(self.num_cols):
            print(f'{i+1}', end = ' ')
        print("")
        print("")


    def get_move_human(self):
        # Get a move from the current player
        move_str = ' '
        move_int = 0
        while (True):
            move_str = input(f"Player {self.current_player}: ").strip()
            if len(move_str) != 2:
                continue
            if not move_str[0].isalpha() or not move_str[1].isdigit():
                continue
            else:
                row = ord(move_str[0]) - ord('a')
                col = int(move_str[1])
                if col < 1 or col > self.num_cols or row < 0 or row > self.num_rows-1:
                    continue
                else:
                    break
        # internally we index columns from 0 .. num_cols-1
        return [row, col-1]


    def get_move_random(self):
        move = super().get_move_random()
        if self.interactive:
            print(f"Player {self.current_player}: "+ self.unconvert_move(move))
        return move


    def get_move_minimax(self, *args, **kwargs):
        move = super().get_move_minimax(*args, **kwargs)
        if self.interactive:
            print(f"Player {self.current_player}: "+ self.unconvert_move(move))
        return move


    def is_valid(self, move):
        # check if the current move is valid
        if self.board[move[0]][move[1]] == self.EMPTY:
            return True
        else:
            return False


    def make_move(self, move):
        self.board[move[0]][move[1]] = self.get_piece()
        self.queue.put(self.last_move)
        self.last_move = move
        self.counter += 1
        self.update_condition()
        self.change_player()

 
    def update_condition(self):
        if self.check_win():
            self.condition = self.current_player
        elif self.check_draw():
            self.condition = 0


    def valid_moves(self):
        moves = []
        row = 0
        col = 0
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.board[row][col] == self.EMPTY:
                    moves.append([row,col])
        return moves
    
    def convert_move(self, move_str):
        return [ord(move_str[0]) - ord('a'), int(move_str[1])-1]
    
    
    def unconvert_move(self, move):
        return chr(move[0]+ord('a')) + str(move[1]+1)


    def unconvert_moves(self, moves):
        moves_str = []
        for move in moves:
            moves_str.append( self.unconvert_move(move) )
        return moves_str

        
    # check if there are <current_piece> pieces in a line
    #   <interval> defines the direction (x,y) of the line
    def __check_in_a_row(self, last_move, current_piece, interval):
        # Coordinates of the last_move made
        x = last_move[0]
        y = last_move[1]
        
        # count how many steps up we can make in the <interval> direction
        step_up = 0
    
        # we can use try/catch blocks to handle when we go out of bounds
        try:
            while (x+(step_up+1)*interval[0] >= 0 and
                   y+(step_up+1)*interval[1] >= 0 and
                   self.board[x+(step_up+1)*interval[0], y+(step_up+1)*interval[1]] == current_piece):
                step_up +=1
        except IndexError:
            pass
    
        # count how many steps down we can make in the <interval> direction
        step_down = 0
    
        # we can use try/catch blocks to handle when we go out of bounds
        # but we also need to handle Python allowing negative indices :-/
        try:
            while (x-(step_down+1)*interval[0] >= 0 and
                   y-(step_down+1)*interval[1] >= 0 and
                   self.board[x-(step_down+1)*interval[0], y-(step_down+1)*interval[1]] == current_piece):
                step_down += 1
        except IndexError:
            pass
    
        if step_up + step_down >= self.connect_x - 1:
            return True
        else:
            return False



class Connect_X(BoardGame):

    def __init__(self, n_rows=6, n_cols=7, x=4):
        super().__init__(n_rows, n_cols)
        # size of connect_x board (for x=4)
        self.connect_x = x


    def check_draw(self):
        if self.counter >= self.num_rows * self.num_cols:
            return True
        else:
            return False


    def check_win(self):
        # To check for a win, we just need to look at the 
        # nearest neighbors of the move that was just made
    
        current_piece = self.get_piece()

        # check column
        if self.__check_in_a_row(self.last_move, current_piece, [1,0]):
            return True
    
        # check row
        if self.__check_in_a_row(self.last_move, current_piece, [0,1]):
            return True
    
        # check upper diagonal
        if self.__check_in_a_row(self.last_move, current_piece, [1,1]):
            return True
    
        # check lower diagonal
        if self.__check_in_a_row(self.last_move, current_piece, [1,-1]):
            return True

        return False


    def display_board(self):
        # Display the current board
        print("")
        for row in self.board:
            for element in row:
                if element == self.EMPTY:
                    print("_", end = " ")
                elif element == self.XPIECE:
                    print("X", end = " ")
                elif element == self.OPIECE:    
                    print("O", end = " ")
            print("")
        for i in range(self.num_cols):
            print(f'{i+1}', end = ' ')
        print("")
        print("")


    def get_move_human(self):
        # Get a move from the current player
        move_str = ' '
        move_int = 0
        while (True):
            move_str = input(f"Player {self.current_player}: ")
            if not move_str.strip().isdigit():
                continue
            else:
                move_int = int(move_str)
                if move_int < 1 or move_int > self.num_cols:
                    continue
                else:
                    break
        # internally we index columns from 0 .. num_cols-1
        return (move_int-1)


    def get_move_random(self):
        move = super().get_move_random()
        if self.interactive:
            print(f"Player {self.current_player}: {move+1}")
        return move
    
    def get_move_minimax(self, *args, **kwargs):
        move = super().get_move_minimax(*args, **kwargs)
        if self.interactive:
            print(f"Player {self.current_player}: {move+1}")
        return move


    def is_valid(self, move):
        # check if the current move is valid
        if self.board[0][move] == self.EMPTY:
            return True
        else:
            return False


    def make_move(self, move):
        # Find where the available slot is    
        for i in range(self.num_rows-1):
            if self.board[i+1][move] != self.EMPTY:
                # i is the correct row
                if self.board[i][move] != self.EMPTY:
                    raise Exception('Illegal move')
                self.board[i][move] = self.get_piece()
                self.queue.put(self.last_move)
                self.last_move = [i, move]       
                self.counter += 1
                self.update_condition()
                self.change_player()
                return

        # Outside of the for loop, i+1 is the correct row.
        # Don't need to check for empty because logically that
        # check has already happened in the for loop
        
        self.board[i+1][move] = self.get_piece()
        self.queue.put(self.last_move)
        self.last_move = [i+1, move]
        self.counter += 1
        self.update_condition()
        self.change_player()
        return
        

    # potential refinement is to ignore all squares that cannot matter
    def score_board(self, player):
        if self.condition > 0:
            if self.condition == player:
                return INFINITY
            else:
                return -INFINITY
        if self.condition == 0:
            return 0

        # otherwise score the board
        score = 0
        # score each row
        for row in self.board:
            score += self.__list_score(np.trim_zeros(row), player)
        # score each column (using numpy's transpose)
        for column in self.board.T:
            score += self.__list_score(np.trim_zeros(column), player)
        
        # score each diagonal
        for i in range(-self.num_rows+1,self.num_cols):
            diagonal = np.diagonal(self.board, offset=i)
            score += self.__list_score(np.trim_zeros(diagonal), player)

        # score each anti-diagonal
        for i in range(-self.num_rows+1,self.num_cols):
            diagonal = np.diagonal(np.fliplr(self.board), offset=i)
            score += self.__list_score(np.trim_zeros(diagonal), player)

        return score


    def update_condition(self):
        if self.check_win():
            self.condition = self.current_player
        elif self.check_draw():
            self.condition = 0


    def valid_moves(self):
        # return list of valid moves
        lst = []
        for i in range(self.num_cols):
            if self.board[0][i] == self.EMPTY:
                lst.append(i)
        return lst


        

    
    

    # check if there are <current_piece> pieces in a line
    #   <interval> defines the direction (x,y) of the line
    def __check_in_a_row(self, last_move, current_piece, interval):
        # Coordinates of the last_move made
        x = last_move[0]
        y = last_move[1]
        
        # count how many steps up we can make in the <interval> direction
        step_up = 0
    
        # we can use try/catch blocks to handle when we go out of bounds
        try:
            while (x+(step_up+1)*interval[0] >= 0 and
                   y+(step_up+1)*interval[1] >= 0 and
                   self.board[x+(step_up+1)*interval[0], y+(step_up+1)*interval[1]] == current_piece):
                step_up +=1
        except IndexError:
            pass
    
        # count how many steps down we can make in the <interval> direction
        step_down = 0
    
        # we can use try/catch blocks to handle when we go out of bounds
        # but we also need to handle Python allowing negative indices :-/
        try:
            while (x-(step_down+1)*interval[0] >= 0 and
                   y-(step_down+1)*interval[1] >= 0 and
                   self.board[x-(step_down+1)*interval[0], y-(step_down+1)*interval[1]] == current_piece):
                step_down += 1
        except IndexError:
            pass
    
        if step_up + step_down >= self.connect_x - 1:
            return True
        else:
            return False

            
    # Score an nparray of integers against the current_piece
    def __list_score(self, array, player):
        # for an nparray of numbers, score them
        
        # We will assume that array has been trimmed of zeros
        # at the beginning and end. There may still be zeros
        # in the middle.
        
        try:
            last_piece = array[0]
        except IndexError:
            return 0

        current_piece = self.get_piece(player)
        
        score = 0 
        streak = 1

        # This implementation counts streaks of zeros but doesn't score them
        for i in range(1, len(array)):
            if array[i] == last_piece:
                streak += 1
            else:
                # score the last streak
                if last_piece == 0:
                    pass
                elif last_piece == current_piece:
                    score += streak**3
                else:
                    score -= streak**3
                last_piece = array[i]
                streak = 1
                
        # score the final streak
        if last_piece == current_piece:
            score += streak**3
        else:
            score -= streak**3

        # print(f'{array} has score {score}')
        return score
                
        
class Othello(BoardGame):
    
    def __init__(self, n_rows=8, n_cols=8):
        super().__init__(n_rows, n_cols)
        
        # initial board configuration for Othello
        self.board[n_rows//2][n_cols//2] = self.OPIECE
        self.board[n_rows//2-1][n_cols//2] = self.XPIECE
        self.board[n_rows//2][n_cols//2-1] = self.XPIECE
        self.board[n_rows//2-1][n_cols//2-1] = self.OPIECE
        
        # Counter to keep track of if we pass
        self.num_passes = 0



    def display_board(self):
        # Display the current board
        print("")
        row_label = 'a'
        for row in self.board:
            print(row_label+' ', end="")
            for element in row:
                if element == self.EMPTY:
                    print("_", end = " ")
                elif element == self.XPIECE:
                    print("X", end = " ")
                elif element == self.OPIECE:    
                    print("O", end = " ")
            print("")
            row_label = chr(ord(row_label)+1)
            
        print("  ", end="")
        for i in range(self.num_cols):
            print(f'{i+1}', end = ' ')
        print("")
        print("")
        #self.display_valid_moves()


    
    
    def get_move(self):
        # make sure there is a valid move
        if self.is_any_valid_move():
            return super().get_move()
        else:
            if self.interactive:
                print("No valid move.")
            # If there is no valid move, return None
            return None


    def get_move_human(self):
        # Get a move from the current player
        while (True):
            move_str = input(f"Player {self.current_player}: ").strip()
            if len(move_str) != 2:
                continue
            if not move_str[0].isalpha() or not move_str[1].isdigit():
                continue
            else:
                row = ord(move_str[0]) - ord('a')
                col = int(move_str[1])
                if col < 1 or col > self.num_cols or row < 0 or row > self.num_rows-1:
                    continue
                else:
                    break
        # internally we index columns from 0 .. num_cols-1
        return [row, col-1]
        

    def get_move_random(self):
        move = super().get_move_random()
        if self.interactive:
            print(f"Player {self.current_player}: "+ self.unconvert_move(move))
        return move
    
    def get_move_minimax(self, *args, **kwargs):
        move = super().get_move_minimax(*args, **kwargs)
        if self.interactive:
            print(f"Player {self.current_player}: "+ self.unconvert_move(move))
        return move
        

        
    def is_valid(self, move):
        if move == None:
            # no valid move available so we skip a turn
            return True

        # check if the current move is valid
        try:
            if self.board[move[0]][move[1]] != self.EMPTY:
                return False
        except IndexError:
            return False
        # Determine our piece and oppo piece
        current_piece = self.get_piece()
        if current_piece == self.XPIECE:
            oppo_piece = self.OPIECE
        else:
            oppo_piece = self.XPIECE

        # check rows/columns/diagonals for a valid move
        intervals = [ [0,1], 
                     [0,-1],
                     [1,0],
                     [-1,0],
                     [1,1],
                     [-1,-1],
                     [1,-1],
                     [-1,1] ]

        for interval in intervals:
            try:
                row = move[0]+interval[0]
                col = move[1]+interval[1]
                
                '''
                valid move means there is some direction where we find some number
                of opponent pieces, followed by one of our pieces
                '''
                
                if (self.board[row][col] == oppo_piece and
                    row >= 0 and
                    col >= 0):
                    row += interval[0]
                    col += interval[1]                    
                    while (self.board[row][col] == oppo_piece and
                           row >= 0 and
                           col >= 0):
                        row += interval[0]
                        col += interval[1]
                    if (self.board[row][col] == current_piece and
                        row >= 0 and
                        col >= 0):
                        return True
            except IndexError:
                # we ran off the end of the board
                pass

        # If we didn't find anything, return False
        return False    
    

    def make_move(self, move):
        if move == None:
            # If no valid move, don't bother storing the board state
            self.queue.put([self.num_passes, None])
            self.num_passes += 1
        else:
            # Entire prior board state must be saved
            # along with the number of passes that have occurred
            self.queue.put([self.num_passes, self.board.copy()])
            self.num_passes = 0

            current_piece = self.get_piece()
            if current_piece == self.XPIECE:
                oppo_piece = self.OPIECE
            else:
                oppo_piece = self.XPIECE
    
            # Flip all pieces, reusing code from is_valid
            
            intervals = [ [0,1], 
                         [0,-1],
                         [1,0],
                         [-1,0],
                         [1,1],
                         [-1,-1],
                         [1,-1],
                         [-1,1] ]
            
            for interval in intervals:
                try:
                    row = move[0]+interval[0]
                    col = move[1]+interval[1]
                    step = 1
    
                    if (self.board[row][col] == oppo_piece and
                        row >= 0 and
                        col >= 0):
                        row += interval[0]
                        col += interval[1]
                        step += 1
                        while (self.board[row][col] == oppo_piece and
                               row >= 0 and
                               col >= 0):
                            row += interval[0]
                            col += interval[1]
                            step += 1
                        if (self.board[row][col] == current_piece and
                            row >= 0 and
                            col >= 0):
                            # flip all the pieces
                            # step = num_pieces_to_flip + 1
                            while (step > 0):
                                row -= interval[0]
                                col -= interval[1]
                                self.board[row][col] = current_piece
                                step -= 1
                except IndexError:
                    # we ran off the end of the board
                    pass
                
        self.counter += 1
        self.update_condition()
        self.change_player()

 
    # Reset the game board
    def reset(self):
        self.board = np.zeros((self.num_rows, self.num_cols), dtype=np.int8)
        
        # initial board configuration for Othello
        self.board[self.num_rows//2][self.num_cols//2] = self.OPIECE
        self.board[self.num_rows//2-1][self.num_cols//2] = self.XPIECE
        self.board[self.num_rows//2][self.num_cols//2-1] = self.XPIECE
        self.board[self.num_rows//2-1][self.num_cols//2-1] = self.OPIECE

        self.counter = 0
        self.condition = -1
        self.last_move = None
        self.queue = queue.LifoQueue()
        self.current_player = 1


    def score_board(self, player=1):
        if player == 1:
            return np.sum(self.board)
        else:
            return -np.sum(self.board)


    def undo_move(self):
        self.condition = -1
        self.counter -= 1
        self.change_player()

        if self.num_passes == 0:
            temp = self.queue.get()
            self.num_passes = temp[0]
            self.board = temp[1]
        else:
            temp = self.queue.get()
            self.num_passes = temp[0]
            # board hasn't changed


    def update_condition(self):
        if self.num_passes >= 2:
            score = self.score_board()
            if score > 0:
                self.condition = 1
            elif score < 0:
                self.condition = 2
            else:
                self.condition = 0


    def valid_moves(self):
        moves = []
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.is_valid([row,col]):
                    moves.append([row,col])
        if len(moves) > 0:
            return moves
        else:
            return [None]


    # This is faster than computing an additional valid_moves every time
    def is_any_valid_move(self):
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                if self.is_valid([row,col]):
                    return True
        return False


    def display_valid_moves(self):
        moves = self.valid_moves()
        if moves == [None]:
            valid_moves_str = ['None']
        else:
            valid_moves_str = self.unconvert_moves(self.valid_moves())
        print('Valid moves: ', end="")
        for valid_move_str in valid_moves_str:
            print(valid_move_str, end = ' ')
        print("")
    

    def convert_move(self, move_str):
        return [ord(move_str[0]) - ord('a'), int(move_str[1])-1]
    
    
    def unconvert_move(self, move):
        return chr(move[0]+ord('a')) + str(move[1]+1)


    def unconvert_moves(self, moves):
        moves_str = []
        for move in moves:
            moves_str.append( self.unconvert_move(move) )
        return moves_str

