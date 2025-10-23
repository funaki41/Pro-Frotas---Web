"""
Utilitários para manipulação segura de valores monetários.

Usa Decimal para evitar problemas de precisão com float.
"""

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from typing import Union


class ValorMonetario:
    """
    Classe segura para manipulação de valores monetários.
    
    Garante precisão exata usando Decimal e fornece métodos
    para conversão de formatos BR/US.
    
    Examples:
        >>> valor = ValorMonetario("1.234,56")
        >>> print(valor)
        R$ 1.234,56
        
        >>> valor1 = ValorMonetario("100.00")
        >>> valor2 = ValorMonetario("100.50")
        >>> valor1.diferenca(valor2)
        Decimal('0.50')
    """
    
    def __init__(self, valor: Union[str, float, int, Decimal]):
        """
        Inicializa um valor monetário.
        
        Args:
            valor: Valor em qualquer formato (str BR/US, float, int, Decimal)
            
        Raises:
            ValueError: Se o valor for inválido
        """
        try:
            if isinstance(valor, str):
                # Remove espaços e prefixos comuns
                valor = valor.strip()
                valor = valor.replace('R$', '').replace('$', '').strip()
                
                # Detecta formato BR (1.234,56) vs US (1,234.56)
                if ',' in valor and '.' in valor:
                    # Tem ambos os separadores
                    ultima_virgula = valor.rfind(',')
                    ultimo_ponto = valor.rfind('.')
                    
                    if ultima_virgula > ultimo_ponto:
                        # Formato BR: 1.234,56
                        valor = valor.replace('.', '').replace(',', '.')
                    else:
                        # Formato US: 1,234.56
                        valor = valor.replace(',', '')
                elif ',' in valor:
                    # Só tem vírgula - assume formato BR
                    valor = valor.replace(',', '.')
                # Só tem ponto ou nenhum separador - já está OK
            
            # Converte para Decimal
            self._valor = Decimal(str(valor))
            
            # Arredonda para 2 casas decimais
            self._valor = self._valor.quantize(
                Decimal('0.01'), 
                rounding=ROUND_HALF_UP
            )
            
        except (InvalidOperation, ValueError) as e:
            raise ValueError(f"Valor inválido: {valor}") from e
    
    @property
    def valor(self) -> Decimal:
        """Retorna o valor como Decimal"""
        return self._valor
    
    def diferenca(self, outro: 'ValorMonetario') -> Decimal:
        """
        Calcula a diferença absoluta entre dois valores.
        
        Args:
            outro: Outro valor monetário
            
        Returns:
            Diferença absoluta
        """
        return abs(self._valor - outro._valor)
    
    def dentro_tolerancia(self, outro: 'ValorMonetario', 
                         tolerancia: Union[Decimal, float, str] = Decimal('1.01')) -> bool:
        """
        Verifica se a diferença está dentro da tolerância.
        
        Args:
            outro: Outro valor monetário
            tolerancia: Valor máximo de diferença permitido
            
        Returns:
            True se diferença <= tolerância
        """
        if not isinstance(tolerancia, Decimal):
            tolerancia = Decimal(str(tolerancia))
        
        return self.diferenca(outro) <= tolerancia
    
    def __str__(self) -> str:
        """Retorna o valor formatado em Real brasileiro"""
        # Converte para string e formata
        valor_str = f"{self._valor:.2f}"
        
        # Separa parte inteira e decimal
        partes = valor_str.split('.')
        parte_inteira = partes[0]
        parte_decimal = partes[1] if len(partes) > 1 else "00"
        
        # Adiciona separador de milhares
        if len(parte_inteira) > 3:
            # Inverte, adiciona pontos, inverte de volta
            parte_inteira_rev = parte_inteira[::-1]
            com_pontos = '.'.join([
                parte_inteira_rev[i:i+3] 
                for i in range(0, len(parte_inteira_rev), 3)
            ])
            parte_inteira = com_pontos[::-1]
        
        return f"R$ {parte_inteira},{parte_decimal}"
    
    def __repr__(self) -> str:
        return f"ValorMonetario('{self._valor}')"
    
    def __eq__(self, outro: 'ValorMonetario') -> bool:
        """Verifica igualdade de valores"""
        if not isinstance(outro, ValorMonetario):
            return False
        return self._valor == outro._valor
    
    def __lt__(self, outro: 'ValorMonetario') -> bool:
        """Verifica se é menor que outro valor"""
        return self._valor < outro._valor
    
    def __le__(self, outro: 'ValorMonetario') -> bool:
        """Verifica se é menor ou igual a outro valor"""
        return self._valor <= outro._valor
    
    def __gt__(self, outro: 'ValorMonetario') -> bool:
        """Verifica se é maior que outro valor"""
        return self._valor > outro._valor
    
    def __ge__(self, outro: 'ValorMonetario') -> bool:
        """Verifica se é maior ou igual a outro valor"""
        return self._valor >= outro._valor
    
    def __add__(self, outro: 'ValorMonetario') -> 'ValorMonetario':
        """Soma dois valores"""
        return ValorMonetario(self._valor + outro._valor)
    
    def __sub__(self, outro: 'ValorMonetario') -> 'ValorMonetario':
        """Subtrai dois valores"""
        return ValorMonetario(self._valor - outro._valor)
    
    def __mul__(self, fator: Union[int, float, Decimal]) -> 'ValorMonetario':
        """Multiplica o valor por um fator"""
        return ValorMonetario(self._valor * Decimal(str(fator)))
    
    def __truediv__(self, divisor: Union[int, float, Decimal]) -> 'ValorMonetario':
        """Divide o valor por um divisor"""
        return ValorMonetario(self._valor / Decimal(str(divisor)))


def converter_para_decimal(valor: Union[str, float, int, Decimal]) -> Decimal:
    """
    Converte um valor para Decimal com 2 casas decimais.
    
    Args:
        valor: Valor em qualquer formato
        
    Returns:
        Valor como Decimal
        
    Examples:
        >>> converter_para_decimal("1.234,56")
        Decimal('1234.56')
        
        >>> converter_para_decimal(1234.56)
        Decimal('1234.56')
    """
    vm = ValorMonetario(valor)
    return vm.valor


def formatar_moeda_br(valor: Union[str, float, int, Decimal]) -> str:
    """
    Formata um valor no padrão monetário brasileiro.
    
    Args:
        valor: Valor em qualquer formato
        
    Returns:
        String formatada (ex: "R$ 1.234,56")
        
    Examples:
        >>> formatar_moeda_br(1234.56)
        'R$ 1.234,56'
        
        >>> formatar_moeda_br("1234.56")
        'R$ 1.234,56'
    """
    vm = ValorMonetario(valor)
    return str(vm)


def valores_iguais(valor1: Union[str, float, Decimal], 
                   valor2: Union[str, float, Decimal],
                   tolerancia: Union[str, float, Decimal] = "1.01") -> bool:
    """
    Verifica se dois valores são iguais dentro de uma tolerância.
    
    Args:
        valor1: Primeiro valor
        valor2: Segundo valor
        tolerancia: Diferença máxima permitida (padrão: R$ 1,01)
        
    Returns:
        True se a diferença for <= tolerância
        
    Examples:
        >>> valores_iguais(100.00, 100.50, 1.00)
        True
        
        >>> valores_iguais(100.00, 105.00, 1.00)
        False
    """
    vm1 = ValorMonetario(valor1)
    vm2 = ValorMonetario(valor2)
    return vm1.dentro_tolerancia(vm2, Decimal(str(tolerancia)))
