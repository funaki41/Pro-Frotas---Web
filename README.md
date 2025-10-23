# 🔍 Sistema de Validação de NFe's

Sistema web moderno para confrontamento de Notas Fiscais Eletrônicas (NFe) com planilhas de abastecimento.

## 📋 Visão Geral

Este sistema automatiza o processo de validação de NFe's comparando:
- **XMLs da Receita Federal** (arquivos fornecidos pelos postos)
- **Planilha de Transações** (relatório do sistema de gestão de frotas)

E gera um **relatório completo** classificando as notas em:
- ✅ **Idênticas**: Match perfeito (valores, CNPJs e prazo OK)
- ⚠️ **Divergentes**: Match com diferença de valor
- 🔗 **Divergentes Agrupadas**: Grupos de notas com soma divergente
- ❌ **Não Encontradas**: Presentes na planilha mas sem XML
- 🕐 **Desconsideradas**: Postergadas (acima de 60 dias)

---

## 🚀 Início Rápido

### Pré-requisitos
```bash
Python 3.11 ou superior
pip (gerenciador de pacotes Python)
```

### Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/validador-nfe.git
cd validador-nfe
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Execute a aplicação**
```bash
streamlit run app.py
```

5. **Acesse no navegador**
```
http://localhost:8501
```

---

## 📁 Estrutura do Projeto

```
validador-nfe/
│
├── app.py                      # Aplicação principal Streamlit
├── requirements.txt            # Dependências
├── config.yaml                 # Configurações
├── README.md                   # Este arquivo
│
├── core/                       # Lógica de negócio
│   ├── __init__.py
│   ├── xml_parser.py          # Parser de XMLs da NFe
│   ├── excel_parser.py        # Parser da planilha
│   ├── matching_engine.py     # Algoritmo de confrontamento
│   └── report_generator.py    # Geração de relatórios
│
├── models/                     # Modelos de dados
│   ├── __init__.py
│   └── models.py              # Dataclasses (NFe, Transacao, etc)
│
├── utils/                      # Utilitários
│   ├── __init__.py
│   ├── valor_monetario.py     # Manipulação de valores
│   ├── cnpj.py                # Validação de CNPJ
│   ├── date_utils.py          # Manipulação de datas
│   └── logger.py              # Sistema de logging
│
├── ui/                         # Componentes da interface
│   ├── __init__.py
│   ├── upload.py              # Tela de upload
│   ├── dashboard.py           # Dashboard de processamento
│   └── relatorio.py           # Visualização de relatórios
│
├── database/                   # Persistência (opcional)
│   ├── __init__.py
│   ├── db_manager.py
│   └── schemas.py
│
└── tests/                      # Testes automatizados
    ├── __init__.py
    ├── test_matching.py
    ├── test_parsers.py
    └── fixtures/              # Dados de teste
```

---

## 🎯 Funcionalidades

### ✅ Implementado
- [x] Modelos de dados robustos (dataclasses)
- [x] Manipulação segura de valores monetários (Decimal)
- [x] Sistema de configuração centralizado
- [x] Cálculo de dias postergados
- [x] Validações de entrada

### 🔄 Em Desenvolvimento
- [ ] Parser de XMLs (NFe)
- [ ] Parser de planilhas Excel
- [ ] Algoritmo de confrontamento
- [ ] Interface Streamlit
- [ ] Geração de relatórios Excel
- [ ] Sistema de logging estruturado

### 📅 Planejado
- [ ] Dashboard analytics
- [ ] Histórico de processamentos
- [ ] Exportação PDF
- [ ] API REST (opcional)
- [ ] Testes automatizados completos

---

## 💡 Como Usar

### 1. Upload de Arquivos

Na tela principal, faça o upload de:
1. **XMLs da Receita** (arquivo .zip contendo os XMLs)
2. **Planilha de Transações** (arquivo .xlsx)

### 2. Configuração

Defina os parâmetros:
- **Data de Fechamento**: Data final do período
- **Período Máximo**: Dias limite para postergação (padrão: 60)
- **Tolerância de Valor**: Diferença aceita em reais (padrão: R$ 1,01)

### 3. Processamento

Clique em **"Processar"** e acompanhe:
- Progresso em tempo real
- Estatísticas instantâneas
- Log detalhado de cada operação

### 4. Resultados

Visualize o relatório com:
- Resumo estatístico
- Tabelas interativas por categoria
- Download do relatório Excel completo
- Arquivo de auditoria (JSON)

