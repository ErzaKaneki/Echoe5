document.addEventListener("DOMContentLoaded", function() {
    // Fetch the environment variable value from the .env file
    require('dotenv').config();
    const clientId = process.env.GOOGLE_OAUTH2_KEY;

    // Inject the environment variable into the HTML element
    const clientIdElement = document.getElementById("g_id_onload");
    if (clientIdElement) {
        clientIdElement.setAttribute("data-client_id", clientId);
    }
});