const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const micBtn = document.getElementById('mic-btn');

// Append a message to the chat window
function appendMessage(content, sender = 'bot') {
    const bubble = document.createElement('div');
    bubble.classList.add(sender === 'user' ? 'user-bubble' : 'bot-bubble');
    bubble.textContent = content;
    chatWindow.appendChild(bubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// Show typing animation
function showTyping() {
    const typingBubble = document.createElement('div');
    typingBubble.classList.add('bot-bubble', 'bubble-typing');
    typingBubble.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    chatWindow.appendChild(typingBubble);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return typingBubble;
}

// Function to handle sending messages
async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    // Append user message
    appendMessage(query, 'user');
    userInput.value = '';

    // Show typing animation
    const typingBubble = showTyping();

    try {
        // Fetch response from the server
        const response = await fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();
        chatWindow.removeChild(typingBubble);
        appendMessage(data.response, 'bot');
    } catch (error) {
        chatWindow.removeChild(typingBubble);
        appendMessage('Error: Unable to connect to server. Please try again later.', 'bot');
        console.error(error);
    }
}

// Handle Send Button
sendBtn.addEventListener('click', sendMessage);

// Handle Enter Key
userInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

// Handle Mic Button
micBtn.addEventListener('click', () => {
    appendMessage("Listening for your voice...", 'bot');
    const recognition = new webkitSpeechRecognition();
    recognition.lang = 'hi-IN';
    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        appendMessage(transcript, 'user');

        // Show typing animation
        const typingBubble = showTyping();

        try {
            // Send transcript to server
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: transcript }),
            });

            const data = await response.json();
            chatWindow.removeChild(typingBubble);
            appendMessage(data.response, 'bot');
        } catch (error) {
            chatWindow.removeChild(typingBubble);
            appendMessage('Error: Unable to connect to server. Please try again later.', 'bot');
            console.error(error);
        }
    };

    recognition.onerror = (event) => {
        appendMessage('Error: Could not recognize your voice. Please try again.', 'bot');
        console.error('Speech Recognition Error:', event.error);
    };

    recognition.start();
});
