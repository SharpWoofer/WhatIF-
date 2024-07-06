document.addEventListener("DOMContentLoaded", function() {
    const input = document.getElementById("movieTitleInput");
    const autocompleteList = document.getElementById("autocompleteList");

    input.addEventListener("input", function() {
        const query = this.value;
        if (!query) {
            autocompleteList.innerHTML = '';
            return;
        }
        fetch(`/search_movies?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(movies => {
                autocompleteList.innerHTML = '';
                movies.forEach(movie => {
                    const div = document.createElement("div");
                    div.textContent = movie;
                    div.addEventListener("click", function() {
                        input.value = movie;
                        autocompleteList.innerHTML = '';
                    });
                    autocompleteList.appendChild(div);
                });
            });
    });
});