# Execução

Resultado esperado após iniciar executar o **Main.py**

> python main.py

```
    [1] Banco relacional criado com ALUNO, PROFESSOR, MATERIA, SALA.

    [2] NOS extraidos via UNION ALL x3 (um SELECT por entidade):
        aluno=8 + materia=4 + professor=3 + sala=4
    [2] ARESTAS extraidas via JOIN x4 + UNION ALL x3:
        ABRIGA=4 + LECIONA_PARA=9 + MINISTRA_EM=4 + TEM_ALUNO=8

    [3] Grafo montado em memoria -> lista de adjacencia:
        aluno_1        Joao Silva               (aluno) -> -
        aluno_2        Maria Oliveira           (aluno) -> -
        aluno_3        Pedro Santos             (aluno) -> -
        aluno_4        Ana Costa                (aluno) -> -
        aluno_5        Lucas Pereira            (aluno) -> -
        aluno_6        Camila Rocha             (aluno) -> -
        aluno_7        Rafael Almeida           (aluno) -> -
        aluno_8        Julia Martins            (aluno) -> -
        materia_1      Introducao a Computacao  (materia) -> aluno_1(TEM_ALUNO), aluno_2(TEM_ALUNO)
        materia_2      Calculo I                (materia) -> aluno_3(TEM_ALUNO), aluno_4(TEM_ALUNO)
        materia_3      Banco de Dados           (materia) -> aluno_5(TEM_ALUNO), aluno_6(TEM_ALUNO)
        materia_4      Estatistica              (materia) -> aluno_7(TEM_ALUNO), aluno_8(TEM_ALUNO)
        professor_1    Dra. Ana Souza           (professor) -> aluno_1(LECIONA_PARA), aluno_2(LECIONA_PARA), aluno_4(LECIONA_PARA), sala_1(MINISTRA_EM), sala_2(MINISTRA_EM)
        professor_2    Prof. Carlos Lima        (professor) -> aluno_3(LECIONA_PARA), aluno_5(LECIONA_PARA), aluno_7(LECIONA_PARA), sala_3(MINISTRA_EM)
        professor_3    Prof. Beatriz Rocha      (professor) -> aluno_4(LECIONA_PARA), aluno_6(LECIONA_PARA), aluno_8(LECIONA_PARA), sala_4(MINISTRA_EM)
        sala_1         S-101                    (sala) -> materia_1(ABRIGA)
        sala_2         S-102                    (sala) -> materia_2(ABRIGA)
        sala_3         S-201                    (sala) -> materia_3(ABRIGA)
        sala_4         S-202                    (sala) -> materia_4(ABRIGA)

    [4] Analises do grafo:
        - Eh DAG? SIM
        ordem topologica (exemplo): professor_1 -> professor_3 -> professor_2 -> sala_1 -> sala_2 -> sala_4
        - Top 3 nos com mais arestas de saida:
            Dra. Ana Souza           -> 5 arestas
            Prof. Beatriz Rocha      -> 4 arestas
            Prof. Carlos Lima        -> 4 arestas
        - Alcancabilidade a partir de cada professor (BFS):
            Dra. Ana Souza           alcança: Joao Silva, Maria Oliveira, Pedro Santos, Ana Costa, Introducao a Computacao, Calculo I, S-101, S-102
            Prof. Carlos Lima        alcança: Pedro Santos, Lucas Pereira, Camila Rocha, Rafael Almeida, Banco de Dados, S-201
            Prof. Beatriz Rocha      alcança: Ana Costa, Camila Rocha, Rafael Almeida, Julia Martins, Estatistica, S-202

        - Salas por professor (JOIN simples):
            Dra. Ana Souza           2 sala(s)
            Prof. Carlos Lima        1 sala(s)
            Prof. Beatriz Rocha      1 sala(s)

    [5] Grafo exportado: /home/gabriel/Coding/Estudos/Python/DAG_data_model/output/grafo.dot
        Renderize com:  dot -Tpng output/grafo.dot -o output/grafo.png
```
