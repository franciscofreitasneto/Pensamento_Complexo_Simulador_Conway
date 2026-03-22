# Pensamento Complexo - Morin
# Comportamento Emergente Sistêmico 
# Princípio da Recursividade
# Princípio do Autoeco-organização
# Francisco Alves de Freitas Neto (16/03/25)
import time
import os
import random

def criar_grade_aleatoria(linhas, colunas):
    # Inicia a grade com 20% de células vivas (sopa primordial aleatória)
    return [[random.choices([0, 1], weights=[0.9, 0.1])[0] for _ in range(colunas)] for _ in range(linhas)]

def imprimir_grade(grade, geracao, colunas):
    os.system('clear')
    print(f"--- Geração: {geracao} | Disciplina de Pensamento Complexo - Comportamento Emergente Sistêmico- Morin ---\n--- Simulador de John Conway ---")
    print("--" * colunas)
    for linha in grade:
        # Usando blocos mais visíveis
        linha_str = "".join(["██" if celula == 1 else "  " for celula in linha])
        print(linha_str)
    print("--" * colunas)

def proxima_geracao(grade):
    linhas = len(grade)
    colunas = len(grade[0])
    nova_grade = [[0 for _ in range(colunas)] for _ in range(linhas)]

    for i in range(linhas):
        for j in range(colunas):
            vizinhos_vivos = 0
            # Conta os vizinhos assumindo bordas contínuas (o tabuleiro se conecta nas pontas)
            for x in [-1, 0, 1]:
                for y in [-1, 0, 1]:
                    if x == 0 and y == 0: continue
                    vizinhos_vivos += grade[(i + x) % linhas][(j + y) % colunas]

            # A Matemática Sintática (Regras locais de Conway)
            if grade[i][j] == 1 and vizinhos_vivos in [2, 3]:
                nova_grade[i][j] = 1
            elif grade[i][j] == 0 and vizinhos_vivos == 3:
                nova_grade[i][j] = 1

    return nova_grade

# Aumentamos o tabuleiro para ver a complexidade emergir
linhas, colunas = 55, 105
grade = criar_grade_aleatoria(linhas, colunas)

geracao = 1
try:
    while True:
        imprimir_grade(grade, geracao, colunas)
        grade = proxima_geracao(grade)
        geracao += 1
        time.sleep(0.20) # Mais rápido para ver a evolução
except KeyboardInterrupt:
    print("\nSimulação interrompida pelo Sujeito Metaenunciativo (Você!).")
