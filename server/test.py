from importlib_metadata import sys
import database as db

if __name__ == '__main__':
    #! check raise du nombre d'argument a faire pour etre propre
    
    requete = f"SELECT tags->'name', ST_X(geom), ST_Y(geom) FROM nodes WHERE tags->'name' LIKE '{sys.argv[1]}';"
    cursor = db.execute_query(requete)
    for row in cursor: # Pour chaque ligne
        print(f"{row[0] :<25}| {row[1] :<12}| {row[2] :<12}")

    cursor.close()
    db.close_connection()
        