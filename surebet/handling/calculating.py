from surebet.handling.surebets import *

result_bets = {
    "o1": "ox2",
    "o2": "o1x",
    "ox": "o12",
}

result_bets_without_draw = {
    "o1": "o2"
}


def calc_surebets(bets1, bets2, with_draw=True):
    surebets = []

    opposite_bets = result_bets if with_draw else result_bets_without_draw
    for bet_name in opposite_bets.keys():
        factor1 = getattr(bets1, bet_name)
        factor2 = getattr(bets2, opposite_bets[bet_name])
        if _check_surebet(factor1, factor2):
            w1 = Wager(bet_name, factor1)
            w2 = Wager(opposite_bets[bet_name], factor2)
            surebets.append(Surebet(w1, w2, _get_profit(factor1, factor2)))

    surebets.extend(_handle_cond_bets(bets1, bets2))

    return surebets


def _check_surebet(factor1, factor2):
    return factor1 and factor2 and (1 / factor1 + 1 / factor2 < 1)


def _get_profit(factor1, factor2):
    profit = (1 / (1 / factor1 + 1 / factor2) - 1) * 100
    return round(profit, 2)


def _calc_cond_surebet(bet_name, cond_bet1, cond_bet2, bets_reversed):
    # calculate suffixes (O/U for total or 1/2 for hand)
    first_suffix = _get_bet_suffix(bet_name, 0)
    second_suffix = _get_bet_suffix(bet_name, 1)

    # cond is the same for cond_bet1 and cond_bet2
    cond = cond_bet1.cond
    opposite_cond = -cond if bet_name == "hand" else cond

    if bets_reversed:
        cond_bet1, cond_bet2 = cond_bet2, cond_bet1

    w1 = CondWager(bet_name, cond_bet1.v1, first_suffix, cond)
    w2 = CondWager(bet_name, cond_bet2.v2, second_suffix, opposite_cond)

    if bets_reversed:
        w1, w2 = w2, w1

    return Surebet(w1, w2, _get_profit(cond_bet1.v1, cond_bet2.v2))


def _get_bet_suffix(bet_name, val_num):
    if bet_name == "hand":
        suffix = ("1", "2")[val_num]
    else:
        suffix = ("O", "U")[val_num]
    return suffix


def _handle_cond_bets(bets1, bets2):
    surebets = []
    for bet_name in ("total", "ind_total1", "ind_total2", "hand"):
        cond_bets2_map = {cond_bet.cond: cond_bet for cond_bet in getattr(bets2, bet_name)}
        for cond_bet1 in getattr(bets1, bet_name):
            cond_bet2 = cond_bets2_map.get(cond_bet1.cond, None)
            if cond_bet2:
                bets_reversed = None
                if _check_surebet(cond_bet1.v1, cond_bet2.v2):
                    bets_reversed = False
                elif _check_surebet(cond_bet1.v2, cond_bet2.v1):
                    bets_reversed = True

                if bets_reversed is not None:
                    cond_surebet = _calc_cond_surebet(bet_name, cond_bet1, cond_bet2, bets_reversed)
                    surebets.append(cond_surebet)
    return surebets
