import time
import os

def criar_grade(linhas, colunas):
    return [[0 for _ in range(colunas)] for _ in range(linhas)]

def imprimir_grade(grade, geracao):
    # Limpa a tela do terminal para criar o efeito de animação
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"--- Geração: {geracao} ---")
    for linha in grade:
        linha_str = "".join(["██" if celula == 1 else "  " for celula in linha])
        print(linha_str)
    print("-" * 30)

def proxima_geracao(grade):
    linhas = len(grade)
    colunas = len(grade[0])
    nova_grade = criar_grade(linhas, colunas)

    for i in range(linhas):
        for j in range(colunas):
            # Contando os vizinhos (com bordas infinitas/toroidais)
            vizinhos_vivos = 0
            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    if x == 0 and y == 0: continue
                    vizinhos_vivos += grade[(i + x) % linhas][(j + y) % colunas]

            # A Lógica Cartesiana Estrita (Axiomas do sistema)
            if grade[i][j] == 1:
                if vizinhos_vivos in [2, 3]:
                    nova_grade[i][j] = 1 # Sobrevive
                else:
                    nova_grade[i][j] = 0 # Morre por falta ou excesso
            else:
                if vizinhos_vivos == 3:
                    nova_grade[i][j] = 1 # Nasce por recursividade do meio

    return nova_grade

# Configurando o ambiente
linhas, colunas = 15, 15
grade = criar_grade(linhas, colunas)

# Inserindo um "Glider" (Planador) - Um padrão que se move sozinho
padrao_glider = [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)]
for i, j in padrao_glider:
    grade[i][j] = 1

# Rodando o universo
geracao = 1
try:
    while True:
        imprimir_grade(grade, geracao)
        grade = proxima_geracao(grade)
        geracao += 1
        time.sleep(0.3)
except KeyboardInterrupt:
    print("\nSimulação interrompida.")
