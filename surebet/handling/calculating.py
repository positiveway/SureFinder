from surebet.handling.surebets import *
from surebet.parsing.bets import FonbetPartBets, CustomBet

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

    wagers_classes = [Wager for _ in range(2)]
    wagers_kwargs = [{} for _ in range(2)]
    for idx, bets in enumerate((bets1, bets2)):
        if isinstance(bets, FonbetPartBets):
            wagers_classes[idx] = FonbetWager

            fonbet_info = FonbetInfo(bets.event_id, bets.score)
            wagers_kwargs[idx] = {"fonbet_info": fonbet_info}

    opposite_bets = result_bets if with_draw else result_bets_without_draw
    for bet_name in opposite_bets.keys():
        bet1 = getattr(bets1, bet_name)
        bet2 = getattr(bets2, opposite_bets[bet_name])

        factors = [0.0 for _ in range(2)]
        for idx, bet in enumerate((bet1, bet2)):
            if isinstance(bet, CustomBet):
                factors[idx] = bet.factor
            else:
                factors[idx] = bet

        if _check_surebet(*factors):
            w1 = wagers_classes[0](bet_name, bet1, **wagers_kwargs[0])
            w2 = wagers_classes[1](opposite_bets[bet_name], bet2, **wagers_kwargs[1])
            surebets.append(Surebet(w1, w2, _get_profit(*factors)))

    surebets.extend(_handle_cond_bets(bets1, bets2, wagers_kwargs))

    return surebets


def _check_surebet(factor1, factor2):
    return factor1 and factor2 and (1 / factor1 + 1 / factor2 < 1)


def _get_profit(factor1, factor2):
    profit = (1 / (1 / factor1 + 1 / factor2) - 1) * 100
    return round(profit, 2)


def _calc_cond_surebet(bet_name, cond_bet1, cond_bet2, bets_reversed, wagers_kwargs):
    # calculate suffixes (O/U for total or 1/2 for hand)
    first_suffix = _get_bet_suffix(bet_name, 0)
    second_suffix = _get_bet_suffix(bet_name, 1)

    # cond is the same for cond_bet1 and cond_bet2
    cond = cond_bet1.cond
    opposite_cond = -cond if bet_name == "hand" else cond

    if bets_reversed:
        cond_bet1, cond_bet2 = cond_bet2, cond_bet1

        wagers_kwargs[0], wagers_kwargs[1] = wagers_kwargs[1], wagers_kwargs[0]

    wager_classes = [CondWager for _ in range(2)]
    for idx, cond_bet in enumerate((cond_bet1, cond_bet2)):
        factor_id_attr = {
            0: "v1_id",
            1: "v2_id",
        }[idx]
        if "fonbet_info" in wagers_kwargs[idx]:
            wager_classes[idx] = FonbetCondWager

            wagers_kwargs[idx]["fonbet_info"].factor_id = getattr(cond_bet, factor_id_attr)

    w1 = wager_classes[0](bet_name, cond_bet1.v1, first_suffix, cond, **wagers_kwargs[0])
    w2 = wager_classes[1](bet_name, cond_bet2.v2, second_suffix, opposite_cond, **wagers_kwargs[1])

    if bets_reversed:
        w1, w2 = w2, w1

        wagers_kwargs[0], wagers_kwargs[1] = wagers_kwargs[1], wagers_kwargs[0]

    return Surebet(w1, w2, _get_profit(cond_bet1.v1, cond_bet2.v2))


def _get_bet_suffix(bet_name, val_num):
    if bet_name == "hand":
        suffix = ("1", "2")[val_num]
    else:
        suffix = ("O", "U")[val_num]
    return suffix


def _handle_cond_bets(bets1, bets2, wagers_kwargs):
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
                    cond_surebet = _calc_cond_surebet(bet_name, cond_bet1, cond_bet2, bets_reversed, wagers_kwargs)
                    surebets.append(cond_surebet)
    return surebets
