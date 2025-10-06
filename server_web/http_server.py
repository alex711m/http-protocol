import socket

#configuration du serveur
HOTE = "localhost"
PORT = 8080 

# Création de la socket du serveur
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serveur_socket:
    # autorisation de la réutilisation de l'adresse pour éviter les erreurs (par ex, "address already in use", ...)
    serveur_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    serveur_socket.bind((HOTE, PORT))
    serveur_socket.listen()
    print(f"Serveur démarré. En écoute sur http://{HOTE}:{PORT}")
    print("appuyez sur ctrl+c puor arrêter le serveur")

    # boucle principal du sevreur
    while True:
        client_socket, adresse = serveur_socket.accept()
        with client_socket:
            print(f"\nConnexion acceptée de {adresse}")
            requete_str = client_socket.recv(1024).decode('utf-8')
            
            print("--- Requête reçue ---\n" + requete_str.strip() + "\n---------------------")

            try:
                premiere_ligne = requete_str.split('\r\n')[0]
                fichier_demande = premiere_ligne.split(' ')[1]
            except IndexError:
                continue # ignore les requêtes malformées

            if fichier_demande == '/':
                fichier_demande = '/index.html'

            #suppression du '/' au début pour avoir un chemin de fichier local
            chemin_fichier = fichier_demande.lstrip('/')

            # logique finale : trouver le fichier ou retourner une erreur 404   
            try:
                # On essaie d'ouvrir et lire le fichier demandé
                with open(chemin_fichier, 'r', encoding='utf-8') as f:
                    corps_reponse = f.read()
                
                #construction d'une réponse 200 OK
                ligne_statut = "HTTP/1.1 200 OK\r\n"
                en_tetes = f"Content-Type: text/html\r\nContent-Length: {len(corps_reponse)}\r\n"
                
            except FileNotFoundError:
                # si le fichier n'existe pas, on prépare une réponse 404
                corps_reponse = "<html><body><h1>404 Not Found</h1><p>Le fichier demande n'existe pas.</p></body></html>"
                ligne_statut = "HTTP/1.1 404 Not Found\r\n"
                en_tetes = f"Content-Type: text/html\r\nContent-Length: {len(corps_reponse)}\r\n"

            # assemblage et envoie de la réponse complète (statut + en-têtes + ligne vide + corps)
            reponse_complete = ligne_statut + en_tetes + "\r\n" + corps_reponse
            client_socket.sendall(reponse_complete.encode('utf-8'))