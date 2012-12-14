
import sys
import os
import logging

psmoveapi_build = os.path.join(os.path.dirname(__file__), '..', 'psmoveapi', 'build')
sys.path.insert(0, psmoveapi_build)

import time
import math
import psmove

import pygame

pygame.mixer.init()

buttons = [
    psmove.Btn_SQUARE,
    psmove.Btn_TRIANGLE,
    psmove.Btn_CROSS,
    psmove.Btn_CIRCLE,
]

colors = [
    (255, 0, 255),
    (0, 255, 0),
    (0, 0, 255),
    (255, 0, 0),
]

sounds = [pygame.mixer.Sound('button%d.wav' % i) for i in range(4)]
print sounds

class Game:
    def __init__(self, moves):
        self.moves = moves
        self.eliminated = []
        self.sequence = []
        self.current_player = -1
        self.current_button = 0
        self.next_player()

    def on_button(self, index, button):
        if self.current_button == len(self.sequence):
            sounds[buttons.index(button)].play()
            self.sequence.append(button)
            self.next_player()
        else:
            if button != self.sequence[self.current_button]:
                self.player_dies()
                self.sequence = []
                self.next_player()
            else:
                sounds[buttons.index(button)].play()
                self.current_button += 1

    def player_dies(self):
        move = self.moves[self.current_player]
        for x in range(5):
            move.set_leds(255, 0, 0)
            move.set_rumble(0)
            move.update_leds()
            time.sleep(.2)
            move.set_leds(0, 0, 0)
            move.set_rumble(255)
            move.update_leds()
            time.sleep(.2)

        move.set_leds(0, 0, 0)
        move.set_rumble(0)
        move.update_leds()

        self.eliminated.append(self.current_player)
        logging.debug('eliminated: ' + ','.join(map(repr, self.eliminated)))
        logging.debug('players: ' + repr(len(self.moves)))
        if len(self.eliminated) == len(self.moves) - 1:
            winner = list(set(range(len(self.moves))).difference(set(self.eliminated)))[0]
            logging.info('winner: ' + repr(winner))
            move = self.moves[winner]
            while True:
                move.set_leds(0, 255, 0)
                move.update_leds()
                time.sleep(1)
            sys.exit(0)

    def next_player(self):
        self.moves[self.current_player].set_leds(0, 0, 0)
        self.current_player += 1
        self.current_player %= len(self.moves)

        while (self.current_player in self.eliminated):
            self.current_player += 1
            self.current_player %= len(self.moves)

        self.moves[self.current_player].set_leds(255, 255, 255)
        self.current_button = 0
        logging.debug('current player: ' + repr(self.current_player))

moves = [psmove.PSMove(i) for i in range(psmove.count_connected())]
game = Game(moves)

while True:
    for idx, move in enumerate(moves):
        while move.poll():
            if game.current_player == idx:
                pressed, released = move.get_button_events()
                for btn_idx, button in enumerate(buttons):
                    if pressed & button:
                        move.set_leds(*colors[btn_idx])
                    elif released & button:
                        game.on_button(idx, button)

        move.update_leds()

