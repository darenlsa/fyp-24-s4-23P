document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chat-form");
    const chatWindow = document.getElementById("chat-window");
    const userInput = document.getElementById("user-input");

    /**
     * Add a message bubble to the chat window.
     * @param {string} message - The message content.
     * @param {string} sender - "user" or "bot" to indicate who sent the message.
     */
    function addMessageBubble(message, sender) {
        const bubble = document.createElement("div");
        bubble.classList.add("chat-bubble", sender);
        bubble.textContent = message;
        chatWindow.appendChild(bubble);
        chatWindow.scrollTop = chatWindow.scrollHeight; // Scroll to the latest message
    }

    /**
     * Handle quick response button clicks by sending predefined messages.
     * @param {string} type - The type of quick response (appointments, prescriptions, etc.).
     */
    window.handleQuickResponse = function (type) {
        const quickResponses = {
            appointments: "Show my upcoming appointments.",
            prescriptions: "Show my prescriptions.",
            billing: "Show my billing details.",
            profile: "Show my profile information.",
        };

        const message = quickResponses[type];
        if (message) {
            addMessageBubble(message, "user"); // Display the user's quick response

            // Send the predefined message to the server
            fetch("/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ message }),
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then((data) => {
                    // Display the bot's response
                    addMessageBubble(data.response || "I'm sorry, I didn't understand that.", "bot");
                })
                .catch((error) => {
                    addMessageBubble("There was an error connecting to the server.", "bot");
                    console.error("Fetch error:", error);
                });
        }
    };

    /**
     * Handle the chat form submission for user input.
     */
    chatForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent the default form submission behavior
        const userMessage = userInput.value.trim(); // Get the user's input

        if (userMessage) {
            addMessageBubble(userMessage, "user"); // Display the user's message

            // Send the user's message to the server
            try {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({ message: userMessage }),
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const data = await response.json();
                // Display the bot's response
                addMessageBubble(data.response || "I'm sorry, I didn't understand that.", "bot");
            } catch (error) {
                addMessageBubble("There was an error connecting to the server.", "bot");
                console.error("Fetch error:", error);
            }

            // Clear the input field
            userInput.value = "";
        }
    });

    /**
     * Handle user logout.
     */
    window.logout = function () {
        fetch('/logout', { method: 'GET' })
            .then(() => {
                window.location.href = '/'; // Redirect to the home page after logout
            })
            .catch((error) => {
                console.error("Logout error:", error);
            });
    };
});
