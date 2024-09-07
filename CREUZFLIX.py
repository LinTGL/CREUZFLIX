import streamlit as st
import pandas as pd
import aiohttp
import asyncio
import os
import random
from category_encoders import BinaryEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import MultiLabelBinarizer
from tools import ( 
    CustomMultiLabelBinarizer,
    preprocessor,
    create_knn_pipeline,
    find_nearest_neighbors_film
)


async def fetch_infos_movies_fr(imdb_id: int):
    params = {
        "api_key": "22180d57e4d3eb864a124ee61b0a50f4",
        "include_adult": "False",
        "language": "fr-FR",
        "append_to_response": "keywords,videos",
    }
    base_url = "https://api.themoviedb.org/3/movie/"
    url = f"{base_url}{imdb_id}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()

async def fetch_infos_movies_en(imdb_id: int):
    params = {
        "api_key": "22180d57e4d3eb864a124ee61b0a50f4",
        "include_adult": "False",
        "language": "en-EN",
        "append_to_response": "keywords,videos",
    }
    base_url = "https://api.themoviedb.org/3/movie/"
    url = f"{base_url}{imdb_id}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as response:
            return await response.json()


st.title(':rainbow-background[_BIENVENUE DANS CREUZFLIX_]')
df_movies_ = pd.read_parquet(r"C:\Users\DELL 7480\Documents\WILD CODE SCHOOL\Projet 2\Projet2-movies\Dataset_clean\film_site.parquet")
(df_movies_.head())

movie_list = df_movies_['titre'].tolist()

df_top_10 = pd.read_parquet(r"C:\Users\DELL 7480\Documents\WILD CODE SCHOOL\Projet 2\Projet2-movies\Dataset_clean\top_10_film_site.parquet")
top_10 = df_top_10.sort_values(by="Rating", ascending=False)

# Convert the sorted DataFrame to a list of movie titles
movie_list_top_10 = top_10['titre'].tolist()

placeholder = "Select a movie"
movie_list.insert(0, placeholder)

st.sidebar.image(r'C:\Users\DELL 7480\Documents\WILD CODE SCHOOL\Projet 2\Streamlit_P2\cinécreuz.jpg')
movie_title = st.sidebar.selectbox("Choix du film", movie_list, index=0)

quotes = {
    1: "Qu'est-ce qui est mieux que gagner une médaille d'or aux Jeux Paralympiques ? --  Marcher.",
    2: "Quelle mamie fait peur aux voleurs ? --  Mamie Traillette.",
    3: "Quels sont les gâteaux préférés de Brigitte Macron ? -- Les petits écoliers",
    4: "C'est l'histoire d'un mec qui rentre dans un bar je voudrais 2 bières s'il vous plait ! --  des pressions ?  -- non, alcoolisme",
    5: "Comment fait-on pour allumer un barbecue breton ? -- On utilise des breizh.",
}

