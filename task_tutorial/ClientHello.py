import grpc
from task_tutorial import helloworld_pb2, helloworld_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = helloworld_pb2_grpc.GreeterStub(channel)
    response = stub.SayHello(helloworld_pb2.HelloRequest(name='dear',
                                                         surname='friend'))
    print("Greeter client received: \n" + response.message + '\n')

if __name__ == '__main__':
 run()
