from xml.dom.minidom import parse
import time
import csv

inicio = time.perf_counter()

mapDocument = parse("EXA618/atividade3/map.osm")

with open('saida_dom.csv', 'w', newline='', encoding='utf-8') as f:
    escritor = csv.writer(f)
    escritor.writerow(['lat', 'lon', 'tipo', 'nome']) # Cabeçalho

    for node in mapDocument.getElementsByTagName("node"):
        tem_amenity = False
        tem_name = False
        tipo, name = "", ""
        
        for tag in node.getElementsByTagName("tag"):
            k = tag.getAttribute("k")
            if k == "amenity":
                tem_amenity = True
                tipo = tag.getAttribute("v")
            elif k == "name":
                tem_name = True
                name = tag.getAttribute("v")
        
        if tem_amenity and tem_name:
            lat = node.getAttribute("lat")
            lon = node.getAttribute("lon")
            escritor.writerow([lat, lon, tipo, name])

fim = time.perf_counter()
print(f"DOM finalizado. Tempo: {fim - inicio:.4f}s")