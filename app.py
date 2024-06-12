import os
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient 
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateTimeField
from wtforms.validators import DataRequired,Length, Email,EqualTo, ValidationError

SECRET_KEY = os.urandom(32)

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
client = MongoClient('localhost', 27017)
db = client['ProjectDBMS']
collection = db['TMDB']

class BasicForm(FlaskForm):
    ids = StringField("ID",validators=[DataRequired()])

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/task1.html")
def task1():
    return render_template("task1.html")

@app.route("/task2.html")
def task2():
     return render_template("task2.html")

@app.route("/task3.html")
def task3():
     return render_template("task3.html")


keyword_lists = {
    "Drama": [
        "love", "relationships", "family", "friendship", "betrayal", "emotions", "heartbreak", "tragedy",
        "redemption", "sacrifice", "struggle", "identity", "coming of age", "growth", "conflict", "humanity",
        "morality", "society", "class", "race", "identity", "dreams", "ambition", "hope", "despair",
        "resilience", "loneliness", "community", "acceptance", "rejection", "courage", "fear", "regret",
        "forgiveness", "empathy", "compassion", "loss", "grief", "joy", "happiness", "suffering", "survival",
        "choices", "growth", "reflection", "change", "legacy", "traditions", "strife", "resolution"
    ],

    "Crime": [
        "detective", "investigation", "murder", "robbery", "heist", "gang", "criminal", "underworld", "mafia",
        "organized crime", "crime scene", "forensics", "evidence", "witness", "interrogation", "sleuth", "whodunit",
        "crime boss", "illegal", "money laundering", "corruption", "betrayal", "drug", "trafficking", "conspiracy",
        "homicide", "suspense", "law enforcement", "prison", "fugitive", "intrigue", "blackmail", "undercover",
        "double-cross", "alibi", "sting operation", "crime spree", "smuggling", "bribery", "forgery", "puzzle",
        "mastermind", "cat-and-mouse", "snitch", "witness protection", "vigilante", "frame-up", "ransom", "hostage"
    ],

    "Comedy": [
        "humor", "laughter", "funny", "jokes", "wit", "hilarity", "comical", "satire", "parody", "spoof",
        "slapstick", "gags", "lighthearted", "amusing", "entertainment", "chuckles", "witty", "farce", "irony",
        "sarcasm", "whimsical", "quirky", "goofy", "ridiculous", "absurd", "eccentric", "silly", "zany", "wacky",
        "ridiculous", "hilarious", "clever", "jovial", "playful", "joyful", "whimsical", "fun-loving", "light-hearted",
        "cheeky", "irreverent", "mischievous", "offbeat", "bizarre", "eccentric", "nutty", "droll", "frolicsome",
        "quirky", "tongue-in-cheek", "zesty"
    ],

    "Animation": [
        "animated", "cartoon", "animation", "animated film", "animated series", "cartoon movie", "cartoon series",
        "animation studio", "animated characters", "cartoon characters", "animation industry", "cartoon industry",
        "animated feature", "cartoon feature", "animated short", "cartoon short", "animation style", "cartoon style",
        "animation techniques", "cartoon techniques", "computer animation", "traditional animation", "2d animation",
        "3d animation", "stop-motion animation", "clay animation", "cell animation", "digital animation", "motion graphics",
        "character animation", "animated storytelling", "animated adventure", "animated comedy", "animated drama",
        "animated fantasy", "animated musical", "animated science fiction", "animated action", "animated family",
        "animated children", "animated animals", "animated creatures", "animated world", "fantasy animation", "sci-fi animation",
        "adventure animation", "comedy animation", "family animation"
    ],

    "Horror": [
        "horror", "fear", "scary", "terrifying", "creepy", "spooky", "frightening", "chilling", "gory", "macabre",
        "supernatural", "haunted", "dark", "eerie", "ghost", "monster", "creature", "zombie", "vampire", "werewolf",
        "demon", "possession", "blood", "gore", "scream", "nightmare", "terror", "panic", "shock", "suspense", 
        "thriller", "jump scare", "psychological", "slasher", "gothic", "horrific", "dread", "gruesome", "spine-chilling",
        "bone-chilling", "hair-raising", "heart-stopping", "horror film", "horror genre", "horror story", "horror movie",
        "horror fiction", "horror novel", "horror series", "horror creature", "horror atmosphere"
    ],

    "Music": [
        "music", "musical", "song", "melody", "rhythm", "tune", "harmony", "beat", "lyrics", "instrument", 
        "concert", "band", "orchestra", "singer", "musician", "composition", "performance", "stage", "guitar", 
        "piano", "drums", "bass", "vocals", "chorus", "verse", "bridge", "hook", "refraim", "solo", "duet", 
        "ensemble", "soundtrack", "score", "recording", "live", "acoustic", "electric", "classical", "jazz", 
        "blues", "rock", "pop", "hip hop", "rap", "folk", "country", "reggae", "electronic", "alternative", "indie"
    ],

    "Romance": [
        "love", "relationships", "romantic", "affection", "passion", "intimacy", "heartfelt", "chemistry", "connection", 
        "flirting", "dating", "couples", "romance", "emotion", "feelings", "attraction", "devotion", "desire", "seduction", 
        "tenderness", "adoration", "courtship", "love story", "kiss", "hug", "candlelight", "whisper", "cuddle", "proposal", 
        "wedding", "engagement", "heartbreak", "betrayal", "forbidden love", "unrequited love", "passionate", "swoon", 
        "infatuation", "longing", "yearning", "affair", "rendezvous", "rom-com", "love triangle", "soulmate", "falling in love", 
        "romantic gesture", "true love", "first love", "broken heart"
    ],

    "Thriller": [
        "suspense", "tension", "mystery", "intrigue", "danger", "adrenaline", "action-packed", "twist", "turn", 
        "plot", "unexpected", "chase", "escape", "survival", "fear", "anxiety", "edge-of-your-seat", "nail-biting", 
        "sneak", "surprise", "puzzle", "investigation", "conspiracy", "criminal", "detective", "thriller", 
        "psychological", "murder", "crime", "killer", "villain", "hero", "heroine", "cat-and-mouse", "intense", 
        "eerie", "creepy", "gripping", "nerve-racking", "suspicion", "dark", "sinister", "foreboding", "mysterious", 
        "unsettling", "thrilling", "scream", "shocking", "adversary", "revelation"
    ]
}

