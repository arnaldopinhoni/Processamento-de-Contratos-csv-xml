
import streamlit as st
import pandas as pd
import re
from unidecode import unidecode

st.set_page_config(page_title="Validador de Layout 2025", layout="wide")
st.title("📥 Validador de Arquivo CSV ou XML — Versão 2025")

colunas_esperadas = [
    'TIPO', 'NOME', 'ENDERECO', 'COMPLEMENTO', 'BAIRRO', 'CEP', 'CIDADE', 'UF',
    'FONE_RESIDENCIA', 'FONE_COMERCIAL', 'PERTO_DE', 'ENTRE_RUAS', 'DATA_NASCIMENTO',
    'SEXO', 'ESTADO_CIVIL', 'CPF', 'RG', 'CODIGOTIT', 'CODIGODEP', 'ATENDIMENTO',
    'ACAO', 'DATA BASE'
]

valores_validos = {
    'TIPO': ['1', '2'],
    'SEXO': ['MASCULINO', 'FEMININO', 'M', 'F', 'm', 'f'],
    'ESTADO_CIVIL': ['CASADO', 'SOLTEIRO', 'VIUVO', 'DIVORCIADO', 'COMPANHEIRO', 'OUTROS'],
    'ATENDIMENTO': ['0', '1'],
    'ACAO': ['1', '2', '3']
}

regex_validos = {
    'CEP': r'^\d{5}-\d{3}$',
    'CPF': r'^\d{3}\.\d{3}\.\d{3}-\d{2}$',
    'DATA': r'^\d{2}/\d{2}/\d{4}$',
    'TELEFONE': r'^\(\d{2,3}\)\d{4,5}-\d{4}$'
}

def validar_conteudo(df):
    erros = []
    for i, row in df.iterrows():
        for col in df.columns:
            valor = str(row[col]).strip()

            if any(c in valor for c in ['Ç', 'ç', "'", "’", "`", "´"]):
                erros.append(f"Linha {i+2} - {col}: contém caractere proibido (Ç, apóstrofo, etc.)")

            if unidecode(valor) != valor:
                erros.append(f"Linha {i+2} - {col}: contém acento ({valor})")

            if col in valores_validos and valor.upper() not in [v.upper() for v in valores_validos[col]]:
                erros.append(f"Linha {i+2} - {col}: valor inválido ({valor})")

            if col == 'CPF' and not re.fullmatch(regex_validos['CPF'], valor):
                erros.append(f"Linha {i+2} - CPF: formato inválido ({valor})")
            if col in ['DATA_NASCIMENTO', 'DATA BASE'] and not re.fullmatch(regex_validos['DATA'], valor):
                erros.append(f"Linha {i+2} - {col}: data inválida ({valor})")
            if col in ['FONE_RESIDENCIA', 'FONE_COMERCIAL'] and valor:
                if not re.fullmatch(regex_validos['TELEFONE'], valor):
                    erros.append(f"Linha {i+2} - {col}: telefone inválido ({valor})")
            if col == 'CEP' and valor:
                if not re.fullmatch(regex_validos['CEP'], valor):
                    erros.append(f"Linha {i+2} - CEP: formato inválido ({valor})")
    return erros

def validar_colunas(df):
    if list(df.columns) != colunas_esperadas:
        return ["❌ As colunas do arquivo não estão na ordem ou formato esperado."]
    return []

uploaded_file = st.file_uploader("Envie um arquivo CSV ou XML para validação", type=["csv", "xml"])

if uploaded_file:
    file_name = uploaded_file.name.lower()
    df = None

    if file_name.endswith('.xml'):
        try:
            df = pd.read_xml(uploaded_file)
        except Exception as e:
            st.error(f"❌ Erro ao ler o arquivo XML: {e}")
            st.stop()
    else:
        possiveis_separadores = [';', ',', '\t', '|']
        for sep in possiveis_separadores:
            for enc in ['utf-8', 'latin1']:
                try:
                    df = pd.read_csv(uploaded_file, sep=sep, encoding=enc)
                    if df.empty:
                        continue
                    if list(df.columns) == colunas_esperadas:
                        break
                except:
                    continue
            if df is not None and not df.empty and list(df.columns) == colunas_esperadas:
                break

    if df is None or df.empty:
        st.error("❌ Não foi possível ler o arquivo. Verifique o conteúdo e o formato.")
        st.stop()

    st.subheader("📊 Pré-visualização dos dados:")
    st.dataframe(df.head())

    erros_colunas = validar_colunas(df)
    erros_conteudo = validar_conteudo(df)

    if not erros_colunas and not erros_conteudo:
        st.success("✅ Layout e conteúdo válidos!")
    else:
        st.error("⚠️ Foram encontrados os seguintes erros:")
        for erro in erros_colunas + erros_conteudo:
            st.write("-", erro)
