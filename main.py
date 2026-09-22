"""
Desafio de Analytics - Faculdade como grafo.

Fluxo da solucao:

    1. Cria o banco relacional com as 4 entidades (database/schema_db.py).
    2. Extrai NOS e ARESTAS usando SQL puro (database/graph_queries.py),
       em que os NOS sao construidos com UNION ALL e as ARESTAS com JOINs.
    3. Monta o grafo em memoria (estrutura simples de Python).
    4. Roda analises sobre o grafo (DAG? grau? alcancabilidade?).
    5. Exporta o grafo no formato DOT para visualizacao externa.

Execute:  python main.py
"""

from collections import deque
from pathlib import Path

from database import graph_queries as gq
from database.schema_db import conectar, preparar_banco

# ---------------------------------------------------------------------------
# 1. Banco relacional
# ---------------------------------------------------------------------------

def preparar_dados() -> None:
    """Cria as tabelas e insere os dados ficticios (idempotente)."""
    preparar_banco()
    print("[1] Banco relacional criado com ALUNO, PROFESSOR, MATERIA, SALA.\n")


# ---------------------------------------------------------------------------
# 2. NOS e ARESTAS via SQL
# ---------------------------------------------------------------------------

def buscar_nos(conn) -> dict:
    """Executa NOS_SQL e devolve {chave: (tipo, rotulo, cor)}."""
    nos = {}
    for linha in conn.execute(gq.NOS_SQL):
        nos[linha["chave"]] = (linha["tipo"], linha["rotulo"], linha["cor"])
    return nos


def buscar_arestas(conn) -> list:
    """Executa ARESTAS_SQL e devolve lista de (origem, destino, relacao)."""
    return [(r["origem"], r["destino"], r["relacao"]) for r in conn.execute(gq.ARESTAS_SQL)]


# ---------------------------------------------------------------------------
# 3. Grafo em memoria
# ---------------------------------------------------------------------------

class GrafoFaculdade:
    """Grafo dirigido minimo: nos com atributos + lista de adjacencia."""

    def __init__(self, nos: dict, arestas: list):
        self.nos = nos                                        # chave -> (tipo, rotulo, cor)
        self.adj = {chave: [] for chave in nos}               # chave -> [(destino, relacao)]
        for origem, destino, relacao in arestas:
            self.adj[origem].append((destino, relacao))       # aresta origem -> destino

    def info(self) -> str:
        """Resumo do grafo via SQL (total de nos e arestas de cada tipo)."""
        return self._resumo_sql()

    def _resumo_sql(self) -> str:
        # Nao temos conexao aqui; resumo e montado pelas queries em main().
        return ""


# ---------------------------------------------------------------------------
# 4. Analises sobre o grafo (logica pura em Python)
# ---------------------------------------------------------------------------

def eh_dag(adj: dict) -> list | None:
    """Ordenacao topologica (Kahn). Devolve None se existir ciclo."""
    grau = {no: 0 for no in adj}
    for vizinhos in adj.values():            # grau de ENTRADA de cada no
        for destino, _ in vizinhos:
            grau[destino] += 1

    fila = deque(no for no, g in grau.items() if g == 0)
    ordem = []
    while fila:
        no = fila.popleft()
        ordem.append(no)
        for destino, _ in adj[no]:
            grau[destino] -= 1
            if grau[destino] == 0:
                fila.append(destino)

    # Se nao processamos todos os nos, existe um ciclo.
    return ordem if len(ordem) == len(adj) else None


def alcancaveis(adj: dict, raiz: str) -> list:
    """BFS simples: todos os nos alcancaveis partindo de `raiz`."""
    vistos = set()
    fila = deque([raiz])
    while fila:                              # percorre arestas para frente
        no = fila.popleft()
        for destino, _ in adj[no]:
            if destino not in vistos:
                vistos.add(destino)
                fila.append(destino)
    return sorted(vistos)


def maior_grau_saida(adj: dict) -> list:
    """Nos ordenados pelo numero de arestas que saem (out-degree)."""
    graus = sorted(
        ((no, len(viz)) for no, viz in adj.items()),
        key=lambda item: -item[1],
    )
    return graus


# ---------------------------------------------------------------------------
# 5. Visualizacao
# ---------------------------------------------------------------------------

def gerar_dot(nos: dict, arestas: list, destino: Path) -> None:
    """Exporta o grafo no formato DOT (legivel por Graphviz/dot)."""
    destino.parent.mkdir(parents=True, exist_ok=True)
    linhas = ['digraph Faculdade {', '  rankdir=LR;', '  node [style=filled];']
    for chave, (tipo, rotulo, cor) in sorted(nos.items()):
        linhas.append(f'  "{chave}" [label="{rotulo}\\n({tipo})", fillcolor="{cor}"];')
    for origem, destino_no, relacao in arestas:
        linhas.append(f'  "{origem}" -> "{destino_no}" [label="{relacao}"];')
    linhas.append('}')
    destino.write_text("\n".join(linhas), encoding="utf-8")


