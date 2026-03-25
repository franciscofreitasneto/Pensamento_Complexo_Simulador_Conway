import pygame
import numpy as np
import random

# --- CONFIGURAÇÕES DO UNIVERSO ---
LARGURA_TELA, ALTURA_TELA = 1920, 1080
TAMANHO_CELULA = 6  
COLUNAS = LARGURA_TELA // TAMANHO_CELULA
LINHAS = ALTURA_TELA // TAMANHO_CELULA

# Paleta de cores
COR_FUNDO = (15, 15, 0)
COR_PRESA = (0, 255, 150)      # Verde (Ordem)
COR_PREDADOR = (255, 10, 10)   # Vermelho (Desordem)

# =====================================================================
# --- PARÂMETROS DO ECOSSISTEMA (O SEU PAINEL DE CONTROLE) ---
# =====================================================================
QTD_PREDADORES_INICIAIS = 250   # Quantidade de predadores no frame 0
VIDA_PREDADOR = 35              # Quantas gerações um predador vive sem comer
REFEICOES_PARA_REPRODUZIR = 3   # Quantas presas precisa comer para gerar 1 filhote
MAX_PREDADORES_VIZINHOS = 4     # Conflito: Morre se tiver X ou mais predadores ao redor (3x3)
CHANCE_DECOMPOSICAO = 0.99      # Chance (0.0 a 1.0) de um morto gerar presas (40%)
QTD_PRESAS_GERADAS_MORTE = 5    # Quantas presas (1 a 8) nascem se a decomposição ocorrer
# =====================================================================

class Predador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vida = VIDA_PREDADOR
        self.refeicoes = 0
        #self.dx = random.choice([-1, 0, 1])
        #self.dy = random.choice([-1, 0, 1])



    def mover(self):
        # Movimento aleatório em qualquer uma das 8 direções
        self.dx = random.choice([-1, 0, 1])
        self.dy = random.choice([-1, 0, 1])
        self.x = (self.x + self.dx) % COLUNAS
        self.y = (self.y + self.dy) % LINHAS
        self.vida -= 1

def criar_grade_aleatoria():
    return np.random.choice([0, 1], size=(LINHAS, COLUNAS), p=[0.9, 0.1])

def inicializar_predadores(quantidade):
    predadores = []
    for _ in range(quantidade):
        x = random.randint(0, COLUNAS - 1)
        y = random.randint(0, LINHAS - 1)
        predadores.append(Predador(x, y))
    return predadores

def atualizar_grade_numpy(grade):
    # Regra de Conway para as presas
    vizinhos = sum(np.roll(np.roll(grade, i, 0), j, 1)
                   for i in (-1, 0, 1) for j in (-1, 0, 1)
                   if (i != 0 or j != 0))
    nova_grade = (vizinhos == 3) | (grade & (vizinhos == 2))
    return nova_grade.astype(int)

def decompor_predador(grade, x, y):
    """Retorno entrópico parametrizado"""
    if random.random() < CHANCE_DECOMPOSICAO:
        vazios = []
        # Vasculha os 8 vizinhos buscando espaços sem presa
        for i in [-1, 0, 1]:
            for j in [-1, 0, 1]:
                if i == 0 and j == 0: continue
                nx, ny = (x + j) % COLUNAS, (y + i) % LINHAS
                if grade[ny, nx] == 0:
                    vazios.append((nx, ny))
        
        # Se houver espaços vazios, planta as presas até o limite definido
        if vazios:
            random.shuffle(vazios)
            limite = min(QTD_PRESAS_GERADAS_MORTE, len(vazios))
            for nx, ny in vazios[:limite]:
                grade[ny, nx] = 1

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("* Simulador Eco-Organizacional Parametrizado *")
    relogio = pygame.time.Clock()

    grade_presas = criar_grade_aleatoria()
    predadores = inicializar_predadores(QTD_PREDADORES_INICIAIS) 
    
    rodando = True
    pausado = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    temporario = False
                    pausado = not pausado
                if evento.key == pygame.K_RETURN:
                    temporario = True
                    pausado = not pausado

        tela.fill(COR_FUNDO)

        # 1. Desenha Presas
        y_presas, x_presas = np.where(grade_presas == 1)
        for i in range(len(x_presas)):
            pygame.draw.rect(tela, COR_PRESA, 
                             (x_presas[i] * TAMANHO_CELULA, y_presas[i] * TAMANHO_CELULA, 
                              TAMANHO_CELULA - 1, TAMANHO_CELULA - 1))

        # 2. Desenha Predadores
        for p in predadores:
            pygame.draw.rect(tela, COR_PREDADOR, 
                             (p.x * TAMANHO_CELULA, p.y * TAMANHO_CELULA, 
                              TAMANHO_CELULA - 1, TAMANHO_CELULA - 1))

        if not pausado:
            # --- LÓGICA DO ECOSSISTEMA ---
            nova_grade_presas = atualizar_grade_numpy(grade_presas)
            
            # Move todos os predadores primeiro
            for p in predadores:
                p.mover()

            # Cria um "Mapa de Calor" rápido para calcular a superlotação de predadores
            mapa_predadores = np.zeros((LINHAS, COLUNAS), dtype=int)
            for p in predadores:
                mapa_predadores[p.y, p.x] += 1
            
            # Soma quantos predadores existem na área 3x3 de cada célula
            densidade_predadores = sum(np.roll(np.roll(mapa_predadores, i, 0), j, 1)
                                       for i in (-1, 0, 1) for j in (-1, 0, 1))

            predadores_sobreviventes = []
            predadores_mortos = []
            novos_filhotes = []

            # Avalia vida e conflito territorial
            for p in predadores:
                if p.vida <= 0:
                    predadores_mortos.append(p)
                # Verifica se há muitos predadores ao redor dele (subtrai 1 para não contar a si mesmo)
                elif (densidade_predadores[p.y, p.x] - 1) >= MAX_PREDADORES_VIZINHOS:
                    predadores_mortos.append(p) # Morre por disputa de território
                else:
                    predadores_sobreviventes.append(p)

            # Processa a caça, acúmulo de energia e reprodução
            predadores_finais = []
            for p in predadores_sobreviventes:
                if nova_grade_presas[p.y, p.x] == 1:
                    # Come a presa
                    nova_grade_presas[p.y, p.x] = 0
                    p.vida = VIDA_PREDADOR  # Reseta o relógio biológico
                    p.refeicoes += 1        # Acumula energia metabólica
                    
                    # Reprodução
                    if p.refeicoes >= REFEICOES_PARA_REPRODUZIR:
                        p.refeicoes = 0
                        dx = random.choice([-2, 0, 2])
                        dy = random.choice([-2, 0, 2])
                        if dx == 0 and dy == 0: dx = 2 
                        nx = (p.x + dx) % COLUNAS
                        ny = (p.y + dy) % LINHAS
                        novos_filhotes.append(Predador(nx, ny))
                
                predadores_finais.append(p)

            # Processa o retorno entrópico (Decomposição)
            for pm in predadores_mortos:
                decompor_predador(nova_grade_presas, pm.x, pm.y)

            # Atualiza o ciclo
            predadores = predadores_finais + novos_filhotes
            grade_presas = nova_grade_presas

            if temporario:
                pausado = not pausado

        pygame.display.flip()
        relogio.tick(500)

    pygame.quit()

if __name__ == "__main__":
    main()