# Display movie information when a movie is selected
if movie_title != placeholder:
    st.write(f"")
    
    # Get the imdb_id for the selected movie
    selected_movie = df_movies_.loc[df_movies_['titre'] == movie_title]
    
    if not selected_movie.empty:
        imdb_id = selected_movie['titre_id'].values[0]

        # Fetch movie info when a movie is selected
        movie_info_fr = asyncio.run(fetch_infos_movies_fr(imdb_id))
        movie_info_en = asyncio.run(fetch_infos_movies_en(imdb_id))

        #by default, we use the French information
        movie_info_ = movie_info_fr
        # Display movie poster or backdrop (resized)
        if 'poster_path' in movie_info_ and movie_info_['poster_path']:
            st.image(f"https://image.tmdb.org/t/p/w500{movie_info_['poster_path']}", caption=movie_title, width=100)
        elif 'backdrop_path' in movie_info_ and movie_info_['backdrop_path']:
            st.image(f"https://image.tmdb.org/t/p/w500{movie_info_['backdrop_path']}", caption=movie_title, width=100)
        else:
            st.write("No image available")

        if 'vote_average' in movie_info_ and movie_info_['vote_average']:
            st.write(f"**Note :** {movie_info_['vote_average']}")

        if 'release_date' in movie_info_ and movie_info_['release_date']:
            st.write(f"**Date :** {movie_info_['release_date']}")
        # Display movie information
        if 'overview' in movie_info_en and movie_info_en['overview']:
            st.write(f"**Résumé :** {movie_info_en['overview']}")
        else:
            random_quote = random.choice(list(quotes.values()))
            st.write(f"**Pas d'overview dispo donc un peu d'humour noir :** {random_quote}")
        
        # Display videos
        if 'videos' in movie_info_ and 'results' in movie_info_['videos']:
            videos = movie_info_['videos']['results']
            # Search for French trailer
            french_trailer = next((video for video in videos if video['type'] == 'Trailer' and video.get('iso_639_1', '') == 'fr'), None)
            # If no French trailer, look for English trailer
            if not french_trailer:
                vidoes_en = movie_info_en['videos']['results']
                english_trailer = next((video for video in vidoes_en if video['type'] == 'Trailer' and video.get('iso_639_1', '') == 'en'), None)
                if english_trailer:
                    if english_trailer['site'] == 'YouTube':
                        st.video(f"https://www.youtube.com/watch?v={english_trailer['key']}")
                    elif english_trailer['site'] == 'Vimeo':
                        st.video(f"https://vimeo.com/{english_trailer['key']}")
                else:
                    # If no English or French trailer, display the first video
                    st.video(f"https://www.youtube.com/watch?v=fc7A6XIF2t8")
            else:
                if french_trailer['site'] == 'YouTube':
                    st.video(f"https://www.youtube.com/watch?v={french_trailer['key']}")
                elif french_trailer['site'] == 'Vimeo':
                    st.video(f"https://vimeo.com/{french_trailer['key']}")

        st.subheader("**Films Similaires**", anchor=False)

        # Prepare data for KNN
        df_movies_X = df_movies_.copy()
        knn_pipeline = create_knn_pipeline()
        knn_pipeline.fit(df_movies_[[col for col in df_movies_.columns if col not in ['titre_id', 'titre']]])

        if st.button("Films similaires"):
            # Find recommended movies
            recommended = find_nearest_neighbors_film(movie_title, knn_pipeline, df_movies_)

            if not recommended.empty:
                st.write("Films similaires")
                cols = st.columns(5)

                for idx, (_, row) in enumerate(recommended.iterrows()):
                    rec_imdb_id = row['titre_id']
                    rec_movie_info = asyncio.run(fetch_infos_movies_fr(rec_imdb_id))

                    with cols[idx % len(cols)]:
                        if 'poster_path' in rec_movie_info and rec_movie_info['poster_path']:
                            st.image(f"https://image.tmdb.org/t/p/w500{rec_movie_info['poster_path']}", caption=rec_movie_info['title'], width=100)
                        elif 'backdrop_path' in rec_movie_info and rec_movie_info['backdrop_path']:
                            st.image(f"https://image.tmdb.org/t/p/w500{rec_movie_info['backdrop_path']}", caption=rec_movie_info['title'], width=100)
                        else:
                            st.write("No image available")
                        overview = rec_movie_info.get('overview', '')
                        if not overview:
                            random_quote = random.choice(list(quotes.values()))
                            st.write(f"**Pas d'overview donc un peu d'humour noir :** {random_quote}")
                        else:
                            st.write(f"**Overview:** {overview}")
            else:
                st.write("Pas de films similaires")
else:
     st.write("")


# ***********************AFFICHAGE TOP 10 DEPUIS 2019 - FILTRE PAR GENRE*****************************
# Display top 10 movies

st.markdown("""<div style="margin-top: 80px;"></div>
    
 """, unsafe_allow_html=True)
st.subheader(':rainbow-background[TOP 10]', divider='rainbow')

# st.markdown("""
#     <div style="margin-top: 20px;"></div>
#     <div style="background: linear-gradient(to right, violet, indigo, blue, green, yellow, orange, red);">
#         <h3 style="color: white; padding: 10px;">TOP 10</h3>
#     </div>
#     <div style="margin-top: 20px;"></div>
    
