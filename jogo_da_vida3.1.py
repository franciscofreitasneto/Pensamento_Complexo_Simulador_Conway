import pygame
import numpy as np
import random

# --- CONFIGURAÇÕES DO UNIVERSO ---
LARGURA_TELA, ALTURA_TELA = 1920, 1080
TAMANHO_CELULA = 6  # Aumentado levemente para melhor visualização dos predadores
COLUNAS = LARGURA_TELA // TAMANHO_CELULA
LINHAS = ALTURA_TELA // TAMANHO_CELULA

# Paleta de cores
COR_FUNDO = (15, 15, 0)
COR_PRESA = (0, 255, 150)      # Verde (A "Ordem" de Conway)
COR_PREDADOR = (255, 10, 10)   # Vermelho (A "Entropia/Desordem")

class Predador:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vida = 3 # Sobrevive por 10 gerações sem comer

    def mover(self):
        # Movimento aleatório em qualquer uma das 8 direções
        dx = random.choice([-1, 0, 1])
        dy = random.choice([-1, 0, 1])
        # A topologia do Torus (universo cíclico) é mantida
        self.x = (self.x + dx) % COLUNAS
        self.y = (self.y + dy) % LINHAS
        self.vida -= 1

def criar_grade_aleatoria():
    # Cria a grade inicial de presas
    grade_aleatoria = np.random.choice([0, 1], size=(LINHAS, COLUNAS), p=[0.9, 0.1])
    return grade_aleatoria

def inicializar_predadores(quantidade):
    predadores = []
    for _ in range(quantidade):
        x = random.randint(0, COLUNAS - 1)
        y = random.randint(0, LINHAS - 1)
        predadores.append(Predador(x, y))
    return predadores

def atualizar_grade_numpy(grade):
    # Processamento rápido das presas usando a regra de Conway
    vizinhos = sum(np.roll(np.roll(grade, i, 0), j, 1)
                   for i in (-1, 0, 1) for j in (-1, 0, 1)
                   if (i != 0 or j != 0))
    nova_grade = (vizinhos == 3) | (grade & (vizinhos == 2))
    return nova_grade.astype(int)

def decompor_predador(grade, x, y):
    """Quando o predador morre, 3 presas nascem na sua vizinhança."""
    vazios = []
    # Vasculha os vizinhos procurando espaços onde não há presas
    for i in [-1, 0, 1]:
        for j in [-1, 0, 1]:
            if i == 0 and j == 0: continue
            nx, ny = (x + j) % COLUNAS, (y + i) % LINHAS
            if grade[ny, nx] == 0:
                vazios.append((nx, ny))
    
    # Escolhe aleatoriamente até 3 espaços vazios para nascerem as presas
    random.shuffle(vazios)
    for nx, ny in vazios[:2]:
        grade[ny, nx] = 1

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("* Simulador Eco-Organizacional - Presa e Predador *")
    relogio = pygame.time.Clock()

    grade_presas = criar_grade_aleatoria()
    # Começamos com 50 predadores (ajuste conforme a densidade desejada)
    predadores = inicializar_predadores(500) 
    
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

        # 1. Desenha as Presas (Verdes)
        y_presas, x_presas = np.where(grade_presas == 1)
        for i in range(len(x_presas)):
            pygame.draw.rect(tela, COR_PRESA, 
                             (x_presas[i] * TAMANHO_CELULA, y_presas[i] * TAMANHO_CELULA, 
                              TAMANHO_CELULA - 1, TAMANHO_CELULA - 1))

        # 2. Desenha os Predadores (Vermelhos)
        for p in predadores:
            pygame.draw.rect(tela, COR_PREDADOR, 
                             (p.x * TAMANHO_CELULA, p.y * TAMANHO_CELULA, 
                              TAMANHO_CELULA - 1, TAMANHO_CELULA - 1))

        if not pausado:
            # --- LÓGICA DO ECOSSISTEMA ---
            
            # Atualiza as presas (Conway Clássico)
            nova_grade_presas = atualizar_grade_numpy(grade_presas)
            
            predadores_sobreviventes = []
            predadores_mortos = []
            posicoes_ocupadas = {}
            novos_filhotes = []

            # Processa o movimento e os conflitos territoriais
            for p in predadores:
                p.mover()
                if p.vida <= 0:
                    predadores_mortos.append(p)
                else:
                    # Verifica conflito de território
                    if (p.x, p.y) in posicoes_ocupadas:
                        predadores_mortos.append(p) # Um deles morre no embate
                    else:
                        posicoes_ocupadas[(p.x, p.y)] = p
                        predadores_sobreviventes.append(p)

            # Processa a caça e a reprodução
            predadores_finais = []
            for p in predadores_sobreviventes:
                if nova_grade_presas[p.y, p.x] == 1:
                    # Predador come a presa
                    nova_grade_presas[p.y, p.x] = 0
                    p.vida = 10 # Recupera as energias
                    
                    # Reprodução a 2 pixels de distância
                    dx = random.choice([-2, 0, 2])
                    dy = random.choice([-2, 0, 2])
                    if dx == 0 and dy == 0: dx = 2 # Garante que não nasça no mesmo lugar
                    
                    nx = (p.x + dx) % COLUNAS
                    ny = (p.y + dy) % LINHAS
                    novos_filhotes.append(Predador(nx, ny))
                
                predadores_finais.append(p)

            # Processa o retorno entrópico (A morte gera vida na vizinhança)
            for pm in predadores_mortos:
                decompor_predador(nova_grade_presas, pm.x, pm.y)

            # Atualiza as listas globais para o próximo ciclo
            predadores = predadores_finais + novos_filhotes
            grade_presas = nova_grade_presas

            if temporario:
                pausado = not pausado

        pygame.display.flip()
        relogio.tick(15)

    pygame.quit()

if __name__ == "__main__":
    main()
