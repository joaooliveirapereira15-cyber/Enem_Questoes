from PIL import Image
import os

def encontrar_faixa_cinza(imagem, cor_alvo, tolerancia=15):
    """
    Encontra as posições exatas de corte na coluna 10,
    considerando a faixa cinza de 44px (margem 3px).
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    altura_base = 44
    margem_erro = 3
    altura_minima = altura_base - margem_erro  # 41 px
    altura_maxima = altura_base + margem_erro  # 47 px
    
    y = 0
    while y < altura - altura_minima:
        altura_faixa_atual = 0
        
        while (y + altura_faixa_atual) < altura:
            pixel = pixels[7, y + altura_faixa_atual]  
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            if (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia):
                altura_faixa_atual += 1
            else:
                break
        
        if altura_minima <= altura_faixa_atual <= altura_maxima:
            # O corte acontece exatamente 2 pixels antes da faixa começar
            posicao_corte = y - 2
            if posicao_corte < 0:
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Padrão detectado em y={y}. Ponto de corte definido em y={posicao_corte}")
            
            # Pula a faixa para continuar a busca depois dela
            y += altura_faixa_atual
        else:
            y += 1
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Fatia a imagem verticalmente nas posições encontradas sem descartar pixels.
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    posicoes_corte = encontrar_faixa_cinza(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhuma faixa cinza encontrada na imagem!")
        return
    
    print(f"Encontrados {len(posicoes_corte)} pontos de corte.")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta do ponto anterior até o ponto de corte atual
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px) -> y de {posicao_anterior} ate {posicao_corte}")
        
        # Correção crucial: a próxima parte começa exatamente onde a anterior terminou.
        # Assim, a margem de 2px + a faixa cinza farão parte do início do próximo bloco.
        posicao_anterior = posicao_corte
    
    # Corta a seção final (do último corte até o fim da imagem)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px) -> y de {posicao_anterior} ate {altura}")

if __name__ == "__main__":
    caminho_imagem = "colunas_concatenadas_verticalmente.png"
    pasta_saida = "questoes_colunas"
    
    cor_do_padrao = (211, 210, 211)
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("Divisão concluída sem perda de dados!")