def predict_genre(overview):
    # Count occurrences of keywords related to each genre
    genre_counts = {genre: sum(overview.lower().count(keyword) for keyword in keywords) 
                    for genre, keywords in keyword_lists.items()}
    # Predict the genre with the maximum count
    predicted_genre = max(genre_counts, key=genre_counts.get)
    return predicted_genre

@app.route('/submit-task-1', methods=['POST','GET'])
def rank_production_countries():
    selected_year = request.form.get('selected_year')
    selected_genre = request.form.get('selected_genre')
    form = BasicForm()
    pipeline = [{"$match": {"$expr": {"$eq": [{"$year": "$release_date"}, int(selected_year)]}}},
                {"$project": {"title": 1,"production_countries": 1, "overview": 1, "popularity": 1, "vote_average": 1, "production_companies": 1}}, 
                {"$limit": 100},
                {"$sort": {"vote_average": -1, "popularity": -1}}]
    
    result = list(collection.aggregate(pipeline))
    # print(result)
    
    matched_movie=[]
    for doc in result:
        overview = doc.get('overview', '')
        predicted_genre = predict_genre(overview)
        doc['predicted_genre'] = predicted_genre
        if doc['predicted_genre'] == selected_genre:
            matched_movie.append(doc)

    data = []
    for i, doc in enumerate(matched_movie):
        doc['rank'] = i + 1
    for doc in matched_movie:
            data.append([doc['title'],doc['popularity'],doc['rank'],doc['production_countries'],doc['production_companies']])
    
    grouped_data = {}
    country_popularity={}
    for item in data:
        title, popularity, rank, production_countries,production_companies = item
        production_countries = production_countries.split(',')
        production_countries = [country.strip() for country in production_countries]
        for country in production_countries:
            if country not in grouped_data:
                grouped_data[country] = []
                country_popularity[country] = 0
            grouped_data[country].append([title,popularity,production_companies,rank])
    
    for country, movies in grouped_data.items():
        for movie in movies:
            country_popularity[country] += movie[1]
    sorted_country_popularity = dict(sorted(country_popularity.items(), key=lambda item: item[1], reverse=True))
    sliced_dict = dict(list(sorted_country_popularity.items())[:5])
    return render_template("task1_response.html",response_data=grouped_data, data2 = sliced_dict,form = form)

