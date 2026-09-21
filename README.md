# Desafio de Analytics

O desafio deverá envolver 4 entidades relacionadas entre si e o resultado deverá ser apresentado como um grafo, representando as relações entre essas entidades.
Requisitos obrigatórios

  *  Utilizar exclusivamente dados presentes na base local.
  *  A solução deve conter SQL
  *  O modelo deve possuir 4 entidades.
  *  A solução final deve representar os relacionamentos entre as entidades em formato de grafo.
  *  Utilizar obrigatoriamente pelo menos 2 operações UNION ou UNION ALL como métodos do nó.
  *  Utilizar obrigatoriamente pelo menos 1 JOIN.

## Objetivo

A partir das quatro entidades disponíveis na base, construa uma estrutura que permita analisar os relacionamentos existentes entre elas e realizar consultas analíticas sobre o grafo resultante.

O desafio deve demonstrar domínio de:

   * Modelagem de dados (em diagrama ou dbdiagram);
   * SQL;
   * JOIN;
   * UNION / UNION ALL;
   * Transformação de dados relacionais em uma estrutura de grafo;

## Proposta

A estrutura de dados deve representar o funcionamento de uma Faculdade Entidades: ALUNO, PROFESSOR, MATÉRIA, SALA

* ALUNO N:N PROFESSOR

* MATERIA 1:N ALUNOS

* SALA 1:1 MATÉRIAS

* PROFESSOR 1:N SALAS
