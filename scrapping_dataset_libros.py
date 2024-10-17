import requests
import re
import os
import pandas as pd
from requests import Response
from bs4 import BeautifulSoup
from typing import Any, Iterable, List

DATASET_PATH: str = os.path.join(os.getcwd(), 'data', 'dataset_libros.csv')

ruta_url: str = 'https://www.gutenberg.org/browse/scores/top1000.php#books-last1'

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

    libros: List[str] = []

    for libro in ol:
        enlaces = libro.findAll('li')
        for enlace in enlaces:
            libros.append(enlace.text)

    libros = [libro for libro in libros if libro != '']

    return libros

def create_dataset(*, libros: List[str], SAVE_PATH: str) -> None:
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

    for libro in libros:
        titulo = re.search(patron_titulo_principal, libro)
        titulo_principal.append(titulo.group(1) if titulo else "")

        secundario = re.search(patron_titulo_secundario, libro)
        titulo_secundario.append(secundario.group(1) if secundario else "")

        autor_libro = re.search(patron_autor, libro)
        autor.append(autor_libro.group(1) if autor_libro else "")

        ref = re.search(patron_n_ref, libro)
        n_ref.append(ref.group(1) if ref else "")
        
    dataset_libros = pd.DataFrame({
        'Titulo Principal': titulo_principal,
        'Titulo Secundario': titulo_secundario,
        'Autor': autor,
        'N° Ref': n_ref,
    })

    dataset_libros.duplicated().sum()

    dataset_libros.drop_duplicates(inplace=True)

    dataset_libros.to_csv(SAVE_PATH, index=False)
    
if __name__ == '__main__':
    libros: List[str] = get_libros(url=ruta_url)
    create_dataset(libros=libros,
                   SAVE_PATH=DATASET_PATH)