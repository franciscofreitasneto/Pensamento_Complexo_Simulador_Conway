import pygame
import numpy as np
import random

# --- CONFIGURAÇÕES DO UNIVERSO ---
LARGURA_TELA, ALTURA_TELA = 1920, 1080
TAMANHO_CELULA = 4  # Quanto menor, maior e mais denso será o mundo
COLUNAS = LARGURA_TELA // TAMANHO_CELULA
LINHAS = ALTURA_TELA // TAMANHO_CELULA

# Paleta de cores (Estilo "Matrix/Terminal")
COR_FUNDO = (15, 15, 20)
COR_CELULA = (0, 255, 150)

def criar_grade_aleatoria():
    grade_aleatoria = np.random.choice(
        [0, 1], 
        size=(LINHAS, COLUNAS), 
        p=[0.9, 0.1] # Altere o 0.2 para aumentar ou diminuir a desordem inicial
    )
    return grade_aleatoria

#def criar_gosper_glider_gun():
#    """Inicializa a grade e insere a estrutura complexa da Glider Gun."""
#    grade = np.zeros((LINHAS, COLUNAS), dtype=int)
    
    # Matriz exata do padrão da Gosper Glider Gun
    #gun = np.zeros((11, 38), dtype=int)
    #gun[5][1] = gun[5][2] = 1
    #gun[6][1] = gun[6][2] = 1
    #gun[3][13] = gun[3][14] = 1
    #gun[4][12] = gun[4][16] = 1
    #gun[5][11] = gun[5][17] = 1
    #gun[6][11] = gun[6][15] = gun[6][17] = gun[6][18] = 1
    #gun[7][11] = gun[7][17] = 1
    #gun[8][12] = gun[8][16] = 1
    #gun[9][13] = gun[9][14] = 1
    #gun[1][25] = 1
    #gun[2][23] = gun[2][25] = 1
    #gun[3][21] = gun[3][22] = 1
    #gun[4][21] = gun[4][22] = 1
    #gun[5][21] = gun[5][22] = 1
    #gun[6][23] = gun[6][25] = 1
    #gun[7][25] = 1
    #gun[3][35] = gun[3][36] = 1
    #gun[4][35] = gun[4][36] = 1

    # Posicionando a "arma" no canto superior esquerdo para ter espaço de disparo
    #grade[10:21, 10:48] = gun
#    return grade

def atualizar_grade_numpy(grade):
    """
    Usa operações matriciais do NumPy para calcular a próxima geração.
    Isso substitui os laços `for` lentos por álgebra linear otimizada.
    """
    # Conta os vizinhos deslocando a matriz em todas as 8 direções
    vizinhos = sum(np.roll(np.roll(grade, i, 0), j, 1)
                   for i in (-1, 0, 1) for j in (-1, 0, 1)
                   if (i != 0 or j != 0))
    
    # Aplica as 4 regras cartesianas de Conway simultaneamente
    nova_grade = (vizinhos == 3) | (grade & (vizinhos == 2))
    return nova_grade.astype(int)

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("* Simulador Complexo - Pensamento Complexo *")
    relogio = pygame.time.Clock()

    #grade = criar_gosper_glider_gun()
    grade = criar_grade_aleatoria()
    
    rodando = True
    pausado = True

    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            # Pressione ESPAÇO para pausar e analisar a estrutura
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    temporario = False
                    pausado = not pausado
                if evento.key == pygame.K_RETURN:
                    temporario = True
                    pausado = not pausado

        tela.fill(COR_FUNDO)

        # Desenha as células vivas
        y, x = np.where(grade == 1)
        for i in range(len(x)):
            pygame.draw.rect(tela, COR_CELULA, 
                             (x[i] * TAMANHO_CELULA, y[i] * TAMANHO_CELULA, 
                              TAMANHO_CELULA - 1, TAMANHO_CELULA - 1))

        if not pausado:
            grade = atualizar_grade_numpy(grade)
            if temporario:
                pausado = not pausado

        pygame.display.flip()
        relogio.tick(10) # Ajuste o FPS para ver a evolução mais rápida ou devagar

    pygame.quit()

if __name__ == "__main__":
    main()