# """, unsafe_allow_html=True)

# Nombre d'images à afficher par page
num_cols = 5
cols = st.columns(num_cols)

# Fetch top 10 movies
top_10 = df_top_10.head(10)

if 'start_idx' not in st.session_state:
    st.session_state.start_idx = 0
if 'end_idx' not in st.session_state:
    st.session_state.end_idx = num_cols

# Buttons to navigate
prev_button, next_button = st.columns(2)

with prev_button:
    if st.button("Précédent"):
        if st.session_state.start_idx > 0:
            st.session_state.start_idx -= num_cols
            st.session_state.end_idx -= num_cols

with next_button:
    if st.button("Suivant"):
        if st.session_state.end_idx < len(top_10):
            st.session_state.start_idx += num_cols
            st.session_state.end_idx += num_cols

# Ensure end_idx does not exceed the length of top_10
if st.session_state.end_idx > len(top_10):
    st.session_state.end_idx = len(top_10)

# Display movies in the current range
for index, movie in enumerate(top_10.iloc[st.session_state.start_idx:st.session_state.end_idx].itertuples()):
    with cols[index % num_cols]:
        rec_imdb_id = movie.titre_id
        rec_movie_info = asyncio.run(fetch_infos_movies_fr(rec_imdb_id))
        if rec_movie_info:
            # Display the image and title
            if 'poster_path' in rec_movie_info and rec_movie_info['poster_path']:
                st.image(f"https://image.tmdb.org/t/p/w500{rec_movie_info['poster_path']}", caption=movie.titre, width=100)
            else:
                # If no poster available, display default image
                st.image(r"C:\Users\DELL 7480\Documents\WILD CODE SCHOOL\Projet 2\Projet2-movies\hulk.jpeg", caption="No Poster Available, so here's SUUUHULK", width=120)

            # Button to select the movie
            if st.button(f"{movie.titre}", key=f"{index}"):
                st.session_state.selected_movie = movie

# Display details of the selected movie
if "selected_movie" in st.session_state:
    selected_movie_info = asyncio.run(fetch_infos_movies_fr(st.session_state.selected_movie.titre_id))
    if selected_movie_info:
        st.markdown(f"###  {st.session_state.selected_movie.titre}")
        if 'poster_path' in selected_movie_info and selected_movie_info['poster_path']:
            st.image(f"https://image.tmdb.org/t/p/w500{selected_movie_info['poster_path']}", caption=selected_movie_info['title'], width=100)
        else:
            # If no poster available, display default image
            st.image(r"C:\Users\DELL 7480\Documents\WILD CODE SCHOOL\Projet 2\Projet2-movies\hulk.jpeg", caption="SUUUHULK", width=120)
        st.write("**A propos du film 🎬**")
        st.write(f"**Genre:** {st.session_state.selected_movie.genres}")
        st.write(f"**Résumé:** {st.session_state.selected_movie.overview}")
        st.write(f"**Date de sortie:** {st.session_state.selected_movie.startYear}")
        st.write(f"**Note:** {st.session_state.selected_movie.Rating}")
        st.write(f"**Durée:** {st.session_state.selected_movie.duree} min")
        st.write("**ENJOY :)**")


# ***************************************FIN AFFICHAGE****************************************************


df_movies_exploded = df_movies_.explode('genres')


# Fonction pour obtenir le meilleur film de chaque genre
def movie_top(df, genre, top_n=5):
    genre_films = df[df['genres'].apply(lambda x: genre in x)]
    if not genre_films.empty:
        sorted_films = genre_films.sort_values(by='Rating', ascending=False)
        top_film = sorted_films.head(top_n)
        return top_film
    else:
        return None

list_genre = ['Drama', 'Romance', 'Comedy', 'Adventure', 'Thriller']



#========= ESSAI +++++++++++


st.markdown("""<div style="margin-top: 100px;"></div>
    
 """, unsafe_allow_html=True)
st.subheader(':rainbow-background[TOP GENRE]', divider='rainbow')


