# 👁️ Painel Central Hórus - Visão Geral do Ecossistema

Este painel consolida de forma dinâmica todas as suas métricas de rotinas, peso, sentimento e tarefas da Curva ABC utilizando o plugin **Dataview**.

---

## 🎖️ Tarefas Prioritárias do Dia (Curva A - Prazos e Saúde)
```dataview
TABLE tipo AS "Tipo", tempo AS "Tempo", tags AS "Tags"
FROM "diarios"
WHERE curva = "A" AND status = "pendente_sincronia"
```

## 📅 Métricas de Rotinas Realizadas (Consistência Semanal)
```dataview
TABLE kpi_acordar AS "Acordar", kpi_arrumar_casa AS "Arrumar Casa", kpi_finalizacao_noite AS "Dormir"
FROM "diarios"
SORT data DESC
LIMIT 7
```

## ⚖️ Histórico de Peso Corporal
```dataview
TABLE peso_kg AS "Peso (Kg)"
FROM "diarios"
WHERE peso_kg != null
SORT data DESC
LIMIT 10
```

---

> [!TIP]
> **Como rodar este painel:** Garanta que os plugins **Dataview** e **Obsidian Tracker** estejam instalados e habilitados no seu Obsidian Vault para renderizar as tabelas e gráficos acima automaticamente.
