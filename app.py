import streamlit as st
import pandas as pd
import plotly.express as px

# Carregar dataset
df = pd.read_csv("datasets/vgsales.csv")

# Limpeza de dados
df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
df = df.dropna(subset=["Year"])
df["Year"] = df["Year"].astype(int)

# Sidebar: filtros
st.sidebar.header("️Filtros")

platforms = sorted(df["Platform"].dropna().unique().tolist())
genres = sorted(df["Genre"].dropna().unique().tolist())
publishers = sorted(df["Publisher"].dropna().unique().tolist())

year_min = int(df["Year"].min())
year_max = int(df["Year"].max())
sales_min = float(df["Global_Sales"].min())
sales_max = float(df["Global_Sales"].max())

sel_platforms = st.sidebar.multiselect("Plataformas", platforms)
sel_genres = st.sidebar.multiselect("Gêneros", genres)
sel_years = st.sidebar.slider("Ano de lançamento", year_min, year_max, (year_min, year_max))
sel_publishers = st.sidebar.multiselect("Empresa responsável pelo lançamento", publishers)
min_sales, max_sales = st.sidebar.slider(
    "Vendas globais (mi)", sales_min, sales_max, (sales_min, sales_max)
)

# Criar DataFrame filtrado
df_filtrado = df.copy()

if sel_platforms:
    df_filtrado = df_filtrado[df_filtrado["Platform"].isin(sel_platforms)]
if sel_genres:
    df_filtrado = df_filtrado[df_filtrado["Genre"].isin(sel_genres)]
df_filtrado = df_filtrado[
    (df_filtrado["Year"] >= sel_years[0]) & (df_filtrado["Year"] <= sel_years[1])
]
if sel_publishers:
    df_filtrado = df_filtrado[df_filtrado["Publisher"].isin(sel_publishers)]
df_filtrado = df_filtrado[
    (df_filtrado["Global_Sales"] >= min_sales) & (df_filtrado["Global_Sales"] <= max_sales)
]

# KPIs no topo + botão de download à direita
st.write("### KPIs do recorte filtrado")
kpi_col1, kpi_col2, kpi_col3, download_col = st.columns([1,1,1,0.5])

total_games = len(df_filtrado)
total_sales = df_filtrado["Global_Sales"].sum() if "Global_Sales" in df_filtrado.columns else 0.0
avg_sales = df_filtrado["Global_Sales"].mean() if "Global_Sales" in df_filtrado.columns else 0.0

kpi_col1.metric("🎯 Jogos (filtrados)", f"{total_games:,}".replace(",", "."))
kpi_col2.metric("🌍 Vendas Globais (mi)", f"{total_sales:,.2f}".replace(",", "."))
kpi_col3.metric("📈 Média de Vendas (mi)", f"{avg_sales:,.2f}".replace(",", "."))

csv_bytes = df_filtrado.to_csv(index=False).encode("utf-8")
download_col.download_button(
    label="⬇️ Baixar CSV filtrado",
    data=csv_bytes,
    file_name="vgsales_filtrado.csv",
    mime="text/csv",
)

# Tabela filtrada
st.subheader("📋 Tabela filtrada")
st.dataframe(
    df_filtrado[["Name","Platform","Year","Genre","Publisher","Global_Sales"]],
    use_container_width=True,
)

# Gráficos Plotly
col1, col2 = st.columns(2)

# Gráfico 1: contagem por gênero
genre_counts = df_filtrado["Genre"].value_counts()
fig1 = px.bar(
    x=genre_counts.index,
    y=genre_counts.values,
    labels={"x":"Gênero","y":"Quantidade"},
    title="Jogos por Gênero",
    color=genre_counts.index,  # cores sólidas por categoria
    color_discrete_sequence=px.colors.qualitative.Pastel,  # tons minimalistas
)
col1.plotly_chart(fig1, use_container_width=True)

# Gráfico 2: vendas globais por plataforma
platform_sales = df_filtrado.groupby("Platform")["Global_Sales"].sum().sort_values(ascending=False)
fig2 = px.bar(
    x=platform_sales.index,
    y=platform_sales.values,
    labels={"x":"Plataforma","y":"Vendas Globais (mi)"},
    title="Vendas Globais por Plataforma",
    color=platform_sales.index,  # cores sólidas por categoria
    color_discrete_sequence=px.colors.qualitative.Set2,  # tons minimalistas
)
col2.plotly_chart(fig2, use_container_width=True)
