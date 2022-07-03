import spade
from spade.agent import Agent
from spade.behaviour import *
import random
import json
import time

BOARD = []
HEIGHT = 6
WIDTH = 7
CHARACTER_RANDOM = "R"
CHARACTER_DEFENSIVE = "D"
CHARACTER_AGGRESSIVE = "A"

class RandomPlayer(Agent):
    class GetAndPlayTurn(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                board_state = json.loads(msg.body)
                next_move = json.dumps(brain_random(board_state))
                msg = spade.message.Message(
                    to = "mojagent3@jabbers.one",
                    body = next_move,
                    )
                await self.send(msg)
                
            else:
                print(f"{self.agent.ime}: Didn't recieve a response!")

    async def setup(self):
        #self.name radi error
        self.ime = "Agent Random"
        print(f"{self.ime}: Starting!")

        behaviourGetAndPlayTurn = self.GetAndPlayTurn()
        self.add_behaviour(behaviourGetAndPlayTurn)

class DefensivePlayer(Agent):
    class GetAndPlayTurn(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                board_state = json.loads(msg.body)
                next_move = json.dumps(brain_defensive(board_state))
                msg = spade.message.Message(
                    to = "mojagent3@jabbers.one",
                    body = next_move,
                    )
                await self.send(msg)
                
            else:
                print(f"{self.agent.ime}: Didn't recieve a response!")

    async def setup(self):
        #self.name radi error
        self.ime = "Agent Defensive"
        print(f"{self.ime}: Starting!")

        behaviourGetAndPlayTurn = self.GetAndPlayTurn()
        self.add_behaviour(behaviourGetAndPlayTurn)

class AggresivePlayer(Agent):
    class GetAndPlayTurn(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:
                board_state = json.loads(msg.body)
                next_move = json.dumps(brain_aggressive(board_state))
                print(f"Moj AGRESIVNI potez je {next_move}")
                msg = spade.message.Message(
                    to = "mojagent3@jabbers.one",
                    body = next_move,
                    )
                await self.send(msg)
                
            else:
                print(f"{self.agent.ime}: Didn't recieve a response!")

    async def setup(self):
        #self.name radi error
        self.ime = "Agent Aggressive"
        print(f"{self.ime}: Starting!")

        behaviourGetAndPlayTurn = self.GetAndPlayTurn()
        self.add_behaviour(behaviourGetAndPlayTurn)

class Game(Agent):
    class StartMessage(OneShotBehaviour):
        async def run(self):
            message_body = json.dumps(self.agent.board)
            msg = spade.message.Message(
                to = "mojagent1@jabbers.one",
                body = message_body,
                )
            await self.send(msg)
    
    class PlayTheGame(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            if msg:

                if json.loads(msg.body) == None:
                    print("Igra je nerjesena")
                    return

                self.agent.brojac += 1
                if self.agent.brojac % 2 == 0:
                    #ONO STA JE DEFINIRANO KAO AGENT 2 U MAINU
                    self.agent.current_character = CHARACTER_DEFENSIVE
                    send_to = "mojagent1@jabbers.one"
                else:
                    #ONO STA JE DEFINIRANO KAO AGENT 1 U MAINU
                    self.agent.current_character = CHARACTER_RANDOM
                    send_to = "mojagent2@jabbers.one"
                

                print(f"{self.agent.ime}: Primio sam slijedeci potez:\n {msg.body} {self.agent.current_character}")
                next_move = json.loads(msg.body)
                row_index, column_index = next_move.split(",")
                self.agent.board[int(row_index)][int(column_index)] = self.agent.current_character

                for row in self.agent.board:
                    print(row)

                win = check_for_win(self.agent.current_character,self.agent.board)
                if win == True:
                    if self.agent.current_character == CHARACTER_RANDOM:
                        winner = "Agent Random"
                    elif self.agent.current_character == CHARACTER_AGGRESSIVE:
                        winner = "Agent Aggressive"
                    elif self.agent.current_character == CHARACTER_DEFENSIVE:
                        winner = "Agent Defensive"

                    print(f"Pobjedio je {winner}")
                    return

                else:
                    message_body = json.dumps(self.agent.board)
                    msg = spade.message.Message(
                        to = send_to,
                        body = message_body,
                        )
                    await self.send(msg)
                
            else:
                print(f"{self.agent.ime}: Didn't recieve a response!")

    async def setup(self):
        self.ime = "Agent Game"
        self.brojac = 0
        self.current_character = ""
        self.board = generate_board()
        print(f"{self.ime}: Starting!")

        behaviourPlayTheGame = self.PlayTheGame()
        self.add_behaviour(behaviourPlayTheGame)
        behaviourStartMessage = self.StartMessage()
        self.add_behaviour(behaviourStartMessage)
        

def get_possible_moves(board_state):
    possible_moves = []

    for row_index, row  in enumerate(board_state):
        if row_index == 0:
            continue
        for column_index, element in enumerate(row):
            if element != '0' and board_state[row_index -1][column_index] == '0':
                new_move = f"{row_index - 1},{column_index}"
                possible_moves.append(new_move)
            if row_index == (HEIGHT - 1) and element == '0':
                new_move = f"{row_index},{column_index}"
                possible_moves.append(new_move)

    return possible_moves

def generate_board():
    height = HEIGHT
    width = WIDTH
    for row in range(height):
        new_row = []

        for element in range(width):
            new_row.append('0')

        BOARD.append(new_row)

    return BOARD


def brain_random(board_state):

    possible_moves = get_possible_moves(board_state)
    if not possible_moves:
        print("Nema mogucih poteza")
        return None

    next_move = random.choice(possible_moves)
    
    return next_move

def brain_aggressive(board_state):
    possible_moves = get_possible_moves(board_state)
    if not possible_moves:
        print("Nema mogucih poteza")
        return None

    moves_count = count_for_characters(CHARACTER_AGGRESSIVE, board_state)
    moves_to_remove = []

    for move in moves_count:
        if move not in possible_moves:
            moves_to_remove.append(move)
    
    for move in moves_to_remove:
        del moves_count[move]
    
    best_moves = [key for key, value in moves_count.items() if value == max(moves_count.values())]

    next_move = random.choice(best_moves)

    return next_move


def brain_defensive(board_state):
    possible_moves = get_possible_moves(board_state)
    if not possible_moves:
        print("Nema mogucih poteza")
        return None

    #PROTIVNIKOV MOVE
    moves_count = count_for_characters(CHARACTER_RANDOM, board_state)
    
    moves_to_remove = []

    for move in moves_count:
        if move not in possible_moves:
            moves_to_remove.append(move)
    
    for move in moves_to_remove:
        del moves_count[move]
    
    best_moves = [key for key, value in moves_count.items() if value == max(moves_count.values())]

    next_move = random.choice(best_moves)

    return next_move

def count_for_characters(character, board_state):
    moves_count = {}

    for row_index, row  in enumerate(board_state):
        for column_index, element in enumerate(row):
            if element != character:
                count_1 = 0
                count_2 = 0
                count_3 = 0
                count_4 = 0
                count_5 = 0
                
                for offset in range(1,4):
                    if column_index + offset < WIDTH:
                        if board_state[row_index][column_index + offset] == character:
                            count_1 += 10 - offset

                    if row_index + offset < HEIGHT and column_index + offset < WIDTH:
                        if board_state[row_index + offset][column_index + offset] == character:
                            count_2 += 10 - offset

                    if row_index + offset < HEIGHT:
                        if board_state[row_index + offset][column_index] == character:
                            count_3 += 10 - offset

                    if row_index + offset < HEIGHT and column_index - offset >= 0:
                        if board_state[row_index + offset][column_index - offset] == character:
                            count_4 += 10 - offset

                    if column_index - offset >= 0:
                        if board_state[row_index][column_index - offset] == character:
                            count_5 += 10 - offset


                max_value = max([count_1, count_2, count_3, count_4, count_5])
                new_move = f"{row_index},{column_index}"
                moves_count[new_move] = max_value

    return moves_count

def check_for_win(character, board_state):

    for row_index, row  in enumerate(board_state):
        for column_index, element in enumerate(row):
            if element == character:
                count_1 = 1
                count_2 = 1
                count_3 = 1
                count_4 = 1
                count_5 = 1

                for offset in range(1,4):
                    if column_index + offset < WIDTH:
                        if board_state[row_index][column_index + offset] == character:
                            count_1 += 1
                    if row_index + offset < HEIGHT and column_index + offset < WIDTH:
                        if board_state[row_index + offset][column_index + offset] == character:
                            count_2 += 1
                    if row_index + offset < HEIGHT:
                        if board_state[row_index + offset][column_index] == character:
                            count_3 += 1
                    if row_index + offset < HEIGHT and column_index - offset >= 0:
                        if board_state[row_index + offset][column_index - offset] == character:
                            count_4 += 1
                    if column_index - offset >= 0:
                        if board_state[row_index][column_index - offset] == character:
                            count_5 += 1

                if count_1 >= 4 or count_2 >= 4 or count_3 >= 4 or count_4 >= 4 or count_5 >= 4:
                    return True

    return False

if __name__ == '__main__':
    agent1 = RandomPlayer("mojagent1@jabbers.one", "agentlozinka")
    agent1.start()
    agent2 = DefensivePlayer("mojagent2@jabbers.one", "agentlozinka")
    agent2.start()
    time.sleep(5)
    agent3 = Game("mojagent3@jabbers.one", "agentlozinka")
    agent3.start()

    input("Press ENTER to exit.\n")

    agent1.stop()
    agent2.stop()
    agent3.stop()

    spade.quit_spade()