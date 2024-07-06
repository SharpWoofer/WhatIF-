from flask import Flask, request, render_template, jsonify
from markupsafe import Markup, escape
import re
import asyncio
import requests
from huggingface_hub import InferenceClient
from dotenv import find_dotenv, load_dotenv
from concurrent.futures import ThreadPoolExecutor
import os

load_dotenv(find_dotenv())
app = Flask(__name__)

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
TMDB_API_KEY = '78842726cdcd13c5f4fbe6b07af1b1d5'
TMDB_BASE_URL = 'https://api.themoviedb.org/3'

async def fetch_movie_overview(title):
    search_url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={title}"
    response = requests.get(search_url)
    data = response.json()
    if data['results']:
        return data['results'][0]['overview']
    else:
        return "No overview found."
    
@app.route('/search_movies', methods=['GET'])
async def search_movies():
    query = request.args.get('query', '')
    search_url = f"{TMDB_BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={query}"
    response = requests.get(search_url)
    data = response.json()
    movies = [movie['title'] for movie in data['results']]
    return jsonify(movies)

async def fetch_trending_movies():
    trending_url = f"{TMDB_BASE_URL}/trending/movie/day?api_key={TMDB_API_KEY}"
    response = requests.get(trending_url)
    data = response.json()
    return data['results'][:10]  # Return top 10 trending movies


async def generate_plot(overview):
    prompt = "Keeping the tone of the movie and its characters intact, generate another plot that would fit based on the original: " + overview + "Always start with the title prased as Title: " "" 

    def sync_generate_plot():
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
        html_output = Markup(generated_content.replace("\n", "<br>"))
        return html_output

    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor() as pool:
        generated_content = await loop.run_in_executor(pool, sync_generate_plot)
    # Use regular expression to extract the title
    title_match = re.search(r'"Title: (.*?)"', generated_content)
    if title_match:
        title_new = title_match.group(1)  # Extract the title
        plot = generated_content.replace(title_match.group(0), '').strip()  # Remove the title from the plot
    else:
        title_new = "Unknown Title"
        plot = generated_content

    return title_new, plot
    # return generated_content
    

@app.route('/', methods=['GET'])
def index():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    trending_movies = loop.run_until_complete(fetch_trending_movies())
    return render_template('index.html', trending_movies=trending_movies)

@app.route('/generate_plot', methods=['POST'])
def generate_plot_route():
    movie_title = request.form['movie_title']
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    movie_overview = loop.run_until_complete(fetch_movie_overview(movie_title))
    if movie_overview != "No overview found.":
        title_new, generated_plot = loop.run_until_complete(generate_plot(movie_overview))
        print(title_new)
        # vprint(generated_plot) -- Debugging
    else:
        title_new = "Unknown Title"
        generated_plot = "Unable to generate plot. Movie overview not found."
    return render_template('result.html', plot=generated_plot, title=movie_title, title_new=title_new)

if __name__ == '__main__':
    app.run(debug=True)