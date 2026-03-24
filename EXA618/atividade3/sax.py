import xml.sax
import time
import csv

class OSMHandler(xml.sax.ContentHandler):
    def __init__(self, escritor_csv):
        self.escritor = escritor_csv
        self.count = 0
        self.current_node_data = {}
        self.is_node = False

    def startElement(self, name, attrs):
        if name == "node":
            self.is_node = True
            self.current_node_data = {
                "lat": attrs.get("lat"),
                "lon": attrs.get("lon"),
                "tags": {}
            }
        elif name == "tag" and self.is_node:
            k = attrs.get("k")
            v = attrs.get("v")
            self.current_node_data["tags"][k] = v

    def endElement(self, name):
        if name == "node":
            tags = self.current_node_data["tags"]
            if "amenity" in tags and "name" in tags:
                self.count += 1
                # Escreve diretamente no CSV em vez de apenas dar print
                self.escritor.writerow([
                    self.current_node_data["lat"],
                    self.current_node_data["lon"],
                    tags["amenity"],
                    tags["name"]
                ])
            self.is_node = False
            self.current_node_data = {}

# Execução
inicio = time.perf_counter()

with open('saida_sax.csv', 'w', newline='', encoding='utf-8') as f:
    escritor = csv.writer(f)
    escritor.writerow(['lat', 'lon', 'tipo', 'nome']) # Cabeçalho
    
    handler = OSMHandler(escritor)
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse("EXA618/atividade3/map.osm")

fim = time.perf_counter()
print(f"SAX finalizado. Tempo: {fim - inicio:.4f}s")