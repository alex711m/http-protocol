import socket

# Configuration

# exemple 1 : Une page qui fonctionne
serveur_cible = "www.google.com" 
port_cible = 80
fichier_demande = "/" 

# Exemple 2 : Une page qui n'existe pas (devrait donner une erreur 404)
#serveur_cible = "info.uqac.ca"
# port_cible = 80
#fichier_demande = "/cette-page-n-existe-pas.html"

# Construction de la requête HTTP (message texte suivant le standard HTTP/1.1)
requete_http = f"GET {fichier_demande} HTTP/1.1\r\nHost: {serveur_cible}\r\nConnection: close\r\n\r\n"

print("--- Requête qui sera envoyée ---")
# .strip() est utilisé ici juste pour rendre l'affichage dans le terminal plus propre
print(requete_http.strip())
print("------------------------------")

# On crée le socket en dehors du bloc 'try' pour qu'il soit accessible dans le 'finally'.
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    #étape 1 : Connexion au serveur
    print(f"\nConnexion à {serveur_cible} sur le port {port_cible}...")
    client_socket.connect((serveur_cible, port_cible))
    print("Connexion réussie !")

    # envoi de la requête : la requête est convertie en bytes avant l'envoi.
    client_socket.sendall(requete_http.encode('utf-8'))
    print("Requête envoyée. En attente de la réponse...")

    # Réception de la réponse : on assemble la réponse qui peut arriver en plusieurs morceaux.
    reponse_bytes = b""
    while True:
        chunk = client_socket.recv(4096)
        if not chunk:
            break # Le serveur a fermé la connexion.
        reponse_bytes += chunk
    print("Réponse reçue intégralement.")

    # analyse de la réponse : décodage les bytes en texte pour pouvoir la traiter.
    reponse_str = reponse_bytes.decode('utf-8', errors='ignore')
    
    # (s'assurer qu'il y a bien des en-têtes avant de séparer)
    if '\r\n\r\n' in reponse_str:
        en_tetes, corps = reponse_str.split('\r\n\r\n', 1)
    else:
        en_tetes = reponse_str
        corps = ""

    # extraction du code de statut de la première ligne.
    ligne_statut = en_tetes.split('\r\n')[0]
    code_statut = ligne_statut.split(' ')[1]

    # affichage du résultat
    print(f"\n--- Le serveur a répondu avec le statut : {ligne_statut} ---")
    
    if code_statut == "200":
        print("SUCCÈS (Code 200) ! Affichage du contenu HTML :\n")
        print(corps)

        # sauvegarde dans une page recovered_page.html
        nom_fichier = "recovered_page.html"
        try:
            with open(nom_fichier, "w", encoding="utf-8") as f:
                f.write(corps)
            print(f"\nContenu également sauvegardé dans le fichier '{nom_fichier}'")
        except Exception as e:
            print(f"\nErreur lors de la sauvegarde du fichier : {e}")
    else:
        print(f"ERREUR ou autre statut (Code {code_statut}).")
        print("--- En-têtes reçus ---\n" + en_tetes)

# gestion des erreurs de connexion
except socket.gaierror:
    print(f"Erreur DNS : Le nom d'hôte '{serveur_cible}' n'a pas pu être résolu.")
except ConnectionRefusedError:
    print(f"Erreur : Connexion refusée par le serveur '{serveur_cible}'.")
except TimeoutError:
    print(f"Erreur : Le délai de connexion a expiré.")
except Exception as e:
    print(f"Une erreur imprévue est survenue : {e}")

finally:
    # Fermeture de la connexion
    print("\n--- Fermeture de la connexion. ---")
    client_socket.close()