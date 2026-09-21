"""
Construcao do grafo feito 100% em SQL.

A ideia central do desafio: transformar os dados RELACIONAIS (4 tabelas)
em uma estrutura de GRAFO (nos + arestas).

    NOS    : cada registro de ALUNO, PROFESSOR, MATERIA e SALA vira um
             no identificado por "<tipo>_<id>".

    ARESTAS: cada relacionamento entre entidades vira uma aresta
             (origem -> destino), rotulada pelo tipo de relacao.

Requisitos obrigatorios atendidos aqui:

    * >= 2 UNION ALL ... como metodos de construcao dos NOS
        -> NOS_SQL combina as 4 entidades com 3 UNION ALL.
    * >= 1 JOIN ....... para montar as ARESTAS
        -> cada aresta nasce de um JOIN entre as tabelas relacionadas.
        -> ARESTAS_SQL usa 3 UNION ALL + 4 JOINs.

Orientacao das arestas escolhida para manter o grafo como um DAG
(sem ciclos), seguindo o fluxo PROFESSOR -> SALA -> MATERIA -> ALUNO:

    PROFESSOR -> SALA   (PROFESSOR 1:N SALAS)          via SALA.professor_id
    SALA      -> MATERIA (SALA 1:1 MATERIAS)            via MATERIA.sala_id
    MATERIA   -> ALUNO  (MATERIA 1:N ALUNOS)            via ALUNO.materia_id
    PROFESSOR -> ALUNO  (ALUNO N:N PROFESSOR)           via ALUNO_PROFESSOR
"""

# ---------------------------------------------------------------------------
# NOS: uma UNION ALL por entidade = 3 operacoes UNION ALL
# Cada SELECT precisa ter as MESMAS colunas (mesma "forma" do registro).
# ---------------------------------------------------------------------------

NOS_SQL = """
WITH nos AS (
    SELECT 'aluno'     AS tipo, 'aluno_'     || CAST(a.id AS TEXT) AS chave,
           a.nome      AS rotulo, 'skyblue'  AS cor
    FROM ALUNO a

    UNION ALL

    SELECT 'professor' AS tipo, 'professor_' || CAST(p.id AS TEXT) AS chave,
           p.nome      AS rotulo, 'lightgreen' AS cor
    FROM PROFESSOR p

    UNION ALL

    SELECT 'materia'   AS tipo, 'materia_'   || CAST(m.id AS TEXT) AS chave,
           m.nome      AS rotulo, 'orange'   AS cor
    FROM MATERIA m

    UNION ALL

    SELECT 'sala'      AS tipo, 'sala_'      || CAST(s.id AS TEXT) AS chave,
           s.numero    AS rotulo, 'plum'     AS cor
    FROM SALA s
)
SELECT chave, tipo, rotulo, cor
FROM nos
ORDER BY tipo, rotulo;
"""

# ---------------------------------------------------------------------------
# ARESTAS: cada relacionamento vira uma aresta dirigida.
# 4 JOINs (um por relacao) + 3 UNION ALL combinando os resultados.
# ---------------------------------------------------------------------------

ARESTAS_SQL = """
WITH arestas AS (
    -- PROFESSOR -> SALA   | PROFESSOR 1:N SALAS
    SELECT 'professor_' || p.id AS origem,
           'sala_'      || s.id AS destino,
           'MINISTRA_EM'  AS relacao,
           'Professor leciona na sala' AS descricao
    FROM SALA s
    JOIN PROFESSOR p ON s.professor_id = p.id

    UNION ALL

    -- SALA -> MATERIA | SALA 1:1 MATERIAS
    SELECT 'sala_'      || s.id AS origem,
           'materia_'   || m.id AS destino,
           'ABRIGA'        AS relacao,
           'Sala abriga a materia' AS descricao
    FROM MATERIA m
    JOIN SALA s ON m.sala_id = s.id

    UNION ALL

    -- MATERIA -> ALUNO | MATERIA 1:N ALUNOS
    SELECT 'materia_'   || m.id AS origem,
           'aluno_'     || a.id AS destino,
           'TEM_ALUNO'     AS relacao,
           'Materia possui o aluno' AS descricao
    FROM ALUNO a
    JOIN MATERIA m ON a.materia_id = m.id

    UNION ALL

    -- PROFESSOR -> ALUNO | ALUNO N:N PROFESSOR (tabela associativa)
    SELECT 'professor_' || p.id AS origem,
           'aluno_'     || a.id AS destino,
           'LECIONA_PARA'  AS relacao,
           'Professor leciona para o aluno' AS descricao
    FROM ALUNO_PROFESSOR ap
    JOIN PROFESSOR p ON ap.professor_id = p.id
    JOIN ALUNO a      ON ap.aluno_id    = a.id
)
SELECT origem, destino, relacao, descricao
FROM arestas
ORDER BY relacao, origem, destino;
"""

# ---------------------------------------------------------------------------
# Queries analiticas sobre o grafo (demonstram o uso de JOIN + UNION ALL
# para responder perguntas de negocio).
# ---------------------------------------------------------------------------

# Quantos nos existem de cada tipo (cardinalidade de cada entidade)?
ANALISE_NOS_POR_TIPO_SQL = """
WITH nos AS (
    SELECT 'aluno'     AS tipo, a.id AS no_id FROM ALUNO a
    UNION ALL
    SELECT 'professor' AS tipo, p.id AS no_id FROM PROFESSOR p
    UNION ALL
    SELECT 'materia'   AS tipo, m.id AS no_id FROM MATERIA m
    UNION ALL
    SELECT 'sala'      AS tipo, s.id AS no_id FROM SALA s
)
SELECT tipo, COUNT(*) AS total
FROM nos
GROUP BY tipo;
"""

# Quantas arestas existem de cada tipo de relacao?
ANALISE_ARESTAS_POR_RELACAO_SQL = """
WITH arestas AS (
    SELECT 'MINISTRA_EM' AS relacao
    FROM SALA s JOIN PROFESSOR p ON s.professor_id = p.id
    UNION ALL
    SELECT 'ABRIGA'
    FROM MATERIA m JOIN SALA s ON m.sala_id = s.id
    UNION ALL
    SELECT 'TEM_ALUNO'
    FROM ALUNO a JOIN MATERIA m ON a.materia_id = m.id
    UNION ALL
    SELECT 'LECIONA_PARA'
    FROM ALUNO_PROFESSOR ap
    JOIN PROFESSOR p ON ap.professor_id = p.id
    JOIN ALUNO a      ON ap.aluno_id    = a.id
)
SELECT relacao, COUNT(*) AS total
FROM arestas
GROUP BY relacao;
"""

# Numero de salas por professor (JOIN simples -> contagem).
SALAS_POR_PROFESSOR_SQL = """
SELECT p.nome AS professor, COUNT(s.id) AS salas
FROM PROFESSOR p
LEFT JOIN SALA s ON s.professor_id = p.id
GROUP BY p.id, p.nome
ORDER BY salas DESC;
"""