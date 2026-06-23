# GabaritoAC

Portal de notícias sobre educação, concursos e processos seletivos do estado do Acre. Construído com Django + Wagtail CMS.

## Stack

- **Backend:** Python 3.12, Django 6, Wagtail 7.4
- **Frontend:** Tailwind CSS v4, Font Awesome 6
- **Banco:** SQLite (dev) / PostgreSQL (produção)
- **Deploy:** Docker, Gunicorn

## Desenvolvimento

```bash
# Ativar virtualenv
python -m venv venv && source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Instalar Tailwind CSS
npm install

# Compilar CSS
npm run build:css

# Criar banco e dados iniciais
python manage.py migrate
python manage.py createsuperuser

# Servidor de desenvolvimento
python manage.py runserver
```

## CSS

O Tailwind CSS v4 usa entrada em `setup/static/css/input.css` e compila para `setup/static/css/setup.css`:

```bash
npm run build:css     # compilar uma vez
npm run watch:css     # watch mode
```

Nunca edite `setup.css` manualmente — edite `input.css` e recompile.

## Variáveis de ambiente

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | produção | — | Chave secreta Django |
| `DJANGO_SETTINGS_MODULE` | — | `setup.settings.dev` | Ambiente (`dev` ou `production`) |
| `ALLOWED_HOSTS` | produção | — | Hosts permitidos |

## Estrutura

```
gabaritoac/
├── home/              # Home page, Sobre, Newsletter
├── noticias/          # Notícias, editais, categorias
├── search/            # Busca interna
├── setup/             # Config Django, templates base, CSS
│   ├── settings/      # base.py, dev.py, production.py
│   ├── static/        # CSS, JS, imagens
│   └── templates/     # Navbar, footer, 404, 500
└── media/             # Uploads (Wagtail images)
```

## Funcionalidades

- Home page com hero, grid de notícias e mural de editais
- Página de artigo com conteúdo em StreamField
- Categorias com badge de cor personalizada
- Newsletter com captura de e-mail
- Mural de editais com status (aberto/últimos dias/encerrado)
- Importação automatizada de editais da UFAC e IFAC
- Banner publicitário em múltiplas posições
- Responsivo para mobile, tablet e desktop
