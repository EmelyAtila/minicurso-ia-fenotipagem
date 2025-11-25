"""
Aplicação Principal de Fenotipagem de Plantas
Interface de linha de comando para processamento de imagens e geração de relatórios
"""

import argparse #Módulo para criar interfaces de linha de comando
import os
import sys
from pathlib import Path

# Adicionar diretório src ao path para que as importações funcionem

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

#Importa as classes e funções dos outros módulos
from image_processor import PlantPhenotyping, bath_process
from report_agent import ReportAgent

def process_single_image(args):
    """
    Processa uma única imagem e, opcionalmente, gera o relatório.
    """
    #1 Validação e Peparação 

    print(f"Processando imagem: {args.input}")

    if not os.path.exists(args.input):
        print(f"❌ Erro: Arquivo não encontrado: {args.input}")
        return
    os.makedirs(args.output, exist_ok=True) # Cria o diretório de saída se não existir

    try:
        # 2.Processamento (Usa a classe PlantPhenotyping)
        processor = PlantPhenotyping(args.input)
        base_name = Path(args.input).stem  # Pega o nome do arquivo sem a extensão
        features = processor.process_complete(args.output, base_name)

        print(f"✅ Processamento concluído! Dados salvos em: {args.output}")

        # 3. Geração de Relatório (Se a flag --report foi passada)
        if args.report:
            print(f"📝 Gerando relatório com análise inteligente...")
            json_path = f"{args.output}/{base_name}_features.json"
            report_path = f"{args.output}/{base_name}_relatorio.md"
            
            agent = ReportAgent() # Cria uma instância do Agente de Relatórios
            agent.generate_full_report(json_path=json_path, output_path=report_path)
            
            print(f"✅ Relatório gerado: {report_path}")
            
    except Exception as e:
        print(f"❌ Erro durante processamento: {str(e)}")

def process_batch(args):
    """
    Processa múltiplas imagens em lote.
    """
    # 1. Validação e Preparação
    if not os.path.exists(args.input):
        print(f"❌ Erro: Diretório não encontrado: {args.input}")
        return
    os.makedirs(args.output, exist_ok=True)
    
    try:
        # 2. Processamento (Usa a função estática batch_process)
        results = batch_process(args.input, args.output)
        
        print(f"\n✅ Processamento em lote concluído!")
        print(f"   - Total de imagens processadas: {len(results)}")
        
        # 3. Geração de Relatório Comparativo (Se a flag --report foi passada)
        if args.report:
            print(f"\n📝 Gerando relatório comparativo com análise inteligente...")
            batch_json_path = f"{args.output}/batch_results.json"
            report_path = f"{args.output}/relatorio_comparativo.md"
            
            agent = ReportAgent()
            # O agente é inteligente o suficiente para saber que batch_results.json é um lote
            agent.generate_full_report(batch_json_path=batch_json_path, output_path=report_path)
            
            print(f"✅ Relatório comparativo gerado: {report_path}")
            
    except Exception as e:
        print(f"❌ Erro durante processamento em lote: {str(e)}")

def main():
    """
    Função principal da aplicação: configura o CLI e executa o comando.
    """
    # 1. Configura o ArgumentParser
    parser = argparse.ArgumentParser(
        description='Sistema de Fenotipagem de Plantas com Visão Computacional e IA'
    )
    
    # 2. Cria os Subcomandos (single, batch, report)
    subparsers = parser.add_subparsers(dest='command', help='Comando a executar')
    
    # Subcomando: single
    parser_single = subparsers.add_parser('single', help='Processar uma única imagem')
    parser_single.add_argument('-i', '--input', required=True, help='Caminho para a imagem de entrada')
    parser_single.add_argument('-o', '--output', required=True, help='Diretório para salvar resultados')
    parser_single.add_argument('--report', action='store_true', help='Gerar relatório com análise inteligente')
    parser_single.set_defaults(func=process_single_image) # Define qual função chamar
    
    # Subcomando: batch
    parser_batch = subparsers.add_parser('batch', help='Processar múltiplas imagens em lote')
    parser_batch.add_argument('-i', '--input', required=True, help='Diretório com imagens de entrada')
    parser_batch.add_argument('-o', '--output', required=True, help='Diretório para salvar resultados')
    parser_batch.add_argument('--report', action='store_true', help='Gerar relatório comparativo')
    parser_batch.set_defaults(func=process_batch) # Define qual função chamar
    
    # ... (O comando 'report' também seria configurado aqui)
    
    # 3. Parse e Execução
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args) # Chama a função associada ao subcomando
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
