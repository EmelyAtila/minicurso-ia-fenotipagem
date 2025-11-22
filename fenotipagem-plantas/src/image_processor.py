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
    
    def segment_plant(self) -> np.ndarray:
        """
        Segmenta a planta do fundo usando técnicas de segmentação por cor (HSV)
        Função que isola a planta do fundo 
        """
        if self.processed_image is None:
            self.preprocess_image()

         #1. converter para HSV (Hue, Saturation, Value)
         # O HSV é melhora para isolar cores específicas(como o verde da planta)   
        hsv = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2HSV)

        #2. Definir o range da cor verde 
        #Ester valores definem o que é considerado "verde" no espaço HSV
        lower_green = np.array([25,40,40])
        upper_green = np.array([90, 255, 255])

        #3. Criar Máscara Binária
        #Tudo que estiver no range verde se torna branco (255), o resto preto (0)
        mask = cv2.inRange(hsv, lower_green, upper_green)

        #4. Operações Morfológicas (Limpeza da Máscara)
        Kernel = np. ones((5,5), np.uint8) #Cria um elemento estruturante 
        #MORPH_OPEN: Fecha alguns buracos na planta (PREENCHE) 
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iteration=2)
        #MORPH_OPEN: Remove pequenos pontos e ruídos fora da planta 
        mask = cv2.morphologyEx(mask,cv2.MORPH_OPEN, kernel, iteration=1)

        #5. Isolamento do maior Contorno(Garante que só a planta seja considerada)
        contours, _ = cv2.findContours = max(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours: 
            #Encontra o contorno com a maior area(Assumindo ser a plantla)
            largest_contour = max(contours, key = cv2.contourArea)
            #Cria uma nova mascara preta
            mask = np.zeros_like(mask)
            #Desenha apenas o maior contorno na nova mascara 
            cv2.drawContours(mask, [largest_contour], -1,255,-1)

            self.mask = mask
            return mask
        
    def extract_morphological_festures(self) ->Dict:
        """
        Extrai características morfológicas (área, perímetro, forma) da planta.
        """
        if self.mask is None:
            self.segment_plant()

        features ={}
        leaft_area = cv2.countNonzero(self.mask)
        features["area_foliar_pixels"] = int(leaft_area)

        contours, _= cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key= cv2.contourArea)
            mask = np.zeros_like(mask)
            cv2.drawContours(mask, [largest_contour], -1,255,-1)

        self.mask = mask
        return mask
        
