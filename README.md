# play_game
#### Video Demo: https://www.youtube.com/watch?v=Hfsw9vOZe9w
#### Description:
play_game is a command-line Python program where the user can play three different board games (Tic-Tac-Toe, Connect 4, and Othello) against another human or againt various computer agents.

This was initially inspired by the classic 1980's film "War Games" where a supercomputer takes control of NORAD's ballistic missile network and almost starts World War III. The climactic scene involves tricking the computer into playing Tic-Tac-Toe, to each it that some games are unwinnable. While I originally had intended a more involved neural network approach to playing some of these games, I eventually settled for a much humbler approach in order to finish on time.

There are two files:
* board_games.py
* play_game.py


### <u>board_games.py</u>
#### ``BoardGame``
The base class ``BoardGame`` is introduced here to describe a two-player turn-based game played on a fixed size m x n board, where each square can be empty or occupied by one or the other player's pieces. These are denoted X and O for command-line play.

The fundamental attributes of this base class are:
* ``num_rows`` and ``num_cols``: the dimensions of the board
* ``board``: an np.array storing the current board state. The states are coded as ``EMPTY`` (0), ``XPIECE`` (+1), or ``OPIECE`` (-1).
* ``counter``: a move counter, incrementing with every move
* ``current_player``: either 1 (X) or 2 (O)
* ``condition``: current condition of the game stored as an integer: an ongoing game (-1), a draw (0), or a win for a player (1 or 2)
* ``interactive``: a boolean controlling whether the board game can communicate information to the player
* ``last_move``: the last move made
* ``queue``: a FILO queue storing the moves, necessary in order to undo moves when traversing the game tree

The methods of the base class are given below (with arguments suppressed). Several are not implemented in the base class, since they will be highly dependent on the game.
* ``__init__()`` and ``configure_player()``: These initialize the board state and configure the player agent.
* ``reset()``: Resets the board to its initial state.
* ``get_piece()``: Returns ``XPIECE`` or ``OPIECE`` associated with a given player (or ``current_player``).
* ``is_valid()``: Takes a move and returns a boolean whether it is valid.
* ``valid_moves()``: Returns a list of valid moves given the current board state. The data type of a "move" is not defined in the base class. Typically, it will be a doublet of integers labelling the square, but could be simpler. (In Connect 4, it is a single integer labelling the column.)
* ``display_board()``: Displays the board. (**Not implemented in base.**)
*  Methods for retrieving a move from a player:
    * ``get_move_human()``: Get a move from a human agent. (**Not implemented in base.**) 
    * ``get_move_random()``: Generates a random move from the available valid moves.
    * ``get_move_minimax()``: Generates a move using the Minimax algorithm. (Details below.)
    * ``players[2]()``: Array of two methods to be used for Player 1 and Player 2. These will call one of the three ``get_move_*`` methods above.
    * ``get_move()``: High level function that gets the next move from the current player.

* ``make_move()``: Takes a move as an argument and makes it for the current player. In addition to updating the board state (**Not implemented in base**), this method will call:
    * ``change_player()``: changes the current player
    * ``update_condition()``: updates the game condition. (**Not implemented in base.**)
* ``undo_move()``: Undoes the last move. A ``make_move()`` followed by ``undo_move()`` should leave the game and all its elements unchanged.

The above are all associated with obvious game dynamics. In addition, several methods are required for the Minimax computer player:
* ``score_board()``: This scores the board for a specific player, returning an integer between -INFINITY and +INFINITY (stored as 10000) depending on how good or bad the current board is for the given player. This is specifically coded for each game. (**Not implemented in base**.)
* ``score_board_random()``: A **universal** scoring algorithm applicable to any game. It works by a dumb version of Monte Carlo sampling, playing a number of games randomly to completion and tallying wins and losses and averaging the score. This calls a recursive function:
    * ``random_recursive_play()``: Plays a game randomly to completion. Returns a score suppressed by how deeply we had to go to find a win/loss. (Deep wins or losses are less trustworthy.)

Note that ``score_board()`` and ``score_board_random()`` are not normalized with respect to each other. That is, one should not expect that a board should receive a similar score from both functions.

The most complicated base method is:

* ``minimax()``: Implements the naive (unoptimized) Minimax algorithm to score each of the possible moves for a given player. It traverses the game tree to a fixed depth or to a terminal node (win/loss/draw). A win returns +INFINITY, a loss returns -INFINITY, and a draw returns 0. At each level, the "optimum" move is chosen (either maximizing the score or minimizing it depending on the player). When reaching a fixed depth node that is not terminal, it scores the board either with ``score_board()`` or ``score_board_random()``. (When the latter is chosen, this is essentially some hybrid of Monte Carlo Minimax, since we deterministically traverse to some depth and then switch over to random sampling. Probably this could be done more intelligently!)