selected_movies = {}  # Initialize an empty dictionary to store selected movies

for genre in list_genre:
    st.subheader(f"{genre}")
    top_films = movie_top(df_movies_, genre)
    if not top_films.empty:
        num_cols = min(len(top_films), 5)  # Adjust the number of columns based on the number of top films
        cols = st.columns(num_cols)
        
        for i, (index, movie) in enumerate(top_films.iterrows()):
            with cols[i % num_cols]:
                rec_imdb_id = movie['titre_id']

                # Fetch movie info in French
                rec_movie_info_fr = asyncio.run(fetch_infos_movies_fr(rec_imdb_id))
                # Fetch movie info in English
                rec_movie_info_en = asyncio.run(fetch_infos_movies_en(rec_imdb_id))

                if rec_movie_info_fr:
                    # Use the French poster if available, otherwise fallback to the English poster
                    poster_path = rec_movie_info_fr.get('poster_path') or rec_movie_info_en.get('poster_path')
                    
                    if poster_path:
                        st.image(f"https://image.tmdb.org/t/p/w500{poster_path}", caption=movie['titre'], width=100)
                    else:                        
                        st.image(r"C:\Users\DELL 7480\Documents\WILD CODE SCHOOL\Projet 2\Projet2-movies\hulk.jpeg", 
                         caption=f"No poster for '{movie.titre}', so here's the return of SUUUHULK", width=110)

                    st.write(f"Note : {movie['Rating']}")

                    # Use a unique key for the button based on the movie's titre_id
                    button_key = f"voir_{rec_imdb_id}_{i}"
                    if st.button("Voir film", key=button_key):
                        # Update the selected_movies dictionary with the selected movie's titre_id
                        selected_movies[rec_imdb_id] = {
                            'movie_info_fr': rec_movie_info_fr,
                            'movie_info_en': rec_movie_info_en,
                            'title': movie['titre'],
                            'rating': movie['Rating']
                        }

                else:
                    st.write(f"No image found for {movie['titre']}")

                # Display details of the selected movie below it
                if rec_imdb_id in selected_movies:
                    selected_movie = selected_movies[rec_imdb_id]
                    selected_movie_fr = selected_movie['movie_info_fr']
                    selected_movie_en = selected_movie['movie_info_en']
                    
                    with st.expander("Détails du Film", expanded=True):
                        if selected_movie_fr.get('poster_path') or selected_movie_en.get('poster_path'):
                            st.image(f"https://image.tmdb.org/t/p/w500{selected_movie_fr.get('poster_path') or selected_movie_en.get('poster_path')}", 
                                     caption=selected_movie_fr['title'], width=100)
                        else:
                            st.image(r"C:\Users\DELL 7480\Documents\WILD CODE SCHOOL\Projet 2\Projet2-movies\hulk.jpeg", 
                                     caption=f"No poster available for '{selected_movie_fr['title']}', so here's the return of SUUUHULK", width=110)

                        # Truncate overview to 100 words and add '...' after the last word if it exceeds 100 words
                        overview = selected_movie_fr.get('overview') or selected_movie_en.get('overview', 'No overview available')
                        overview_words = overview.split()
                        truncated_overview = ' '.join(overview_words[:30]) + (' ...' if len(overview_words) > 50 else '')
                        
                        # Display movie details
                        st.markdown(f"### {selected_movie['title']}")
                        st.write("**A propos du Film 🎬**")
                        st.write(f"**Genre:** {', '.join([genre['name'] for genre in selected_movie_fr.get('genres', [])])}")
                        st.write(f"**Résumé:** {truncated_overview}")
                        st.write(f"**Date de sortie :** {selected_movie_fr.get('release_date', 'No release date available')}")
                        st.write(f"**Note:** {selected_movie_fr.get('vote_average', 'No rating available')}")
                        st.write(f"**Durée :** {selected_movie_fr.get('runtime', 'No runtime available')} min")
                        st.write("**ENJOY :)**")

    else:
        st.write(f"Aucun film trouvé pour le genre {genre}")





