from surebet.pulling import *

result_bets = {
    "o1": "ox2",
    "o2": "o1x",
    "ox": "o12",
}

result_bets_without_draw = {
    "o1": "o2"
}


def pull(wagers_bets, with_draw=True):
    surebets = []

    opposite_bets = result_bets if with_draw else result_bets_without_draw
    for bet_name in opposite_bets.keys():
        factor1 = getattr(wagers_bets[0], bet_name)
        factor2 = getattr(wagers_bets[1], opposite_bets[bet_name])
        if check_surebet(factor1, factor2):
            w1 = Wager(bet_name, factor1)
            w2 = Wager(opposite_bets[bet_name], factor2)
            surebets.append(Surebet(w1, w2, get_profit(factor1, factor2)))

    surebets.extend(handle_cond_bets(wagers_bets))

    return surebets


def check_surebet(factor1, factor2):
    return factor1 != 0.0 and factor2 != 0.0 and 1 / factor1 + 1 / factor2 < 1


def get_profit(factor1, factor2):
    return round((1 - (1 / factor1 + 1 / factor2)) * 100, 2)


def handle_cond_bets(wagers_bets):
    surebets = []
    for bet_name in ("total", "ind_total1", "ind_total2", "hand"):
        for cond_bet1 in getattr(wagers_bets[0], bet_name):
            for cond_bet2 in getattr(wagers_bets[1], bet_name):
                if cond_bet1.cond == cond_bet2.cond:
                    if check_surebet(cond_bet1.v1, cond_bet2.v2):
                        w1 = Wager(get_wager_bet_name(bet_name, cond_bet1.cond, 0), cond_bet1.v1)
                        w2 = Wager(get_wager_bet_name(bet_name, cond_bet2.cond, 1), cond_bet2.v2)
                        surebets.append(Surebet(w1, w2, get_profit(cond_bet1.v1, cond_bet2.v2)))

                    if check_surebet(cond_bet1.v2, cond_bet2.v1):
                        w1 = Wager(get_wager_bet_name(bet_name, cond_bet1.cond, 1), cond_bet1.v2)
                        w2 = Wager(get_wager_bet_name(bet_name, cond_bet2.cond, 0), cond_bet2.v1)
                        surebets.append(Surebet(w1, w2, get_profit(cond_bet1.v2, cond_bet2.v1)))
    return surebets


def get_wager_bet_name(bet_name, cond, val_pos):
    if bet_name == "hand":
        cond = -cond if val_pos else cond
        bet_name += ("1", "2")[val_pos]
    else:
        bet_name += ("O", "U")[val_pos]

    return "{}({})".format(bet_name, cond)
