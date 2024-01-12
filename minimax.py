from typing import Tuple
from copy import deepcopy
from game import State, Player

inf = 10000


class MinimaxSearchPlayer(Player):
    """
    Player based on minimax search.
    """

    def get_action(self, state: State):
        """
        An interface for recursively searching.
        """
        assert state.get_current_player() == self.player

        def minimax_search(s: State) -> Tuple:
            """
            Recursively search values of all succeeding nodes, taking maximum of children
            when current player is the agent (self.player) and minimum for opponent.

            Parameters:
                s: the current state

            Return:
                Tuple(value, action): the node value and the best action (if exists)
            
            Note: before you perform an action, you might need to copy the original state for in-place update.
            """
            end, winner = s.game_end()
            value, action = None, None
            if end: # game end
                if winner == -1:
                    value = 0 # draw
                else:
                    value = (1 if winner == self.player else -1) # win or lose
            else:
                if s.get_current_player() == self.player:
                    value = float('-inf')
                    for a in s.get_all_actions(): # 遍历当前状态的合法动作集合
                        child_state = deepcopy(s)   # 深拷贝当前状态
                        child_state.perform_action(a)  # R(s,a)  执行动作a，变成了下一个状态
                        child_value, _ = minimax_search(child_state) # 递归调用，false表示最小值玩家
                        if child_value > value:
                            value = child_value
                            action = a
                else:
                    value = float('inf')
                    for a in s.get_all_actions():
                        child_state = deepcopy(s)
                        child_state.perform_action(a)
                        child_value, _ = minimax_search(child_state)
                        if child_value < value:
                            value = child_value
                            action = a
                            
            return value, action
        
        return minimax_search(state)[1] # 返回最优动作


class AlphaBetaSearchPlayer(Player):
    """
    Player based on alpha-beta search.
    """

    def get_action(self, state: State):
        """
        An interface for recursively searching.
        """
        assert state.get_current_player() == self.player

        def alpha_beta_search(s: State, alpha, beta):
            """
            Based on minimax search, record current maximum value of the max player (alpha)
            and current minimum value of the min player (beta), use alpha and beta to prune.

            Parameters:
                s: the current state
                alpha: the current maximum value of the max player
                beta: the current minimum value of the min player

            Return:
                Tuple(value, action): the node value and the best action (if exists)
            
            Note: before you perform an action, you might need to copy the original state for in-place update.
            """
            end, winner = s.game_end()
            value, action = None, None
            if end:
                if winner == -1:
                    value = 0
                else:
                    value = (1 if winner == self.player else -1)
            else:
                if s.get_current_player() == self.player:  
                    value = float('-inf')
                    for a in s.get_all_actions():
                        child_state = deepcopy(s)
                        child_state.perform_action(a)
                        child_value, _ = alpha_beta_search(child_state, alpha, beta)
                        if child_value > value: # 取最大value
                            value = child_value
                            action = a
                        if value >= beta:
                            break  # Pruning
                        alpha = max(alpha, value)

                else:  
                    value = float('inf')
                    for a in s.get_all_actions():
                        child_state = deepcopy(s)
                        child_state.perform_action(a)
                        child_value, _ = alpha_beta_search(child_state, alpha, beta)
                        if child_value < value: # 取最小value
                            value = child_value
                            action = a
                        if value <= alpha: 
                            break  # Pruning
                        beta = min(beta, value)

            return value, action

        return alpha_beta_search(state, -inf, inf)[1] # 初始化alpha和beta


class CuttingOffAlphaBetaSearchPlayer(Player):

    def __init__(self, max_depth, evaluation_func=None):
        """
        Player based on cutting off alpha-beta search.
        Parameters:
            max_depth: maximum searching depth. The search will stop when the depth exists max_depth.
            evaluation_func: a function taking a state as input and
                outputs the value in the current player's perspective.
        """
        super().__init__()
        self.max_depth = max_depth
        self.evaluation_func = (lambda s: 0) if evaluation_func is None else evaluation_func

    def evaluation(self, state: State):
        """
        Calculate the evaluation value relative to the agent player (rather than state's current player),
        i.e., take negation if the current player is opponent or do nothing else wise.
        """
        # 转化为player perspective
        value = self.evaluation_func(state)
        if self.player != state.get_current_player():
            value = -value
        return value

    def get_action(self, state: State):
        """
        An interface for recursively searching.
        """
        assert state.get_current_player() == self.player

        def cutting_off_alpha_beta_search(s: State, d, alpha, beta):
            """
            Search for several depth and use evaluation value as cutting off.

            Parameters:
                s: the current state
                d: the remaining search depth, the search will stop when d=0 , depth 和层可能有一些区别
                alpha: the current maximum value of the max player
                beta: the current minimum value of the min player

            Return:
                Tuple(value, action): the node value and the best action (if exists)
            
            Note: before you perform an action, you might need to copy the original state for in-place update.
            """
            end, winner = s.game_end()
            value, action = None, None
            if end:
                if winner == -1:
                        value = 0
                else:
                    value = (1 if winner == self.player else -1)
            elif d == 0:
                value = self.evaluation(s)
            else:
                if s.get_current_player() == self.player:  
                    value = -inf
                    for a in s.get_all_actions():
                        child_state = deepcopy(s)
                        child_state.perform_action(a)
                        child_value, _ = cutting_off_alpha_beta_search(child_state, d, alpha, beta)
                        if child_value > value:
                            value, action = child_value, a
                        if value >= beta:
                            break                  
                        alpha = max(alpha, value)
                else:  
                    value = inf
                    for a in s.get_all_actions():
                        child_state = deepcopy(s)
                        child_state.perform_action(a)
                        child_value, _ = cutting_off_alpha_beta_search(child_state, d - 1, alpha, beta)
                        if child_value < value:
                            value, action = child_value, a
                        if value <= alpha:
                            break
                        beta = min(beta, value)
            return value, action

        return cutting_off_alpha_beta_search(state, self.max_depth, -inf, inf)[1]
