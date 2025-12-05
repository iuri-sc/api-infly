import pandas as pd
from sqlalchemy import create_engine

# configurações
mysql_url = "mysql+mysqlconnector://root:123456@localhost:3306/infly_anonima"
pg_url = "postgresql+psycopg2://postgres:123456@localhost:5432/dw_infly_anonymous"

mysql_engine = create_engine(mysql_url)
pg_engine = create_engine(pg_url)

# queries
cliente_query = """
SELECT
    ps.id           AS id_pessoa,
    ps.nome         AS nome_pessoa,
    gp.nome         AS tipo_pessoa,
    ps.fone         AS fone,
    ps.email        AS email,
    ps.data_nasc    AS data_nascimento,
    ps.sexo         AS sexo,
    tp.nome         AS tipo_cliente,
    cc.nome         AS categoria_cliente
FROM pessoa AS ps
LEFT JOIN tipo_cliente AS tp 
    ON ps.tipo_cliente_id = tp.id
LEFT JOIN categoria_cliente AS cc 
    ON ps.categoria_cliente_id = cc.id
LEFT JOIN pessoa_grupo AS pg 
    ON pg.pessoa_id = ps.id
JOIN grupo_pessoa AS gp 
    ON gp.id = pg.grupo_pessoa_id
    AND gp.nome = 'Cliente';
"""

negociacao_query = """
SELECT
    ng.id                       AS id_negociacao,
    ng.cliente_id               AS id_cliente,
    ng.vendedor_id              AS id_vendedor,
    ng.data_inicio              AS data_inicio,
    ng.data_fechamento          AS data_fechamento,
    ng.data_fechamento_esperada AS data_fechamento_esperada,
    oc.nome                     AS origem_contato,
    en.nome                     AS etapa_negociacao,
    na.descricao                AS atividade_negociacao,
    na.horario_inicial          AS horario_inicial,
    na.horario_final            AS horario_final,
    ta.nome                     AS tipo_atividade,
    ni.produto_id               AS id_produto,
    ni.quantidade               AS quantidade_produto,
    ni.valor                    AS valor_produto
FROM negociacao AS ng
LEFT JOIN origem_contato AS oc 
    ON ng.origem_contato_id = oc.id
LEFT JOIN etapa_negociacao AS en 
    ON ng.etapa_negociacao_id = en.id
LEFT JOIN negociacao_atividade AS na 
    ON ng.id = na.negociacao_id
LEFT JOIN tipo_atividade AS ta 
    ON na.tipo_atividade_id = ta.id
LEFT JOIN negociacao_item AS ni 
    ON ng.id = ni.negociacao_id;

"""

conta_query = """
SELECT
    co.id                        AS id_conta,
    co.pessoa_id                 AS id_pessoa,
    co.despesa                   AS despesa,
    tpc.nome                     AS tipo_conta,
    ca.nome                      AS categoria_conta,
    fp.nome                      AS forma_pagamento,
    co.pedido_venda_id           AS id_pedido_venda,
    gt.nome                      AS gateway_pagamento,
    co.dt_vencimento             AS data_vencimento,
    co.dt_emissao                AS data_emissao,
    co.dt_pagamento              AS data_pagamento,
    co.dt_renegociacao           AS data_renegociacao,
    co.parcela                   AS parcela,
    co.ano_mes_emissao           AS ano_mes_emissao,
    co.ano_mes_vencimento        AS ano_mes_vencimento,
    co.ano_mes_pagamento         AS ano_mes_pagamento,
    co.valor                     AS valor
FROM conta AS co
LEFT JOIN categoria AS ca 
    ON co.categoria_id = ca.id
LEFT JOIN tipo_conta AS tpc 
    ON ca.tipo_conta_id = tpc.id
LEFT JOIN forma_pagamento AS fp 
    ON co.forma_pagamento_id = fp.id
LEFT JOIN gateway_pagamento AS gt 
    ON co.gateway_pagamento_id = gt.id;
"""

item_query = """
SELECT
    pv.id                   AS id_pedido,
    pvi.id                  AS id_item_pedido,
    tp.nome                 AS tipo_pedido,
    pv.cliente_id           AS id_cliente,
    pv.vendedor_id          AS id_vendedor,
    pv.condicao_pagamento_id AS id_condicao_pagamento,
    pv.dt_pedido            AS data_pedido,
    pv.valor_total          AS valor_total_pedido,
    pvi.produto_id          AS id_produto,
    pvi.quantidade          AS quantidade_produto,
    pvi.valor               AS valor_produto
FROM pedido_venda AS pv
LEFT JOIN pedido_venda_item AS pvi 
    ON pv.id = pvi.pedido_venda_id
LEFT JOIN tipo_pedido AS tp 
    ON pv.tipo_pedido_id = tp.id
LEFT JOIN estado AS es 
    ON pv.estado_pedido_venda_id = es.id;
"""

