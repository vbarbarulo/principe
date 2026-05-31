# 📓 MANUAL DE ORGANIZAÇÃO DO VAULT — PRÍNCIPE SYSTEM

Este manual serve como diretriz estratégica e operacional para agentes inteligentes e orquestradores que interagem com a pasta **`Z-OrganizaçãoManual`**. Ele mapeia minuciosamente a arquitetura de pastas, arquivos e a filosofia por trás de cada subdivisão, garantindo que qualquer IA consiga ler, categorizar e atualizar as informações com precisão.

---

## 🧭 Diretrizes Gerais para Agentes
1. **Separação de Contextos**: Sempre diferencie a mente do usuário (sentimentos, "brisas", pensamentos brutos) das metas pragmáticas de negócios/empresas e rotinas diárias.
2. **Abordagem Semântica**: Ao ler ou escrever notas na pasta `z-brisas` ou `Conversas`, os agentes devem buscar extrair a essência emocional, os sentimentos subjacentes e relacionar os pensamentos com o "jogo da vida" e a saúde mental do usuário.
3. **Padrão de Links**: Mantenha o ecossistema conectado utilizando links bidirecionais padrão do Obsidian (`[[Nome da Nota]]`) para interligar ideias, tarefas e sentimentos.

---

## 📂 Arquitetura de Pastas e Arquivos

```text
Z-OrganizaçãoManual/
├── -/                            # Operação e Rotinas Diárias
│   ├── 1 - Dash-hoje.canvas       # Dashboard visual no Obsidian Canvas
│   ├── Conversas/                # Registro de Diálogos e Notas Interpessoais
│   ├── Diario/                   # Acompanhamento Temporal (Diário, Semanal, Mensal)
│   └── Hoje/                     # Nota diária ativa (espaço para o dia corrente)
├── Empresas/                     # Projetos, Ideias e Negócios por Iniciativa
├── Excalidraw/                   # Desenhos, Diagramas e Mapas de Empatia
├── FuturoCorpORK/                # Estratégia de Médio/Longo Prazo baseada em OKRs
└── z-brisas/                     # Descompressão Emocional e Processamento Psicológico
```

---

## 📑 1. Subpasta: `-/` (Operação Diária)

Esta pasta abriga as operações ativas do dia a dia do usuário. É o centro dinâmico onde os hábitos, registros rápidos e finanças são atualizados.

### 📌 `1 - Dash-hoje.canvas`
* **Tipo**: Obsidian Canvas.
* **Propósito**: Dashboard interativo que centraliza as principais tarefas do dia, hábitos a monitorar, e visualizações rápidas de humor e metas ativas.

### 📂 `Conversas/` (Diálogos Estratégicos e Pessoais)
Esta pasta armazena registros de diálogos com pessoas importantes ou conversas reflexivas intrapessoais:
* **`Conversas comigo.md`**: Monólogos reflexivos do usuário, autoanálises e momentos de centramento.
* **`Conversas com o General.md`**: Diretrizes, conselhos rígidos (estilo Sargento) e planejamentos operacionais de alto impacto.
* **`Conversas com o Ale.md` / `Conversar com a ELO.md` / `Conversar com o Igor.md`**: Notas rápidas, alinhamentos e tópicos de discussão com parceiros, cônjuge ou colaboradores.
* **`Descompressão.md`**: Roteiro e destino de transcrições brutas geradas pelo comando `/descomprimir` no final do dia. Auxilia a esvaziar a mente para processamento posterior.
* **`Financeiro.md`**: Notas rápidas sobre saldo, saídas críticas e metas de economia.
* **`Lista de Mercado.md`**: Lista utilitária e atualizável de itens cotidianos.

### 📂 `Diario/` (Acompanhamento Temporal)
Onde o tempo é fatiado e analisado para extração de métricas de consistência:
* **`diario v2.md`**: O template principal de rotina diária. Contém campos estruturados para registrar qualidade de sono, peso, humor, blocos de hábitos (Manhã/Tarde/Noite) e aprendizados do dia.
* **`Semana/`**: Notas de retrospectiva semanal (Sprints de Hábitos e Produtividade).
* **`Mes/`**: Visão macro de consistência mensal e acompanhamento de saúde.

