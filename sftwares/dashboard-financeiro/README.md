# FinDash - Dashboard Financeiro Profissional

![Dashboard Logo](https://via.placeholder.com/800x200?text=FinDash+Dashboard+Financeiro)

## 📊 Visão Geral

FinDash é um sistema web desenvolvido com Python e Flask que fornece uma solução completa para análise de dados financeiros. Este dashboard profissional permite visualizar e analisar arquivos CSV contendo dados de pagamentos, oferecendo gráficos interativos, estatísticas detalhadas e insights valiosos para tomada de decisões.

### ✨ Características Principais

- **Interface Moderna**: Design responsivo e intuitivo com tema claro/escuro
- **Análise de Dados Robusta**: Processamento de CSVs com dados financeiros
- **Visualizações Interativas**: Gráficos dinâmicos usando Plotly
- **Estatísticas Detalhadas**: Métricas importantes para análise financeira
- **Exportação de Dados**: Possibilidade de exportar análises para Excel
- **Dashboard Personalizável**: Controles para ajustar visualizações

## 📋 Requisitos do Sistema

- Python 3.9 ou superior
- Navegador web moderno
- Pacotes Python listados em `requirements.txt`

## 🚀 Instalação

1. Clone o repositório:
   ```bash
   git clone https://github.com/ltd/daahboard-financeiro.git
   cd daahboard-financeiro
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   
   # No Windows
   venv\Scripts\activate
   
   # No macOS/Linux
   source venv/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Execute a aplicação:
   ```bash
   python app.py
   ```

5. Acesse o dashboard no navegador:
   ```
   http://localhost:5000
   ```

## 📊 Estrutura do Projeto

```
findash/
├── app.py                 # Aplicação principal Flask
├── templates/             # Templates HTML
│   ├── base.html          # Template base
│   ├── index.html         # Página inicial
│   ├── upload.html        # Página de upload
│   └── dashboard.html     # Dashboard principal
├── static/                # Arquivos estáticos (CSS, JS, imagens)
│   └── img/
│       └── logo.png       # Logo do FinDash
├── uploads/               # Diretório para arquivos carregados
├── requirements.txt       # Dependências do projeto
└── README.md              # Documentação
```

## 📝 Formato dos Dados

O sistema está configurado para processar arquivos CSV com o seguinte formato:

```
"Entidade";"Credor";"Tipo Pessoa";"Numero Ordem de Pagamento";"Empenho";"Vinculo";"Data";"Valor Pago";"Numero";"Ano"
```

### Exemplo:

```
"Prefeitura Municipal";"Fornecedor A";"Jurídica";"12345";"67890";"Contrato 123";"2025-01-15";"10000,00";"001";"2025"
```

## 🔧 Configuração e Personalização

### Configuração do Aplicativo

Edite o arquivo `app.py` para personalizar configurações como:

- Porta do servidor (`app.run(port=5000)`)
- Tamanho máximo de upload (`app.config['MAX_CONTENT_LENGTH']`)
- Chave secreta (`app.secret_key`)

### Personalização Visual

- **Tema**: O dashboard suporta tema claro e escuro, alterável na interface
- **Cores dos Gráficos**: Diversas escalas de cores disponíveis para visualizações
- **Altura dos Gráficos**: Ajustável na interface do usuário

## 📊 Visualizações Disponíveis

O dashboard oferece as seguintes visualizações:

1. **Pagamentos por Entidade**: Gráfico de barras mostrando o total de pagamentos por entidade
2. **Evolução de Pagamentos**: Gráfico de linha mostrando a evolução dos pagamentos ao longo do tempo
3. **Distribuição por Tipo de Pessoa**: Gráfico de pizza mostrando a distribuição por tipo de pessoa (física/jurídica)
4. **Top 10 Credores**: Gráfico de barras mostrando os 10 maiores credores
5. **Heatmap de Pagamentos**: Mapa de calor mostrando pagamentos por mês e ano
6. **Distribuição por Vínculo**: Boxplot mostrando a distribuição de valores por vínculo

## 📱 Responsividade

O dashboard é totalmente responsivo e se adapta a diferentes tamanhos de tela:

- **Desktop**: Experiência completa com todos os recursos
- **Tablet**: Layout ajustado para telas médias
- **Mobile**: Interface simplificada para melhor experiência em dispositivos móveis

## 🔒 Segurança

- O sistema não armazena dados financeiros permanentemente
- Arquivos carregados são armazenados temporariamente na pasta `uploads/`
- Não há conexão com banco de dados externo

## 🛠️ Desenvolvimento

### Tecnologias Utilizadas

- **Backend**: Python, Flask
- **Processamento de Dados**: Pandas, NumPy
- **Visualização**: Plotly
- **Frontend**: HTML5, CSS3, JavaScript
- **Design**: Bootstrap, FontAwesome

### Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Faça push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo LICENSE para detalhes.

## 📞 Suporte

Para suporte ou dúvidas, abra uma issue no repositório ou entre em contato pelo email: suporte@findash.com.br

---

Desenvolvido com ❤️ por ltd | © 2025