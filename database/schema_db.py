"""
Modelo relacional da Faculdade (banco SQLite).

Entidades obrigatorias do desafio: ALUNO, PROFESSOR, MATERIA e SALA.

Cardinalidades definidas na proposta:

    ALUNO      N:N PROFESSOR   -> tabela associativa ALUNO_PROFESSOR
    MATERIA    1:N ALUNOS      -> ALUNO.materia_id referencia MATERIA.id
    SALA       1:1 MATERIAS    -> MATERIA.sala_id referencia SALA.id (UNIQUE)
    PROFESSOR  1:N SALAS       -> SALA.professor_id referencia PROFESSOR.id

A ordem de criacao das tabelas segue a ordem das dependencias de FOREIGN KEY,
assim o PRAGMA foreign_keys = ON nunca reclama de referencia inexistente.
"""

import sqlite3
from pathlib import Path

# Caminho do banco na raiz do projeto (junto deste modulo).
DB_PATH = Path(__file__).resolve().parent.parent / "faculdade.db"

# ---------------------------------------------------------------------------
# DDL: cria as 4 entidades + a tabela associativa que resolve o N:N
# ---------------------------------------------------------------------------

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS PROFESSOR (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS SALA (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    numero       TEXT NOT NULL UNIQUE,
    professor_id INTEGER REFERENCES PROFESSOR(id)   -- PROFESSOR 1:N SALAS
);

CREATE TABLE IF NOT EXISTS MATERIA (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    nome    TEXT NOT NULL,
    sala_id INTEGER UNIQUE REFERENCES SALA(id)      -- SALA 1:1 MATERIAS (UNIQUE)
);

CREATE TABLE IF NOT EXISTS ALUNO (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    nome       TEXT NOT NULL,
    matricula  TEXT NOT NULL UNIQUE,
    materia_id INTEGER REFERENCES MATERIA(id)       -- MATERIA 1:N ALUNOS
);

-- Tabela associativa do relacionamento ALUNO N:N PROFESSOR
CREATE TABLE IF NOT EXISTS ALUNO_PROFESSOR (
    aluno_id     INTEGER NOT NULL REFERENCES ALUNO(id),
    professor_id INTEGER NOT NULL REFERENCES PROFESSOR(id),
    PRIMARY KEY (aluno_id, professor_id)
);
"""

# ---------------------------------------------------------------------------
# Seed: dados ficticios coerentes com as cardinalidades
#   3 professores, 4 salas, 4 materias, 8 alunos e relacoes N:N
# ---------------------------------------------------------------------------

SEED_SQL = """
INSERT INTO PROFESSOR (id, nome) VALUES
    (1, 'Dra. Ana Souza'),
    (2, 'Prof. Carlos Lima'),
    (3, 'Prof. Beatriz Rocha');

-- Professora Ana ocupa 2 salas (1:N salas por professor)
INSERT INTO SALA (id, numero, professor_id) VALUES
    (1, 'S-101', 1),
    (2, 'S-102', 1),
    (3, 'S-201', 2),
    (4, 'S-202', 3);

-- Cada materia tem exatamente 1 sala (1:1)
INSERT INTO MATERIA (id, nome, sala_id) VALUES
    (1, 'Introducao a Computacao', 1),
    (2, 'Calculo I',               2),
    (3, 'Banco de Dados',          3),
    (4, 'Estatistica',             4);

-- Cada aluno cursa 1 materia (muitos alunos por materia)
INSERT INTO ALUNO (id, nome, matricula, materia_id) VALUES
    (1, 'Joao Silva',      '2024-001', 1),
    (2, 'Maria Oliveira',  '2024-002', 1),
    (3, 'Pedro Santos',    '2024-003', 2),
    (4, 'Ana Costa',       '2024-004', 2),
    (5, 'Lucas Pereira',   '2024-005', 3),
    (6, 'Camila Rocha',    '2024-006', 3),
    (7, 'Rafael Almeida',  '2024-007', 4),
    (8, 'Julia Martins',   '2024-008', 4);

-- Relacoes ALUNO N:N PROFESSOR (um aluno pode ter varios professores)
INSERT INTO ALUNO_PROFESSOR (aluno_id, professor_id) VALUES
    (1, 1), (2, 1), (3, 2), (4, 1),
    (4, 3), (5, 2), (6, 3), (7, 2), (8, 3);
"""


def conectar(database: Path = DB_PATH) -> sqlite3.Connection:
    """Abre (ou cria) o banco e ativa a checagem de FOREIGN KEY."""
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def preparar_banco(database: Path = DB_PATH) -> None:
    """Recria as tabelas e carrega os dados. Idempotente."""
    conn = conectar(database)
    try:
        conn.executescript("DROP TABLE IF EXISTS ALUNO_PROFESSOR;"
                           "DROP TABLE IF EXISTS ALUNO;"
                           "DROP TABLE IF EXISTS MATERIA;"
                           "DROP TABLE IF EXISTS SALA;"
                           "DROP TABLE IF EXISTS PROFESSOR;")
        conn.executescript(SCHEMA_SQL)
        conn.executescript(SEED_SQL)
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    preparar_banco()
    print("Banco criado em:", DB_PATH)
