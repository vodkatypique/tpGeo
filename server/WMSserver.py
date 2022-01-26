#!/usr/bin/python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse
from gen_img import create_tile

PORT_NUMBER = 4242


class WMSHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/wms"):
            # Ici on récupère les valeurs de paramètres GET
            params = urlparse.parse_qs(urlparse.urlparse(self.path).query)

            # params contient tous les paramètres GET
            # Il faut maintenant les traiter...
            # ... C'est à vous !
            print(params)

            if 'request' not in params.keys() or params['request'] != ['GetMap']:
                self.send_error(404, "'request' parameter should have the value 'GetMap'")
                return

            if 'layers' not in params.keys():
                self.send_error(404, "'layers' parameter is missing")
                return

            img_size = dict()
            for val in ['height', 'width']:
                if val not in params.keys():
                    self.send_error(404, "'{}' parameter is missing".format(val))
                    return
                else:
                    img_size[val] = int(params[val][0])

            if 'srs' not in params.keys() or params['srs'] != ['EPSG:3857']:
                self.send_error(404, "'srs' parameter should have the value 'EPSG:3857'")
                return

            bbox = []
            if 'bbox' not in params.keys():
                self.send_error(404, "'bbox' parameter is missing")
                return
            
            for x in params['bbox'][0].split(','):
                bbox.append(x)

            p1 = bbox[0] + ' ' + bbox[1]
            p2 = bbox[0] + ' ' + bbox[3]
            p3 = bbox[2] + ' ' + bbox[3]
            p4 = bbox[2] + ' ' + bbox[1]
            
            filename = create_tile(p1, p2, p3, p4, 3857, img_size['height'], img_size['height'])
            self.send_png_image(filename)

            return

        self.send_error(404, 'Fichier non trouvé : %s' % self.path)

    def send_plain_text(self, content):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain; charset=UTF-8')
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))

    def send_png_image(self, filename):
        self.send_response(200)
        self.send_header('Content-type', 'image/png')
        self.end_headers()
        with open(filename, 'rb') as file:
            self.wfile.write(file.read())

    def send_html_file(self, filename):
        self.send_response(200)
        self.end_headers()
        self.serveFile(filename)


if __name__ == "__main__":
    try:
        # Ici on crée un serveur web HTTP, et on affecte le traitement
        # des requêtes à notre releaseHandler ci-dessus.
        server = HTTPServer(('', PORT_NUMBER), WMSHandler)
        print('Serveur démarré sur le port ', PORT_NUMBER)
        print('Ouvrez un navigateur et tapez dans la barre d\'url :'
              + ' http://localhost:%d/' % PORT_NUMBER)

        # Ici, on demande au serveur d'attendre jusqu'à la fin des temps...
        server.serve_forever()

    # ...sauf si l'utilisateur l'interrompt avec ^C par exemple
    except KeyboardInterrupt:
        print('^C reçu, je ferme le serveur. Merci.')
        server.socket.close()
