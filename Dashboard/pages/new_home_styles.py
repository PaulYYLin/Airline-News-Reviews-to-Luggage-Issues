# styles for the landing page
def load_css():
    return """
<style>
/* ====================
    CSS VARIABLES - Color scheme and theme settings
==================== */
    :root {
    /* Background colors */
    --bg-gray: #d3d3d3;

    /* Text colors */
    --heading-skyblue: #1e90ff;
    --text-white: #ffffff;

    /* Accent and interactive elements */
    --accent-blue: #004080;
    --border-white: #ffffff;

    /* Colours from styles.py */

    /* Background colors */
    --bg-primary: rgba(0, 0, 0, 0.9);
    --bg-secondary: rgba(30, 30, 30, 0.8);
    
    /* Text colors */
    --text-primary: rgba(255, 255, 255, 0.9);
    --text-secondary: rgba(220, 220, 220, 0.7);
    
    /* Accent and interactive elements */
    --accent-color: rgba(255, 215, 0, 0.7);
    --border-color: rgba(255, 255, 255, 0.2);
    --shadow-color: rgba(255, 255, 255, 0.3);

    /* UI Components */
    --input-bg: rgba(30, 30, 30, 0.7);
    --message-user-bg: rgba(70, 70, 70, 0.6);
    --message-bot-bg: rgba(50, 50, 50, 0.6);
    --button-bg: rgba(50, 50, 50, 0.5);
    --button-hover-bg: rgba(80, 80, 80, 0.7);
}

/* ====================
    GLOBAL STYLES - Base application appearance
==================== */
.stApp {
    background: var(--bg-gray);
    color: var(--text-primary);
}

/* ====================
    CHAT INTERFACE - Chat containers and messages
==================== */
.chat-container {
    background: linear-gradient(to bottom, var(--bg-secondary), rgba(40, 40, 40, 0.6));
    border-radius: 15px;
    border: 2px solid var(--border-color);
    box-shadow: 0 0 15px var(--shadow-color);
    max-width: 800px;
    margin: 20px auto 20px auto;
    padding: 20px;
    height: 450px;
    overflow-y: auto;
}

/* User message bubble */
.user-message {
    background-color: var(--message-user-bg);
    border-radius: 15px 15px 3px 15px;
    padding: 12px 18px;
    margin: 10px 0 10px auto;
    max-width: 75%;
    display: inline-block;
    float: right;
    clear: both;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    animation: fadeIn 0.5s ease-in-out;
}

/* Bot message bubble */
.bot-message {
    background-color: var(--message-bot-bg);
    border-radius: 15px 15px 15px 3px;
    padding: 12px 18px;
    margin: 10px 0;
    max-width: 75%;
    display: inline-block;
    float: left;
    clear: both;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
    animation: fadeIn 0.5s ease-in-out;
}


/* ====================
    CLASSES - Class appearances
==================== */

.landing-div {
    background-color: var(--heading-skyblue);
    border: solid 5px var(--text-white);
    border-radius: 15px;
    text-align: center;
    padding-left: 20px;
    padding-right: 20px;
}

.landing-div .landing-title {
    font-size: 3rem;
    color: var(--text-white);
    margin: 0;
}

.custom-grid-container {
    display: grid;
    grid-template-columns: 5rem auto 5rem;
    grid-template-rows: auto auto auto;
    gap: 10px;
    margin: 20px;
    background-color: var(--text-white);
    padding: 20px;
    border-radius: 15px;
    box-sizing: border-box;
    align-content: center;
}

.custom-grid-row {
    display: contents;
}

.custom-column {
    display: flex;
    background-color: var(--accent-blue);
    color: var(--text-white);
    border-radius: 15px;
    padding: 5px;
    text-align: center;
    justify-content:center;
    align-items: center;
}

.custom-column .column-heading{
    font-size: 2.5rem;
}

.custom-column-full-span {
    grid-column: span 3;
    text-align: center;
    background-color: var(--text-white);
    color: var(--accent-blue);
}

.custom-column-full-span .subtitle {
    color: var(--accent-blue);
    font-style: italic;
    font-size: 1.5rem;
}

</style>
"""