produto_query = """
SELECT
    pr.id        AS id_produto,
    pr.nome      AS nome_produto,
    fp.nome      AS familia_produto
FROM produto AS pr
JOIN tipo_produto AS tp 
    ON pr.tipo_produto_id = tp.id
    AND tp.nome = 'Produto'
LEFT JOIN familia_produto AS fp 
    ON pr.familia_produto_id = fp.id;

"""
vendedor_query = """
SELECT
    ps.id           AS id_pessoa,
    ps.nome         AS nome_pessoa,
    gp.nome         AS tipo_pessoa,
    ps.fone         AS fone,
    ps.email        AS email,
    ps.data_nasc    AS data_nascimento,
    ps.sexo         AS sexo,
    tp.nome         AS tipo_cliente,
    cc.nome         AS categoria_cliente
FROM pessoa AS ps
LEFT JOIN tipo_cliente AS tp 
    ON ps.tipo_cliente_id = tp.id
LEFT JOIN categoria_cliente AS cc 
    ON ps.categoria_cliente_id = cc.id
LEFT JOIN pessoa_grupo AS pg 
    ON pg.pessoa_id = ps.id
JOIN grupo_pessoa AS gp 
    ON gp.id = pg.grupo_pessoa_id
    AND gp.nome = 'Vendedor';

"""

# extração
print("extraindo dados do banco origem...")
clientes = pd.read_sql(cliente_query, mysql_engine)
produtos = pd.read_sql(produto_query, mysql_engine)
vendedores = pd.read_sql(vendedor_query, mysql_engine)
itens = pd.read_sql(item_query, mysql_engine)
contas = pd.read_sql(conta_query, mysql_engine)
negociacoes = pd.read_sql(negociacao_query, mysql_engine)
print("extração concluída.\n")

# transformação
print("transformando dados para o modelo estrela...")

# dimensão cliente
d_cliente = clientes.rename(
    columns={
        "id_pessoa": "id",
        "nome_pessoa": "nome",
        "fone": "fone",
        "sexo": "sexo",
        "categoria_cliente": "categoria",
        "data_nascimento": "data_nascimento",
    }
)[["id", "nome", "tipo_pessoa", "tipo_cliente", "email", "fone", "sexo", "categoria", "data_nascimento"]]

# dimensão produto
d_produto = produtos.rename(
    columns={
        "id_produto": "id",
        "nome_produto": "nome",
        "familia_produto": "familia_produto",
    }
)[["id", "nome", "familia_produto"]]

# dimensão vendedor
d_vendedor = vendedores.rename(
    columns={
        "id_pessoa": "id",
        "nome_pessoa": "nome",
        "email": "email",
        "fone": "fone",
        "tipo_pessoa": "tipo",
        "categoria_cliente": "categoria",
        "data_nascimento": "data_nasc",
    }
)[["id", "nome", "email", "fone", "tipo", "categoria", "data_nasc"]]

# dimensão calendário
datas = pd.concat(
    [
        itens["data_pedido"],
        contas["data_pagamento"],
        contas["data_vencimento"],
        contas["data_emissao"],
        contas["data_renegociacao"],
        negociacoes["data_inicio"],
        negociacoes["data_fechamento"],
        negociacoes["data_fechamento_esperada"],
        negociacoes["horario_inicial"],
        negociacoes["horario_final"],
    ],
    ignore_index=True,
)

datas = pd.to_datetime(datas.dropna().unique())

d_calendario = pd.DataFrame({"data": datas})
d_calendario["ano"] = d_calendario["data"].dt.year
d_calendario["mes"] = d_calendario["data"].dt.month
d_calendario["dia"] = d_calendario["data"].dt.day
d_calendario["nome_mes"] = d_calendario["data"].dt.strftime("%B")
d_calendario["semana"] = d_calendario["data"].dt.isocalendar().week
d_calendario["trimestre"] = d_calendario["data"].dt.quarter
d_calendario.reset_index(inplace=True)
d_calendario.rename(columns={"index": "id"}, inplace=True)

mapa_calendario = dict(zip(d_calendario["data"], d_calendario["id"]))

# fato pedido item
f_pedido_item = itens.rename(
    columns={
        "id_item_pedido": "id",
        "data_pedido": "data_pedido",
        "id_cliente": "id_cliente",
        "id_vendedor": "id_vendedor",
        "id_produto": "id_produto",
        "id_condicao_pagamento": "id_condicao_pagamento",
        "quantidade_produto": "quantidade_pedida",
        "tipo_pedido": "tipo_pedido",
    }
)
f_pedido_item["data_pedido"] = pd.to_datetime(
    f_pedido_item["data_pedido"], errors="coerce"
)
f_pedido_item["id_calendario"] = f_pedido_item["data_pedido"].map(mapa_calendario)
f_pedido_item = f_pedido_item[
    [
        "id",
        "data_pedido",
        "id_cliente",
        "id_vendedor",
        "id_produto",
        "id_condicao_pagamento",
        "quantidade_pedida",
        "tipo_pedido",
        "id_calendario",
        "valor_produto",
        "valor_total_pedido"
    ]
]

