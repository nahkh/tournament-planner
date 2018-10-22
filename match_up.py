from random import shuffle, choice, random
from copy import deepcopy

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
    
def exponential_temperature(t):
    return 0.999 ** t

def simulated_annealing(games, T=exponential_temperature, stopping_temperature = 0.0000000001):
    pairings = list(map(create_pairings, games))
    t = 0
    while T(t) > stopping_temperature and calculate_score(pairings) > 0:
        current_score = calculate_score(pairings)
        new_pairings = swap_random_players(pairings)
        new_score = calculate_score(new_pairings)
        if current_score > new_score or random() < T(t):
            pairings = new_pairings
        t += 1
    return pairings

games = read_games('games-50.txt')
pairings = list(map(create_pairings, games))
print('Random pairings give %i duplicate pairs' % calculate_score(pairings))

simulated_annealing_pairs = simulated_annealing(games)
print('Simulated annealing pairings give %i duplicate pairs' % calculate_score(simulated_annealing_pairs))
