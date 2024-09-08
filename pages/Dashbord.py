import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.dates as mdates
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go
from PlotViz import (nbre_film_décennie)
from PlotViz import (dataviz_avant_apres)
from PlotViz import (distribution_notes)
from PlotViz import (vote_décennie )
from PlotViz import (nbre_films_genre )
from PlotViz import (nbre_films_notes_pays)


title_html = """
    <div style="margin-top: 50px; text-align: center; color: Maroon; font-family: Times; font-size: 60px;">
        Système de Recommandation de Films
    </div>
    """
st.markdown(title_html, unsafe_allow_html=True)

st.image(r"C:\Users\DELL 7480\Documents\WILD CODE SCHOOL\Projet 2\Streamlit_P2\cinéma-removebg-preview.png")


presente_html = """
    <div style="margin-top: 50px; text-align: center; color: Maroon; font-family: Times; font-size: 25px;">
        Présenté par : Linda - Lala - Thomas
    </div>
    """
st.markdown(presente_html, unsafe_allow_html=True)


st.markdown("<div style='margin-top: 100px; text-align: center; background: linear-gradient(to bottom, #6b0303, #7d0c0c); border-radius: 10px; font-size : 150%; padding: 20px;'><em>Notre client, les dirigeants d'un cinéma en perte de vitesse situé dans la Creuse nous ont contactés. Ils ont décidé de passer le cap du digital en créant un site Internet taillé pour les locaux. Voici notre analyse afin de créer leur app...</em></div>", unsafe_allow_html=True)




movies_parquet = pd.read_parquet(r"C:\Users\DELL 7480\Documents\WILD CODE SCHOOL\Projet 2\Projet2-movies\movies2.parquet")
movies_cleaned = pd.read_parquet(r"C:\Users\DELL 7480\Documents\WILD CODE SCHOOL\Projet 2\Projet2-movies\movies_cleaned2.parquet")

df1= movies_parquet
df2 = movies_cleaned



illustration_html = """
    <div style="margin-top: 100px; text-align: center; color: white; font-family: Arial Black; font-style: italic; font-size: 48px;">
        Illustrations Graphiques
    </div>
    """
st.markdown(illustration_html, unsafe_allow_html=True)

space_html = """
    <div style="margin-top: 100px; text-align: center; color: white; font-family: Arial Black; font-style: italic; font-size: 48px;">
        
    </div>
    """
st.markdown(space_html, unsafe_allow_html=True)
    # Appel de votre fonction

 # Affichage du graphique dans Streamlit

st.markdown("<div style='margin-top: 100px; text-align: center; background: linear-gradient(to bottom, #6b0303, #7d0c0c); border-radius: 10px;'>Dans un premier temps on avait pris le parti de retenir que les films au dessus de la médiane, mais après réflexion nous avons décidé détendre un peu avant celle-ci.</div>", unsafe_allow_html=True)
fig12 = distribution_notes(df1, df2)

col1, col2 = st.columns(2)

with col1:
    fig12[0]

with col2:
    fig12[1]


st.markdown("<div style='margin-top: 100px; text-align: center; background: linear-gradient(to bottom, #6b0303, #7d0c0c); border-radius: 10px;'>Graphique sur le nombre de films, qui nous a permis d'avoir une vue d'ensemble pour aider à la prise de décision.</div>", unsafe_allow_html=True)

fig = nbre_film_décennie(df1, df2)
fig


st.markdown("<div style='margin-top: 100px; text-align: center; background: linear-gradient(to bottom, #6b0303, #7d0c0c); border-radius: 10px;'>Ce graphique nous a aidé à comptabiliser le nombre de vote sur la période que nous souhaitions conserver.</div>", unsafe_allow_html=True)
fig31 = vote_décennie (df1, df2)
fig31



st.markdown("<div style='margin-top: 100px; text-align: center; background: linear-gradient(to bottom, #6b0303, #7d0c0c); border-radius: 10px;'>L'affichage des genres nous a permis de constater les genres les plus représentés dans notre base de données.</div>", unsafe_allow_html=True)
fig41 = nbre_films_genre(df1, df2)
fig41

  