@app.route("/task1_response")
def task1_response():
    return render_template("task1_response.html")

@app.route('/submit-task-2', methods=['POST','GET'])
def get_popular_genres_by_language():
    selected_year = request.form.get('selected_year')
    #print(selected_year)
    form = BasicForm()
    if not selected_year:
        return jsonify({"error": "Year is required."}), 400

    pipeline = [{"$match": {"$expr": {"$eq": [{"$year": "$release_date"}, int(selected_year)]}}},
                {"$project": {"title": 1,"spoken_languages": 1, "overview": 1, "popularity": 1, "vote_average": 1}}, 
                {"$limit": 100},
                {"$sort": {"popularity": -1}}]
    
    result = list(collection.aggregate(pipeline))
    # print(result)
    
    for doc in result:
        overview = doc.get('overview', '')
        predicted_genre = predict_genre(overview)
        doc['predicted_genre'] = predicted_genre

    data = []   
    for i, doc in enumerate(result):
        doc['rank'] = i + 1
    for doc in result:
        data.append([doc['title'],doc['popularity'],doc['rank'],doc['spoken_languages'],doc['predicted_genre']])
    
    grouped_data = {}
    for title, popularity, rank, spoken_languages,predicted_genre in data:
        spoken_languages = spoken_languages.split(',')
        spoken_languages = [lan.strip() for lan in spoken_languages]
        
        for language in spoken_languages:
            if language not in grouped_data:
                grouped_data[language] = [] 
            grouped_data[language].append([title, popularity, rank, predicted_genre])
                    
    return render_template("task2_response.html",response_data=grouped_data, form = form)

@app.route("/task2_response")
def task2_response():
    return render_template("task2_response.html")

@app.route('/submit-task-3', methods=['POST','GET'])
def get_movie_with_keyword():
    selected_keyword = request.form.get('selected_genre')
   # print(selected_keyword)
    form = BasicForm()
    if not selected_keyword or selected_keyword not in keyword_lists:
        return jsonify({"error": "Invalid or missing keyword."}), 400
    selected_list = keyword_lists[selected_keyword]

    pipeline = [
        {"$match": {"overview": {"$regex": "|".join(selected_list), "$options": "i"}, "revenue": {"$gt": 0}, "budget": {"$gt": 0}}},
        {"$project": {"title": 1, "overview": 1, "revenue": 1, "budget": 1, "profit": {"$subtract": ["$revenue", "$budget"]}}},
        {"$sort": {"profit": -1}},
        {"$limit": 5}
    ]
    result = list(collection.aggregate(pipeline))
    #print(result)
    data = []
    response_data = {'result': result, 'message': 'Task 3 data sent successfully'}
    for ele in response_data['result']:
        data.append([ele['title'],ele['profit']])
    response_data = [{'title': item[0], 'profit': item[1]} for item in data]  
    
    return render_template("task3_response.html",response_data=response_data, form = form)

@app.route("/task3_response")
def task3_response():
    return render_template("task3_response.html")


if __name__ == "__main__":
    app.run(debug=True)







