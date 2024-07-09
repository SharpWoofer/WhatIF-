from flask import Flask, request, render_template, jsonify
from markupsafe import Markup, escape
import re
import requests
from huggingface_hub import InferenceClient
from dotenv import find_dotenv, load_dotenv
import os

load_dotenv(find_dotenv())
app = Flask(__name__)

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

def fetch_movie_overview(title):
    search_url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(search_url)
    data = response.json()
    if data['results']:
        return data['results'][0]['overview']
    else:
        return "No overview found."

@app.route('/search_movies', methods=['GET'])
def search_movies():
    query = request.args.get('query', '')
    search_url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(search_url)
    data = response.json()
    movies = [movie['title'] for movie in data['results']]
    return jsonify(movies)

def fetch_trending_movies():
    trending_url = f"{TMDB_BASE_URL}/trending/movie/day?api_key={TMDB_API_KEY}"
    response = requests.get(trending_url)
    data = response.json()
    # Include poster path in the results
    for movie in data['results'][:10]:
        movie['poster_path'] = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
    return data['results'][:10]  # Return top 10 trending movies with poster paths

def generate_plot(overview, seed):
    # Incorporate the seed into the prompt
    prompt = f"Seed: {seed}. Keeping the tone of the movie and its characters intact, generate another plot that would fit based on the original: {overview} Always start with the title phrased as Title: "

    client = InferenceClient(
        "mistralai/Mistral-7B-Instruct-v0.3",
        token=os.getenv("HUGGINGFACE_API_TOKEN"),
    )
    generated_content = ""
    for message in client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=30000,
        stream=True,
    ):
        generated_content += message.choices[0].delta.content
    print(generated_content)
    # Use regular expression to extract the title
    title_match = re.search(r'Title: (.*?)\n', generated_content)
    if title_match:
        title_new = title_match.group(1)  # Extract the title
        plot = generated_content.replace(title_match.group(0), '').strip()  # Remove the title from the plot
        return title_new, Markup(plot.replace("\n", "<br>"))
    else:
        title_new = "Unknown Title"
        html_output = Markup(generated_content.replace("\n", "<br>"))
        return title_new, html_output
    
@app.route('/trending_movies', methods=['GET'])
def get_trending_movies():
    return jsonify(fetch_trending_movies())

@app.route('/', methods=['GET'])
def index():
    trending_movies = fetch_trending_movies()
    return render_template('index.html', trending_movies=trending_movies)

@app.route('/generate_plot', methods=['POST'])
def generate_plot_route():
    movie_title = request.form['movie_title']
    seed = request.form.get('seed', None)
    
    movie_overview = fetch_movie_overview(movie_title)
    if movie_overview != "No overview found.":
        title_new, generated_plot = generate_plot(movie_overview, seed)
        print(title_new)
    else:
        title_new = "Unknown Title"
        generated_plot = "Unable to generate plot. Movie overview not found."
    
    return render_template('result.html', plot=generated_plot, title=movie_title, title_new=title_new)


if __name__ == '__main__':
    app.run()