# fato conta
f_conta = contas.rename(
    columns={
        "id_conta": "id",
        "data_pagamento": "dt_pagamento",
        "data_vencimento": "dt_vencimento",
        "data_emissao": "dt_emissao",
        "id_pessoa": "id_pessoa",
        "id_pedido_venda": "id_pedido_venda",
        "categoria_conta": "categoria_conta",
        "forma_pagamento": "forma_pagamento",
        "gateway_pagamento": "gateway_pagamento",
        "tipo_conta": "tipo_conta",
    }
)
f_conta["dt_pagamento"] = pd.to_datetime(f_conta["dt_pagamento"], errors="coerce")
f_conta["dt_vencimento"] = pd.to_datetime(f_conta["dt_vencimento"], errors="coerce")
f_conta["dt_emissao"] = pd.to_datetime(f_conta["dt_emissao"], errors="coerce")

f_conta["id_calendario_pagamento"] = f_conta["dt_pagamento"].map(mapa_calendario)
f_conta["id_calendario_vencimento"] = f_conta["dt_vencimento"].map(mapa_calendario)
f_conta["id_calendario_emissao"] = f_conta["dt_emissao"].map(mapa_calendario)

f_conta = f_conta[
    [
        "id",
        "id_pessoa",
        "id_pedido_venda",
        "categoria_conta",
        "forma_pagamento",
        "gateway_pagamento",
        "tipo_conta",
        "id_calendario_pagamento",
        "id_calendario_vencimento",
        "id_calendario_emissao",
        "despesa",
        "parcela",
        "valor"
    ]
]

# fato negociação
f_negociacao = negociacoes.rename(
    columns={
        "id_negociacao": "id",
        "id_cliente": "id_cliente",
        "id_vendedor": "id_vendedor",
        "id_produto": "id_produto",
        "atividade_negociacao": "atividade_negociacao",
        "etapa_negociacao": "etapa_negociacao",
        "origem_contato": "origem_contato",
        "tipo_atividade": "tipo_atividade",
        "quantidade_produto": "quantidade_produto",
    }
)
f_negociacao["data_inicio"] = pd.to_datetime(
    negociacoes["data_inicio"], errors="coerce"
)
f_negociacao["data_fechamento"] = pd.to_datetime(
    negociacoes["data_fechamento"], errors="coerce"
)
f_negociacao["data_fechamento_esperada"] = pd.to_datetime(
    negociacoes["data_fechamento_esperada"], errors="coerce"
)
f_negociacao["horario_inicial"] = pd.to_datetime(
    negociacoes["horario_inicial"], errors="coerce"
)
f_negociacao["horario_final"] = pd.to_datetime(
    negociacoes["horario_final"], errors="coerce"
)

f_negociacao["id_calendario_inicio"] = f_negociacao["data_inicio"].map(mapa_calendario)
f_negociacao["id_calendario_fechamento"] = f_negociacao["data_fechamento"].map(
    mapa_calendario
)
f_negociacao["id_calendario_fechamento_esperada"] = f_negociacao[
    "data_fechamento_esperada"
].map(mapa_calendario)
f_negociacao["id_horario_inicial"] = f_negociacao["horario_inicial"].map(
    mapa_calendario
)
f_negociacao["id_horario_final"] = f_negociacao["horario_final"].map(mapa_calendario)

f_negociacao = f_negociacao[
    [
        "id",
        "id_cliente",
        "id_vendedor",
        "id_produto",
        "atividade_negociacao",
        "etapa_negociacao",
        "origem_contato",
        "tipo_atividade",
        "quantidade_produto",
        "id_calendario_inicio",
        "id_calendario_fechamento",
        "id_calendario_fechamento_esperada",
        "id_horario_inicial",
        "id_horario_final",
        "valor_produto"
    ]
]

# bridge entre f_pedido_item e d_produto
bridge_pedido_produto = f_pedido_item[["id", "id_produto"]].copy()
bridge_pedido_produto.rename(columns={"id": "id_pedido"}, inplace=True)

bridge_pedido_produto.drop_duplicates(subset=["id_pedido", "id_produto"], inplace=True)
bridge_pedido_produto.reset_index(inplace=True)
bridge_pedido_produto.rename(columns={"index": "id"}, inplace=True)

print("transformações concluídas.\n")

# carga
print("carregando dados no data warehouse...")

d_cliente.to_sql("d_cliente", pg_engine, if_exists="replace", index=False)
d_produto.to_sql("d_produto", pg_engine, if_exists="replace", index=False)
d_vendedor.to_sql("d_vendedor", pg_engine, if_exists="replace", index=False)
d_calendario.to_sql("d_calendario", pg_engine, if_exists="replace", index=False)
f_pedido_item.to_sql("f_pedido_item", pg_engine, if_exists="replace", index=False)
f_conta.to_sql("f_conta", pg_engine, if_exists="replace", index=False)
f_negociacao.to_sql("f_negociacao", pg_engine, if_exists="replace", index=False)
bridge_pedido_produto.to_sql(
    "bridge_pedido_produto", pg_engine, if_exists="replace", index=False
)

print("etl finalizado com sucesso! uhulll :)")
