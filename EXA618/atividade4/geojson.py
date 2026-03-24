import json 
import pandas as pd

df = pd.read_csv('saida_sax.csv')

geojson = {
    "type": "FeatureCollection",
    "features": []
}

for index, row in df.iterrows():
    feature = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [row['lon'], row['lat']]
        },
        "properties": {
            "name": row['nome'],
            "tipo": row['tipo']
        }
    }
    geojson["features"].append(feature)

with open('geo.geojson', 'w') as f:    json.dump(geojson, f, ensure_ascii=True, indent=4)