def imprimir_grafo(nos: dict, adj: dict) -> None:
    """Mostra a lista de adjacencia de forma legivel."""
    print("[4] Grafo montado em memoria -> lista de adjacencia:")
    for chave in sorted(adj):
        tipo, rotulo, _ = nos[chave]
        viz = ", ".join(f"{d}({r})" for d, r in sorted(adj[chave])) or "-"
        print(f"    {chave:<14} {rotulo:<24} ({tipo}) -> {viz}")
    print()


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def validar_fragmentos(conn, nome: str, fragmentos: list) -> None:
    """Executa cada fragmento SQL isoladamente e relata os resultados.

    Serve como 'check-up' da modelagem: se um fragmento falhar, o erro
    aponta exatamente o nome dele, sem misturar responsabilidades.
    """
    print(f"    validando {nome}:")
    for rotulo, frag in fragmentos:
        try:
            total = conn.execute(
                f"SELECT COUNT(*) AS c FROM ({frag})"
            ).fetchone()["c"]
        except Exception as erro:
            raise RuntimeError(f"[FALHA no fragmento '{rotulo}'] {erro}") from erro
        print(f"        {rotulo:<24} {total} linha(s)")


def main() -> None:
    preparar_dados()

    with conectar() as conn:
        # --- Valida cada fragmento isoladamente (responsabilidade unica) ---
        print("[2] Check-up dos fragmentos SQL (execucao isolada):")
        validar_fragmentos(conn, "nos", gq.NOS_FRAGMENTOS)
        validar_fragmentos(conn, "arestas", gq.ARESTAS_FRAGMENTOS)
        print()

        # --- SQL (composicao UNION ALL) transforma o relacional em grafo ---
        nos = buscar_nos(conn)
        arestas = buscar_arestas(conn)

        # --- Queries analiticas (JOIN + UNION ALL em acao) ---
        nos_por_tipo = conn.execute(gq.CONTAGEM_NOS_POR_TIPO_SQL).fetchall()
        arestas_por_relacao = conn.execute(gq.CONTAGEM_ARESTAS_POR_RELACAO_SQL).fetchall()
        salas_por_professor = conn.execute(gq.SALAS_POR_PROFESSOR_SQL).fetchall()

    # --- Grafo em memoria ---
    grafo = GrafoFaculdade(nos, arestas)

    print("[3] NOS extraidos via UNION ALL x4 (um SELECT por entidade):")
    print("    " + " + ".join(f"{linha['tipo']}={linha['total']}" for linha in nos_por_tipo))
    print("[3] ARESTAS extraidas via JOIN + UNION ALL x4:")
    print("    " + " + ".join(f"{linha['relacao']}={linha['total']}" for linha in arestas_por_relacao))
    print()
    imprimir_grafo(nos, grafo.adj)

    # --- Analises sobre o grafo ---
    ordem = eh_dag(grafo.adj)
    print("[5] Analises do grafo:")
    print("    - Eh DAG?", "SIM" if ordem else "NAO (existe ciclo)")
    if ordem:
        exemplos = [c for c in ordem if nos[c][0] == "professor"] + \
                   [c for c in ordem if nos[c][0] != "professor"]
        print("      ordem topologica (exemplo):", " -> ".join(exemplos[:6]))

    print("    - Top 3 nos com mais arestas de saida:")
    for chave, grau_saida in maior_grau_saida(grafo.adj)[:3]:
        print(f"        {nos[chave][1]:<24} -> {grau_saida} arestas")

    # Alcançabilidade: o que cada professor "enxerga" no grafo?
    print("    - Alcancabilidade a partir de cada professor (BFS):")
    for chave in sorted(nos, key=lambda c: nos[c][0] + c):
        if nos[chave][0] != "professor":
            continue
        destinos = alcancaveis(grafo.adj, chave)
        detalhe = ", ".join(f"{nos[d][1]}" for d in destinos) or "-"
        print(f"        {nos[chave][1]:<24} alcança: {detalhe}")
    print()

    print("    - Salas por professor (JOIN simples):")
    for linha in salas_por_professor:
        print(f"        {linha['professor']:<24} {linha['salas']} sala(s)")
    print()

    # --- Exporta o DOT para visualizacao externa ---
    dot = Path(__file__).resolve().parent / "output" / "grafo.dot"
    gerar_dot(nos, arestas, dot)
    print(f"[6] Grafo exportado: {dot}")
    print('    Renderize com:  dot -Tpng output/grafo.dot -o output/grafo.png')


if __name__ == "__main__":
    main()
