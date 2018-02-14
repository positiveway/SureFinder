def get_initials(name):
    # 'Ana Sofia' => 'A S'
    return ' '.join(map(lambda part: part[0].capitalize(), name.strip().split()))


def compress_firstname(team):
    # 'Sanchez, Ana Sofia' => 'Sanchez A-S'
    # 'Marker, Lauren' => 'Marker L'
    if ('/' not in team) and (',' in team):
        lastname, _, firstname = team.partition(',')
        initials = get_initials(firstname)
        formatted_initials = '-'.join(initials.split())
        return '{} {}'.format(lastname, formatted_initials)
    return team


def compress_multiple_spaces(team):
    # '  asd  qwe1  aW' => 'asd qwe1 aW'
    return ' '.join(team.split())


def remove_dots(string):
    # '.dkjjl.. .YUW. a.4' => 'dkjjl YUW a 4'
    return compress_multiple_spaces(string.replace('.', ' ')).strip()


def convert_marat_pair_team_player(player):
    # 'J.De Loore' => 'De Loore J'
    if '.' in player:
        firstname, _, lastname = player.rpartition('.')
        return '{} {}'.format(lastname, remove_dots(firstname))
    return player


def convert_marat_pair_team(team):
    # 'J.De Loore/Y.Mertens' => 'De Loore J/Mertens Y'
    if '/' in team:
        player1, _, player2 = team.partition('/')
        return convert_marat_pair_team_player(player1) + '/' + convert_marat_pair_team_player(player2)
    return team


def delete_spaces_around_slash(team):
    # 'Meliss V / Spiteri D' => 'Meliss V/Spiteri D'
    return '/'.join(map(lambda player: player.strip(), team.split('/')))


def convert_olimp(olimp):
    """
    Effects:
    1 Firstname compressing ('Sanchez, Ana Sofia' => 'Sanchez A-S')
    2 Dots removing ('Makarova E./Vesnina E.' => 'Makarova E/Vesnina E')
    3 Deleting of spaces around slash in pair team ('Meliss V / Spiteri D' => 'Meliss V/Spiteri D')
    """
    for event in olimp.tennis:
        event.team1 = delete_spaces_around_slash(remove_dots(compress_firstname(event.team1)))
        event.team2 = delete_spaces_around_slash(remove_dots(compress_firstname(event.team2)))
    return olimp


def convert_marat(marat):
    """
    Effects:
    1 Firstname compressing ('Marker, Lauren' => 'Marker L')
    2 Pair team player converting ('J.De Loore/Y.Mertens' => 'De Loore J/Mertens Y')
    """
    for event in marat.tennis:
        event.team1 = convert_marat_pair_team(compress_firstname(event.team1))
        event.team2 = convert_marat_pair_team(compress_firstname(event.team2))
    return marat