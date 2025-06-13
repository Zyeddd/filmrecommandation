import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import numpy as np
import requests
from sklearn.neighbors import NearestNeighbors
from sklearn.preprocessing import OneHotEncoder
from st_clickable_images import clickable_images
from st_on_hover_tabs import on_hover_tabs

# Configuration de la page
st.set_page_config(page_title="WMDb", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")

# Constantes TMDb
API_KEY = '1efc9bac137c809078181e5c2c13cafc'
BASE_URL = 'https://api.themoviedb.org/3'
IMAGE_BASE_URL = 'https://image.tmdb.org/t/p/w500'
YOUTUBE_BASE_URL = "https://www.youtube.com/watch?v="

# CSS custom
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: #000 !important;
    width: 80px !important;
    min-width: 80px !important;
    transition: width 0.3s ease;
    overflow: hidden !important;
}
section[data-testid="stSidebar"]:hover {
    width: 400px !important;
    min-width: 400px !important;
}
section[data-testid="stSidebar"] ul li svg {
    color: #f5c518 !important;
    transition: color 0.3s ease;
}
section[data-testid="stSidebar"] ul li span {
    color: white !important;
    transition: color 0.3s ease;
}
section[data-testid="stSidebar"] ul li:hover span,
section[data-testid="stSidebar"] ul li[data-selected="true"] span {
    color: #f5c518 !important;
    font-weight: bold !important;
}
section[data-testid="stSidebar"] > div:before {
    content: "";
    display: flex;
    justify-content: flex-start;
    align-items: center;
    height: 90px;
    padding-left: 40px;
    background-image: url('https://i.imgur.com/woVWY9R.png');
    background-size: 68px auto;
    background-repeat: no-repeat;
    background-position: left center;
    margin-bottom: 10px;
}
section[data-testid="stSidebar"]:hover > div:before {
    background-size: 110px auto;
}
</style>
""", unsafe_allow_html=True)

# Chargement des données
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Zyeddd/filmrecommandation/main/df_imdb_final.csv"
    return pd.read_csv(url)

df = load_data()

# Fonctions TMDb
@st.cache_data
def get_popular_movies():
    try:
        url = f"{BASE_URL}/movie/popular"
        params = {'api_key': API_KEY, 'language': 'fr-FR'}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except:
        return {'results': []}

def get_movie_details(movie_id):
    try:
        url = f"{BASE_URL}/movie/{movie_id}"
        params = {'api_key': API_KEY, 'language': 'fr-FR'}
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except:
        return {}

def get_movie_trailer(movie_id):
    try:
        url = f"{BASE_URL}/movie/{movie_id}/videos"
        params = {'api_key': API_KEY, 'language': 'fr-FR'}
        response = requests.get(url, params=params)
        response.raise_for_status()
        videos = response.json().get("results", [])
        for video in videos:
            if video["type"] == "Trailer" and video["site"] == "YouTube":
                return f"{YOUTUBE_BASE_URL}{video['key']}"
        return None
    except:
        return None

# Barre latérale
with st.sidebar:
    selected = on_hover_tabs(
        tabName=[
            'Accueil',
            'Notre démarche',
            'Le cinéma dans la Creuse',            
            'Chiffres-clés',
            'Trouvez votre prochain film'
        ],
        iconName=['home', 'list', 'map', 'bar_chart', 'search'],
        default_choice=0
    )


# Onglet Accueil
if selected == "Accueil":
    st.title("WMDb : explorez le cinéma autrement !")

    st.markdown(
        "<div style='padding-left: 40px; font-size:20px;'>d'Hollywood à la Creuse, il n'y a qu'un clic...</div><br><br>",
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style='max-width: 85%; text-align: justify; font-size:16px; line-height:1.6;'>
            <p>
            Vous l'avez peut-être remarqué, la Creuse, en collaboration avec les directions des cinémas, 
            a significativement renforcé son offre de cinéma ces dernières années !
            </p>
            <p>
            Les directeurs de salle souhaitent accompagner cet élan en améliorant l'expérience cinématographique de tous.
            C'est de cette volonté qu'est née la <strong>plateforme WMDb</strong>, qui vous propose des recommandations 
            de films personnalisées, adaptées à vos goûts.
            </p>
            <p>
            À terme, notre équipe <span style='text-decoration: line-through;'>de médiums et de voyants</span> 
            d'experts data sera même en mesure de vous envoyer directement des recommandations ciblées 
            en fonction de vos préférences ! 🔮
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("**Découvrez dès maintenant les dernières sorties ciné :**")

    st.markdown("""
    <hr style='margin-top:40px;'>
    <div style='text-align:center; font-size:13px; color:grey;'>
    Projet réalisé par Stevens A., Christopher B., Alexis C., et Zyed G. – Wild Code School · Promo 2025
    </div>
    """, unsafe_allow_html=True)


    st.markdown("""
    <style>
    .film-card {
        background-color: #111;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 25px;
        display: flex;
        gap: 20px;
        min-height: 240px;
        transition: transform 0.3s ease;
    }
    .film-card:hover {
        transform: scale(1.02);
    }
    .film-card img {
        width: 120px;
        border-radius: 8px;
    }
    .film-info {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .film-title {
        font-size: 18px;
        font-weight: bold;
        color: #f5c518;
    }
    .film-note {
        color: white;
        font-weight: bold;
        margin-top: 4px;
    }
    .film-details {
        font-size: 14px;
        color: #ccc;
        margin-top: 4px;
    }
    .film-overview {
        font-size: 13px;
        color: #aaa;
        margin-top: 10px;
    }
    a {
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

    with st.spinner("Chargement des films en tendance..."):
        popular_movies = get_popular_movies()

    if popular_movies["results"]:
        cols = st.columns(2)
        for i, movie in enumerate(popular_movies["results"][:8]):
            with cols[i % 2]:
                poster_path = movie.get("poster_path")
                movie_id = movie.get("id")
                details = get_movie_details(movie_id)
                trailer_url = get_movie_trailer(movie_id)

                card_html = "<div class='film-card'>"

                if poster_path:
                    poster_url = f"{IMAGE_BASE_URL}{poster_path}"
                    card_html += f"<img src='{poster_url}' alt='affiche'>"

                card_html += "<div class='film-info'>"
                card_html += f"<div class='film-title'>{movie['title']}</div>"
                card_html += f"<div class='film-details'>Date de sortie : {movie.get('release_date', 'N/A')}</div>"
                card_html += f"<div class='film-note'>⭐ {movie['vote_average']}/10 ({movie['vote_count']} votes)</div>"

                genres = [g["name"] for g in details.get("genres", [])]
                if genres:
                    card_html += f"<div class='film-details'>Genres : {', '.join(genres)}</div>"

                overview = movie.get('overview') or "Résumé non disponible."
                short = overview[:180] + "..." if len(overview) > 180 else overview
                card_html += f"<div class='film-overview'>{short}</div>"

                if trailer_url:
                    card_html += f"<div class='film-details'><a href='{trailer_url}' target='_blank'>🎞️ Voir la bande-annonce</a></div>"

                card_html += "</div></div>"
                st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("Aucun film tendance trouvé pour le moment.")


# Onglet Notre démarche
elif selected == "Notre démarche":
    st.title("Notre démarche")

    st.markdown("""
### Notre objectif 🎯

Notre équipe a été sollicitée par un directeur de cinéma dans la Creuse.  
Il souhaite dynamiser la fréquentation de son cinéma en proposant aux habitants un **moteur de recommandation de films personnalisé**, qui permettra à terme de leur envoyer des notifications en fonction de leurs préférences cinématographiques.  
Notre mission : **faire naître cette plateforme de recommandations.**

---

### Les étapes de notre projet 🛠️

Nous avons démarré d'une situation de **cold start** : aucune préférence utilisateur enregistrée.  
Pour répondre à ce défi, nous avons découpé notre travail en plusieurs étapes : étude de marché locale, exploration des données, création de dashboards, et mise en place d’un moteur de recommandations intelligent basé sur les préférences cinématographiques.

---

#### 🗺️ A. Étude de marché sur la Creuse
                
Une première analyse a été menée à l'aide des données du **CNC** et de **l'INSEE**.
Elle nous a permis d'identifier les caractéristiques de la population de la Creuse ainsi que son lien avec le cinéma.  

---
#### 🖥️B. Analyse et création du système de recommandations
                
#### 📦 1. Collecte des données
- Bases de données volumineuses au format `.tsv.gz` extraites depuis le site IMDb
- Objectif : récupérer les **informations essentielles** pour recommander des films (titre, genres, réalisateurs, acteurs, notes…)
- Challenge : **volumétrie très élevée** → nécessité de filtrer, croiser, simplifier


#### 🧹 2. Nettoyage et préparation
- Suppression des lignes incomplètes ou inutilisables
- Élimination des colonnes non pertinentes
- Filtres avancés (nombre de votes, note, langue, région…)
- Jointures sur les fichiers `title.basics`, `title.ratings`, `name.basics`, `title.principals`
- Création de nouvelles colonnes (décennie, genre1/2/3, etc.)
✅ Résultat : **`df_imdb_final.csv`**


#### 🧠 3. Exploration & analyses
- Visualisation des genres, notes, votes
- Identification des **films, réalisateurs, acteurs les plus présents**
- Création de **KPI visuels** pour mieux comprendre les préférences


#### 🤖 4. Recommandation de films
- Approche **KNN (proches voisins)** fondée sur les genres
- Filtrage possible par **réalisateur**, **acteurs** ou **genres**
- Tri final par **note décroissante**


#### 🌐 5. Déploiement de l'application
- Interface **Streamlit** entièrement personnalisée (charte graphique IMDb, animations, navigation optimisée)
- Hébergement sur GitHub + Streamlit Cloud

---

#### 🔧 Outils utilisés
- Python (Pandas, scikit-learn, seaborn…)
- GitHub
- Trello
- Streamlit

---

#### 📂 Ressources
- Fichiers IMDb `.tsv.gz` (title, ratings, names, principals…)
- Documentation officielle IMDb
- API TMDb pour les affiches & résumés
""", unsafe_allow_html=True)

# Onglet Creuse
elif selected == "Le cinéma dans la Creuse":
    st.title("🌳 Un département marqué par des défis socio-économiques") #PARTIE 1/2
    st.subheader("Une population  vieillissante") #SOUS-PARTIE 1/2

    col1, col2 = st.columns([1.3, 1.7])  # élargir légèrement la colonne 1 pour l'image

    with col1:
        st.image("https://raw.githubusercontent.com/Zyeddd/filmrecommandation/main/evol_repa_ages.png", use_container_width=True)

    with col2:
        st.markdown(
            """
            <div style="display: flex; align-items: center; height: 100%; min-height: 450px;">
                <div style="font-size:16px;">
                    Entre <strong>2010</strong> et <strong>2021</strong>, la population de la Creuse a diminué de <strong>6%</strong>.<br>
                    Cette baisse globale masque une évolution marquante : la seule tranche d’âge en hausse est celle des 
                    <strong>60 à 74 ans</strong>, en progression de <strong>+22,4%</strong>. 
                    Le département vieillit donc de manière significative.
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


    st.subheader("Un territoire en difficulté économique")  # SOUS-PARTIE 2/2

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("""
        <div style="font-size:16px; text-align: justify; padding-top: 30%;">
            En <strong>2021</strong>, le revenu médian annuel des habitants de la Creuse était de <strong>20 620 €</strong>,
            soit bien en dessous de la médiane régionale (<strong>22 710 €</strong>) et nationale (<strong>24 330 €</strong>).
            <br><br>
            Ce différentiel souligne les <strong>difficultés économiques</strong> auxquelles est confronté le territoire :
            <strong>1 personne sur 5</strong> vit sous le <strong>seuil de pauvreté</strong>.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        df_revenus = pd.DataFrame({
            "Territoire": ["Creuse", "Nouvelle-Aquitaine", "France"],
            "Revenu médian (€)": [20620, 22710, 24330]
        })

        fig_rev = px.bar(
            df_revenus,
            x="Territoire",
            y="Revenu médian (€)",
            text="Revenu médian (€)",
            color="Territoire",
            color_discrete_sequence=["#F5C518", "#AAAAAA", "#666666"]
        )

        fig_rev.update_traces(
            texttemplate='%{text:.0f}€',
            textposition='inside',
            insidetextanchor='end'
        )

        fig_rev.update_layout(
            title="Comparaison du revenu médian en 2021",
            yaxis_title="Revenu médian annuel (€)",
            xaxis_title="",
            showlegend=False,
            yaxis=dict(tickformat=","),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            margin=dict(t=60, b=40)
        )

        st.plotly_chart(fig_rev, use_container_width=True)

    st.title("🛡️ Un cinéma local qui résiste")  # PARTIE 2/2

    # SOUS-PARTIE 1/3 : Infrastructures
    st.subheader("Infrastructures disponibles")

    kpi_cols = st.columns(3)
    kpi_data = [
        ("🏛️", "7 salles de cinéma"),
        ("🎬", "12 écrans"),
        ("🍿", "2 150 fauteuils")
    ]

    for col, (emoji, label) in zip(kpi_cols, kpi_data):
        with col:
            st.markdown(f"<div style='text-align:center;font-size:22px;'>{emoji} {label}</div>", unsafe_allow_html=True)

    # SOUS-PARTIE 2/3 : Offre démultipliée
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Une offre cinématographique décuplée")

    card_style = (
        "background-color:#white;border-radius:12px;padding:25px;"
        "color:black;text-align:center;"
    )

    col_left, col_right = st.columns([1, 1])

    # Carte 1 – Diffusions
    with col_left:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="font-size:18px;font-weight:bold;">Projections</div>
                <div style="font-size:38px;font-weight:bold;margin:8px 0;">
                    74 400
                </div>
                <div style="font-size:24px; line-height:1.3;">
                    films diffusés en 2022<br>
                    <span style="color:#FF4B4B;font-size:18px;">▲ +755% par rapport à 2015</span>
                </div>
                <div style="font-size:11px;font-style:italic;margin-top:8px;">
                    Source : CNC
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Carte 2 – Fréquentation
    with col_right:
        st.markdown(
            f"""
            <div style="{card_style}">
                <div style="font-size:18px;font-weight:bold;">Fréquentation</div>
                <div style="font-size:38px;font-weight:bold;margin:8px 0;">
                    1,168&nbsp;M
                </div>
                <div style="font-size:24px; line-height:1.3;">
                    entrées en 2022<br>
                    <span style="color:#FF4B4B;font-size:18px;">▲ +567% par rapport à 2015</span>
                </div>
                <div style="font-size:11px;font-style:italic;margin-top:8px;">
                    Source : CNC
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    
    st.markdown("""
    <br>
    <div style="font-size:16px;">
    L’offre cinématographique a été <strong>massivement renforcée depuis 2015</strong>, avec une hausse remarquable des <strong>projections</strong> (+755%) et de la <strong>fréquentation</strong> (+567%) sur l’ensemble du territoire.
    </div>
    """, unsafe_allow_html=True)

# SOUS-PARTIE 3/3 : ARTS ET ESSAI
    st.subheader("La Creuse, terre de cinéma engagé")
    st.markdown(
    """
    <div style="text-align:center; font-size:38px; font-weight:bold; margin-bottom:0.2em;">
        📜 11 cinémas sur 12
    </div>
    <div style="text-align:center; font-size:16px;">
        sont labellisés <strong>Art & Essai</strong>
    </div>
    """,
    unsafe_allow_html=True
)
    st.markdown(
    """
    <div style=font-size:15px;">
    Ce label, soutenu par les instances culturelles, met en lumière et participe au financement des programmations mettant en avant des films de qualité artistique, culturelle ou patrimoniale.<br>
    Un élément supplémentaire à prendre en compte pouvant favoriser une émulation</strong>.
    </div>
    """,
    unsafe_allow_html=True
)


# Onglet Chiffres-clés
elif selected == "Chiffres-clés":
    st.title("Chiffres-clés")

    st.subheader("Répartition des genres avec note moyenne et réalisateur populaire")
    df_genres = df.groupby("genre1_film").agg(Nombre_de_films=("genre1_film", "count"), AverageRating=("averageRating", "mean")).reset_index().rename(columns={"genre1_film": "Genre"})
    df_genres["AverageRating"] = df_genres["AverageRating"].round(2)

    def get_most_popular_movie(genre):
        sub_df = df[df["genre1_film"] == genre]
        if sub_df.empty:
            return "Non spécifié"
        group = sub_df.groupby("title")["numVotes"].sum()
        return group.idxmax() if not group.empty else "Non spécifié"

    df_genres["Film_populaire"] = df_genres["Genre"].apply(get_most_popular_movie)

    genre_colors = {"Comedy": "#FFCC00", "Drama": "#FF5733", "Action": "#C70039", "Crime": "#900C3F", "Biography": "#581845", "Adventure": "#1A5276", "Documentary": "#2E86C1", "Horror": "#117A65", "Animation": "#D4AC0D", "Mystery": "#6C3483", "Thriller": "#A04000"}
    df_genres["Color"] = df_genres["Genre"].map(genre_colors)

    fig_treemap = px.treemap(df_genres, path=["Genre", "Film_populaire", "AverageRating"], values="Nombre_de_films", title="Répartition des genres de films", color="Genre", color_discrete_map=genre_colors)
    st.plotly_chart(fig_treemap)

    st.subheader("Durée moyenne des films par genre")

    avg_duration = df.groupby("genre1_film")["duration"].mean().sort_values(ascending=False).head(10)
    avg_duration_df = avg_duration.reset_index()
    avg_duration_df.columns = ["Genre", "Durée moyenne"]

    # Appliquer la même couleur que dans le treemap, sinon gris clair par défaut
    avg_duration_df["Color"] = avg_duration_df["Genre"].map(genre_colors).fillna("#DDDDDD")

    fig2 = px.bar(
        avg_duration_df,
        x="Genre",
        y="Durée moyenne",
        title="Durée moyenne des films par genre",
        color="Genre",
        color_discrete_map=genre_colors,
        labels={"Durée moyenne": "Durée moyenne (minutes)"}
    )
    st.plotly_chart(fig2)


    st.subheader("Top 10 réalisateurs par nombre de votes")

    # Agrégation par nombre de votes
    top_directors_votes = (
        df.groupby("name_dir")["numVotes"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )

    # Palette sobre : jaune orangé clair
    colors = sns.color_palette("YlOrBr", n_colors=10)[::-1]

    # Tracé du graphique
    plt.figure(figsize=(10, 6))
    bars = sns.barplot(
        x=top_directors_votes.values / 1_000_000,
        y=top_directors_votes.index,
        palette=colors
    )

    # Ajout des étiquettes sur les barres
    for i, v in enumerate(top_directors_votes.values / 1_000_000):
        bars.text(v + 0.1, i, f"{v:.1f}M", va='center')

    plt.title("Top 10 des réalisateurs les plus populaires")
    plt.xlabel("Nombre de votes (en millions)")
    plt.ylabel("Réalisateurs")
    plt.tight_layout()

    st.pyplot(plt.gcf())


    st.subheader("Acteurs les plus populaires par genre")
    # Préparation des données
    actor_melted = pd.melt(
        df,
        id_vars=['numVotes', 'genre1_film', 'genre2_film', 'genre3_film'],
        value_vars=['name_act1', 'name_act2', 'name_act3'],
        value_name='name_act'
    ).dropna(subset=['name_act'])

    genre_actor_melted = pd.melt(
        actor_melted,
        id_vars=['numVotes', 'name_act'],
        value_vars=['genre1_film', 'genre2_film', 'genre3_film'],
        value_name='genre'
    ).dropna(subset=['genre'])

    genre_rating_actor_stats = genre_actor_melted.groupby(["genre", "name_act"])["numVotes"].sum().reset_index()
    top_actors_per_genre = genre_rating_actor_stats.loc[
        genre_rating_actor_stats.groupby("genre")["numVotes"].idxmax()
    ]
    top_actors_per_genre_sorted = top_actors_per_genre.sort_values(by="numVotes", ascending=False).head(10)

    fig4 = px.sunburst(
        top_actors_per_genre_sorted,
        path=['genre', 'name_act'],
        values='numVotes',
        color='numVotes',
        color_continuous_scale='Plasma',
        width=800,
        height=800,
        labels={'numVotes': 'Nombre de Votes'}
    )
    fig4.update_layout(
        font=dict(size=16),
        title="🔹 Acteurs les plus populaires par Genre"
    )
    st.plotly_chart(fig4)

# Onglet Recommandation
# Onglet Recommandation
elif selected == "Trouvez votre prochain film":
    st.title("Trouvez votre prochain film")
    st.markdown(
                "<div style='font-size:20px;'><strong>Vous n'êtes plus qu'à quelques swipes de votre prochain match cinématographique... ❤️‍🔥</strong></div>",
                unsafe_allow_html=True)

    film_choices = sorted(df["title"].dropna().unique())
    selected_title = st.selectbox("🎬 Choisissez un film que vous aimez :", [""] + film_choices)

    genres_list = sorted(set(g for g in pd.unique(df[["genre1_film", "genre2_film", "genre3_film"]].values.ravel()) if pd.notna(g)))
    directors_list = sorted(df["name_dir"].dropna().unique())
    actors_list = sorted(set(a for a in pd.unique(df[["name_act1", "name_act2", "name_act3"]].values.ravel()) if pd.notna(a)))

    st.markdown(
                "<div style='font-size:20px;'><strong>Trop de matches ? Affinez votre recherche 🎯</strong></div>",
                unsafe_allow_html=True)   
    selected_genres = st.multiselect("Genres :", genres_list)
    selected_director = st.selectbox("Réalisateur :", [""] + directors_list)
    selected_actors = st.multiselect("Acteurs préférés (2 max) :", actors_list, max_selections=2)

    recommended = df.copy()

    # Création de la colonne "decade" dans recommended uniquement
    recommended["decade"] = (recommended["year"] // 10 * 10).astype(int).astype(str) + "s"

    # Décennies disponibles
    decades = sorted(recommended["decade"].dropna().unique())
    selected_decade = st.selectbox("Décennie :", options=["Toutes"] + decades)

    # Application du filtre décennal
    if selected_decade != "Toutes":
        recommended = recommended[recommended["decade"] == selected_decade]


    # 1. FILM SIMILAIRE (si titre saisi)
    if selected_title:
        ref_row = df[df["title"] == selected_title].iloc[0]
        ref_genres = set([ref_row["genre1_film"], ref_row["genre2_film"], ref_row["genre3_film"]]) - {np.nan}
        def count_common_genres(row):
            film_genres = set([row["genre1_film"], row["genre2_film"], row["genre3_film"]]) - {np.nan}
            return len(ref_genres & film_genres)
        recommended = recommended[recommended["title"] != selected_title]
        recommended["common_genres"] = recommended.apply(count_common_genres, axis=1)
        recommended = recommended[recommended["common_genres"] > 0]
    else:
        recommended["common_genres"] = 0

    # 2. FILTRES GENRES
    if selected_genres:
        recommended = recommended[
            recommended[["genre1_film", "genre2_film", "genre3_film"]].apply(
                lambda x: any(g in selected_genres for g in x if pd.notna(g)), axis=1
            )
        ]

    # 3. FILTRE RÉALISATEUR
    if selected_director:
        recommended = recommended[recommended["name_dir"] == selected_director]

    # 4. FILTRE ACTEURS
    if selected_actors:
        def count_common_actors(row):
            film_actors = set([row["name_act1"], row["name_act2"], row["name_act3"]]) - {np.nan}
            return len(film_actors & set(selected_actors))
        recommended["common_actors"] = recommended.apply(count_common_actors, axis=1)
        recommended = recommended[recommended["common_actors"] >= 2]
    else:
        recommended["common_actors"] = 0

    recommended = recommended.sort_values(by=["common_genres", "averageRating"], ascending=[False, False])

    st.subheader("🔍 Films recommandés")

    st.markdown("""
    <style>
    .film-card {
        background-color: #111;
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 25px;
        display: flex;
        gap: 20px;
        min-height: 240px;
        transition: transform 0.3s ease;
    }
    .film-card:hover {
        transform: scale(1.02);
    }
    .film-card img {
        width: 120px;
        border-radius: 8px;
    }
    .film-info {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .film-title {
        font-size: 18px;
        font-weight: bold;
        color: #f5c518;
    }
    .film-note {
        color: white;
        font-weight: bold;
        margin-top: 4px;
    }
    .film-details {
        font-size: 14px;
        color: #ccc;
        margin-top: 4px;
    }
    .film-overview {
        font-size: 13px;
        color: #aaa;
        margin-top: 10px;
    }
    a {
        color: #1f77b4;
    }
    </style>
    """, unsafe_allow_html=True)

    if not recommended.empty:
        cols = st.columns(2)
        for i, (_, row) in enumerate(recommended.head(8).iterrows()):
            with cols[i % 2]:
                imdb_id = row["titleID"]
                api_url = f"https://api.themoviedb.org/3/find/{imdb_id}?api_key={API_KEY}&language=fr-FR&external_source=imdb_id"
                response = requests.get(api_url)
                data = response.json().get("movie_results", [])
                poster_path = data[0].get("poster_path") if data else None
                tmdb_id = data[0].get("id") if data else None

                # Détails + bande-annonce
                details = {}
                trailer_url = None
                if tmdb_id:
                    try:
                        details = requests.get(f"{BASE_URL}/movie/{tmdb_id}?api_key={API_KEY}&language=fr-FR").json()
                        videos = requests.get(f"{BASE_URL}/movie/{tmdb_id}/videos?api_key={API_KEY}&language=fr-FR").json()
                        for video in videos.get("results", []):
                            if video["type"] == "Trailer" and video["site"] == "YouTube":
                                trailer_url = f"{YOUTUBE_BASE_URL}{video['key']}"
                                break
                    except:
                        pass

                card_html = "<div class='film-card'>"
                if poster_path:
                    poster_url = f"https://image.tmdb.org/t/p/w200{poster_path}"
                    card_html += f"<img src='{poster_url}' alt='affiche'>"

                card_html += "<div class='film-info'>"
                card_html += f"<div class='film-title'>{row['title']}</div>"
                card_html += f"<div class='film-note'>⭐ {row['averageRating']}/10</div>"

                genres = ', '.join(g for g in [row['genre1_film'], row['genre2_film'], row['genre3_film']] if pd.notna(g))
                if genres:
                    card_html += f"<div class='film-details'>Genres : {genres}</div>"

                if row["name_dir"]:
                    card_html += f"<div class='film-details'>Réalisateur : {row['name_dir']}</div>"

                overview = details.get("overview") or "Résumé non disponible."
                short = overview[:180] + "..." if len(overview) > 180 else overview
                card_html += f"<div class='film-overview'>{short}</div>"

                if trailer_url:
                    card_html += f"<div class='film-details'><a href='{trailer_url}' target='_blank'>🎞️ Voir la bande-annonce</a></div>"

                card_html += "</div></div>"
                st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("Aucun film ne correspond à vos critères.")

