const input = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const chatBox = document.getElementById("chat-box");


function addMessage(message, sender) {

    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message");

    if (sender === "user") {

        messageDiv.classList.add("user-message");

        messageDiv.innerHTML = `
            <div class="message-content">
                ${message}
            </div>
        `;

    } else {

        messageDiv.classList.add("bot-message");

        messageDiv.innerHTML = `
            <div class="avatar">🤖</div>

            <div class="message-content">
                ${message}
            </div>
        `;
    }

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}


async function sendMessage() {

    const question = input.value.trim();

    if (question === "") {
        return;
    }

    addMessage(question, "user");

    input.value = "";

    addMessage("Thinking... 🤔", "bot");


    try {

        const response = await fetch("/ask", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                question: question
            })

        });


        const data = await response.json();


        const messages =
            document.querySelectorAll(".bot-message");

        const lastMessage =
            messages[messages.length - 1];

        lastMessage.querySelector(
            ".message-content"
        ).innerHTML = data.answer;


    } catch (error) {

        const messages =
            document.querySelectorAll(".bot-message");

        const lastMessage =
            messages[messages.length - 1];

        lastMessage.querySelector(
            ".message-content"
        ).innerHTML =
            "Sorry, something went wrong. Please try again.";
    }
}


sendButton.addEventListener(
    "click",
    sendMessage
);


input.addEventListener(
    "keypress",
    function(event) {

        if (event.key === "Enter") {
            sendMessage();
        }

    }
);