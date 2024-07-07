document.addEventListener('DOMContentLoaded', function() {
    const carouselContent = document.querySelector('.carousel-content');
    const inputBox = document.querySelector('#movieTitleInput'); // Updated to select the specific input box by ID

    // Fetch trending movies and populate the carousel
    fetch('/trending_movies') // Adjust the URL based on your backend route
        .then(response => response.json())
        .then(movies => {
            movies.forEach(movie => {
                const img = document.createElement('img');
                img.src = movie.poster_path; // Set the source of the image to the movie's poster path
                img.alt = movie.title; // Use the movie's title as alt text
                img.classList.add('movie-poster'); // Add class for styling and event listener
                img.addEventListener('click', () => {
                    inputBox.value = movie.title; // Set the movie title in the input box on click
                });
                carouselContent.appendChild(img); // Append the image to the carousel content
            });
        })
        .catch(error => console.error('Error loading movies:', error));
});