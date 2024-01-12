function getRecommendations() {
    var movieInput = document.getElementById('movieInput').value;
    var numRecommendations = document.getElementById('numRecommendations').value;

    // Show loader
    showLoader();

    // Perform AJAX request to Flask API
    fetch(`/recommend?movie=${movieInput}&num=${numRecommendations}`)
        .then(response => response.json())
        .then(data => {
            // Hide loader
            hideLoader();

            // Display first recommendation information
            displayFirstRecommendation(data.titles[0], data.posters[0]);

            // Display main recommendations
            displayRecommendations(data.titles.slice(1), data.posters.slice(1));
        })
        .catch(error => console.error('Error:', error));
}

function showLoader() {
    var loaderContainer = document.getElementById('loaderContainer');
    loaderContainer.style.display = 'flex';
}

function hideLoader() {
    var loaderContainer = document.getElementById('loaderContainer');
    loaderContainer.style.display = 'none';
}

function displayFirstRecommendation(title, poster) {
    var firstRecommendationContainer = document.getElementById('firstRecommendation');
    firstRecommendationContainer.innerHTML = '';

    var card = createMovieCard(title, poster);
    card.style.width = '150px'
    card.style.alignItems ='center'
    card.style.justifyContent ='center'
    firstRecommendationContainer.appendChild(card);

    // Remove the 'hidden' class to make the first recommendation visible
    firstRecommendationContainer.classList.remove('hidden');
}

function displayRecommendations(recommendations, recommendations_poster) {
    var recommendationList = document.getElementById('recommendationList');
    recommendationList.innerHTML = '';

    for (var i = 0; i < recommendations.length; i++) {
        var card = createMovieCard(recommendations[i], recommendations_poster[i]);
        card.style.width = '150px'
        recommendationList.appendChild(card);
    }

    var recommendationsDiv = document.getElementById('recommendations');
    recommendationsDiv.classList.remove('hidden');
}

function createMovieCard(title, poster) {
    var card = document.createElement('div');
    card.className = 'movie-card';

    var img = document.createElement('img');
    img.src = poster;
    img.alt = title;
    card.appendChild(img);

    var movieTitle = document.createElement('p');
    movieTitle.textContent = title;
    card.appendChild(movieTitle);

    return card;
}