#### ``TicTacToe``
The child class ``TicTacToe`` implements Tic-Tac-Toe. This is a very simple game to implement. Since I implemented it after Connect 4, it reuses a number of functions for checking for streaks in rows, columns, or diagonals that are overkill for Tic-Tac-Toe.


#### ``Connect_X``
The child class implements a generalized version of Connect 4. The streak size x (stored in ``connect_x``) and board dimensions are chosen whenever a game is created and default to the conventional Connect 4. (This was the first game I implemented, eventually moving much of its functionality to the ``BoardGame`` base class.)

Aside from the public methods inherited from and redefined from ``BoardGame``, there are two private methods:
* ``__check_in_a_row()``: Given a starting point and a direction, this returns a boolean if the starting point is contained within a sufficient sized streak. (For a given direction vector, this looks in both "positive" and "negative" directions.)
* ``__list_score()``: Scores a line of numbers, corresponding to a subset of a row, column, or diagonal, used in ``score_board()``.

The implementation of ``score_board()`` used in Connect_X is really quite stupid. I just give points for streaks of size 2 and 3 (so this is poorly designed for generic Connect_X). No attempt is made to preference having empty space around to grow. Originally I had planned to modify this, but I found that ``score_board_random()`` actually played quite well against ``score_board()``, so for Connect 4, the random version of Minimax is to be preferred.

I grew to appreciate the use of exceptions when indexing beyond the end of an array, since it eliminated the need to explicitly avoid running off the edge of the board when counting pieces in a streak. However, this was balanced by the fact that Python allows negative indices.


#### ``Othello``
This implements the game Othello (i.e Reversi with a fixed initial configuration). Like Connect 4, the board size can be changed upon instantiation but defaults to the standard 8x8 board.

Unlike Connect 4 and Tic-Tac-Toe, the Othello board is highly dynamic, with player moves flipping other pieces. This required me to overhaul how ``undo_move()`` works, storing not just the last moves, but all of the previous board states. Also, Othello incorporates "pass" moves where a player is not able to make a move. This is implemented by making a move whose value is ``None``. Gameplay ends when two successive passes occur. This is kept track of by the ``num_passes`` variable. I was stymied for hours by a silly bug where I had forgotten that I needed to keep track of the previous ``num_passes`` values as well for ``undo_move()`` to work properly.

Unlike Connect 4, there is an obvious implementation for ``score_board()``: taking the difference in the number of pieces, since this is how the winner is determined.

A few methods have been left that I used for debugging. These are:
* ``display_valid_moves()``: Originally called by ``display_board()``, this shows all the valid moves.
* ``convert_move()``, ``unconvert_move()``, ``unconvert_moves()``: Methods to convert between alphanumeric board labels and zero-indexed doublets.




### <u>play_game.py</u>
This is the console program that implements game play. It includes a ``GameWrapper`` class that includes a name and a ``BoardGame`` object. These are limited to Tic-Tac-Toe, Connect 4, and Othello for the moment.

When started without any command-line arguments, the ``console_main()`` function is called, which gives the user a choice of game. Upon choosing a game, the user must assign either a human or a computer agent to Player 1 and Player 2. A computer agent may be either random or Minimax, and one can choose the depth of the Minimax tree as well as the parameters of ``score_board_random`` (if a Monte-Carlo Minimax is chosen). If two computer players are chosen, the user can ask for any number of games to be played, with statistics collected. I found this useful to gauge how the computer agents were doing vs. random play and vs. each other.

The user may also specify command-line arguments to bypass the menu and go directly to play. These are fairly self-explanatory in the code and in the Usage text.



### <u>Additional comments</u>
My original vision for this project turned out to be a bit too ambitious. I had hoped to implement some sort of convolutional neural network (which is why I had used np.array to begin with). While I found some guides for using off-the-shelf libraries, I decided it would take me too far afield to fully implement those.

When this was originally Connect 4 alone, I had toyed with the idea of using pygame to draw the board, or to implement via Ajax and Javascript on a webserver to play. However, I decided it would be more interesting to spend the time developing Othello and to try to refine the Minimax algorithm.

The current command-line implementation makes it simple to collect statistics about computer agents. For example, I was able to experimentally observe the theoretical result that perfect play in 4 x 4 Othello leads to a second player win. Supposedly this is true for 6 x 6 Othello as well, but this was not so obvious when I cranked up my Minimax parameters. I would like to extend this project a bit more later to show statistics for 8 x 8 Othello as the Minimax parameters are increased.

Another potential improvement would be to implement a time-based rather than depth-based limit for the AI.

