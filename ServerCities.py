import time
import random
from concurrent import futures

import grpc

import citiesGame_pb2
import citiesGame_pb2_grpc

#TODO юзеров как дикт сделать, добавить поле активности
# но лучше так не делать

standart_cities = ['Москва', 'Архангельск', 'Караганда', 'Астана']

class CitiesGame(citiesGame_pb2_grpc.CitiesGameServiceServicer):
    def __init__(self):
        self.users = []
        self.rooms = [{
                'players': [],
                'cities': [],
                'active_player': '',
                'current_city': '',
                'game_status': 0
                }]
        self.max_players_count = 2

    def Greeter(self, request, context):
        self.users.append(request.username)
        self.createLobby()
        return citiesGame_pb2.UserReply(greeting_reply='Hello, %s ! Wellcome to the Cities-game'%(request.username))

    def createLobby(self):
        if self.users:
            if len(self.rooms[-1]['players']) == self.max_players_count:
                self.rooms[-1]['game_status'] = True
                self.rooms[-1]['active_player'] = random.choice(self.rooms[-1]['players'])
                self.rooms.append({
                    'players': [],
                    'cities': [],
                    'active_player': '',
                    'current_city': '',
                    'game_status': 0
                })
            else:
                self.rooms[-1]['players'].append(self.users.pop(0))

        if self.max_players_count == 1:
            self.rooms[-1]['game_status'] = True
            self.rooms[-1]['active_player'] = self.rooms[-1]['players'][0]

    def LobbyReady(self, request, context):
        username = request.username
        for room in self.rooms:
            if username in room['players']:
                if room['game_status']:
                    return citiesGame_pb2.GameDone(message='Lobby is ready for game', done_status=1)
                else:
                    return citiesGame_pb2.GameDone(message='Please wait for other players...', done_status=0)

    def change_active_player(self, room, username):
        if self.max_players_count == 1:
            return

        if room['players'].index(username) + 1 >= len(room['players']):
            room['active_player'] = room['players'][0]
        else:
            room['active_player'] = room['players'][room['players'].index(username) + 1]

    def roomInfo(self, room):
        print('-------------\n')
        print(f'Information about room # {self.rooms.index(room)}\n')
        print(f'Is room active: {bool(room["game_status"])}\n')
        if room["game_status"]:
            print(f'Players in room: {room["players"]}\n')
            print(f'Active player: {room["active_player"]}\n')
            print(f'Cities list: {room["cities"]}\n')
            print(f'Current city: {room["current_city"]}\n')
        print('-------------')

    #TODO сделать тело игры, поправить прото-файл, перекомпилировать
    def GameBody(self, request, context):
        username = request.username
        current_word = request.city_word
        for room in self.rooms:
            self.roomInfo(room)
            if username in room['players']:
                if len(room['players']) == 1 and self.max_players_count != 1:
                    self.rooms.pop(self.rooms.index(room))
                    return citiesGame_pb2.GameStatus(message='You are winner!', game_end=True)
                if username == room['active_player']:
                    if current_word not in room['cities'] and current_word in standart_cities:
                        if room['current_city'] == '' or room['current_city'][-1].lower() == current_word[0].lower():
                            room['current_city'] = current_word
                            # room['cities'].append(room['cities'].index(current_word))
                            room['cities'].append(current_word)
                            self.change_active_player(room, username)
                            return citiesGame_pb2.GameStatus(message='Success!', game_end=False)
                        else:
                            room['players'].pop(room['players'].index(username))
                            self.change_active_player(room, username)
                            return citiesGame_pb2.GameStatus(message='Fail! You broke rules!', game_end=True)
                    else:
                        room['players'].pop(room['players'].index(username))
                        self.change_active_player(room, username)
                        return citiesGame_pb2.GameStatus(message='Fail! This city does not exist...', game_end=True)
                else:
                    return citiesGame_pb2.GameStatus(message='It is not your turn to play...', game_end=False)

    def CityName(self, request, context):
        username = request.username
        for room in self.rooms:
            if username in room['players']:
                return citiesGame_pb2.City(city=f'Last city is {room["current_city"]}')


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    citiesGame_pb2_grpc.add_CitiesGameServiceServicer_to_server(CitiesGame(), server)
    server.add_insecure_port('[::]:13000')
    server.start()
    print("server working")
    try:
        while True:
            time.sleep(2000)
    except KeyboardInterrupt:
        print("Keyboard interrupt...")
        server.stop(0)


if __name__ == '__main__':
    serve()
