import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import ast

st.set_page_config(
    page_title="Global Temperature Explorer",
    page_icon="🌍",
    layout="wide"
)

# ---- Light theme + custom styling ----
st.markdown(
    """
    <style>
    .stApp {
        background-color: #FFFFFF;
    }
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        color: #1a1a1a;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        font-size: 1.15rem;
        color: #777777;
        margin-bottom: 1.5rem;
    }
    .intro-box {
        background-color: #F9F9F9;
        border-left: 4px solid #E4572E;
        padding: 1.2rem 1.5rem;
        border-radius: 6px;
        margin-bottom: 2rem;
        color: #333333;
    }
    .intro-box a {
        color: #2E86AB;
        font-weight: 600;
        text-decoration: none;
    }
    .caption-text {
        color: #999999;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Hero section ----
st.markdown('<div class="hero-title">Comparing Average Monthly Temperatures By City</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="hero-subtitle">Python Project By Giorgi Beridze</div>',
    unsafe_allow_html=True
)

# ---- About / links ----
with st.container():
    st.markdown(
        """
        <div class="intro-box">
        Visit my <a href="https://github.com/beridzeg45" target="_blank">GitHub</a> account for code.
        </div>
        """,
        unsafe_allow_html=True
    )

# ---- Load data ----
@st.cache_data
def load_data():
    data = pd.read_csv("city_temperatues.csv")
    if isinstance(data['loc'].iloc[0], str):
        data['loc'] = data['loc'].apply(ast.literal_eval)
    return data

df = load_data()

months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

PALETTE = ['#E4572E', '#2E86AB', '#5FA55A', '#8E44AD', '#D4A017',
           '#C0392B', '#16A085', '#7F8C8D', '#E67E22', '#2C3E50']

DEFAULT_CITIES = ['Surami (Georgia)', 'Tyre (Lebanon)', 'Wellington (New Zealand)']


def build_temp_chart(city_list, df, colors):
    temps_df = pd.DataFrame()
    for city in city_list:
        row = df[df['City'] == city].iloc[0]
        temps_df[city] = row[months].astype(float)

    plt.rcParams['font.family'] = 'DejaVu Sans'
    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    ax.yaxis.grid(True, color='#DDDDDD', linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)

    use_labels = len(city_list) <= 6

    for city, series in temps_df.items():
        color = colors[city]
        ax.plot(months, series, marker='o', markersize=6, linewidth=2.8,
                 color=color, solid_capstyle='round', zorder=3)

        if use_labels:
            ax.annotate(city.split(' (')[0], xy=(11, series.iloc[-1]), xytext=(8, 0),
                textcoords='offset points', va='center', ha='left',
                fontsize=10.5, fontweight='bold', color=color)

            max_i = series.values.argmax()
            min_i = series.values.argmin()
            ax.annotate(f"{series.iloc[max_i]:.0f}°", xy=(max_i, series.iloc[max_i]),
                        xytext=(0, 9), textcoords='offset points', ha='center',
                        fontsize=8, color=color, fontweight='medium')
            ax.annotate(f"{series.iloc[min_i]:.0f}°", xy=(min_i, series.iloc[min_i]),
                        xytext=(0, -14), textcoords='offset points', ha='center',
                        fontsize=8, color=color, fontweight='medium')

    if not use_labels:
        ax.legend([c.split(' (')[0] for c in temps_df.columns],
                  fontsize=8, frameon=False, loc='upper left', bbox_to_anchor=(1.0, 1.0))

    ax.set_xlim(-0.4, 11.9 if use_labels else 11.3)
    ax.set_xticks(range(12))
    ax.set_xticklabels(months, fontsize=9.5, color='#333333')
    ax.tick_params(axis='y', labelsize=9, colors='#333333')
    ax.set_ylabel('Temperature (°C)', fontsize=10, color='#333333', labelpad=8)

    for spine in ['top', 'right', 'left']:
        ax.spines[spine].set_visible(False)
    ax.spines['bottom'].set_color('#999999')
    ax.spines['bottom'].set_linewidth(0.8)

    fig.suptitle('Average Monthly Temperature', fontsize=14, fontweight='bold',
                 color='#1a1a1a', x=0.1, y=0.97, ha='left')
    ax.set_title(' · '.join(c.split(' (')[0] for c in city_list), fontsize=10,
                  color='#777777', loc='left', pad=10)
    fig.text(0.1, 0.01, 'Data: monthly climate normals', fontsize=7.5, color='#999999')

    plt.subplots_adjust(left=0.1, right=0.84 if use_labels else 0.76, top=0.87, bottom=0.1)
    return fig


def build_map(city_list, df, colors):
    fig = go.Figure()

    for city in city_list:
        row = df[df['City'] == city].iloc[0]
        lon, lat = row['loc']['Lon'], row['loc']['Lat']
        color = colors[city]

        fig.add_trace(go.Scattergeo(
            lon=[lon], lat=[lat],
            mode='markers+text',
            marker=dict(size=13, color=color, line=dict(width=1.8, color='white')),
            text=[city.split(' (')[0]],
            textposition='top right',
            textfont=dict(size=13, color=color, family='DejaVu Sans, Arial'),
            showlegend=False,
        ))

    fig.update_geos(
        projection_type='natural earth',
        showland=True, landcolor='#F2F2F2',
        showocean=True, oceancolor='#EAF3FA',
        showcountries=True, countrycolor='#CFCFCF',
        showcoastlines=True, coastlinecolor='#B0B0B0', coastlinewidth=0.8,
        lataxis_range=[-60, 90],
        showframe=False,
        bgcolor='white',
    )
    fig.update_layout(
        title=dict(
            text='City Locations',
            font=dict(size=20, color='#1a1a1a', family='DejaVu Sans, Arial', weight='bold'),
            x=0.02, y=0.95
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        margin=dict(l=10, r=10, t=60, b=30),
        height=560,
        annotations=[
            dict(
                text="Basemap: Natural Earth",
                showarrow=False,
                xref="paper", yref="paper",
                x=0.02, y=0.0,
                font=dict(size=10.5, color='#999999')
            )
        ]
    )
    return fig


# ---- Heatmap (always visible, centered) ----
hcol1, hcol2, hcol3 = st.columns([1, 2, 1])
with hcol2:
    st.image("temperature_land_only.png", use_container_width=True)

# ---- Search bar (centered, below heatmap) ----
search_col1, search_col2, search_col3 = st.columns([1, 2, 1])
with search_col2:
    selected_cities = st.multiselect(
        label="Search and select cities",
        options=sorted(df['City'].unique().tolist()),
        default=DEFAULT_CITIES,
        placeholder="Type a city name..."
    )

colors = {city: PALETTE[i % len(PALETTE)] for i, city in enumerate(selected_cities)}

# ---- Charts below the search bar ----
if selected_cities:
    col1, col2 = st.columns(2)
    with col1:
        fig_line = build_temp_chart(selected_cities, df, colors)
        st.pyplot(fig_line, use_container_width=True)
    with col2:
        fig_map = build_map(selected_cities, df, colors)
        st.plotly_chart(fig_map, use_container_width=True)
