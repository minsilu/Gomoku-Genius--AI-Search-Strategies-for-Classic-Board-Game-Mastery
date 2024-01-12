from __future__ import print_function

from game import Board, DummyPlayer, Human, Game
from minimax import MinimaxSearchPlayer, AlphaBetaSearchPlayer, CuttingOffAlphaBetaSearchPlayer
from mcts import MCTSPlayer
from alphazero import AlphaZeroPlayer
from evaluation import get_evaluation_func


def get_player(player_name, args):
    if player_name == "DummyPlayer":
        return DummyPlayer()
    elif player_name == "Human":
        return Human()
    elif player_name == "MinimaxSearchPlayer":
        return MinimaxSearchPlayer()
    elif player_name == "AlphaBetaSearchPlayer":
        return AlphaBetaSearchPlayer()
    elif player_name == "CuttingOffAlphaBetaSearchPlayer":
        return CuttingOffAlphaBetaSearchPlayer(args.max_depth, get_evaluation_func(args.evaluation_func))
    elif player_name == "MCTSPlayer":
        return MCTSPlayer(args.c, args.n_playout)
    elif player_name == "AlphaZeroPlayer":
        return AlphaZeroPlayer(get_evaluation_func(args.evaluation_func), args.c, args.n_playout)
    else:
        raise KeyError(player_name)


def run(args):
    n = args.n_in_row
    width, height = args.width, args.height
    try:
        board = Board(width=width, height=height, n_in_row=n)
        game = Game(board)
        player_1 = get_player(args.player_1, args)
        player_2 = get_player(args.player_2, args)
        # set start_player=0 for human first
        winner = game.start_play(player_1, player_2, start_player=0, is_shown=1)
        return winner
    except KeyboardInterrupt:
        print('\n\rquit')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--width", type=int, default=9, help="Width of board.")
    parser.add_argument("--height", type=int, default=9, help="Height of board.")
    parser.add_argument("--n_in_row", type=int, default=5, help="Number of pieces in a row to win.")
    parser.add_argument("--player_1", type=str, default="DummyPlayer", \
        choices=["Human", "DummyPlayer", "MinimaxSearchPlayer", "AlphaBetaSearchPlayer", "CuttingOffAlphaBetaSearchPlayer", "MCTSPlayer", "AlphaZeroPlayer"], \
            help="Agent of Player 1")
    parser.add_argument("--player_2", type=str, default="DummyPlayer", \
        choices=["Human","DummyPlayer", "MinimaxSearchPlayer", "AlphaBetaSearchPlayer", "CuttingOffAlphaBetaSearchPlayer", "MCTSPlayer", "AlphaZeroPlayer"], \
            help="Agent of Player 2")
    
    parser.add_argument("--max_depth", type=int, default=1, help="Maximum search depth (CuttingOffAlphaBetaSearch only).")
    parser.add_argument("--evaluation_func", type=str, default="dummy_evaluation_func",\
        choices=["dummy_evaluation_func","detailed_evaluation_func"],
        help="Evaluation function (CuttingOffAlphaBetaSearch/AlphaZero only).")
    parser.add_argument("--c", type=float, default=1, help="Trade-off hyperparameter (MCTS/AlphaZero only).")
    parser.add_argument("--n_playout", type=int, default=5000, help="Number of playouts (MCTS/AlphaZero only).")
    args = parser.parse_args()

    if (args.player_1 == "MCTSPlayer" and args.player_2 == "AlphaZeroPlayer") or \
        (args.player_1 == "AlphaZeroPlayer" and args.player_2 == "MCTSPlayer") or \
        (args.player_1 == "CuttingOffAlphaBetaSearchPlayer" and args.player_2 == "MCTSPlayer") or \
        (args.player_1 == "CuttingOffAlphaBetaSearchPlayer" and args.player_2 == "CuttingOffAlphaBetaSearchPlayer") or \
        (args.player_1 == "MCTSPlayer" and args.player_2 == "CuttingOffAlphaBetaSearchPlayer"):
        print("Next, the game will be played 10 times, the result will be saved to the result/result.txt.")
        play1_win = 0
        play2_win = 0
        play_tie = 0
        for i in range(10):
            winner = run(args)
            if winner == 1:
                play1_win += 1
            elif winner == 2:
                play2_win += 1
            elif winner == -1:
                play_tie += 1
        # 将结果写入result文件夹下的result.txt文件中
        # 代码如下：
        with open("result/result.txt", "a") as f:
            f.write("player1: %s, player2: %s, play1_win: %d, play2_win: %d, tie: %d \n" % (args.player_1, args.player_2, play1_win, play2_win, play_tie))    
    # 连跑5次, 之后修改为1次
    run(args)
