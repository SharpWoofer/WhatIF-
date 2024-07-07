document.addEventListener('DOMContentLoaded', () => {
    const checkbox = document.getElementById('checkbox');

    // Apply the saved theme on page load
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-theme');
        checkbox.checked = true; // Ensure the checkbox is in the correct state
    } else {
        document.body.classList.add('light-theme');
        checkbox.checked = false; // Ensure the checkbox is in the correct state
    }

    checkbox.addEventListener('change', function() {
        if(this.checked) {
            document.body.classList.remove('light-theme');
            document.body.classList.add('dark-theme');
            localStorage.setItem('theme', 'dark'); // Save the theme preference
        } else {
            document.body.classList.remove('dark-theme');
            document.body.classList.add('light-theme');
            localStorage.setItem('theme', 'light'); // Save the theme preference
        }
    });
});