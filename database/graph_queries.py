"""
Construcao do grafo em SQL, modelado de forma MODULAR.

A ideia: em vez de um unico bloco SQL gigante, cada SELECT de nos e de
aresta e definido como um FRAGMENTO isolado, com responsabilidade unica
e nome proprio (ex.: "nos_de_aluno", "aresta_ministra_em").

Vantagens:

    * Execucao isolada -> se um fragmento falhar, sabemos exatamente qual
      e onde (o main.py valida cada um individualmente).
    * Composicao simples -> os fragmentos sao unidos com UNION ALL,
      satisfazendo o requisito de ">= 2 UNION ALL como metodos do no".
    * Reuso -> as consultas analiticas (contagem de nos/arestas) consomem
      os proprios fragmentos, sem duplicar SQL.

Fluxo de dados (relacional -> grafo):

    NOS    : ALUNO, PROFESSOR, MATERIA e SALA viram nos "<tipo>_<id>".
    ARESTAS: cada relacionamento vira uma aresta (origem -> destino), com
             uma UNION ALL por tipo de relacao + JOINs.

Orientacao das arestas (mantem o grafo como DAG):

    PROFESSOR -> SALA    (PROFESSOR 1:N SALAS)       via SALA.professor_id
    SALA      -> MATERIA  (SALA 1:1 MATERIAS)         via MATERIA.sala_id
    MATERIA   -> ALUNO   (MATERIA 1:N ALUNOS)         via ALUNO.materia_id
    PROFESSOR -> ALUNO   (ALUNO N:N PROFESSOR)        via ALUNO_PROFESSOR
"""

# ===========================================================================
# FRAGMENTO 1 - NOS
# Cada fragmento e um SELECT completo que produz nos de UMA entidade.
# Colunas sempre na mesma ordem: (chave, tipo, rotulo, cor).
# ===========================================================================

NOS_ALUNO_SQL = """
SELECT 'aluno_'  || CAST(a.id AS TEXT) AS chave,
       'aluno'                   AS tipo,
       a.nome                    AS rotulo,
       'skyblue'                 AS cor
FROM ALUNO a
"""

NOS_PROFESSOR_SQL = """
SELECT 'professor_' || CAST(p.id AS TEXT) AS chave,
       'professor'              AS tipo,
       p.nome                   AS rotulo,
       'lightgreen'             AS cor
FROM PROFESSOR p
"""

NOS_MATERIA_SQL = """
SELECT 'materia_'  || CAST(m.id AS TEXT) AS chave,
       'materia'                AS tipo,
       m.nome                   AS rotulo,
       'orange'                 AS cor
FROM MATERIA m
"""

NOS_SALA_SQL = """
SELECT 'sala_' || CAST(s.id AS TEXT)       AS chave,
       'sala'                   AS tipo,
       s.numero                 AS rotulo,
       'plum'                   AS cor
FROM SALA s
"""

# Lista nomeada de fragmentos (nome, sql) - usada na composicao e na validacao.
NOS_FRAGMENTOS = [
    ("nos_de_aluno", NOS_ALUNO_SQL),
    ("nos_de_professor", NOS_PROFESSOR_SQL),
    ("nos_de_materia", NOS_MATERIA_SQL),
    ("nos_de_sala", NOS_SALA_SQL),
]

# ===========================================================================
# FRAGMENTO 2 - ARESTAS
# Cada fragmento transforma UMA relacao em uma aresta dirigida.
# Colunas sempre na mesma ordem: (origem, destino, relacao, descricao).
# ===========================================================================

ARESTA_PROFESSOR_SALA_SQL = """
SELECT 'professor_' || p.id             AS origem,
       'sala_'      || s.id             AS destino,
       'MINISTRA_EM'                    AS relacao,
       'Professor leciona na sala'      AS descricao
FROM SALA s
JOIN PROFESSOR p ON s.professor_id = p.id
"""

ARESTA_SALA_MATERIA_SQL = """
SELECT 'sala_'      || s.id             AS origem,
       'materia_'   || m.id             AS destino,
       'ABRIGA'                         AS relacao,
       'Sala abriga a materia'          AS descricao
FROM MATERIA m
JOIN SALA s ON m.sala_id = s.id
"""

ARESTA_MATERIA_ALUNO_SQL = """
SELECT 'materia_'   || m.id             AS origem,
       'aluno_'     || a.id             AS destino,
       'TEM_ALUNO'                      AS relacao,
       'Materia possui o aluno'         AS descricao
FROM ALUNO a
JOIN MATERIA m ON a.materia_id = m.id
"""

ARESTA_PROFESSOR_ALUNO_SQL = """
SELECT 'professor_' || p.id             AS origem,
       'aluno_'     || a.id             AS destino,
       'LECIONA_PARA'                   AS relacao,
       'Professor leciona para o aluno' AS descricao
FROM ALUNO_PROFESSOR ap
JOIN PROFESSOR p ON ap.professor_id = p.id
JOIN ALUNO a      ON ap.aluno_id    = a.id
"""

ARESTAS_FRAGMENTOS = [
    ("aresta_ministra_em", ARESTA_PROFESSOR_SALA_SQL),
    ("aresta_abriga", ARESTA_SALA_MATERIA_SQL),
    ("aresta_tem_aluno", ARESTA_MATERIA_ALUNO_SQL),
    ("aresta_leciona_para", ARESTA_PROFESSOR_ALUNO_SQL),
]

# ===========================================================================
# COMPOSICAO
# Funcao unica de juncao: fragmentos independentes virando uma unica
# consulta via UNION ALL - o requisito obrigatorio do desafio.
# ===========================================================================

UNION_ALL = "\n\n    UNION ALL\n\n"


def combinar(fragmentos: list[tuple[str, str]]) -> str:
    """Une os SQL de cada fragmento com UNION ALL (core, sem ORDER BY)."""
    return UNION_ALL.join(frag.replace(";", "").strip() for _, frag in fragmentos)


# Consultas prontas para o grafo (core + ordenacao final para leitura).
NOS_SQL = combinar(NOS_FRAGMENTOS) + "\nORDER BY tipo, rotulo;\n"
ARESTAS_SQL = combinar(ARESTAS_FRAGMENTOS) + "\nORDER BY relacao, origem, destino;\n"


# ===========================================================================
# CONSULTAS ANALITICAS (responsabilidade unica, cada uma responde 1 pergunta)
# Reutilizam os fragmentos acima por composicao - sem duplicar SQL.
# ===========================================================================

# Pergunta 1: quantos nos existem por tipo de entidade?
CONTAGEM_NOS_POR_TIPO_SQL = f"""
SELECT tipo, COUNT(*) AS total
FROM ( {combinar(NOS_FRAGMENTOS)} )
GROUP BY tipo
ORDER BY total DESC;
"""

# Pergunta 2: quantas arestas existem por tipo de relacao?
CONTAGEM_ARESTAS_POR_RELACAO_SQL = f"""
SELECT relacao, COUNT(*) AS total
FROM ( {combinar(ARESTAS_FRAGMENTOS)} )
GROUP BY relacao
ORDER BY total DESC;
"""

# Pergunta 3: quantas salas cada professor ocupa? (JOIN simples de contagem)
SALAS_POR_PROFESSOR_SQL = """
SELECT p.nome AS professor, COUNT(s.id) AS salas
FROM PROFESSOR p
LEFT JOIN SALA s ON s.professor_id = p.id
GROUP BY p.id, p.nome
ORDER BY salas DESC;
"""
