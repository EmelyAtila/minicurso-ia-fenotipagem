"""
Agente Inteligente para Análise de Dados de Fenotipagem e Geração de
Relatórios
"""

import json
import os
from typing import Dict, List
from datetime import datetime
from openai import OpenAI  # Biblioteca pra interagir com a API da OpenAI

class ReportAgent:
    """
    Agente inteligente que analisa dados de fenotipagem e gera relatórios completos
    """
    
    def __init__(self, model: str = "gpt-4.1-mini"):
        """
        Construtor da classe. Inicializa o cliente da API da OpenAI.
        """
        # O cliente da OpenAI lê automaticamente a variável de ambiente OPENAI_API_KEY
        self.client = OpenAI()
        self.model = model  # Define o modelo a ser usado (ex: gpt-4.1-mini)

    def analyze_single_plant(self, features: Dict) -> str:
        """
        Analisa características de uma única planta usando o LLM.
        """
        prompt = f"""Você é um especialista em fenotipagem de plantas e análise de imagens. Analise os seguintes dados morfológicos e de cor extraídos de uma imagem de planta:

{json.dumps(features, indent=2, ensure_ascii=False)}

Forneça uma análise detalhada e profissional que inclua:
1. Características Morfológicas: Interprete área foliar, perímetro, dimensões.
2. Análise de Forma: Baseado na solidez e compacidade, descreva a forma geral.
3. Análise de Cor e Saúde: Interprete os índices de vegetação (ExG, VARI).
4. Conclusões e Recomendações: Forneça uma avaliação geral e sugestões.

Seja técnico mas acessível, usando terminologia científica apropriada."""

        # Faz a chamada à API da OpenAI
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "Você é um especialista em fenotipagem de plantas, análise de imagens e agronomia."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,  # Controla a criatividade da resposta (0.0 é mais determinístico)
            max_tokens=1500
        )

        # Compatibilidade com diferentes formatos de resposta
        try:
            analysis = response.choices[0].message.content
        except Exception:
            # fallback para estruturas de dicionário
            analysis = response.choices[0]["message"]["content"]

        return analysis

    def generate_markdown_report(self, data: Dict, output_path: str) -> str:
        """
        Gera relatório completo em formato Markdown.
        """
        report_lines = []

        # 1. Cabeçalho do Relatório
        report_lines.append("# Relatório de Fenotipagem de Plantas\n\n")
        report_lines.append(f"**Data**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n\n")

        if "features" in data:
            # 2. Chama a função de análise da IA
            analysis = self.analyze_single_plant(data["features"])
            report_lines.append("## 1. Análise da Planta\n\n")
            report_lines.append(analysis + "\n\n")

            # 3. Adiciona a Tabela de Dados Extraídos
            report_lines.append("## 2. Dados Extraídos\n\n")
            report_lines.append("| Característica | Valor |\n|---|---|\n")
            for key, value in data["features"].items():
                val_str = f"{value:.4f}" if isinstance(value, float) else str(value)
                report_lines.append(f"| {key.replace('_', ' ').title()} | {val_str} |\n")

        # 4. Salva o conteúdo no arquivo
        report_content = "".join(report_lines)
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        return output_path

    def generate_full_report(self, json_path: str, output_path: str) -> str:
        data = self.load_phenotyping_data(json_path)
        return self.generate_markdown_report(data, output_path)