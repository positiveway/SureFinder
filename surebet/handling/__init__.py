class Surebet:
    def __init__(self, w1, w2, profit, reverse=False):
        self.w1 = w1
        self.w2 = w2
        self.profit = profit
        self.reverse = reverse  # defines order for CondWager (Under/Over or Over/Under; H1/H2 or H2/H1)


class CondWager:
    def __init__(self, name, cond, factor):
        self.name = name
        self.cond = cond
        self.factor = factor


class Wager:
    def __init__(self, name, factor):
        self.name = name
        self.factor = factor


class HandlingException(Exception):
    pass
