"""
Modelos de dados para o sistema de validação de NFe's.

Define as estruturas de dados imutáveis usadas em todo o sistema.
"""

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum


class TipoResultado(Enum):
    """Tipos de resultado do confrontamento"""
    IDENTICA = "identica"
    DIVERGENTE = "divergente"
    DIVERGENTE_AGRUPADA = "divergente_agrupada"
    NAO_ENCONTRADA = "nao_encontrada"
    DESCONSIDERADA = "desconsiderada"


@dataclass(frozen=True)
class NFe:
    """
    Representa uma Nota Fiscal Eletrônica extraída de XML.
    
    Attributes:
        numero: Número da NFe (ex: "11395373")
        data_emissao: Data de emissão da nota
        cnpj_emitente: CNPJ do posto/fornecedor (formato: apenas números)
        cnpj_destinatario: CNPJ da empresa destinatária
        valor: Valor total da nota
        xml_path: Caminho para o arquivo XML original
        tipo_nota: Tipo da nota (0=Entrada, 1=Saída)
    """
    numero: str
    data_emissao: date
    cnpj_emitente: str
    cnpj_destinatario: str
    valor: Decimal
    xml_path: str
    tipo_nota: int = 1
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        if self.valor <= 0:
            raise ValueError(f"Valor da NFe deve ser positivo: {self.valor}")
        
        if len(self.cnpj_emitente) != 14:
            raise ValueError(f"CNPJ emitente inválido: {self.cnpj_emitente}")
        
        if len(self.cnpj_destinatario) != 14:
            raise ValueError(f"CNPJ destinatário inválido: {self.cnpj_destinatario}")


@dataclass(frozen=True)
class Transacao:
    """
    Representa uma transação da planilha de abastecimento.
    
    Attributes:
        numero_nfe: Número da NFe informado na planilha
        data_abastecimento: Data do abastecimento
        cnpj_posto: CNPJ do posto (emitente)
        cnpj_empresa: CNPJ da empresa (destinatária)
        valor_total: Valor total da transação
        dias_atraso: Dias em atraso calculados
        postergado: Indica se está marcado como postergado ("Sim"/"Não")
        id_agrupada: ID de agrupamento (se aplicável)
        linha_planilha: Número da linha na planilha original (para rastreamento)
    """
    numero_nfe: str
    data_abastecimento: date
    cnpj_posto: str
    cnpj_empresa: str
    valor_total: Decimal
    dias_atraso: int
    postergado: str
    linha_planilha: int
    id_agrupada: Optional[str] = None
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        if self.valor_total <= 0:
            raise ValueError(f"Valor da transação deve ser positivo: {self.valor_total}")
        
        if len(self.cnpj_posto) != 14:
            raise ValueError(f"CNPJ posto inválido: {self.cnpj_posto}")
        
        if len(self.cnpj_empresa) != 14:
            raise ValueError(f"CNPJ empresa inválido: {self.cnpj_empresa}")
    
    @property
    def esta_postergado(self) -> bool:
        """Verifica se a transação está marcada como postergada"""
        return self.postergado.lower().strip() == "sim"


@dataclass
class ResultadoConfronto:
    """
    Resultado do confrontamento entre uma transação e uma NFe.
    
    Attributes:
        tipo: Tipo de resultado (enum TipoResultado)
        transacao: Transação da planilha
        nfe: NFe correspondente (None se não encontrada)
        diferenca_valor: Diferença absoluta entre valores
        dias_postergados: Dias entre data_abastecimento e data_fechamento
        motivo: Descrição textual do resultado
        detalhes: Informações adicionais para debug
    """
    tipo: TipoResultado
    transacao: Transacao
    nfe: Optional[NFe]
    diferenca_valor: Decimal
    dias_postergados: int
    motivo: str
    detalhes: dict = field(default_factory=dict)
    
    @property
    def valor_planilha(self) -> Decimal:
        """Valor da planilha"""
        return self.transacao.valor_total
    
    @property
    def valor_xml(self) -> Optional[Decimal]:
        """Valor do XML (None se NFe não encontrada)"""
        return self.nfe.valor if self.nfe else None
    
    @property
    def numero_nfe(self) -> str:
        """Número da NFe"""
        return self.transacao.numero_nfe
    
    @property
    def cnpj_emitente(self) -> str:
        """CNPJ do emitente"""
        return self.transacao.cnpj_posto
    
    @property
    def cnpj_destinatario(self) -> str:
        """CNPJ do destinatário"""
        return self.transacao.cnpj_empresa
    
    @property
    def data_abastecimento(self) -> date:
        """Data do abastecimento"""
        return self.transacao.data_abastecimento
    
    @property
    def data_emissao(self) -> Optional[date]:
        """Data de emissão da NFe (None se não encontrada)"""
        return self.nfe.data_emissao if self.nfe else None


