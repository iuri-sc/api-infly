from pydantic import BaseModel, EmailStr

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    
class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str
    
class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    
    class Config:
        from_attributes = True
        
class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    
    class Config:
        from_attributes = True
        
class LeadsResponse(BaseModel):
    lead: str
    quantidade: int
    
    class Config:
        from_attributes = True
        
class MatriculasLeadsResponse(BaseModel):
    ano: int
    mes: int
    nome_mes: str
    total_matriculas: int
    total_leads: int

    class Cosnfig:
        from_attributes = True
        
class TaxaConversaoResponse(BaseModel):
    ano: int
    mes: int
    nome_mes: str
    total_leads: int
    total_matriculas: int
    taxa_conversao: float

    class Config:
        from_attributes = True
        
class InadimplenciaResponse(BaseModel):
    ano: int
    mes: int
    nome_mes: str
    valor_total: float
    receita_total: float
    valor_inadimplente: float
    taxa_inadimplencia: float
    percentual_mensalidades_pagas: float

    class Config:
        from_attributes = True
                
"""        
class LucroMensalResponse(BaseModel):
    ano: int
    mes: int
    receita_total: float
    despesa_total: float
    lucro: float
"""