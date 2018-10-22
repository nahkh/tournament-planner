from random import random

number_of_games = 15

with open('names.txt') as f:
    names = [row.strip() for row in f.readlines()]

attendance = [(name, random()) for name in names]

games = []


def generate_n_games(n, filename):
    with open(filename, 'w') as f:
        for i in range(n):
            attendees = [name for name, p in attendance if p > random()]
            f.write(','.join(attendees) + '\n')
        

for i in range(15, 55, 5):
    generate_n_games(i, 'games-%i.txt' % i)
