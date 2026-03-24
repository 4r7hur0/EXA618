import urllib.request
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import os

seeds_file = 'EXA618/atividade5/seeds.txt'
output_file = 'EXA618/atividade5/index.html'

html_final = """
<html>
<head>
    <meta charset='utf-8'>
    <title>Resultado Agregado</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background-color: #f4f4f9; }
        .card { border: 1px solid #ddd; padding: 15px; border-radius: 8px; margin-bottom: 20px; background: white; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
        img { display: block; margin: 10px 0; border-radius: 4px; max-height: 250px; object-fit: cover; }
        a { color: #007bff; text-decoration: none; font-weight: bold; }
        a:hover { text-decoration: underline; }
        .fonte-link { font-size: 0.85em; color: #555; margin-top: 10px; }
    </style>
</head>
<body>
    <h1>Dados dos Alunos</h1>
"""

try:
    with open(seeds_file, 'r', encoding='utf-8') as f:
        for linha in f:
            url = linha.strip()
            if not url: continue
            
            try:
                page = urllib.request.urlopen(url)
                html = str(page.read().decode('utf-8'))
                soup = BeautifulSoup(html, 'lxml')
                
                todas_as_imgs = soup.find_all('img')
                
                if todas_as_imgs:
                    raw_src = todas_as_imgs[0].attrs.get("src")
                    
                    if raw_src:
                        titulo = soup.title.string.strip() if soup.title else "Sem Título"
                        
                        # urljoin resolve caminhos relativos (../imagem.png ou /imagem.png)
                        # baseando-se na URL de origem (seja ela http ou file://)
                        primeira_img_src = urljoin(url, raw_src)
                        
                        html_final += f"<div class='card'>"
                        html_final += f"<h2><a href='{url}' target='_blank'>{titulo}</a></h2>"
                        html_final += f"<img src='{primeira_img_src}' width='200'>"
                        html_final += f"<p class='fonte-link'>Fonte: <a href='{url}' target='_blank'>{url}</a></p></div>"
                        
                        print(f"Incluído: {titulo}")
                    else:
                        print(f"Ignorado (sem src): {url}")
                else:
                    print(f"Ignorado (sem tag img): {url}")

            except Exception as e:
                print(f"Erro em {url}: {e}")

    html_final += "</body></html>"

    with open(output_file, 'w', encoding='utf-8') as f_out:
        f_out.write(html_final)
    
    print(f"\nTerminou.")

except FileNotFoundError:
    print("Arquivo seeds.txt não encontrado.")