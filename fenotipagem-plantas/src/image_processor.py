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
    
    def preprocess_image(self) -> np.ndarray:
        """
        Pré-processa a imagem para melhorar a segmentação (redução de ruído).
        """
        #1. Converte de BGR (Padrão OpenCV) para RGB
        img_rgb = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)

        #2. Aplicar Desfoque Gaussiano(Gaussian Blur) para reduzir ruído
        #(5,5) é o tamanho do kernel, 0 é o desvio padrão 
        blurred = cv2.GaussianBlur(img_rgb, (5, 5), 0)
        
        self.preprocess_image = blurred
        return blurred