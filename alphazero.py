import copy
from game import State, Player
from mcts import MCTS


class AlphaZero(MCTS):
    """
    A modification based on pure MCTS, replacing randomly playout with using an evaluation function.
    """
    def __init__(self, start_state: State, evaluation_func, c=5, n_playout=10000):
        """
        Parameters:
            evaluation_func: a function taking a state as input and
                outputs the value in the current player's perspective.
        """
        super().__init__(start_state, c, n_playout)
        self.evaluation_func = evaluation_func

    def get_leaf_value(self, state: State):
        # TODO
        # 基于随机游戏并不是很好的方案，重新使用评估函数代替随机游戏过程
        # 调用评估函数得到，直接作为权值估计即可，不需要再按照这个评估函数游戏至分出胜负
        current_player = state.get_current_player()
        end, winner = state.game_end()
        if end:
            if winner == -1:  
                return 0
            else:
                return 1 if winner == current_player else -1
        return self.evaluation_func(state)


class AlphaZeroPlayer(Player):
    """AI player based on MCTS"""
    def __init__(self, evaluation_func, c=5, n_playout=2000):
        super().__init__()
        self.evaluation_func = evaluation_func
        self.c = c
        self.n_playout = n_playout

    def get_action(self, state: State):
        mcts = AlphaZero(state, self.evaluation_func, self.c, self.n_playout)
        for n in range(self.n_playout):
            state_copy = copy.deepcopy(state)
            mcts.playout(state_copy)
        return max(mcts.root.children.items(),
                   key=lambda act_node: act_node[1].n_visits)[0]