---

## 🔧 Configuração Avançada

### config.yaml

```yaml
# Configurações do Sistema

# Período de validação
periodo:
  maximo_dias: 60  # Dias limite para postergação
  
# Validação de valores
validacao:
  tolerancia_valor: 1.01  # Tolerância em reais
  usar_decimal: true      # Usar Decimal (recomendado)

# Empresa
empresa:
  cnpj_destinatario: "12.345.678/0001-90"  # CNPJ padrão

# Colunas da planilha
planilha:
  mapeamento:
    numero_nfe: "AS"          # Coluna do número da NFe
    data_abastecimento: "D"   # Coluna da data
    cnpj_posto: "H"           # Coluna do CNPJ emitente
    cnpj_empresa: "J"         # Coluna do CNPJ destinatário
    valor_total: "AN"         # Coluna do valor
    postergado: "AR"          # Coluna de postergado
    dias_atraso: "G"          # Coluna de dias em atraso

# Logging
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  formato: "json"  # json ou text
  arquivo: "logs/validador.log"
```

---

## 🧪 Testes

### Executar todos os testes
```bash
pytest
```

### Executar com cobertura
```bash
pytest --cov=. --cov-report=html
```

### Executar testes específicos
```bash
pytest tests/test_matching.py
pytest tests/test_parsers.py -v
```

---

## 📊 Exemplo de Uso (Python)

```python
from models.models import Configuracao
from core.matching_engine import MatchingEngine
from core.xml_parser import parse_xmls_from_zip
from core.excel_parser import parse_transacoes_from_excel
from datetime import date

# 1. Configurar
config = Configuracao(
    data_fechamento=date(2025, 9, 30),
    periodo_maximo_dias=60,
    tolerancia_valor="1.01"
)

# 2. Carregar dados
nfes = parse_xmls_from_zip("DFe_280_0110_a_1010.zip")
transacoes = parse_transacoes_from_excel("Relatorio_NFes.xlsx")

# 3. Processar
engine = MatchingEngine(config)
relatorio = engine.confrontar(nfes, transacoes)

# 4. Ver resultados
print(relatorio.resumo())
# {
#   'total_processado': 6791,
#   'identicas': {'quantidade': 4386, 'percentual': 64.6, ...},
#   'divergentes': {'quantidade': 71, 'percentual': 1.0, ...},
#   ...
# }

# 5. Exportar
from core.report_generator import exportar_relatorio_excel
exportar_relatorio_excel(relatorio, "Relatorio_Final.xlsx")
```

---

## 🐛 Troubleshooting

### Problema: Erro ao ler planilha Excel
**Solução:** Verifique se:
- O arquivo está no formato .xlsx (não .xls)
- As colunas estão mapeadas corretamente no config.yaml
- Não há células mescladas no cabeçalho

### Problema: XMLs não são reconhecidos
**Solução:** Certifique-se de que:
- Os arquivos são XMLs válidos da NFe
- Estão dentro de um arquivo .zip
- Não estão corrompidos

### Problema: Valores divergentes inesperados
**Solução:** Verifique:
- A tolerância configurada (padrão: R$ 1,01)
- O formato dos valores na planilha
- Se há arredondamentos diferentes

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona NovaFuncionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

### Padrões de Código

- Usar **Black** para formatação
- Usar **type hints** em todas as funções
- Escrever **docstrings** (formato Google)
- Adicionar **testes** para novas funcionalidades
- Seguir **PEP 8**

---

## 📝 Changelog

### v0.1.0 (Em Desenvolvimento)
- ✅ Estrutura base do projeto
- ✅ Modelos de dados
- ✅ Utilitários de valor monetário
- ✅ Sistema de configuração
- 🔄 Parser de XMLs
- 🔄 Interface Streamlit

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👥 Autores

- **Desenvolvedor Principal** - [Seu Nome](https://github.com/seu-usuario)

---

## 🙏 Agradecimentos

- Equipe de gestão de frotas pelo feedback
- Comunidade Streamlit pelos exemplos
- Desenvolvedores das bibliotecas utilizadas

---

## 📞 Suporte

Para suporte, envie um email para: suporte@exemplo.com

Ou abra uma issue no GitHub: https://github.com/seu-usuario/validador-nfe/issues

---

**Desenvolvido com ❤️ para facilitar a validação de NFe's**
