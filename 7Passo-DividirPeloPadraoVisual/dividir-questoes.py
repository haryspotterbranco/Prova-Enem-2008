from PIL import Image
import os

def encontrar_faixa_cinza_claro_2008(imagem):
    """
    Detecta as divisórias da prova de 2008 caçando a faixa cinza-clara horizontal
    que acompanha o número de cada questão na margem esquerda.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Foca a análise no início horizontal da faixa (lado esquerdo, colunas 15 a 120)
    x_inicio = 15
    x_fim = 120
    comprimento_busca = x_fim - x_inicio
    
    y = 10
    while y < altura - 10:
        pixels_cinza_claro = 0
        
        for x in range(x_inicio, x_fim):
            r, g, b = pixels[x, y][:3]
            
            # FILTRO DO CINZA CLARO: Um tom homogêneo abaixo do branco puro (255) 
            # mas acima dos textos escuros (geralmente entre 180 e 242)
            if 180 <= r <= 242 and 180 <= g <= 242 and 180 <= b <= 242 and abs(r - g) < 8 and abs(g - b) < 8:
                pixels_cinza_claro += 1
                
        # Se a linha contiver uma quantidade sólida desse cinza-claro contínuo, achamos o cabeçalho!
        if pixels_cinza_claro > (comprimento_busca * 0.65):
            
            # Aplica o recuo exato de 25 pixels acima que você pediu
            posicao_corte = y - 25
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Faixa cinza-clara de cabeçalho detectada em y={y}. Cortando em y={posicao_corte}")
            
            # Pula uma margem vertical segura para ir direto ao corpo da questão
            y += 50  
            continue
            
        y += 1
        
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida):
    """
    Gerencia a abertura e o fatiamento das questões de 2008
    """
    if not os.path.exists(caminho_imagem):
        print(f"Erro: O arquivo '{caminho_imagem}' não foi encontrado.")
        return
        
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    print(f"Imagem carregada: {largura}x{altura} pixels. Caçando as faixas cinza-claras dos números...")
    
    posicoes_corte = encontrar_faixa_cinza_claro_2008(imagem)
    
    if not posicoes_corte:
        print("\n[AVISO]: O algoritmo não encontrou a faixa cinza-clara.")
        print("Dica: Se a folha estiver muito amarelada/escura, me avise para calibrar o tom do cinza.")
        return
        
    print(f"\nSucesso! Foram encontradas {len(posicoes_corte)} marcações de cabeçalho autênticas.")
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"questao_{i+1:02d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo}")
        
        # Ajusta o avanço baseado no recuo de 25px adotado
        posicao_anterior = posicao_corte + 25 

    # Captura o último bloco da prova
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        nome_arquivo = f"questao_{len(posicoes_corte)+1:02d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo (Parte final): {caminho_completo}")

if __name__ == "__main__":
    arquivo_da_prova = "colunas_concatenadas_verticalmente.png" 
    pasta_destino = "questoes_separadas_2008"
    
    dividir_imagem_por_faixas(arquivo_da_prova, pasta_destino)
    print("\nProcesso finalizado!")