import streamlit as st
import os
import pandas as pd
import pickle
import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline, Pipeline
from sklearn.metrics import classification_report
from sklearn.neighbors import NearestNeighbors
from sentence_transformers import SentenceTransformer

RECOMENDADOR_MODEL_PATH: str = os.path.join(os.getcwd(), 'models', 'modelo_recomendador.pickle')
ESTADO_ANIMO_PATH: str = os.path.join(os.getcwd(), 'models', 'modelo_estado_animo.pickle')

class Models:
    def __init__(self) -> None:
        self.modelo_recomendador: Pipeline = pickle.load(open(RECOMENDADOR_MODEL_PATH, 'rb'))
        self.modelo_animo: Pipeline = pickle.load(open(ESTADO_ANIMO_PATH, 'rb'))
        
        self.dataset_juegos: pd.DataFrame = pd.read_csv(os.path.join(os.getcwd(), 'data', 'bgg_database.csv'))
        self.dataset_peliculas: pd.DataFrame = pd.read_csv(os.path.join(os.getcwd(), 'data', 'IMDB-Movie-Data.csv'))
        self.dataset_libros: pd.DataFrame = pd.read_csv(os.path.join(os.getcwd(), 'data', 'dataset_libros.csv'))
        
        self.df_embedings_totales: pd.DataFrame = pd.read_csv(os.path.join(os.getcwd(), 'data', 'embedings_totales.csv'))
        self.transformer: SentenceTransformer = SentenceTransformer('sentence-transformers/distiluse-base-multilingual-cased')
        
    def embbed(self, string: str) -> np.ndarray:
        encoding: np.ndarray = self.transformer.encode(string,
                                       convert_to_numpy=True,
                                       output_value='sentence_embedding')
        
        print(f'Encoding shape: {encoding.shape}')
        
        return encoding.reshape(1, -1)
        
    def predict_animo(self, prompt: str) -> str:
        return self.modelo_animo.predict([prompt])[0]
    
    def predict_media(self, prompt: str) -> List[tuple[str, float, str]]:
        '''
        Devuelve 5 recomendaciones más acordes a la consulta
        '''
        consulta: np.ndarray = self.embbed(prompt)

        recomendaciones: List[tuple[str, float, str]] = []
        
        # Realizar la búsqueda de los vecinos más cercanos
        distances, indices = self.modelo_recomendador[0].kneighbors(consulta)

        for j in range(5):
            # Obtenemos el índice del vecino más cercano
            idx = indices[0][j]
            i = self.df_embedings_totales['index'].iloc[idx]
            dataset = self.df_embedings_totales['tipo'].iloc[idx]

            # Dependiendo del dataset, accedemos al DataFrame correspondiente
            if dataset == 'juego':
                vecino = self.dataset_juegos['game_name'].iloc[i]
            elif dataset == 'libro':
                vecino = self.dataset_libros['Titulo Principal'].iloc[i]
            elif dataset == 'pelicula':
                vecino = self.dataset_peliculas['Title'].iloc[i]
            
            recomendaciones.append((vecino, distances[0][j], dataset))
            
            # Imprimir el vecino y la distancia
            print(f"Vecino {j + 1}: {vecino} - Distancia: {distances[0][j]:.4f} - {dataset}")
            
        return recomendaciones
        
if __name__ == '__main__':
    recomendador = Models()

    st.title("Recomendador de contenido multimedia.")
    
    emotion, phrase = st.columns([2, 5])
    
    animo: str = emotion.text_input(label='Estado de ánimo: ')
    frase: str = phrase.text_input(label='Ingrese frase: ')
    
    procesar = st.button(label="Procesar")
    
    if procesar:
        recomendaciones: List[tuple[str, float, str]] = recomendador.predict_media(prompt=f'{frase, {animo}}')
        
        for media, acc, type_ in recomendaciones:
            with st.container():
                c1, c2, c3 = st.columns([5, 3, 1])
                
                c1.write(media)
                c2.write(type_)
                c3.write(round(acc, 2))            