@dataclass
class RelatorioConfronto:
    """
    Relatório consolidado do confrontamento.
    
    Attributes:
        identicas: Lista de confrontos idênticos
        divergentes: Lista de confrontos com divergência de valor
        divergentes_agrupadas: Lista de confrontos agrupados divergentes
        nao_encontradas: Lista de transações sem NFe correspondente
        desconsideradas: Lista de transações postergadas (>60 dias)
        data_processamento: Data/hora do processamento
        total_processado: Total de transações processadas
    """
    identicas: List[ResultadoConfronto] = field(default_factory=list)
    divergentes: List[ResultadoConfronto] = field(default_factory=list)
    divergentes_agrupadas: List[ResultadoConfronto] = field(default_factory=list)
    nao_encontradas: List[ResultadoConfronto] = field(default_factory=list)
    desconsideradas: List[ResultadoConfronto] = field(default_factory=list)
    data_processamento: datetime = field(default_factory=datetime.now)
    total_processado: int = 0
    
    def __post_init__(self):
        """Calcula o total processado"""
        self.total_processado = (
            len(self.identicas) +
            len(self.divergentes) +
            len(self.divergentes_agrupadas) +
            len(self.nao_encontradas) +
            len(self.desconsideradas)
        )
    
    @property
    def total_identicas(self) -> Decimal:
        """Soma dos valores de transações idênticas"""
        return sum((r.valor_planilha for r in self.identicas), start=Decimal("0"))
    
    @property
    def total_divergentes(self) -> Decimal:
        """Soma dos valores de transações divergentes"""
        return sum((r.valor_planilha for r in self.divergentes), start=Decimal("0"))
    
    @property
    def total_divergentes_agrupadas(self) -> Decimal:
        """Soma dos valores de transações divergentes agrupadas"""
        return sum((r.valor_planilha for r in self.divergentes_agrupadas), start=Decimal("0"))
    
    @property
    def total_nao_encontradas(self) -> Decimal:
        """Soma dos valores de transações não encontradas"""
        return sum((r.valor_planilha for r in self.nao_encontradas), start=Decimal("0"))
    
    @property
    def total_desconsideradas(self) -> Decimal:
        """Soma dos valores de transações desconsideradas"""
        return sum((r.valor_planilha for r in self.desconsideradas), start=Decimal("0"))
    
    @property
    def percentual_identicas(self) -> float:
        """Percentual de transações idênticas"""
        if self.total_processado == 0:
            return 0.0
        return (len(self.identicas) / self.total_processado) * 100
    
    @property
    def percentual_divergentes(self) -> float:
        """Percentual de transações divergentes"""
        if self.total_processado == 0:
            return 0.0
        total_div = len(self.divergentes) + len(self.divergentes_agrupadas)
        return (total_div / self.total_processado) * 100
    
    @property
    def percentual_nao_encontradas(self) -> float:
        """Percentual de transações não encontradas"""
        if self.total_processado == 0:
            return 0.0
        return (len(self.nao_encontradas) / self.total_processado) * 100
    
    def resumo(self) -> dict:
        """Retorna um resumo estatístico do relatório"""
        return {
            "total_processado": self.total_processado,
            "identicas": {
                "quantidade": len(self.identicas),
                "percentual": round(self.percentual_identicas, 2),
                "valor_total": float(self.total_identicas)
            },
            "divergentes": {
                "quantidade": len(self.divergentes),
                "percentual": round(self.percentual_divergentes, 2),
                "valor_total": float(self.total_divergentes)
            },
            "divergentes_agrupadas": {
                "quantidade": len(self.divergentes_agrupadas),
                "valor_total": float(self.total_divergentes_agrupadas)
            },
            "nao_encontradas": {
                "quantidade": len(self.nao_encontradas),
                "percentual": round(self.percentual_nao_encontradas, 2),
                "valor_total": float(self.total_nao_encontradas)
            },
            "desconsideradas": {
                "quantidade": len(self.desconsideradas),
                "valor_total": float(self.total_desconsideradas)
            }
        }


@dataclass
class Configuracao:
    """
    Configurações do sistema.
    
    Attributes:
        data_fechamento: Data de fechamento do período
        periodo_maximo_dias: Período máximo em dias (padrão: 60)
        tolerancia_valor: Tolerância de diferença de valor (padrão: R$ 1,01)
        cnpj_destinatario_padrao: CNPJ da empresa destinatária
    """
    data_fechamento: date
    periodo_maximo_dias: int = 60
    tolerancia_valor: Decimal = Decimal("1.01")
    cnpj_destinatario_padrao: str = ""
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        if self.periodo_maximo_dias <= 0:
            raise ValueError("Período máximo deve ser positivo")
        
        if self.tolerancia_valor < 0:
            raise ValueError("Tolerância de valor deve ser não-negativa")
    
    def calcular_dias_postergados(self, data_abastecimento: date) -> int:
        """
        Calcula os dias postergados entre a data de abastecimento e fechamento.
        
        Args:
            data_abastecimento: Data do abastecimento
            
        Returns:
            Número de dias postergados (positivo)
        """
        delta = self.data_fechamento - data_abastecimento
        return max(0, delta.days)
    
    def esta_dentro_prazo(self, data_abastecimento: date) -> bool:
        """
        Verifica se a data de abastecimento está dentro do prazo.
        
        Args:
            data_abastecimento: Data do abastecimento
            
        Returns:
            True se dentro do prazo, False caso contrário
        """
        dias = self.calcular_dias_postergados(data_abastecimento)
        return dias <= self.periodo_maximo_dias
