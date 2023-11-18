from fastapi import FastAPI
import pandas as pd
from datetime import datetime
from typing import Dict
from typing import List, Dict
from collections import defaultdict

app = FastAPI()

PlayTimeGenre_data = pd.read_csv("Archivos_para_API/PlayTimeGenre.csv")
UserForGenre_data = pd.read_csv("Archivos_para_API/UserForGenre.csv")
UsersRecommend_data = pd.read_csv("Archivos_para_API/UsersRecommend.csv")
SentimentAnalysis_data = pd.read_csv("Archivos_para_API/SentimentAnalysis.csv")

@app.get("/")
def homepage():
    return {"Mensaje": "¡Bienvenido a la aplicación de análisis de videojuegos!"}

@app.get("/playtime_genre/{genero}")
def PlayTimeGenre(genero: str):
    # Filtra los juegos del género especificado
    playtime_genre_Data = PlayTimeGenre_data[PlayTimeGenre_data['genres'] == genero]

    if playtime_genre_Data.empty:
        return {"Año de lanzamiento con más horas jugadas para Género " + genero: "No se encontraron juegos del género " + genero}
    
    # Agrupa por año y calcula las horas jugadas totales
    year_playtime = playtime_genre_Data.groupby('release_date')['playtime_forever'].sum()

    if year_playtime.empty:
        return {"Año de lanzamiento con más horas jugadas para Género " + genero: "No hay datos de horas jugadas para el género " + genero}
    
    # Encuentra el año con más horas jugadas
    max_year = year_playtime.idxmax()
    
    # Convierte el valor 'max_year' a un entero de Python antes de devolverlo
    max_year = int(max_year)

    return {"Año de lanzamiento con más horas jugadas para Género " + genero: max_year}

@app.get("/user_for_genre/{genero}")
def user_for_genre(genero: str):
    # Filtrar los datos para el género seleccionado
    genre_games = UserForGenre_data[UserForGenre_data['genres'] == genero]

    # Mensaje en caso que no se encuentre el género seleccionado
    if genre_games.empty:
        return {"Mensaje": f"No se encontraron juegos del género {genero}"}

    # Obtener el usuario con más horas jugadas
    max_hours_user = genre_games.loc[genre_games['playtime_forever'].idxmax(), 'user_id']

    # Agrupar por año y sumar las horas jugadas
    hours_by_year = genre_games.groupby('release_date')['playtime_forever'].sum().reset_index()

    # Convertir el resultado a formato JSON
    result = {
        "Usuario con más horas jugadas para Género {}".format(genero): max_hours_user,
        "Horas jugadas": [{"Año": int(year), "Horas": int(hours)} for year, hours in zip(hours_by_year['release_date'], hours_by_year['playtime_forever'])]
    }

    return result
@app.get("/UsersRecommend/{year}")
def get_users_recommend(year: int):
    # Filtrar los datos del DataFrame por el año proporcionado
    game_filtered = UsersRecommend_data[UsersRecommend_data['release_date'] == year]

    # Verificar si el DataFrame está vacío después de filtrar por año
    if game_filtered.empty:
        return {"message": "No hay datos para el año proporcionado"}

    # Obtener los tres juegos con mayor valor según la columna 'total_count_recommend'
    top_games = game_filtered.nlargest(3, 'total_count_recommend')

    # Imprimir el contenido de top_games para depuración
    print(top_games)

    # Verificar la longitud de top_games antes de acceder a las filas
    if len(top_games) >= 2:
        retorno = [
            {"Puesto 1": top_games.iloc[0]['item_name']},
            {"Puesto 2": top_games.iloc[1]['item_name']},
            {"Puesto 3": top_games.iloc[2]['item_name']}
        ]
    else:
        retorno = [{"message": "No hay suficientes juegos para clasificar"}]

    return {"top_games": retorno}

@app.get("/UsersNotRecommend/{year}")
def get_users_not_recommend(year: int):
    # Filtrar los datos del DataFrame por el año proporcionado
    game_filtered = UsersRecommend_data[UsersRecommend_data['release_date'] == year]

    # Verificar si el DataFrame está vacío después de filtrar por año
    if game_filtered.empty:
        return {"message": "No hay datos para el año proporcionado"}

    # Obtener los tres juegos con menor valor según la columna 'total_count_recommend'
    bottom_games = game_filtered.nsmallest(3, 'total_count_recommend')

    # Imprimir el contenido de top_games para depuración
    print(bottom_games)

    # Verificar la longitud de top_games antes de acceder a las filas
    if len(bottom_games) >= 2:
        retorno = [
            {"Puesto 1": bottom_games.iloc[0]['item_name']},
            {"Puesto 2": bottom_games.iloc[1]['item_name']},
            {"Puesto 3": bottom_games.iloc[2]['item_name']}
        ]
    else:
        retorno = [{"message": "No hay suficientes juegos para clasificar"}]

    return {"bottom_games": retorno}

@app.get("/sentimentanalysis/{year}")
def sentiment_analysis(year: int):
    # Filtrar los datos del DataFrame por el año proporcionado
    game_filtered = SentimentAnalysis_data[SentimentAnalysis_data['release_date'] == year]

    # Verificar si el DataFrame está vacío después de filtrar por año
    if game_filtered.empty:
        return {"message": "No hay datos para el año proporcionado"}
    
    # Inicializar un diccionario para contar las categorías de sentimiento
    conteo_sentimientos = defaultdict(int)

    # Contar las categorías de sentimiento
    for index, reseña in game_filtered.iterrows():
        sentimiento = reseña["sentiment_analysis"]
        if sentimiento == 0:
            conteo_sentimientos["Neutral"] += 1
        elif sentimiento == 1:
            conteo_sentimientos["Positive"] += 1
        elif sentimiento == 2:
            conteo_sentimientos["Negative"] += 1

    # Formatear el resultado según el ejemplo proporcionado
    return_sentimentanalysis = { "Negative": conteo_sentimientos["Negative"], 
                                "Neutral": conteo_sentimientos["Neutral"], 
                                "Positive": conteo_sentimientos["Positive"] }

    return return_sentimentanalysis

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)