import requests
import re
import os
import pandas as pd
from requests import Response
from bs4 import BeautifulSoup
from typing import Any, Iterable, List, Tuple

DATASET_PATH: str = os.path.join(os.getcwd(), 'data', 'dataset_libros.csv')
TEST_DATASET_PATH: str = os.path.join(os.getcwd(), 'data', 'dataset_libros_test.csv')

ruta_abs: str = 'https://www.gutenberg.org'
ruta_url: str = 'https://www.gutenberg.org/browse/scores/top1000.php#books-last1'

def obtener_resumen(*, url: str) -> str:
    print(f'> {url}')
    response = requests.get(url)
    response.raise_for_status()  
    
    soup = BeautifulSoup(response.text, 'html.parser')

    summary_tag = soup.find('th', string='Summary')
    
    if summary_tag:
        resumen = summary_tag.find_next_sibling('td').get_text(strip=True)
        return resumen
    else:
        return "Resumen no encontrado"

def get_libros(*, url: str) -> List[str]:
    """
    Extrae una lista de títulos de libros desde una página web dada.

    Esta función realiza una solicitud HTTP GET a la URL proporcionada, 
    luego parsea el contenido HTML de la página para buscar todas las etiquetas 
    <ol> (listas ordenadas) y extrae los elementos de la lista de libros que 
    están dentro de etiquetas <li>. Devuelve una lista de títulos de libros 
    como cadenas de texto, eliminando cualquier entrada vacía.

    Parámetros:
    -----------
    url : str
        La URL de la página web desde la cual se extraerán los títulos de libros.

    Retorna:
    --------
    List[str]
        Una lista de títulos de libros extraídos del contenido HTML de la página web.
        Los títulos vacíos o no válidos son eliminados de la lista.

    Ejemplo:
    --------
    >>> get_libros(url="https://ejemplo.com/libros")
    ['El Quijote', 'Cien años de soledad', 'La sombra del viento']
    """
    response: Response = requests.get(url, verify=False)

    soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')

    ol: Iterable[Any] = soup.findAll('ol')

    libros: List[Tuple[str, str]] = []

    for libro in ol:
        enlaces = libro.findAll('li')
        for enlace in enlaces:
            link: str = enlace.a.get('href')
            
            if 'ebooks' in link:
                resumen: str = obtener_resumen(url=f'{ruta_abs}{link}')
            
            libros.append((enlace.text, resumen))

    libros = [libro for libro in libros if libro[0] != '']

    return libros

def create_dataset(*, libros: List[Tuple[str, str]], SAVE_PATH: str) -> None:
    """
    Crea un conjunto de datos estructurado a partir de una lista de descripciones de libros.

    La función toma una lista de descripciones de libros y extrae de cada entrada el título principal, 
    el título secundario (si existe), el autor (si se encuentra), y el número de referencia. 
    Luego, organiza los datos en un DataFrame de pandas, elimina las filas duplicadas y guarda el 
    resultado en un archivo CSV en la ubicación especificada por el usuario.

    Parámetros:
    -----------
    libros : List[str]
        Una lista de descripciones de libros, donde cada descripción contiene el título del libro, 
        el autor y el número de referencia en un formato predefinido.
    
    SAVE_PATH : str
        Ruta donde se guardará el archivo CSV con los datos extraídos.

    Retorna:
    --------
    None
        La función no retorna ningún valor. Guarda el conjunto de datos procesado en un archivo CSV.

    Detalles del proceso:
    ---------------------
    - `patron_titulo_principal`: Captura el título principal del libro hasta encontrar "Or," o "by" o "(".
    - `patron_titulo_secundario`: Captura el título secundario si existe después de "Or," y antes de "by".
    - `patron_autor`: Captura el nombre del autor si está presente en el formato "by [autor]".
    - `patron_n_ref`: Captura el número de referencia entre paréntesis.
    - Se elimina cualquier fila duplicada antes de guardar los datos en el archivo CSV.

    Ejemplo:
    --------
    >>> libros = [
            "The Great Gatsby; Or, A Novel by F. Scott Fitzgerald (1234) https://link.com",
            "To Kill a Mockingbird by Harper Lee (5678) https://link.com"
        ]
    >>> create_dataset(libros=libros, SAVE_PATH="dataset_libros.csv")
    """
    patron_titulo_principal: str = r'^(.*?)(?:;?\s?Or,|\sby|\s\()' 
    patron_titulo_secundario: str = r';?\s?Or,?\s(.*?)\sby'  
    patron_autor: str = r'by\s(.*?)\s\(' 
    patron_n_ref: str = r'\((\d+)\)' 
    patron_link: str = r'\)\s(.*)'  

    titulo_principal: List[str] = []
    titulo_secundario: List[str] = []
    autor: List[str] = []
    n_ref: List[str] = []
    resumenes: List[str] = []
    
    for libro, resumen in libros:
        titulo = re.search(patron_titulo_principal, libro)
        titulo_principal.append(titulo.group(1) if titulo else "")

        secundario = re.search(patron_titulo_secundario, libro)
        titulo_secundario.append(secundario.group(1) if secundario else "")

        autor_libro = re.search(patron_autor, libro)
        autor.append(autor_libro.group(1) if autor_libro else "")

        ref = re.search(patron_n_ref, libro)
        n_ref.append(ref.group(1) if ref else "")
        
        resumenes.append(resumen)
        
    dataset_libros = pd.DataFrame({
        'Titulo Principal': titulo_principal,
        'Titulo Secundario': titulo_secundario,
        'Autor': autor,
        'N° Ref': n_ref,
        'Resumen': resumenes
    })

    dataset_libros.duplicated().sum()

    dataset_libros.drop_duplicates(inplace=True)

    dataset_libros.to_csv(SAVE_PATH, index=False)
    
if __name__ == '__main__':
    libros = get_libros(url=ruta_url)
    create_dataset(libros=libros,
                   SAVE_PATH=DATASET_PATH)