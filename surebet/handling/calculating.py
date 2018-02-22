from surebet.handling.surebets import *
from surebet.parsing.bets import FonbetPartBets, IdBet

result_bets = {
    "o1": "ox2",
    "o2": "o1x",
    "ox": "o12",
}
result_bets.update({val: key for key, val in result_bets.items()})  # add reversed bets

result_bets_without_draw = {
    "o1": "o2"
}
result_bets_without_draw.update({val: key for key, val in result_bets_without_draw.items()})  # add reversed bets


def calc_surebets(bets1, bets2, with_draw=True):
    surebets = []

    def get_wager_params(bets):
        wager_class = Wager
        wager_kwargs = {}
        if isinstance(bets, FonbetPartBets):
            wager_class = FonbetWager

            fonbet_info = FonbetInfo(bets.event_id, bets.score)
            wager_kwargs = {"fonbet_info": fonbet_info}
        return wager_class, wager_kwargs

    w1_class, w1_kwargs = get_wager_params(bets1)
    w2_class, w2_kwargs = get_wager_params(bets2)

    def get_factor(bet):
        factor = bet
        if isinstance(bet, IdBet):
            factor = bet.factor
        return factor

    opposite_bets = result_bets if with_draw else result_bets_without_draw
    for bet_name in opposite_bets.keys():
        bet1 = getattr(bets1, bet_name)
        bet2 = getattr(bets2, opposite_bets[bet_name])

        factor1 = get_factor(bet1)
        factor2 = get_factor(bet2)

        if _check_surebet(factor1, factor2):
            w1 = w1_class(bet_name, bet1, **w1_kwargs)
            w2 = w2_class(opposite_bets[bet_name], bet2, **w2_kwargs)
            surebets.append(Surebet(w1, w2, _get_profit(factor1, factor2)))

    surebets.extend(_handle_cond_bets(bets1, bets2, w1_kwargs, w2_kwargs))

    return surebets


def _check_surebet(factor1, factor2):
    return factor1 and factor2 and (1 / factor1 + 1 / factor2 < 1)


def _get_profit(factor1, factor2):
    profit = (1 / (1 / factor1 + 1 / factor2) - 1) * 100
    return round(profit, 2)


def _calc_cond_surebet(bet_name, cond_bet1, cond_bet2, bets_reversed, w1_kwargs, w2_kwargs):
    # calculate suffixes (O/U for total or 1/2 for hand)
    first_suffix = _get_bet_suffix(bet_name, 0)
    second_suffix = _get_bet_suffix(bet_name, 1)

    # cond is the same for cond_bet1 and cond_bet2
    cond = cond_bet1.cond
    opposite_cond = -cond if bet_name == "hand" else cond

    if bets_reversed:
        cond_bet1, cond_bet2 = cond_bet2, cond_bet1

        w1_kwargs, w2_kwargs = w2_kwargs, w1_kwargs

    def get_wager_params(w_kwargs, cond_bet, w_num):
        w_class = CondWager

        factor_id_attr = {
            0: "v1_id",
            1: "v2_id",
        }[w_num]
        if "fonbet_info" in w_kwargs:
            w_class = FonbetCondWager
            w_kwargs["fonbet_info"].factor_id = getattr(cond_bet, factor_id_attr)

        return w_class, w_kwargs

    w1_class, w1_kwargs = get_wager_params(w1_kwargs, cond_bet1, 0)
    w2_class, w2_kwargs = get_wager_params(w2_kwargs, cond_bet2, 1)

    w1 = w1_class(bet_name, cond_bet1.v1, first_suffix, cond, **w1_kwargs)
    w2 = w2_class(bet_name, cond_bet2.v2, second_suffix, opposite_cond, **w2_kwargs)

    if bets_reversed:
        w1, w2 = w2, w1

        w1_kwargs, w2_kwargs = w2_kwargs, w1_kwargs

    return Surebet(w1, w2, _get_profit(cond_bet1.v1, cond_bet2.v2))


def _get_bet_suffix(bet_name, val_num):
    if bet_name == "hand":
        suffix = ("1", "2")[val_num]
    else:
        suffix = ("O", "U")[val_num]
    return suffix


def _handle_cond_bets(bets1, bets2, w1_kwargs, w2_kwargs):
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
                    cond_surebet = _calc_cond_surebet(bet_name, cond_bet1, cond_bet2, bets_reversed,
                                                      w1_kwargs, w2_kwargs)
                    surebets.append(cond_surebet)
    return surebets
