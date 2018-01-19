from surebet.handling import *

result_bets = {
    "o1": "ox2",
    "o2": "o1x",
    "ox": "o12",
}

result_bets_without_draw = {
    "o1": "o2"
}


def calc_surebets(bets_pair, with_draw=True):
    if not bets_pair or len(bets_pair) != 2:
        raise HandlingException("wagers bets have wrong len")

    surebets = []

    opposite_bets = result_bets if with_draw else result_bets_without_draw
    for bet_name in opposite_bets.keys():
        factor1 = getattr(bets_pair[0], bet_name)
        factor2 = getattr(bets_pair[1], opposite_bets[bet_name])
        if check_surebet(factor1, factor2):
            w1 = Wager(bet_name, factor1)
            w2 = Wager(opposite_bets[bet_name], factor2)
            surebets.append(Surebet(w1, w2, get_profit(factor1, factor2)))

    surebets.extend(handle_cond_bets(bets_pair))

    return surebets


def check_surebet(factor1, factor2):
    return factor1 and factor2 and (1 / factor1 + 1 / factor2 < 1)


def get_profit(factor1, factor2):
    profit = (1 - (1 / factor1 + 1 / factor2)) * 100
    return round(profit, 2)


def handle_cond_bets(bets_pair):
    surebets = []
    for bet_name in ("total", "ind_total1", "ind_total2", "hand"):
        cond_bets2 = {cond_bet.cond: cond_bet for cond_bet in getattr(bets_pair[1], bet_name)}
        for cond_bet1 in getattr(bets_pair[0], bet_name):
            if cond_bet1.cond in cond_bets2:
                cond_bet2 = cond_bets2[cond_bet1.cond]

                # calculate suffixes (O/U for total or 1/2 for hand)
                first_suffix = get_bet_suffix(bet_name, 0)
                second_suffix = get_bet_suffix(bet_name, 1)
                # cond is the same for cond_bet1 and cond_bet2
                opposite_cond = -cond_bet1.cond if bet_name == "hand" else cond_bet1.cond
                if check_surebet(cond_bet1.v1, cond_bet2.v2):
                    w1 = CondWager(bet_name, cond_bet1.v1, first_suffix, cond_bet1.cond)
                    w2 = CondWager(bet_name, cond_bet2.v2, second_suffix, opposite_cond)
                    surebets.append(Surebet(w1, w2, get_profit(cond_bet1.v1, cond_bet2.v2)))

                if check_surebet(cond_bet1.v2, cond_bet2.v1):
                    w1 = CondWager(bet_name, cond_bet1.v2, second_suffix, opposite_cond)
                    w2 = CondWager(bet_name, cond_bet2.v1, first_suffix, cond_bet2.cond)
                    surebets.append(Surebet(w1, w2, get_profit(cond_bet1.v2, cond_bet2.v1)))
    return surebets


def get_bet_suffix(bet_name, val_num):
    if bet_name == "hand":
        suffix = ("1", "2")[val_num]
    else:
        suffix = ("O", "U")[val_num]
    return suffix
