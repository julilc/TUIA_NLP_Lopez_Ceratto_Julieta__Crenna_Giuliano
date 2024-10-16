import sklearn
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
from prettytable import PrettyTable
#import tensorflow_text
import bokeh
import bokeh.models
import bokeh.plotting
import numpy as np
import os
import tensorflow as tf
import tensorflow_hub as hub
from sklearn.preprocessing import OneHotEncoder
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import PyPDF2
import pytesseract
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
import gdown
from gensim.models import KeyedVectors
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import nltk
from nltk.corpus import stopwords
import matplotlib.pyplot as plt
import spacy
#Visualizador incluido en spacy
from spacy import displacy
import stanza
import transformers
import sentence_transformers
from transformers import BertTokenizer
from gliner import GLiNER