# Sistema de Dashboard Financeiro com Flask
# Autor: Claude
# Data: 23/04/2025

import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
from werkzeug.utils import secure_filename
from datetime import datetime
import locale
import io
import uuid
import calendar

# Configurações da aplicação
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'uploads')
ALLOWED_EXTENSIONS = {'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Inicialização da aplicação Flask
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB max upload
app.secret_key = 'finance_dashboard_secret_key'

# Removida a inicialização do Bootstrap que estava causando problemas

# Configuração da localização para formatação de moeda
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')  # Windows
    except:
        locale.setlocale(locale.LC_ALL, '')  # Fallback para o locale padrão

# Função para verificar se a extensão do arquivo é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Função para processar o arquivo CSV e retornar um DataFrame pandas
def process_csv_file(file_path, delimiter=';'):
    try:
        df = pd.read_csv(file_path, delimiter=delimiter, encoding='utf-8')
        # Renomear colunas se necessário para garantir consistência
        column_mapping = {
            'Entidade': 'Entidade',
            'Credor': 'Credor',
            'Tipo Pessoa': 'Tipo_Pessoa',
            'Numero Ordem de Pagamento': 'Numero_OP',
            'Empenho': 'Empenho',
            'Vinculo': 'Vinculo',
            'Data': 'Data',
            'Valor Pago': 'Valor_Pago',
            'Numero': 'Numero',
            'Ano': 'Ano'
        }
        
        # Renomear colunas para padrão interno
        df = df.rename(columns=column_mapping)
        
        # Converter coluna de data para datetime
        df['Data'] = pd.to_datetime(df['Data'], errors='coerce')
        
        # Limpar e converter a coluna Valor_Pago para float
        df['Valor_Pago'] = df['Valor_Pago'].astype(str).str.replace('.', '')
        df['Valor_Pago'] = df['Valor_Pago'].str.replace(',', '.').astype(float)
        
        # Converter colunas numéricas
        numeric_columns = ['Numero_OP', 'Empenho', 'Numero', 'Ano']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    except Exception as e:
        print(f"Erro ao processar o arquivo CSV: {e}")
        return None

# Função para criar visualizações
def create_visualizations(df):
    visualizations = {}
    
    # 1. Gráfico de pagamentos por entidade
    pagamentos_entidade = df.groupby('Entidade')['Valor_Pago'].sum().reset_index()
    pagamentos_entidade = pagamentos_entidade.sort_values('Valor_Pago', ascending=False)
    
    fig_entidade = px.bar(
        pagamentos_entidade, 
        x='Entidade', 
        y='Valor_Pago',
        title='Total de Pagamentos por Entidade',
        color='Valor_Pago',
        color_continuous_scale='Viridis',
        labels={'Valor_Pago': 'Valor Total Pago (R$)', 'Entidade': 'Entidade'},
        height=500
    )
    fig_entidade.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(50, 50, 50, 0.8)',
        paper_bgcolor='rgba(30, 30, 30, 0.8)',
        font=dict(color='white'),
        xaxis={'categoryorder':'total descending'}
    )
    visualizations['pagamentos_entidade'] = fig_entidade.to_json()
    
    # 2. Gráfico de linha de pagamentos ao longo do tempo
    try:
        df_time = df.copy()
        df_time['Mes'] = df_time['Data'].dt.month
        df_time['Ano_Data'] = df_time['Data'].dt.year
        pagamentos_tempo = df_time.groupby(['Ano_Data', 'Mes'])['Valor_Pago'].sum().reset_index()

        # Criar a coluna de data completa - maneira corrigida
        pagamentos_tempo['Data_Completa'] = pagamentos_tempo.apply(
            lambda row: f"{int(row['Ano_Data'])}-{int(row['Mes']):02d}-01", axis=1
        )

        pagamentos_tempo['Data_Completa'] = pd.to_datetime(pagamentos_tempo['Data_Completa'])
        pagamentos_tempo = pagamentos_tempo.sort_values('Data_Completa')
        
        fig_tempo = px.line(
            pagamentos_tempo, 
            x='Data_Completa', 
            y='Valor_Pago',
            title='Evolução de Pagamentos ao Longo do Tempo',
            labels={'Valor_Pago': 'Valor Total Pago (R$)', 'Data_Completa': 'Data'},
            height=500,
            markers=True
        )
        fig_tempo.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(50, 50, 50, 0.8)',
            paper_bgcolor='rgba(30, 30, 30, 0.8)',
            font=dict(color='white')
        )
        visualizations['pagamentos_tempo'] = fig_tempo.to_json()
    except Exception as e:
        print(f"Erro ao criar gráfico de evolução temporal: {e}")
        # Criar um gráfico vazio como fallback
        fig_tempo = go.Figure()
        fig_tempo.update_layout(
            title="Evolução de Pagamentos ao Longo do Tempo (Erro ao processar)",
            height=500,
            template='plotly_dark',
            plot_bgcolor='rgba(50, 50, 50, 0.8)',
            paper_bgcolor='rgba(30, 30, 30, 0.8)',
            font=dict(color='white')
        )
        fig_tempo.add_annotation(
            text="Erro ao processar os dados temporais.",
            showarrow=False,
            font=dict(size=14, color="white")
        )
        visualizations['pagamentos_tempo'] = fig_tempo.to_json()
    
    # 3. Gráfico de pizza para distribuição por tipo de pessoa
    try:
        pagamentos_tipo = df.groupby('Tipo_Pessoa')['Valor_Pago'].sum().reset_index()
        
        fig_tipo = px.pie(
            pagamentos_tipo, 
            values='Valor_Pago', 
            names='Tipo_Pessoa',
            title='Distribuição de Pagamentos por Tipo de Pessoa',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Viridis,
            height=500
        )
        fig_tipo.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(50, 50, 50, 0.8)',
            paper_bgcolor='rgba(30, 30, 30, 0.8)',
            font=dict(color='white')
        )
        visualizations['pagamentos_tipo'] = fig_tipo.to_json()
    except Exception as e:
        print(f"Erro ao criar gráfico de tipo de pessoa: {e}")
        # Criar um gráfico vazio como fallback
        fig_tipo = go.Figure()
        fig_tipo.update_layout(
            title="Distribuição por Tipo de Pessoa (Erro ao processar)",
            height=500,
            template='plotly_dark',
            plot_bgcolor='rgba(50, 50, 50, 0.8)',
            paper_bgcolor='rgba(30, 30, 30, 0.8)',
            font=dict(color='white')
        )
        visualizations['pagamentos_tipo'] = fig_tipo.to_json()
    
    # 4. Gráfico de top credores
    try:
        top_credores = df.groupby('Credor')['Valor_Pago'].sum().reset_index()
        top_credores = top_credores.sort_values('Valor_Pago', ascending=False).head(10)
        
        fig_credores = px.bar(
            top_credores, 
            x='Credor', 
            y='Valor_Pago',
            title='Top 10 Credores por Valor Total',
            color='Valor_Pago',
            color_continuous_scale='Viridis',
            labels={'Valor_Pago': 'Valor Total Pago (R$)', 'Credor': 'Credor'},
            height=500
        )
        fig_credores.update_layout(
            template='plotly_dark',
            plot_bgcolor='rgba(50, 50, 50, 0.8)',
            paper_bgcolor='rgba(30, 30, 30, 0.8)',
            font=dict(color='white'),
            xaxis={'categoryorder':'total descending'}
        )
        visualizations['top_credores'] = fig_credores.to_json()
    except Exception as e:
        print(f"Erro ao criar gráfico de top credores: {e}")
        # Criar um gráfico vazio como fallback
        fig_credores = go.Figure()
        fig_credores.update_layout(
            title="Top 10 Credores (Erro ao processar)",
            height=500,
            template='plotly_dark',
            plot_bgcolor='rgba(50, 50, 50, 0.8)',
            paper_bgcolor='rgba(30, 30, 30, 0.8)',
            font=dict(color='white')
        )
        visualizations['top_credores'] = fig_credores.to_json()
    
    # 5. Heatmap de pagamentos por mês e ano
    try:
        if not df_time.empty and 'Mes' in df_time.columns and 'Ano_Data' in df_time.columns:
            # Criar a tabela pivot com segurança
            pivot_data = df_time.pivot_table(
                index='Mes', 
                columns='Ano_Data', 
                values='Valor_Pago', 
                aggfunc='sum'
            ).fillna(0)
            
            # Adicionar nomes dos meses
            month_names = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
                5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
                9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            new_index = []
            for idx in pivot_data.index:
                mes_num = int(idx)
                if mes_num in month_names:
                    new_index.append(month_names[mes_num])
                else:
                    new_index.append(str(mes_num))
            
            pivot_data.index = new_index
            
            fig_heatmap = px.imshow(
                pivot_data,
                labels=dict(x="Ano", y="Mês", color="Valor Pago (R$)"),
                title="Heatmap de Pagamentos por Mês e Ano",
                color_continuous_scale='Viridis',
                height=500
            )
            fig_heatmap.update_layout(
                template='plotly_dark',
                plot_bgcolor='rgba(50, 50, 50, 0.8)',
                paper_bgcolor='rgba(30, 30, 30, 0.8)',
                font=dict(color='white')
            )
            visualizations['heatmap_pagamentos'] = fig_heatmap.to_json()
    except Exception as e:
        print(f"Erro ao criar heatmap: {e}")
        # Criar um gráfico vazio como fallback
        fig_heatmap = go.Figure()
        fig_heatmap.update_layout(
            title="Heatmap de Pagamentos (Erro ao processar)",
            height=500,
            template='plotly_dark',
            plot_bgcolor='rgba(50, 50, 50, 0.8)',
            paper_bgcolor='rgba(30, 30, 30, 0.8)',
            font=dict(color='white')
        )
        visualizations['heatmap_pagamentos'] = fig_heatmap.to_json()
    
    # 6. Boxplot de valores pagos por vínculo
    try:
        if 'Vinculo' in df.columns:
            fig_boxplot = px.box(
                df, 
                x='Vinculo', 
                y='Valor_Pago',
                title='Distribuição de Valores por Vínculo',
                color='Vinculo',
                labels={'Valor_Pago': 'Valor Pago (R$)', 'Vinculo': 'Vínculo'},
                height=500
            )
            fig_boxplot.update_layout(
                template='plotly_dark',
                plot_bgcolor='rgba(50, 50, 50, 0.8)',
                paper_bgcolor='rgba(30, 30, 30, 0.8)',
                font=dict(color='white')
            )
            visualizations['boxplot_vinculos'] = fig_boxplot.to_json()
    except Exception as e:
        print(f"Erro ao criar boxplot: {e}")
        # Criar um gráfico vazio como fallback
        fig_boxplot = go.Figure()
        fig_boxplot.update_layout(
            title="Distribuição por Vínculo (Erro ao processar)",
            height=500,
            template='plotly_dark',
            plot_bgcolor='rgba(50, 50, 50, 0.8)',
            paper_bgcolor='rgba(30, 30, 30, 0.8)',
            font=dict(color='white')
        )
        visualizations['boxplot_vinculos'] = fig_boxplot.to_json()
    
    return visualizations
    
