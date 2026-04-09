# Atividade 2.1 — Mini Blog (Flask + CSV)

Página de blog em Python usando Flask, com:
- envio de mensagens (autor + mensagem)
- registro de data/hora do envio
- persistência em arquivo `CSV` lido/escrito pelo app

## Estrutura
- `app.py`: aplicação Flask
- `templates/index.html`: página (form + listagem)
- `data/messages.csv`: arquivo gerado automaticamente com `author,message,created_at`

## Como rodar (Windows / PowerShell)
Entre na pasta do projeto:

```powershell
cd C:\laragon\www\ahhh\atividade2.1
```

Crie e ative um ambiente virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```powershell
pip install -r requirements.txt
```

Rode o servidor:

```powershell
python .\app.py
```

Acesse:
- `http://127.0.0.1:5000/`

## Deploy no Vercel (recomendado para este projeto)
### Repositório
- Faça commit da pasta `atividade2.1` e envie para o GitHub.

### Criar o projeto no Vercel
1. Acesse [vercel.com](https://vercel.com) → **Add New…** → **Project**.
2. Importe o repositório.
3. Em **Root Directory**, defina **`atividade2.1`** (importante: é onde estão `vercel.json`, `api/` e `app.py`).
4. O Vercel detecta Python; **Build** instala `requirements.txt` automaticamente.
5. **Deploy**.

Após o deploy, a URL pública (ex.: `https://seu-projeto.vercel.app`) abre o blog.

### Arquivos usados no Vercel
- `vercel.json`: encaminha todas as rotas para a função Python `api/index.py`.
- `api/index.py`: importa o Flask `app` de `app.py` (WSGI para serverless).

### Persistência do CSV no Vercel (importante)
- Em ambiente local, o arquivo fica em `data/messages.csv`.
- No Vercel, o código grava em **`/tmp/atividade21_blog_data/messages.csv`** (disco do deploy não permite escrita).
- Em serverless, dados em `/tmp` podem **sumir** entre cold starts ou instâncias diferentes — é uma limitação da plataforma, não do Flask.
- Para persistência “de verdade” na nuvem, use um banco (ex.: Vercel Postgres) ou storage gerenciado; para a **atividade em sala**, rodar local + mostrar o CSV costuma ser o esperado.

## Deploy no Render (alternativa)
### Subir no GitHub
- Faça commit da pasta `atividade2.1` e suba para um repositório no GitHub.

### Criar o serviço no Render
- No Render, crie um **Web Service** a partir do repositório.
- Aponte o **Root Directory** para `atividade2.1`.
- Comandos:
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

Você também pode usar o arquivo `render.yaml` deste projeto.

### Persistência do CSV (Render)
- Em plano Free, o disco pode ser **efêmero**; use **Persistent Disk** ou banco se precisar guardar sempre.

## Como apresentar em sala (roteiro rápido)
- Abrir a página no navegador.
- Enviar uma mensagem.
- Mostrar que o arquivo `data/messages.csv` foi criado/atualizado com autor/mensagem/data.
- Mostrar rapidamente no `app.py`:
  - rotas `GET /` e `POST /`
  - leitura/escrita do CSV
  - redirect pós-POST (evita duplicar ao dar refresh)

