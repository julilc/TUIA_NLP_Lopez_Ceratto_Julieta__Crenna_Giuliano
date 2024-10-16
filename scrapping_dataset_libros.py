from rqst import *
ruta_url = 'https://www.gutenberg.org/browse/scores/top1000.php#books-last1'
response = requests.get(ruta_url, verify=False)
soup = BeautifulSoup(response.text, 'html.parser')
ol = soup.findAll('ol')
libros = []
for libro in ol:
    enlaces = libro.findAll('li')
    for enlace in enlaces:
        libros.append(enlace.text)

libros = [libro for libro in libros if libro != '']


# Expresión regular para extraer las partes
patron_titulo_principal = r'^(.*?)(?:;?\s?Or,|\sby|\s\()'  # Captura todo hasta "Or," o "by" o "(" si no hay más
patron_titulo_secundario = r';?\s?Or,?\s(.*?)\sby'  # Captura el título secundario si está
patron_autor = r'by\s(.*?)\s\('  # Captura el autor si está
patron_n_ref = r'\((\d+)\)'  # Captura el número entre paréntesis
patron_link = r'\)\s(.*)'  # Captura todo después del paréntesis final para el enlace
titulo_principal = []
titulo_secundario = []
autor = []
n_ref = []
for libro in libros:
    # Extraer título principal
    titulo = re.search(patron_titulo_principal, libro)
    titulo_principal.append(titulo.group(1) if titulo else "")

    # Extraer título secundario (si existe)
    secundario = re.search(patron_titulo_secundario, libro)
    titulo_secundario.append(secundario.group(1) if secundario else "")

    # Extraer autor (si existe)
    autor_libro = re.search(patron_autor, libro)
    autor.append(autor_libro.group(1) if autor_libro else "")

    # Extraer número de referencia
    ref = re.search(patron_n_ref, libro)
    n_ref.append(ref.group(1) if ref else "")
dataset_libros = pd.DataFrame({
    'Titulo Principal': titulo_principal,
    'Titulo Secundario': titulo_secundario,
    'Autor': autor,
    'N° Ref': n_ref,
})

##Quito lineas duplicadas
dataset_libros.duplicated().sum()

dataset_libros.drop_duplicates(inplace=True)

#Guardo dataset en .csv
dataset_libros.to_csv('./src/dataset_libros.csv', index=False)