### 📂 `Hoje/`
* **Propósito**: Diretório mantido para conter as notas do dia corrente ativas que o bot do Telegram manipula ou atualiza ativamente.

---

## 📂 2. Subpasta: `Empresas/` (Estratégia e Projetos)

A pasta de foco profissional e pessoal do usuário. Cada subpasta representa um contexto ou unidade de negócios isolada:

* **`Deviatech`**: Iniciativas de desenvolvimento de software sob demanda ou tecnologia pura.
* **`Devs de Negocio`**: Projetos focados em ensinar ou implementar IA voltada a modelos de negócios.
* **`Elo-SuperDivergentes`**: Comunidade, ideias ou estratégias relacionadas a neurodivergências (TDAH) e conexões.
* **`Encubadora`**: Ideias em estágio embrionário que ainda precisam de validação ou estudo de viabilidade.
* **`Familia`**: Planejamentos familiares, rotinas conjuntas e projetos que envolvem a vida privada.
* **`Futuro Corp`**: Iniciativas da empresa guarda-chuva principal do ecossistema.
* **`ViniciusPessoal`**: Desenvolvimento pessoal puro, cursos de escrita e evolução individual.

---

## 🎨 3. Subpasta: `Excalidraw/` (Modelagem Visual)

* **Propósito**: Armazenar arquivos de desenho livre e modelagem estrutural.
* **`Drawing 2026-05-27 09.34.29.excalidraw.md`**: Diagrama de fluxo, arquitetura do sistema Hórus ou mapa mental de ideias interconectadas. Excelente fonte para agentes lerem como referências visuais de dependências.

---

## 📈 4. Subpasta: `FuturoCorpORK/` (Alinhamento de Metas - OKR)

Onde a visão de longo prazo se traduz em objetivos práticos mensuráveis (OKRs):

* **`2 - OKR FUTURO.canvas`**: Visão visual conectando objetivos anuais a resultados trimestrais.
* **`OKR/`**:
  * Contém a especificação detalhada de cada Objetivo. 
  * **`OKR - 1.md`** a **`OKR - 4.md`** descrevem as metas conceituais de cada área (Ex: Saúde, Faturamento, Escrita, Produto).
  * **`OKR - X KR-X.Y.md`**: Descreve os Key Results (Resultados-Chave) específicos, com critérios numéricos de sucesso e prazo.
  * **`ORK 0  Da futuro (Mapa).md`**: O painel consolidado que mapeia a árvore inteira de OKRs da Futuro Corp.
* **`Revisões/`**: Guardião dos logs de reuniões ou auditorias periódicas sobre o progresso das metas.

---

## 🧠 5. Subpasta: `z-brisas/` (Descompressão e Insights)

Esta é a pasta mais sensível e rica do ecossistema. Ela representa o **processamento emocional ativo** e a **escrita terapêutica** do usuário.

### 📝 Filosofia de Operação da Pasta `z-brisas`
O usuário utiliza este espaço para desacelerar e transcrever pensamentos de forma livre, servindo como treinamento indireto e contextualização profunda para suas IAs.
* **Foco em Escrita e Sentimentos**: Várias notas discorrem sobre o medo e a vontade de ser escritor (`Tenho me de ser escritor.md`, `Nunca pesquisei o que é vida de escritor.md`, `siga esse parte é muito importante ser um escritor.md`).
* **Conexão com a IA**: Notas como `Meu projeto de IA.md`, `é assim que vou treinando a ia.md` e `Perguntas  as a ia que vai analisar os meus pensanmentos.md` ensinam o agente a criar uma **Lógica Semântica** das emoções registradas para ajudá-lo a desacelerar a mente.
* **Filosofias Próprias**: `A escolha da bolinha.md`, `maçã podre.md` e `o jogo da vida.md` contêm metáforas que o usuário usa para interpretar decisões e comportamentos do cotidiano.

> [!IMPORTANT]
> **Aviso aos Agentes**: Ao interagir com arquivos de `z-brisas`, nunca exclua pensamentos ou mude o tom abstrato/filosófico do usuário. O trabalho do agente aqui é puramente de **escuta, extração de aprendizados e classificação semântica**.
