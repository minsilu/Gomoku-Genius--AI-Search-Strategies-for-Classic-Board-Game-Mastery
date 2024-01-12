"""
Evaluation functions
"""


def dummy_evaluation_func(state):
    # 没有评估函数
    return 0.0


def distance_evaluation_func(state):
    # 用点到中心的距离计算评估函数，只引入的棋盘中心的先验
    player = state.get_current_player()
    info = state.get_info()
    score = 0.0
    for p, info_p in info.items():
        if p == player:
            score -= info_p["max_distance"]     # 让己方的棋子离中心越近越好
        else:
            score += info_p["max_distance"]     # 让敌方的棋子离中心越远越好
    return score


def detailed_evaluation_func(state):
    player = state.get_current_player()
    info = state.get_info()
    score = 0.0

    weights_player = {
        # "live_four": 100000, # 当我有活四时，我必胜
        # "four": 100000, # 当我有冲四时，我必胜
        # "live_three": 4000, # 当我有活三时，马上下成活四，对方若只防守必败，对方若没有冲四，我必胜
        # "three": 500, # 
        # "live_two": 50,
        # "max_distance": -100
        "live_four": 100000, # 
        "four": 10000, # 100000表现不错
        "live_three": 8000, # 
        "three": 500, # 
        "live_two": 50, 
        "max_distance": -100 # 50表现不错
    }

    weights_opponent = {
        # "live_four": 50000, # 当对方有活四时，我靠堵必败，除非我有活四或者冲四
        # "four": 9000, # 当对方有冲四时，可以堵，但对方有两个冲四时，我仅靠堵就很有可能输
        # "live_three": 2000, # 当对方有活三时，可以堵，但对方有两个活三时，我只靠堵很有可能输
        # "three": 500,
        # "live_two": 50,
        # "max_distance": -100
        "live_four": 50000, 
        "four": 8000, # 5000表现不错
        "live_three": 4000, 
        "three": 250, 
        "live_two": 50,
        "max_distance": -100
    }

    for p, info_p in info.items():
        if p == player:
            for factor, weight in weights_player.items():
                score += info_p[factor] * weight
        else:
            for factor, weight in weights_opponent.items():
                score -= info_p[factor] * weight

    # 将评估值限制在 [-1, 1] 区间
    # max_possible_score = max(weights_player["live_four"], weights_opponent["live_four"])
    score = score / 10000
    score = min(max(score, -1), 1) 
    
    return score


def get_evaluation_func(func_name):
    if func_name == "dummy_evaluation_func":
        return dummy_evaluation_func
    elif func_name == "distance_evaluation_func":
        return distance_evaluation_func
    elif func_name == "detailed_evaluation_func":
        return detailed_evaluation_func
    else:
        raise KeyError(func_name)
