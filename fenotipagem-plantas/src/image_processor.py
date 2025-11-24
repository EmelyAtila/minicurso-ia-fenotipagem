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
        Kernel = np.ones((5,5), np.uint8) #Cria um elemento estruturante 
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
            features["area_convexa"] = float(hull_area) #observar 

            if hull_area > 0:
                solidity = leaft_area / hull_area
                features['solidez'] = float(solidity)

            #Momentos de Hu (Invariantes de Forma)
            moments = cv2.moments(largest_contour)
            if moments['m00'] != 0:
                cx = int(moments["m10"] / moments["m00"]) #observar 
                cy = int(moments["m01"] / moments["m00"]) #observar 
                features["centro_massa_x"] = cx #observar 
                features["centro_massa_y"] = cy #observar 

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

        # ... (código de verificação e máscara)
        if self.mask is None or self.processed_image is None: return {}
        masked_image = cv2.bitwise_and(self.processed_image,self.processed_image, mask=self.mask)
        hsv = cv2.cvtColor(masked_image, cv2.COLOR_RGB2HSV)
        color_features = {}

        # Estatísticas RGB (Média e Desvio Padrão)
        for i, channel_name in enumerate(["R", "G", "B"]):
            channel = self.processed_image[:,:,i]
            masked_channel = channel[self.mask > 0]
            if len(masked_channel) > 0:
                color_features[f"mean_{channel_name}"] = float(np.mean(masked_channel))
                color_features[f"std_{channel_name}"] = float(np.std(masked_channel))
        
        # Cálculo dos Índices de Vegetação
        masked_r = self.processed_image[:, :, 0][self.mask > 0]
        masked_g = self.processed_image[:, :, 1][self.mask > 0]
        masked_b = self.processed_image[:, :, 2][self.mask > 0]

        if len(masked_r) > 0:
            # ExG (Excess Green Index): 2G - R - B
            # Alto valor indica planta mais verde e saudável
            exg = 2 * masked_g.astype(float) - masked_r.astype(float) - masked_b.astype(float)
            color_features["excess_green_index"] = float(np.mean(exg)) 

            # VARI (Visible Atmospherically Resistant Index)
            # Outro índice de vigor, menos sensível a variações de luz
            denominator = masked_g.astype(float) + masked_r.astype(float) - masked_b.astype(float)
            vari = np.divide(masked_g.astype(float) - masked_r.astype(float), denominator, out=np.zeros_like(denominator,dtype=float), where=denominator!=0)
            color_features["vari_index"] = float(np.mean(vari))
        return color_features


    def _extract_texture_features(self) -> Dict:
        """
        Extrai características de textura usando gradientes (Sobel).
        """
        # ... (código para calcular gradientes e variância Laplaciana)
        # O conceito é:
        # 1. Converter a imagem para escala de cinza.
        # 2. Aplicar filtros de borda (Sobel, Laplacian) para medir a variação de intensidade.
        # 3. Valores altos indicam textura complexa (nervuras, rugosidade).
        if self.mask is None or self.processed_image is None: return {}

        # Converte para escala de cinza e aplica a máscara
        gray = cv2.cvtColor(self.processed_image, cv2.COLOR_RGB2GRAY) 
        masked_gray = cv2.bitwise_and(gray, gray, mask=self.mask)
        texture_features = {}

        # Sobel (Gradiente): Detecta a taxa de mudança de intensidade (bordas)
        sobelx = cv2.Sobel(masked_gray, cv2.CV_64F, 1, 0, ksize=3) # Gradiente na direção X
        sobely = cv2.Sobel(masked_gray, cv2.CV_64F, 0, 1, ksize=3) # Gradiente na direção Y

        # Magnitude do Gradiente: Combina X e Y para ter a força total da borda
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        masked_gradient = gradient_magnitude[self.mask > 0]

        if len(masked_gradient) > 0:
            texture_features["gradient_mean"] = float(np.mean(masked_gradient))
            texture_features["gradient_std"] = float(np.std(masked_gradient))

        # Laplaciano: Mede a variação de segunda ordem (nitidez/rugosidade)""
        laplacian = cv2.Laplacian(masked_gray, cv2.CV_64F)
        masked_laplacian = laplacian[self.mask > 0]
        
        if len(masked_laplacian) > 0:
            texture_features['laplacian_variance'] = float(np.var(masked_laplacian))

        return texture_features


    #Funções de Saída e Pipeline Completo  
    def save_visualization(self, output_path: str) -> None:
        """
        Salva uma imagem de visualização com 4 painéis (Original, Máscara, etc.).
        """
        if self.mask is None: self.segment_plant()
        h, w = self.original_image.shape[:2]
        panel1 = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
        panel2 = cv2.cvtColor(self.mask, cv2.COLOR_GRAY2RGB)
        panel3 = self.original_image.copy()
        overlay = np.zeros_like(panel3)
        overlay[self.mask > 0] = [0, 255, 0]
        panel3 = cv2.addWeighted(panel3, 0.7, overlay, 0.3, 0)
        panel3 = cv2.cvtColor(panel3, cv2.COLOR_BGR2RGB)
        panel4 = self.original_image.copy()
        contours, _ = cv2.findContours(self.mask, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.drawContours(panel4, [largest_contour], -1, (0, 255, 0), 3)
            x, y, w_c, h_c = cv2.boundingRect(largest_contour)
            cv2.rectangle(panel4, (x, y), (x+w_c, y+h_c), (255, 0, 0), 2)

        panel4 = cv2.cvtColor(panel4, cv2.COLOR_BGR2RGB)
        top_row = np.hstack([panel1, panel2])
        bottom_row = np.hstack([panel3, panel4])
        combined = np.vstack([top_row, bottom_row])
        cv2.imwrite(output_path, cv2.cvtColor(combined, cv2.COLOR_RGB2BGR))

    def save_features_json(self, output_path: str) -> None:
        """
        Salva as características extraídas em um arquivo JSON.
        """
        if not self.features: self.extract_morphological_features()
        output_data = {"image_path": self.image_path, "timestamp": datetime.now().isoformat(), "features": self.features}
        with open(output_path, "w", encodinf= "utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

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
        import os
        from pathlib import Path
        results = []
        image_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]
        for file_path in Path(input_dir).iterdir():
            if file_path.suffix.lower() in image_extensions:
                try:
                    print(f"Processando: {file_path.name}")
                    processor = PlantPhenotyping(str(file_path))
                    base_name = file_path.stem
                    features = processor.process_complete(output_dir, base_name)
                    results.append({"filename": file_path.name, "features": features})
                except Exception as e:
                    print(f"Erro ao processar {file_path.name}: {str(e)}")
        consolidated_path = f"{output_dir}/batch_results.json"
        with open(consolidated_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        return results