# Função para gerar estatísticas descritivas dos dados
def generate_statistics(df):
    stats = {}
    
    # Total de pagamentos
    try:
        stats['total_pagamentos'] = locale.currency(df['Valor_Pago'].sum(), grouping=True)
    except:
        stats['total_pagamentos'] = f"R$ {df['Valor_Pago'].sum():,.2f}"
    
    # Valor médio de pagamentos
    try:
        stats['media_pagamentos'] = locale.currency(df['Valor_Pago'].mean(), grouping=True)
    except:
        stats['media_pagamentos'] = f"R$ {df['Valor_Pago'].mean():,.2f}"
    
    # Maior pagamento
    try:
        stats['maior_pagamento'] = locale.currency(df['Valor_Pago'].max(), grouping=True)
    except:
        stats['maior_pagamento'] = f"R$ {df['Valor_Pago'].max():,.2f}"
    
    # Menor pagamento (positivo)
    pagamentos_positivos = df[df['Valor_Pago'] > 0]['Valor_Pago']
    if not pagamentos_positivos.empty:
        try:
            stats['menor_pagamento'] = locale.currency(pagamentos_positivos.min(), grouping=True)
        except:
            stats['menor_pagamento'] = f"R$ {pagamentos_positivos.min():,.2f}"
    else:
        stats['menor_pagamento'] = "N/A"
    
    # Número total de transações
    stats['num_transacoes'] = len(df)
    
    # Número de entidades únicas
    stats['num_entidades'] = df['Entidade'].nunique()
    
    # Número de credores únicos
    stats['num_credores'] = df['Credor'].nunique()
    
    return stats

