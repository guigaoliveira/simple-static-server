import socket
import codecs
import os

def read_file(path):
    try:
        with codecs.open(path, 'rb') as f:
            contents = f.read()
            f.close()
    except IOError:
        contents = None
    return contents

def send_text(client_connection, data):
    return client_connection.send(data.encode('utf-8'))

def send_bad_request(client_connection): 
    bad_request_payload = """HTTP/1.1 400 Bad Request\r\n\r\n
        <html><head></head><body><h1>400 Bad Resquest</h1></body></html>\r\n"""
    return send_text(client_connection, bad_request_payload)

def handle_request(client_connection, request):
    request_list_string = request.decode("utf-8").split(' ')
    
    if(len(request_list_string) < 3):
        return send_bad_request(client_connection) 
    
    method = request_list_string[0]
    path = request_list_string[1].split('?')[0].lstrip('/')
    protocol_info = request_list_string[2]
    
    if protocol_info.find('HTTP') == -1:
        return send_bad_request(client_connection) 
    
    if 'GET' == method:
        
        file_contents = None
        
        if(path == ''):
            path = 'index.html'
            
        file_contents = read_file(path)
        
        if(file_contents is not None):
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
            not_found_payload = """HTTP/1.1 404 Not Found\r\n\r\n 
                <html>
                <head></head>
                <body><h1>404 Not Found</h1></body>
                </html>\r\n"""
            return send_text(client_connection, not_found_payload)
    else:
        return send_bad_request(client_connection) 
    
HOST = '127.0.0.1'
PORT = 8081

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
listen_socket.bind((HOST, PORT))
listen_socket.listen(1)

while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024)
    print(
        f"[debug] Dados recebidos de um cliente:\n{request.decode('utf-8')}")
    handle_request(client_connection, request)
    client_connection.close()
        
listen_socket.close()
