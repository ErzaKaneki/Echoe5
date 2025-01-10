function toggleDarkMode() {
	const currentTheme = document.documentElement.getAttribute('data-theme');
	const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

	document.documentElement.setAttribute('data-theme', newTheme);
	localStorage.setItem('theme', newTheme);

	//Update button icon
	const icon = document.getElementById('dark-mode-icon');
	icon.className = newTheme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
}

//Set initial theme based on localStorage or system preference
document.addEventListener('DOMContentLoaded', () => {
	const savedTheme = localStorage.getItem('theme');
	const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
	const theme = savedTheme || (prefersDark ? 'dark' : 'light');

	document.documentElement.setAttribute('data-theme', theme);
	const icon = document.getElementById('dark-mode-icon');
	icon.className = theme === 'dark' ? 'fas fa-moon' : 'fas fa-sun';
});
