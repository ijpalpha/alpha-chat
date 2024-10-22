document.getElementById("processPdfBtn").addEventListener("click", function() {
    fetch("/process_pdf", {
        method: "POST",
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => console.error('Error processing PDF:', error));
});

document.getElementById("sendBtn").addEventListener("click", function() {
    const userInput = document.getElementById("userInput").value;
    if (!userInput) return;

    const messageElement = document.createElement("div");
    messageElement.textContent = "You: " + userInput;
    document.getElementById("messages").appendChild(messageElement);

    fetch("/ask", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: userInput })
    })
    .then(response => response.json())
    .then(data => {
        const answerElement = document.createElement("div");
        answerElement.textContent = "Bot: " + data.answer;
        document.getElementById("messages").appendChild(answerElement);
        document.getElementById("userInput").value = ''; // Clear input
    })
    .catch(error => console.error('Error asking question:', error));
});
