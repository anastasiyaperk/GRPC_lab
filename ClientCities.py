import msvcrt
import sys
import threading
import time

import grpc

import citiesGame_pb2
import citiesGame_pb2_grpc


def run():
    name = input("Enter a username: ")
    addr = 'localhost:'+input('Enter a port on localhost to connect: ')
    channel =''
    try:
        channel = grpc.insecure_channel(addr)
    except:
        print("During connection establishing an error has occurred!")
        exit(0)

    stub = citiesGame_pb2_grpc.CitiesGameServiceStub(channel)
    username = citiesGame_pb2.UserName(username=name)
    responce = stub.Greeter(username)
    print(responce.greeting_reply)

    is_game_ready = False
    is_game_over = False
    while not is_game_ready:
        responce = stub.LobbyReady(username)
        message, is_game_ready = responce.message, responce.done_status
        print(message)
        if message == 'Please wait for other players...':
            time.sleep(10)

    while not is_game_over:
        responce = stub.CityName(username)
        print(responce.city)

        # word = readInput("Enter city: ", 'Non-existing city', timeout=19)
        word = input("Enter city: ")

        responce = stub.GameBody(citiesGame_pb2.UserGame(username=name, city_word=word))

        message, is_game_over = responce.message, responce.game_end
        print(message)
        if message == 'It is not your turn to play!':
            time.sleep(10)
            

if __name__ == '__main__':
    run()
