from sqlalchemy import Column, Integer, String, Text, Double, ForeignKey, Date
from .database import Base

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    
class Calendario(Base):
    __tablename__ = "d_calendario"
    
    id = Column(Integer, primary_key=True, index=True)
    data = Column(Date)
    ano = Column(Integer)
    mes = Column(Integer)
    dia = Column(Integer)
    nome_mes = Column(Text)
    semana = Column(Integer)
    trimestre = Column(Integer)
    
class Conta(Base):
    __tablename__ = "f_conta"
    
    id = Column(Integer, primary_key=True, index=True)
    id_pessoa = Column(Integer)
    id_pedido_venda = Column(Integer)
    categoria_conta = Column(Text)
    forma_pagamento = Column(Text)
    gateway_pagamento = Column(Text)
    tipo_conta = Column(Text)
    despesa = Column(Text)
    parcela = Column(Double)
    valor = Column(Double)
    id_calendario_pagamento = Column(Integer, ForeignKey("d_calendario.id"))
    id_calendario_vencimento = Column(Integer, ForeignKey("d_calendario.id"))
    id_calendario_emissao = Column(Integer, ForeignKey("d_calendario.id"))
    
class Negociacao(Base):
    __tablename__ = "f_negociacao"
    
    id = Column(Integer, primary_key=True, index=True)
    id_cliente = Column(Integer)
    id_vendedor = Column(Integer)
    id_produto = Column(Integer)
    atividade_negociacao = Column(Text)
    etapa_negociacao = Column(Text)
    origem_contato = Column(Text)
    tipo_atividade = Column(Text)
    quantidade_produto = Column(Integer)
    id_calendario_inicio = Column(Integer, ForeignKey("d_calendario.id"))
    id_calendario_fechamento = Column(Integer, ForeignKey("d_calendario"))
    id_calendario_fechamento_esperada = Column(Integer, ForeignKey("d_calendario.id"))
    id_horario_inicial = Column(Integer, ForeignKey("d_calendario.id"))
    id_horario_final = Column(Integer, ForeignKey("d_calendario.id"))
    valor_produto = Column(Double)