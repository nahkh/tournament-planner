from random import shuffle, choice, random
from copy import deepcopy
from time import time

def millis():
    return int(round(time() * 1000))

def read_games(filename):
    games = []
    with open(filename) as f:
        for line in f.readlines():
            names = line.split(',')
            games.append(frozenset([name.strip() for name in names]))
    return games

def create_pairings(game):
    if len(game) < 2:
        raise ValueError('Cannot play a game with less than two players')
    players = list(game)
    shuffle(players)
    previous = None
    pairings = []
    for name in players:
        if previous == None:
            previous = name
        else:
            pairings.append(pair(previous, name))
            previous = None
    if previous != None:
        pairings.append(pair(previous, players[0]))
    return pairings

def validate_pairings(games, pairings):
    for game, game_pairings in zip(games, pairings):
        player_occurrances = {}
        for pair in game_pairings:
            player_occurrances[pair[0]] = player_occurrances.get(pair[0], 0) + 1
            player_occurrances[pair[1]] = player_occurrances.get(pair[1], 0) + 1
        assert len(game) == len(player_occurrances),'Every player should occur at least once in a pairing'
        should_see_player_with_two_matches = len(game) % 2 == 1
        for player, count in player_occurrances.items():
            if count == 2 and should_see_player_with_two_matches:
                count = 1
                should_see_player_with_two_matches = False
            assert count == 1,'Player %s has too many matches (%i)'%(player, count)
                
        

def pair(a, b):
    if a == b:
        raise ValueError('Player %s cannot play with themselves' % a)
    if a < b:
        return (a, b)
    else:
        return (b, a)

def calculate_score(pairings_list):
    def flatten(list_of_lists):
        for i_list in list_of_lists:
            for value in i_list:
                yield value
    seen_pairs = set()
    duplicates = 0
    for pair in flatten(pairings_list):
        if pair in seen_pairs:
            duplicates += 1
        else:
            seen_pairs.add(pair)
    return duplicates

def swap_random_players(pairings):
    ''' Create a new pairing list by swapping players in two random pairs within a random game
    '''
    new_pairings = deepcopy(pairings)
    illegal_swap = True
    while illegal_swap:
        match = choice(new_pairings)
        first_pair = choice(match)
        second_pair = choice(match)
        if len({first_pair[0], first_pair[1], second_pair[0], second_pair[1]}) == 4:
            illegal_swap = False
    match.remove(first_pair)
    match.remove(second_pair)
    if random() < 0.5:
        match.append(pair(first_pair[0], second_pair[0]))
        match.append(pair(first_pair[1], second_pair[1]))
    else:
        match.append(pair(first_pair[0], second_pair[1]))
        match.append(pair(first_pair[1], second_pair[0]))
    return new_pairings

def swap_pairs_with_high_overlaps(pairings):
    pairings = deepcopy(pairings)
    overlaps = {}
    for i in range(len(pairings)):
        for i_pair in pairings[i]:
            if i_pair not in overlaps:
                overlaps[i_pair] = []
            overlaps[i_pair].append(i)
    max_overlaps = max(map(len, overlaps.values()))
    max_pairs = {pair: games for pair, games in overlaps.items() if len(games) == max_overlaps}
    
    illegal_swap = True
    attempt_count = 0
    while illegal_swap and attempt_count < 10:
        first_pair = choice(list(max_pairs.keys()))
        game_index = choice(overlaps[first_pair])
        match = pairings[game_index]
        second_pair = choice(match)
        if len({first_pair[0], first_pair[1], second_pair[0], second_pair[1]}) == 4:
            illegal_swap = False
        attempt_count += 1
    if illegal_swap:
        # Couldn't find a good pair to swap, delegating to random
        print('Delegate to random')
        return swap_random_players(pairings)
    match.remove(first_pair)
    match.remove(second_pair)
    if random() < 0.5:
        match.append(pair(first_pair[0], second_pair[0]))
        match.append(pair(first_pair[1], second_pair[1]))
    else:
        match.append(pair(first_pair[0], second_pair[1]))
        match.append(pair(first_pair[1], second_pair[0]))
    return pairings
        
    
    
def exponential_temperature(alpha):
    return lambda t: 0.999 ** t

def simulated_annealing(games, pair_swap=swap_pairs_with_high_overlaps,T=exponential_temperature(0.999), stopping_temperature = 0.0000000001):
    pairings = list(map(create_pairings, games))
    t = 0
    while T(t) > stopping_temperature and calculate_score(pairings) > 0:
        #print('Temperature %f' % T(t))
        current_score = calculate_score(pairings)
        new_pairings = pair_swap(pairings)
        new_score = calculate_score(new_pairings)
        if current_score > new_score or random() < T(t):
            pairings = new_pairings
        t += 1
    return pairings

def write_pairings(filename, pairings):
    with open(filename, 'w') as f:
        for i, game_pairings in enumerate(pairings):
            f.write('Game %i\n' % (i + 1))
            for pairing in game_pairings:
                f.write('%s vs %s\n' % pairing)
            f.write('\n')

games = read_games('games-50.txt')
s = millis()
pairings = list(map(create_pairings, games))
e = millis()
validate_pairings(games, pairings)
print('Random pairings gave %i duplicate pairs in %i ms' % (calculate_score(pairings), e - s))

s = millis()
pairings = simulated_annealing(games, pair_swap=swap_random_players)
e = millis()
validate_pairings(games, pairings)
print('Simulated annealing with random swaps gave %i duplicate pairs in %i ms' % (calculate_score(pairings), e - s))

s = millis()
pairings = simulated_annealing(games)
e = millis()
validate_pairings(games, pairings)
print('Simulated annealing with high overlap preference gave %i duplicate pairs in %i ms' % (calculate_score(pairings), e - s))

write_pairings('result.txt', pairings)
