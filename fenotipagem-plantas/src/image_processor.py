"""
Módulo de Processamento de Imagens para Fenotipagem de Plantas
Utiliza OpenCV e técnicas de visão computacional para extrair
características morfológicas
"""

# Importações
import cv2 # OpenCV (Visão Computacional)
import numpy as np # NumPy (Cálculo Numérico e Arrays)
from typing import Dict, List # Tipagem (Melhora a legibilidade e documentação)
import json # Para trabalhar com arquivos JSON
from datetime import datetime # Para registrar o timestamp

class PlantPhenotyping:
    """
    Classe para processamento de imagens e extração de características fenotípicas de plantas
    """
    def __init__(self, image_path : str):
        """
        Construtor da classe. Inicializa o processador com o caminho da imagem.
        """
        self.image_path = image_path
        # Carrega a imagem. cv2.imread retorna um array NumPy.
        self.original_image = cv2.imread(image_path)

    # Tratamento de erro: se a imagem não carregar, lança uma exceção.
    if self.original_image is None:
       raise ValueError(f"Não foi possivél processar a imagem: {image_path}")

    # Variáveis de instância (atributos) para armazenar o estado do processamento
    self.processed_image = None
    self.mask = None
    self.features = {}