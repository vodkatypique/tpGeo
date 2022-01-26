import psycopg2
from postgis.psycopg import register
import config

connection = None


def set_connection(fn):
    def wrapped(*args, **kwargs):
        global connection
        if not connection:
            init_connection()
        return fn(connection, *args, **kwargs)
    return wrapped


OOM_HINT = """
Vérifiez que vous n'avez pas oublié une condition dans une jointure.
Si le problème persite, essayez de relancer l'exécuteur de requêtes.
"""

#########################################################
# Cette fonction exécute sur la base
# la requête passée en paramètre
#########################################################
@set_connection
def execute_query(*args, **kwargs):
    try:
        # On récupère un objet curseur qui permet de parcourir
        # l'ensemble résultat à la manière d'un itérateur.
        connection, query, parameters = args[0], args[1], args[2:]
        cursor = connection.cursor()
        print(connection, query)

        # On exécute la requête ici.
        cursor.execute(query) if len(parameters) == 0 else cursor.execute(query, parameters)

        # Après exécution de la requête, on récupère la réponse du SGBD
        # et on renvoie le tout.
        return cursor

    except MemoryError:
        print("""
Pas assez de mémoire pour exécuter la requête SQL.
{}""".format(OOM_HINT))
        raise
    except psycopg2.Error as e:
        if len(e.args) > 0:
            msg = e.args[0]
        else:
            msg = ("""
Erreur pendant l'exécution de la requête.
Cette erreur peut se produire s'il n'y a pas assez de mémoire.
""".format(OOM_HINT))
        print(msg)
        raise


#########################################################
# Cette fonction exécute sur la base
# la requête de mise-à-jour passée en paramètre
#########################################################
@set_connection
def execute_update(connection, query):
    try:
        # On récupère un objet curseur qui permet de parcourir
        # l'ensemble résultat à la manière d'un itérateur.
        cursor = connection.cursor()

        # On exécute la requête ici.
        cursor.execute(query)

    except psycopg2.Error as e:
        print("Erreur d'exécution de la requête - %s:" % e.args[0])


def commit():
    global connection

    if not connection:
        init_connection()

    try:
        connection.commit()

    except psycopg2.Error as e:
        print("Erreur d'exécution de la requête - %s:" % e.args[0])


#########################################################
# Cette fonction initialise la connexion à la base
#########################################################
def init_connection():
    global connection

    try:
        connection = psycopg2.connect(dbname=config.DATABASE,
                                      user=config.USER,
                                      password=config.PASSWORD,
                                      host=config.HOSTNAME)
        register(connection)
    except psycopg2.Error as e:
        print("Database connexion error - %s:" % e.args[0])
        close_connection()


#########################################################
# Cette fonction ferme la connexion à la base
#########################################################
def close_connection():
    global connection

    if connection:
        connection.close()
        connection = None
