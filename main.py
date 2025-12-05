from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone, date
from sqlalchemy import func, case, or_

from . import database, models, schemas

SECRET_KEY = "chave_secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=database.engine)

pwd_hasher = PasswordHasher()


def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def criar_token(dados: dict):
    to_encode = dados.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@app.post("/register", response_model=schemas.UsuarioResponse)
def register(user: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    user_existence = (
        db.query(models.Usuario).filter(models.Usuario.email == user.email).first()
    )
    if user_existence:
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    senha_hash = pwd_hasher.hash(user.senha)
    
    novo_user = models.Usuario(nome=user.nome, email=user.email, senha_hash=senha_hash)
    db.add(novo_user)
    db.commit()
    db.refresh(novo_user)
    return novo_user


@app.post("/login", response_model=schemas.TokenResponse)
def login(user: schemas.UsuarioLogin, db: Session = Depends(get_db)):
    usuario = (
        db.query(models.Usuario).filter(models.Usuario.email == user.email).first()
    )
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")

    try: 
        pwd_hasher.verify(usuario.senha_hash, user.senha)
    except VerifyMismatchError:
        raise HTTPException(status_code=401, detail="Senha incorreta")

    token = criar_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/origem-leads", response_model=list[schemas.LeadsResponse])
def leads(
    periodo: int = Query(6, description="Periodo em meses (3, 6 ou 12)"),
    db: Session = Depends(get_db)
):
    hoje = date.today()
    meses = hoje.replace(day=1) - timedelta(days=30 * periodo)
    
    resultados = (
        db.query(
            models.Negociacao.origem_contato,
            func.count(func.distinct(models.Negociacao.id)).label("quantidade")
        )
        .join(models.Calendario, models.Calendario.id == models.Negociacao.id_calendario_inicio)
        .filter(
            models.Calendario.data >= meses,
            models.Calendario.data <= hoje
        )
        .group_by(models.Negociacao.origem_contato)
        .order_by(func.count(models.Negociacao.id).desc())
        .all()
    )
    
    resposta = [
        {
            "lead": r.origem_contato or "Não especificado",
            "quantidade": int(r.quantidade or 0)
        }
        for r in resultados
    ]
    
    return resposta

@app.get("/matricula-lead", response_model=list[schemas.MatriculasLeadsResponse])
def matricula_lead(
    periodo: int = Query(6, description="Periodo em meses (3, 6 ou 12)"),
    db: Session = Depends(get_db)
):
    hoje = date.today()
    data_inicio = hoje.replace(day=1) - timedelta(days=30 * periodo)
    
    # leads por mês
    leads = (
        db.query(
            models.Calendario.ano,
            models.Calendario.mes,
            models.Calendario.nome_mes,
            func.count(func.distinct(models.Negociacao.id_cliente)).label("total_leads")
        )
        .join(models.Calendario, models.Calendario.id == models.Negociacao.id_calendario_inicio)
        .filter(models.Calendario.data >= data_inicio)
        .group_by(models.Calendario.ano, models.Calendario.mes, models.Calendario.nome_mes)
        .all()
    )
    
    # transformar em dicionário
    leads_dict = {
        (l.ano, l.mes): {
            "ano": int(l.ano),
            "mes": int(l.mes),
            "nome_mes": l.nome_mes,
            "total_leads": int(l.total_leads)
        }
        for l in leads
    }
    
    # matriculas por mês
    matriculas = (
        db.query(
            models.Calendario.ano,
            models.Calendario.mes,
            models.Calendario.nome_mes,
            func.count(models.Negociacao.id).label("total_matriculas")
        )
        .join(
            models.Negociacao,
            models.Negociacao.id_calendario_inicio == models.Calendario.id
        )
        .filter(
            models.Calendario.data >= data_inicio,
            or_(
                models.Negociacao.etapa_negociacao.like("NEGOCIA%"),
                models.Negociacao.etapa_negociacao == "MATRICULADO"
            )
        )
        .group_by(
            models.Calendario.ano,
            models.Calendario.mes,
            models.Calendario.nome_mes
        )
        .order_by(
            models.Calendario.ano.asc(),
            models.Calendario.mes.asc()
        )
        .all()
    )
    
    # juntar leads e matriculas
    resposta_final = []
    
    for m in matriculas:
        chave = (m.ano, m.mes)
        
        total_leads = leads_dict.get(chave, {}).get("total_leads", 0)
        
        resposta_final.append({
            "ano": int(m.ano),
            "mes": int(m.mes),
            "nome_mes": m.nome_mes,
            "total_leads": int(total_leads),
            "total_matriculas": int(m.total_matriculas)
        })
        
    return resposta_final

@app.get("/taxa-conversao", response_model=list[schemas.TaxaConversaoResponse])
def taxa_conversao(
    periodo: int = Query(6, description="Periodo em meses (3, 6 ou 12)"),
    db: Session = Depends(get_db)
):
    hoje = date.today()
    data_inicio = hoje.replace(day=1) - timedelta(days=30 * periodo)
    
    # leads por mês
    leads = (
        db.query(
            models.Calendario.ano,
            models.Calendario.mes,
            models.Calendario.nome_mes,
            func.count(func.distinct(models.Negociacao.id_cliente)).label("total_leads")
        )
        .join(models.Calendario, models.Calendario.id == models.Negociacao.id_calendario_inicio)
        .filter(models.Calendario.data >= data_inicio)
        .group_by(models.Calendario.ano, models.Calendario.mes, models.Calendario.nome_mes)
        .all()
    )
    
    leads_dict = {
        (l.ano, l.mes): int(l.total_leads) for l in leads
    }
    
    # matriculas pro mês
    matriculas = (
        db.query(
            models.Calendario.ano,
            models.Calendario.mes,
            models.Calendario.nome_mes,
            func.count(models.Negociacao.id).label("total_matriculas")
        )
        .join(models.Negociacao, models.Negociacao.id_calendario_inicio == models.Calendario.id)
        .filter(
            models.Calendario.data >= data_inicio,
            or_(
                models.Negociacao.etapa_negociacao.like("NEGOCIA%"),
                models.Negociacao.etapa_negociacao == "MATRICULADO"
            )
        )
        .group_by(models.Calendario.ano, models.Calendario.mes, models.Calendario.nome_mes)
        .order_by(models.Calendario.ano.asc(), models.Calendario.mes.asc())
        .all()
    )
    
    resposta = []
    for m in matriculas:
        chave = (m.ano, m.mes)
        total_leads = leads_dict.get(chave, 0)
        total_matriculas = int(m.total_matriculas)
        taxa = (total_matriculas / total_leads * 100) if total_leads > 0 else 0
        
        resposta.append({
            "ano": int(m.ano),
            "mes": int(m.mes),
            "nome_mes": m.nome_mes,
            "total_leads": total_leads,
            "total_matriculas": total_matriculas,
            "taxa_conversao": round(taxa, 2)
        })
    
    return resposta

@app.get("/inadimplencia", response_model=list[schemas.InadimplenciaResponse])
def inadimplencia(
    periodo: int = Query(6, description="Periodo em meses (3, 6, 12)"),
    db: Session = Depends(get_db)
):
    hoje = date.today()
    data_inicio = hoje.replace(day=1) - timedelta(days=30 * periodo)
    
    resultados = (
        db.query(
            models.Calendario.ano,
            models.Calendario.mes,
            models.Calendario.nome_mes,
            func.sum(models.Conta.valor).label("valor_total"),
            func.sum(
                case(
                    (models.Conta.id_calendario_pagamento != None, models.Conta.valor),
                    else_=0
                )
            ).label("receita_total"),
            func.sum(
                case(
                    (models.Conta.id_calendario_pagamento == None, models.Conta.valor),
                    else_=0
                )
            ).label("valor_inadimplente")
        )
        .join(models.Calendario, models.Calendario.id == models.Conta.id_calendario_vencimento)
        .filter(models.Calendario.data >= data_inicio)
        .group_by(models.Calendario.ano, models.Calendario.mes, models.Calendario.nome_mes)
        .order_by(models.Calendario.ano.asc(), models.Calendario.mes.asc())
        .all()
    )
    
    resposta = []
    for r in resultados:
        valor_total = float(r.valor_total or 0)
        receita_total = float(r.receita_total or 0)
        valor_inadimplente = float(r.valor_inadimplente or 0)
        
        taxa_inadimplencia = (valor_inadimplente / valor_total * 100) if valor_total > 0 else 0
        percentual_pagas = (receita_total / valor_total * 100) if valor_total > 0 else 0
        
        resposta.append({
            "ano": int(r.ano),
            "mes": int(r.mes),
            "nome_mes": r.nome_mes,
            "valor_total": valor_total,
            "receita_total": receita_total,
            "valor_inadimplente": valor_inadimplente,
            "taxa_inadimplencia": round(taxa_inadimplencia, 2),
            "percentual_mensalidades_pagas": round(percentual_pagas, 2)    
        })
        
    return resposta