# Rotas da aplicação
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Verificar se há arquivo na requisição
        if 'file' not in request.files:
            flash('Nenhum arquivo encontrado', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Se o usuário não selecionar um arquivo
        if file.filename == '':
            flash('Nenhum arquivo selecionado', 'error')
            return redirect(request.url)
        
        # Se o arquivo tem uma extensão permitida
        if file and allowed_file(file.filename):
            # Gerar um nome de arquivo único
            unique_filename = str(uuid.uuid4()) + '_' + secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(file_path)
            
            # Processar o arquivo
            delimiter = request.form.get('delimiter', ';')
            df = process_csv_file(file_path, delimiter)
            
            if df is not None:
                # Salvar o caminho do arquivo na sessão
                session['file_path'] = file_path
                session['data_loaded'] = True
                
                # Redirecionar para a página do dashboard
                return redirect(url_for('dashboard'))
            else:
                flash('Erro ao processar o arquivo. Verifique se o formato está correto.', 'error')
                return redirect(request.url)
        else:
            flash('Tipo de arquivo não permitido. Por favor, faça upload de um arquivo CSV.', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/dashboard')
def dashboard():
    if 'data_loaded' not in session or not session['data_loaded']:
        flash('Nenhum dado carregado. Por favor, faça upload de um arquivo CSV primeiro.', 'warning')
        return redirect(url_for('upload_file'))
    
    file_path = session['file_path']
    df = process_csv_file(file_path)
    
    if df is None:
        flash('Erro ao processar o arquivo. Tente novamente.', 'error')
        return redirect(url_for('upload_file'))
    
    # Gerar visualizações e estatísticas
    try:
        visualizations = create_visualizations(df)
        # Converter visualizações para JSON para evitar problemas de serialização
        import json
        visualizations_json = json.dumps(visualizations)
    except Exception as e:
        print(f"Erro ao criar visualizações: {e}")
        visualizations_json = json.dumps({})  # JSON vazio em caso de erro
    
    # Gerar estatísticas
    try:
        stats = generate_statistics(df)
    except Exception as e:
        print(f"Erro ao gerar estatísticas: {e}")
        stats = {
            'total_pagamentos': 'Erro',
            'media_pagamentos': 'Erro',
            'maior_pagamento': 'Erro',
            'menor_pagamento': 'Erro',
            'num_transacoes': 0,
            'num_entidades': 0,
            'num_credores': 0
        }
    
    return render_template(
        'dashboard.html', 
        visualizations=visualizations_json, 
        stats=stats
    )
    
@app.route('/exportar-dados')
def exportar_dados():
    if 'file_path' not in session:
        flash('Nenhum dado disponível para exportação.', 'error')
        return redirect(url_for('index'))
    
    file_path = session['file_path']
    df = process_csv_file(file_path)
    
    if df is None:
        flash('Erro ao processar o arquivo para exportação.', 'error')
        return redirect(url_for('dashboard'))
    
    # Preparar o arquivo Excel para download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Dados', index=False)
        
        # Acessar a planilha do Excel
        workbook = writer.book
        worksheet = writer.sheets['Dados']
        
        # Adicionar formatação para valores monetários
        money_format = workbook.add_format({'num_format': 'R$ #,##0.00'})
        
        # Aplicar formatação à coluna de valores pagos
        valor_col_idx = df.columns.get_loc('Valor_Pago') + 1  # +1 porque o Excel começa em 1, não 0
        worksheet.set_column(valor_col_idx, valor_col_idx, 18, money_format)
        
        # Ajustar largura das colunas automaticamente
        for i, col in enumerate(df.columns):
            column_width = max(len(col) + 2, df[col].astype(str).map(len).max() + 2)
            worksheet.set_column(i, i, column_width)
    
    output.seek(0)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return send_file(
        output,
        as_attachment=True,
        download_name=f'analise_financeira_{timestamp}.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@app.route('/api/data')
def get_data():
    if 'file_path' not in session:
        return jsonify({'error': 'Nenhum dado carregado'}), 400
    
    file_path = session['file_path']
    df = process_csv_file(file_path)
    
    if df is None:
        return jsonify({'error': 'Erro ao processar o arquivo'}), 400
    
    # Converter para json com manipulação de formato de data
    df_json = df.to_dict(orient='records')
    return jsonify(df_json)

# Executar a aplicação se este arquivo for executado diretamente
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)