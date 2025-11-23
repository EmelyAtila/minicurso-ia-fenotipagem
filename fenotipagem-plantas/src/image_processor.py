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

        #1. Área Foliar (contagem de pixels brancos na máscara).
        leaft_area = cv2.countNonzero(self.mask)
        features['area_foliar_pixels'] = int(leaft_area)

        #2. Perímetro, Compacidade, Dimensões, Solidez, etc.
        contours, _ = cv2.findContours(self.mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)

            #Perímetro
            perimeter = cv2.arcLength(largest_contour, True)
            features['perimetro'] = float(perimeter)

            # Compacidade (Circularidade)
            if perimeter > 0:
                compactness = (4 * np.pi * leaft_area) / (perimeter ** 2)
                features['compacidade'] = float(compactness)

            #Bounding Box (Largura e Altura)
            x, y, w, h = cv2.boundingRect(largest_contour)
            features['largura'] = int(w)
            features['altura'] = int(h)
            features['aspect_ratio'] = float(h / w) if w > 0 else 0

            #Solidez (Solidity)
            hull = cv2.convexHull(largest_contour)
            hull_area = cv2.contourArea(hull)
            if hull_area > 0:
                solidity = leaft_area / hull_area
                features['solidez'] = float(solidity)

            #Momentos de Hu (Invariantes de Forma)
            moments = cv2.moments(largest_contour)
            if moments['m00'] != 0:
                hu_moments = cv2.HuMoments(moments)
                for i, hu in enumerate(hu_moments):
                    features[f'hu_moment_{i +1}'] = float(hu[0])

        #3. Adicionar características de cor e textura (funções auxiliares)
        features.update(self._extract_color_features())
        features.update(self._extract_texture_features())
        
        self.features = features
        return features
    

    #Funções Privadas
    def _extract_color_features(self) -> Dict:
        """
        Extrai características de cor, incluindo índices de vegetação (ExG, VARI).
        """
        # ... (código para extrair médias RGB, HSV e calcular ExG e VARI)
        # O código completo está no arquivo final, mas o conceito é:
        # 1. Aplicar a máscara na imagem original para isolar a cor da planta.
        # 2. Calcular a média e o desvio padrão de cada canal de cor (R, G, B).
        # 3. Aplicar as fórmulas dos índices de vegetação (ExG = 2G - R - B, etc.).
        pass # Placeholder para o código completo

    def _extract_texture_features(self) -> Dict:
        """
        Extrai características de textura usando gradientes (Sobel).
        """
        # ... (código para calcular gradientes e variância Laplaciana)
        # O conceito é:
        # 1. Converter a imagem para escala de cinza.
        # 2. Aplicar filtros de borda (Sobel, Laplacian) para medir a variação de intensidade.
        # 3. Valores altos indicam textura complexa (nervuras, rugosidade).
        pass # Placeholder para o código completo


    #Funções de Saída e Pipeline Completo  
    def save_visualization(self, output_path: str) -> None:
        """
        Salva uma imagem de visualização com 4 painéis (Original, Máscara, etc.).
        """
        # ... (código para combinar as imagens e salvar)
        pass # Placeholder

    def save_features_json(self, output_path: str) -> None:
        """
        Salva as características extraídas em um arquivo JSON.
        """
        # ... (código para serializar o dicionário self.features para JSON)
        pass # Placeholder

    def process_complete(self, output_dir: str, base_name: str) -> Dict:
        """
        Executa o pipeline completo: pré-processamento -> segmentação -> extração -> salvamento.
        """
        self.preprocess_image()
        self.segment_plant()
        features = self.extract_morphological_features()
        
        # Define os caminhos de saída
        viz_path = f"{output_dir}/{base_name}_visualization.png"
        json_path = f"{output_dir}/{base_name}_features.json"
        
        # Salva os resultados
        self.save_visualization(viz_path)
        self.save_features_json(json_path)
        
        return features

    def batch_process(input_dir: str, output_dir: str) -> List[Dict]:
        """
        Função estática para processar múltiplas imagens em um diretório.
        """
        # ... (código para iterar sobre arquivos, chamar PlantPhenotyping.process_complete e consolidar resultados)
        pass # Placeholder
