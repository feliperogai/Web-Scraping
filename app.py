from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup

# Inicializa a aplicação Flask
app = Flask(__name__)

def scrape_page(url):
    """
    Faz o scraping de uma página da web dada a URL.

    Args:
        url (str): A URL da página a ser raspada.

    Returns:
        dict: Um dicionário contendo o título da página, links, 
              conteúdo principal e URLs de imagens. Se ocorrer um erro, 
              retorna um dicionário com a mensagem de erro.
    """
    try:
        # Realiza uma requisição GET para a URL fornecida
        response = requests.get(url)
        # Verifica se a requisição foi bem-sucedida (status 200)
        response.raise_for_status()
    except requests.RequestException as e:
        # Em caso de erro, retorna um dicionário com a mensagem de erro
        return {"error": str(e)}

    # Analisa o conteúdo HTML da página usando BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Obtém o título da página
    title = soup.title.string if soup.title else 'Título não encontrado'
    
    # Coleta todos os links (href) presentes na página, organizados por texto
    links = [{"texto": a.get_text(strip=True), "url": a['href']} for a in soup.find_all('a', href=True)]
    
    # Extrai o conteúdo textual principal da página e separa em parágrafos
    paragraphs = [p.get_text(strip=True) for p in soup.find_all('p')]
    main_content = "\n\n".join(paragraphs) if paragraphs else 'Conteúdo não encontrado.'
    
    # Coleta as URLs de todas as imagens presentes na página
    images = [{"url": img['src'], "alt": img.get('alt', 'Imagem sem descrição')} for img in soup.find_all('img', src=True)]

    # Retorna um dicionário com os dados extraídos
    return {
        'Título da Página': title,
        'Links': links,
        'Conteúdo Principal': main_content,
        'Imagens': images
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Lida com a rota principal da aplicação.

    Se a requisição for GET, renderiza o formulário. Se for POST,
    realiza o scraping da URL fornecida e exibe os resultados.

    Returns:
        str: O HTML renderizado da página, incluindo os resultados do scraping.
    """
    result = {}  # Dicionário para armazenar os resultados do scraping
    if request.method == 'POST':
        # Obtém a URL do formulário enviado
        url = request.form.get('url')
        # Chama a função de scraping e armazena os resultados
        result = scrape_page(url)

    # Renderiza o template index.html, passando os resultados para ele
    return render_template('index.html', result=result)

if __name__ == '__main__':
    # Executa a aplicação Flask em modo de depuração
    app.run(debug=True)