import random

import copy
import numpy as np
from game import State, Player
import math
from copy import deepcopy


class TreeNode(object):
    """A node in the MCTS tree. Each node keeps track of its total utility U, and its visit-count n_visit.
    """

    def __init__(self, parent, state: State):
        """
        Parameters:
            parent (TreeNode | None): the parent node of the new node.
            state (State): the state corresponding to the new node.
        """
        self.parent = parent
        self.actions = deepcopy(state.get_all_actions())  # a list of all actions
        self.children = {}  # a map from action to TreeNode
        self.n_visits = 0 # 探索次数
        self.U = 0  # total utility 总收益

    def expand(self, action, next_state):
        """
        Expand tree by creating a new child.

        Parameters:
            action: the action taken to achieve the child.
            next_state: the state corresponding to the child.
        """
        child_node = TreeNode(parent=self, state=next_state)
        self.children[action] = child_node
        

    def get_ucb(self, c):
        """Calculate and return the ucb value for this node in the parent's perspective.
        It is a combination of leaf evaluations U/N and the ``uncertainty'' from the number
        of visits of this node and its parent.
        Note that U/N is in this node's perspective, so a negation is required.

        Parameters:
            c: the trade-off hyperparameter.
        """
        # 节点UCB的计算
        if self.n_visits == 0:
            return float('inf')
        else:
            # 取负号       
            return - self.U / self.n_visits + c * math.sqrt(math.log(self.parent.n_visits) / self.n_visits)

    def select(self, c):
        """Select action among children that gives maximum UCB value.

        Parameters:
            c: the hyperparameter in the UCB value.

        Return: A tuple of (action, next_node)
        """
        # 代码中选择节点时会**固定选取UCB最大的节点
        return max(self.children.items(), key=lambda act_node: act_node[1].get_ucb(c))

    def update(self, leaf_value):
        """
        Update node values from leaf evaluation.

        Parameters:
            leaf_value: the value of subtree evaluation from the current player's perspective.
        """
        self.n_visits += 1
        self.U += leaf_value

    def update_recursive(self, leaf_value):
        """Like a call to update(), but applied recursively for all ancestors.
        """
        # If it is not root, this node's parent should be updated first.
        if self.parent:
            self.parent.update_recursive(-leaf_value)
        self.update(leaf_value)

    def get_unexpanded_actions(self):
        return list(set(self.actions) - set(self.children.keys()))


class MCTS(object):
    """A simple implementation of Monte Carlo Tree Search."""

    def __init__(self, start_state: State, c=5, n_playout=10000):
        """
        Parameters:
            c: the hyperparameter in the UCB value.
            n_playout: the number of total playouts.
        """
        self.start_state = start_state
        self.root = TreeNode(None, start_state) # 创建根节点
        self.c = c
        self.n_playout = n_playout

    def playout(self, state: State):
        """
        Run a single playout from the root to the leaf, getting a value at
        the leaf and propagating it back through its parents.
        State is modified in-place, so a copy must be provided.
        """
        node = self.root 
        while not state.game_end()[0]: # 如果游戏没有结束
            unexpanded_actions = node.get_unexpanded_actions()
            if len(unexpanded_actions) > 0: # 如果还有未扩展的子节点
                action = random.choice(unexpanded_actions) # 随机选择一个未扩展的动作
                state.perform_action(action) # 执行动作后的子状态
                node.expand(action, state) # 扩展节点
                node = node.children[action] # 将当前节点设置为扩展后的子节点
                break
            else: # 如果所有的动作都已经扩展过了
                # Greedily select next move.
                action, node = node.select(self.c) # 基于 UCB 值选择下一个动作和节点，固定取UCB最大的节点
                state.perform_action(action) # 执行选择的动作

        leaf_value = self.get_leaf_value(state) # palyout, 评估叶子节点的值
        # Update value and visit count of nodes in this traversal.
        node.update_recursive(leaf_value) # 递归更新节点的值

    def get_leaf_value(self, state: State, limit=1000):
        """
        Randomly playout until the end of the game, returning +1 if the current
        player wins, -1 if the opponent wins, and 0 if it is a tie.

        Note: the value should be under the perspective of state.get_current_player()
        """
        current_player = state.get_current_player()
        for i in range(limit):
            end, winner = state.game_end()
            if end:
                break
            available_actions = state.get_all_actions()
            random_action = random.choice(available_actions)
            state.perform_action(random_action)
        if winner == -1:  
            return 0
        else:
            return 1 if winner == current_player else -1
        


class MCTSPlayer(Player):
    """AI player based on MCTS"""
    def __init__(self, c=0.1, n_playout=2000):
        super().__init__()
        self.c_puct = c
        self.n_playout = n_playout

    def get_action(self, state: State):
        mcts = MCTS(state, self.c_puct, self.n_playout) # 创建MCTS实例 tree = Node(state)
        for n in range(self.n_playout):
            state_copy = copy.deepcopy(state)
            mcts.playout(state_copy) # MCTS-sample(tree)
        return max(mcts.root.children.items(),
                   key=lambda act_node: act_node[1].n_visits)[0] # 返回最大访问次数的子节点action
