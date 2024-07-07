document.addEventListener("DOMContentLoaded", function() {
    let scrollAmount = 0;
    const carousel = document.querySelector('.carousel');
    setInterval(() => {
        if(scrollAmount < carousel.scrollWidth - carousel.clientWidth) {
            scrollAmount += 200; // Scroll by 200px every 2 seconds
        } else {
            scrollAmount = 0; // Reset scroll amount to start
        }
        carousel.scrollTo({left: scrollAmount, behavior: 'smooth'});
    }, 2000);
});