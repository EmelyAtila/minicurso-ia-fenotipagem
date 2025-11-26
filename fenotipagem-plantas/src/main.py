#!/usr/bin/env python3
"""
Aplicação Principal de Fenotipagem de Plantas
Interface de linha de comando para processamento de imagens e geração de relatórios
"""

import argparse
import os
import sys
import json
from pathlib import Path

# Adicionar diretório src ao path para que as importações funcionem
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Importa as classes e funções dos outros módulos
from image_processor import PlantPhenotyping, batch_process
from report_agent import ReportAgent


def process_single_image(args):
    """
    Processa um único imagem e, opcionalmente, gera o relatório.
    """
    
    print(f"Processando imagem: {args.input}")
    
    # 1. Validação e Preparação
    if not os.path.exists(args.input):
        print(f"❌ Erro: Arquivo não encontrado: {args.input}")
        return
    
    # Cria o diretório de saída se não existir
    os.makedirs(args.output, exist_ok=True)
    
    base_name = Path(args.input).stem
    json_path = f"{args.output}/{base_name}_features.json"
    
    try:
        # 2. Lógica de Pular Processamento (se o JSON já existe)
        if os.path.exists(json_path):
            print(f"Arquivo de dados {json_path} encontrado. Pulando processamento de imagem.")
            
            # Carrega os dados existentes para usar no relatório
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            features = data['features'] # Pega apenas o dicionário de features
            
        else:
            # 2. Processamento (Usa a classe PlantPhenotyping)
            processor = PlantPhenotyping(args.input)
            features = processor.process_complete(args.output, base_name)
            
            print(f"✅ Processamento concluído! Dados salvos em: {args.output}")

        # 3. Geração de Relatório (Opcional)
        if args.report:
            print(f"📝 Gerando relatório com análise inteligente...")
            report_path = f"{args.output}/{base_name}_relatorio.md"
            
            # Cria uma instância do Agente de Relatórios
            agent = ReportAgent() 
            
            # Chama o método de análise, passando os features diretamente
            # O método generate_markdown_report no ReportAgent agora espera o dicionário 'data'
            # Aqui, estamos passando apenas os features, então precisamos adaptar a chamada
            
            # Como o ReportAgent espera o JSON completo, vamos usar o método generate_full_report
            # que carrega o JSON e gera o relatório.
            agent.generate_full_report(json_path=json_path, output_path=report_path)
            
            print(f"✅ Relatório gerado: {report_path}")
            
    except Exception as e:
        print(f"❌ Erro durante processamento: {e}")


def process_batch(args):
    """
    Processa múltiplas imagens em um diretório.
    """
    print(f"Processando lote no diretório: {args.input}")
    
    if not os.path.isdir(args.input):
        print(f"❌ Erro: Diretório não encontrado: {args.input}")
        return
    
    os.makedirs(args.output, exist_ok=True)
    
    try:
        # Chama a função de processamento em lote do image_processor
        results = batch_process(args.input, args.output)
        
        print(f"✅ Processamento de lote concluído! {len(results)} arquivos processados.")
        
        # 3. Geração de Relatório de Lote (Opcional)
        if args.report:
            print(f"📝 Gerando relatório de análise de lote...")
            
            # O ReportAgent precisa de um método para analisar o lote
            # Como não implementamos o método de lote, vamos apenas confirmar a conclusão
            print("⚠️ Geração de relatório de lote não implementada. Dados consolidados em batch_results.json.")
            
    except Exception as e:
        print(f"❌ Erro durante processamento de lote: {e}")


def main():
    """
    Função principal que configura o parser de argumentos.
    """
    parser = argparse.ArgumentParser(description="Aplicação de Fenotipagem de Plantas CLI")
    subparsers = parser.add_subparsers(title="Comandos", dest="command")

    # Comando 'single'
    parser_single = subparsers.add_parser("single", help="Processa uma única imagem.")
    parser_single.add_argument("-i", "--input", required=True, help="Caminho para o arquivo de imagem.")
    parser_single.add_argument("-o", "--output", default="data/output", help="Diretório de saída.")
    parser_single.add_argument("--report", action="store_true", help="Gera relatório de análise da IA.")
    parser_single.set_defaults(func=process_single_image)

    # Comando 'batch'
    parser_batch = subparsers.add_parser("batch", help="Processa um diretório de imagens.")
    parser_batch.add_argument("-i", "--input", required=True, help="Caminho para o diretório de entrada.")
    parser_batch.add_argument("-o", "--output", default="data/output/batch", help="Diretório de saída.")
    parser_batch.add_argument("--report", action="store_true", help="Gera relatório de análise de lote (Ainda não implementado).")
    parser_batch.set_defaults(func=process_batch)

    args = parser.parse_args()

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
