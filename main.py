import json
import socket
from _thread import *
import threading
import copy

FORMAT = 'utf-8'
SIZE = 1024
file_name = 'save_file.txt'

class Character:
    def __init__(self, hp, mana, stamina, effective_magic, effective_attack, effective_defense, mana_regen,
                 stamina_regen, attack_damage, magic_damage):
        self.hp = hp
        self.max_hp = hp
        self.mana = mana
        self.max_mana = mana
        self.stamina = stamina
        self.max_stamina = stamina
        self.effective_magic = effective_magic
        self.effective_attack = effective_attack
        self.effective_defense = effective_defense
        self.mana_regen = mana_regen
        self.stamina_regen = stamina_regen
        self.attack_damage = attack_damage
        self.magic_damage = magic_damage

    def is_alive(self):
        return self.hp > 0

    def attack(self, other):
        damage = self.attack_damage - other.effective_defense
        if damage < 0:
            damage = 0
        other.hp -= damage
        self.stamina -= 60

    def magic_attack(self, other):
        damage = self.magic_damage
        if damage < 0:
            damage = 0
        other.hp -= int(damage * 1.2)
        self.mana -= 60

    def mana_decrease(self):
        self.mana -= 35

    def regenerate(self):
        if self.mana < self.max_mana:
            self.mana += 10
            if self.mana > self.max_mana:
                self.mana = self.max_mana
        if self.stamina < self.max_stamina:
            self.stamina += 15
            if self.stamina > self.max_stamina:
                self.stamina = self.max_stamina


def report(player_object, player):
    dict = {'Name': player_object.name, 'HP': player.hp, 'Mana': player.mana, 'Stamina': player.stamina}
    info = json.dumps(dict)
    player_object.csoc.send(info.encode(FORMAT))


def action_handler(player_object):
    print('Listening for Action....')
    action = int(player_object.csoc.recv(SIZE).decode(FORMAT))
    player_object.action = action
    print('got action!', action)


def report_enemy(player_object, player, player_object_self):
    dict = {'Name': player_object.name, 'HP': player.hp, 'Mana': player.mana, 'Stamina': player.stamina}
    info = json.dumps(dict)
    player_object_self.csoc.send(info.encode(FORMAT))


