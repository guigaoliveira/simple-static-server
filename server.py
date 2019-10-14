import socket
import codecs
import os

HOST = ''
PORT = 8081

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

listen_socket.bind((HOST, PORT))

listen_socket.listen(1)

print('Serving HTTP on port %s ...' % PORT)


def read_file(path):
    try:
        with codecs.open(path, 'rb') as f:
            contents = f.read()
            f.close()

    except IOError:
        contents = None
    return contents


def handle_request(client_connection, request):

    def send_str(data):
        return client_connection.send(data.encode('utf-8'))

    method, path, protocol_info, *_ = request.decode("utf-8").split(' ')

    path = path.split('?')[0].lstrip('/')

    if protocol_info.find('HTTP') == -1:
        print('[debug] Protocolo inválido')
        return None

    if 'GET' == method:

        file_contents = None

        if(path == ''):
            path = 'index.html'

        file_contents = read_file(path)

        if(file_contents != None):
            header = 'HTTP/1.1 200 OK\n'

            extension = os.path.splitext(path)[1]

            extension_and_mime = {
                '.jpg': 'image/jpg',
                '.js': 'text/javascript',
                '.css': 'text/css',
                '.ico': 'image/x-icon',
                '.html': 'text/html'
            }

            mime_type = extension_and_mime[extension]

            header += f"Content-Type: {mime_type} \n\n"

            final_response = header.encode('utf-8') + file_contents

            return client_connection.send(final_response)
        else:
            return send_str("HTTP/1.1 404 Not Found\r\n\r\n <html> <head></head> <body> <h1>404 Not Found</h1> </body> </html>\r\n")

    else:
        return send_str("HTTP/1.1 400 Bad Request\r\n\r\n <html> <head></head> <body> <h1>400 Bad Resquest</h1> </body> </html>\r\n")


while True:

    client_connection, client_address = listen_socket.accept()

    request = client_connection.recv(1024)

    print(
        f"[debug] Dados recebidos de um cliente:\n{request.decode('utf-8')}")

    handle_request(client_connection, request)

    client_connection.close()


listen_socket.close()