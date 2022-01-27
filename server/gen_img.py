from importlib_metadata import sys
from sqlalchemy import outerjoin
import database as db
import drawer as d
import pyproj
import os


"""
Cree une tuile PNG (de taille larg*long) contenant tous les chemins 'highway' contenus dans le rectangle
englobant dont les 4 sommets sont p1, p2, p3 et p4.

srid represente l'identifiant EPSG du systeme de coordonnes dans lequel sont donnes les points 
du rectangle englobant.

La fonctione renvoie le nom de l'image generee.
"""
def create_tile(p1: str, p2: str, p3, p4, srid, larg, long):
    # On place l'imagine dans un dossier axbXcxd
    dossier = p1.replace(".", "_").replace(" ", "x") + "X" + p3.replace(".", "_").replace(" ", "x")

    # L'image prend le nom de ses dimensions
    path = f"./{p1.replace('.', '_').replace(' ', 'x')}X{p3.replace('.', '_').replace(' ', 'x')}/{larg}x{long}.png"
    
    # si l'image est deja generee (en cache) on la renvoie sans traitement supplementaire
    if os.path.isfile(path):
        print("deja en cache")
        return path

    # Sinon, on la cree a partir d'une requete a la base de donnees
    requete = f"select ST_AsText(ST_Transform(linestring, 3857)) \
    from ways \
    where tags ? 'highway' \
    and ST_Contains(ST_MakePolygon( \
    ST_Transform( \
    ST_GeomFromText(\
    'LINESTRING(\
    {p1}, {p2}, {p3}, {p4}, {p1})', {srid}), 4326)), bbox);"
    

    cursor = db.execute_query(requete)
    im = d.Image(int(larg), int(long))

    # on utilise le module pyproj pour projeter les coordonnes en EPSG:3857
    # (Puisque l'on autorise l'entree a etre dans un autre système de coordonnees, en precisant l'id
    # de ce systeme en parametre)
    outputGrid = pyproj.Proj(projparams = 'epsg:3857')
    InputGrid = pyproj.Proj(projparams = f'epsg:{srid}') # en fait c'est bien srid la, car on l'applique a p1 et pas au resultat de la requete

    xmin, ymin = float(p1.split(' ')[0]), float(p1.split(' ')[1]) 
    xmin, ymin = pyproj.transform(InputGrid, outputGrid, xmin, ymin)
        
    xmax, ymax = float(p3.split(' ')[0]), float(p3.split(' ')[1])
    xmax, ymax = pyproj.transform(InputGrid, outputGrid, xmax, ymax)
    
    
    # Pour chaque ligne de resultat de la requete
    for row in cursor:
        linstring = row[0].split(',')
        linstring[0] = linstring[0][11:]
        linstring[-1] = linstring[-1][:-1]

        # on realise une transformation affine
        linstring = [
            [
                float(larg)*(float(elt.split(' ')[0])-xmin)/(xmax-xmin),
                float(long)*(1 - (float(elt.split(' ')[1])-ymin)/(ymax-ymin))
            ] for elt in linstring
        ]
        # On dessine la forme
        im.draw_linestring(linstring, (255, 0, 0, 1))

    try:
        os.mkdir(dossier)
    except Exception:
        pass
    
    im.save(path)
    cursor.close()
    db.close_connection()
    return path
    
        
if __name__ == '__main__': #arg : x1 x2 x3 x4 idReferentiel largeur hauteur   
    create_tile("5.7 45.1", "5.7 45.2", "5.8 45.2", "5.8 45.1", 4326, 2000, 2000)