def play_game(player1_object, player2_object):
    characters = [
        Character(hp=100, mana=50, stamina=75, effective_magic=80, effective_attack=90, effective_defense=70,
                  mana_regen=5, stamina_regen=10, attack_damage=20, magic_damage=30),
        Character(hp=120, mana=40, stamina=60, effective_magic=70, effective_attack=80, effective_defense=80,
                  mana_regen=4, stamina_regen=8, attack_damage=25, magic_damage=35),
        Character(hp=80, mana=60, stamina=80, effective_magic=90, effective_attack=70, effective_defense=60,
                  mana_regen=6, stamina_regen=12, attack_damage=15, magic_damage=40),
        Character(hp=150, mana=30, stamina=50, effective_magic=60, effective_attack=100, effective_defense=90,
                  mana_regen=3, stamina_regen=6, attack_damage=30, magic_damage=20)
    ]

    player1 = copy.copy(characters[player1_object.character - 1])
    player2 = copy.copy(characters[player2_object.character - 1])
    csoc1 = player1_object.csoc
    csoc2 = player2_object.csoc

    while player1.is_alive() and player2.is_alive():
        report(player_object=player1_object, player=player1)
        report(player_object=player2_object, player=player2)

        report_enemy(player_object=player1_object, player=player1, player_object_self=player2_object)
        report_enemy(player_object=player2_object, player=player2, player_object_self=player1_object)

        start_new_thread(action_handler, (player1_object,))
        start_new_thread(action_handler, (player2_object,))

        action1 = -1
        action2 = -1
        while True:
            if player1_object.action != -1 and player2_object.action != -1:
                action1 = player1_object.action
                player1_object.action = -1
                action2 = player2_object.action
                player2_object.action = -1
                break

        if action1 == 1 and action2 == 1:
            if player1.effective_attack > player2.effective_attack:
                player2.hp -= abs(player1.effective_attack - player2.effective_attack)
            elif player2.effective_attack > player1.effective_attack:
                player1.hp -= abs(player2.effective_attack - player1.effective_attack)
            else:
                player1.hp -= abs(player2.effective_attack - player1.effective_attack)
                player2.hp -= abs(player1.effective_attack - player2.effective_attack)
            string1 = f'both{player1_object.name}and{player2_object.name} attacked'
            save_to_file(string1,file_name)
            player1.stamina -= 40
            player2.stamina -= 40

        elif action1 == 1 and action2 == 2:
            player1.hp -= player2.magic_damage
            string2 = f'{player1_object.name} attacked and {player2_object.name} used magic'
            save_to_file(string2,file_name)
            player1.stamina -= 30
            player2.mana_decrease()

        elif action1 == 1 and action2 == 3:
            a = 100 - player2.effective_defense
            player2.hp -= (player1.attack_damage * a / 100)
            string3 = f'{player1_object.name} attacked and {player2_object.name} used defense'
            save_to_file(string3,file_name)
            player1.stamina -= 35
            player2.stamina -= 20

        elif action1 == 2 and action2 == 1:
            player2.hp -= player1.magic_damage
            string4 = f'{player2_object.name} attacked and {player1_object.name} used magic'
            save_to_file(string4,file_name)
            player2.stamina -= 30
            player1.mana_decrease()

        elif action1 == 2 and action2 == 2:
            if player1.effective_magic > player2.effective_magic:
                player2.hp -= abs(player1.effective_magic - player2.effective_magic)
            elif player2.effective_magic > player1.effective_magic:
                player1.hp -= abs(player2.effective_magic - player1.effective_magic)
            string5 = f'both{player1_object.name}and{player2_object.name} used magic'
            save_to_file(string5,file_name)
            player1.mana_decrease()
            player2.mana_decrease()

        elif action1 == 2 and action2 == 3:
            player2.hp -= player1.magic_damage
            string5 = f'{player1_object.name} used magic while {player2_object} defended'
            save_to_file(string5,file_name)
            player2.stamina -= 20
            player1.mana_decrease()

        elif action1 == 3 and action2 == 1:
            b = 100 - player1.effective_defense
            player1.hp -= (player2.attack_damage * b / 100)
            string6 = f'{player2_object.name} attacked and {player1_object.name} used defense'
            save_to_file(string6,file_name)
            player2.stamina -= 35
            player1.stamina -= 20

        elif action1 == 3 and action2 == 2:
            player1.hp -= player2.magic_damage
            string7 = f'{player2_object.name} used magic while {player1_object} defended'
            save_to_file(string7,file_name)
            player1.stamina -= 20
            player2.mana_decrease()

        elif action1 == 3 and action2 == 3:
            string8 = f'{player1_object.name} and {player2_object.name} both used defense'
            player1.stamina -= 20
            player2.stamina -= 20

        player1.regenerate()
        player2.regenerate()

    if player1.is_alive():
        csoc1.sendall(player1_object.name + " wins!".encode(FORMAT))
        csoc2.sendall(player1_object.name + " wins!".encode(FORMAT))
    else:
        csoc1.sendall(player2_object.name + " wins!".encode(FORMAT))
        csoc2.sendall(player2_object.name + " wins!".encode(FORMAT))


def save_to_file(string, filename):
    with open(filename, 'w') as file:
        file.write(string)
    print(f"The {filename} has been updated.")


global player_list
player_list = []


def user_handel(soc):
    print('Listening!....')
    csoc, _ = soc.accept()
    print('player connected')
    player_name = csoc.recv(SIZE).decode(FORMAT)
    player_character = int(csoc.recv(SIZE).decode(FORMAT))
    p = Player(player_name, csoc, player_character)
    player_list.append(p)


soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.bind(("127.0.0.1", 9090))
soc.listen(2)

start_new_thread(user_handel, (soc,))
start_new_thread(user_handel, (soc,))


class Player:
    def __init__(self, name, csoc, character):
        self.name = name
        self.csoc = csoc
        self.character = character
        self.action = -1


while len(player_list) != 2:
    a = 0
print('Satrting Game!')
play_game(player_list[0], player_list[1])
