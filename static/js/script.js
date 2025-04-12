const recordBtn = document.getElementById("recordBtn");
const resultText = document.getElementById("result");

let mediaRecorder;
let audioChunks = [];
let isWaitingForEmailChoice = false;

// Fonction de synthèse vocale
function speakMessage(message) {
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = "fr-FR";
    utterance.rate = 1;
    utterance.pitch = 1;

    function setVoice() {
        const voices = window.speechSynthesis.getVoices();
        const frenchVoice = voices.find(v => v.lang === "fr-FR") || voices[0];
        if (frenchVoice) {
            utterance.voice = frenchVoice;
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(utterance);
        }
    }

    if (window.speechSynthesis.getVoices().length > 0) {
        setVoice();
    } else {
        window.speechSynthesis.onvoiceschanged = () => {
            setVoice();
            window.speechSynthesis.onvoiceschanged = null;
        };
    }
}

// Message d'accueil au chargement
window.addEventListener("load", () => {
    setTimeout(() => {
        speakMessage("Bonjour ! Je suis votre assistant vocal. Cliquez sur le bouton pour commencer.");
    }, 1500);
});

// Événement sur le bouton principal
recordBtn.addEventListener("click", async () => {
    if (recordBtn.classList.contains("processing")) {
        resetButton();
        return;
    }

    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        recordBtn.textContent = "🎤 Commencer l'enregistrement";
    } else {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                alert("Votre navigateur ne supporte pas l'accès au micro.");
            }
            
            mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });
            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                const formData = new FormData();
                formData.append("audio", audioBlob, "audio.webm");

                recordBtn.disabled = true;
                recordBtn.textContent = "🔄 Traitement...";

                try {
                    const response = await fetch("/transcribe", {
                        method: "POST",
                        body: formData
                    });

                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.error || "Le serveur a renvoyé une erreur.");
                    }

                    const responseData = await response.json();
                    const transcription = responseData.text || "Aucune transcription disponible.";

                    resultText.innerHTML = `<strong>Transcription :</strong> "${transcription}"`;

                    if (isWaitingForEmailChoice) {
                        handleEmailSelection(transcription);
                    } else {
                        sendCommandToServer(transcription);
                    }

                } catch (error) {
                    console.error("Erreur:", error);
                    resultText.textContent = `Erreur: ${error.message || "Erreur inconnue"}`;
                } finally {
                    if (!isWaitingForEmailChoice) {
                        resetButton();
                    }
                }
            };

            mediaRecorder.start();
            recordBtn.textContent = "🛑 Arrêter l'enregistrement";

        } catch (error) {
            console.error("Erreur d'accès au micro:", error);
            resultText.textContent = "🎤 Impossible d'accéder au microphone. Vérifiez votre configuration.";
        }
    }
});

// Double-clic pour forcer reset
recordBtn.addEventListener("dblclick", () => {
    resetButton();
});

// Clic droit pour forcer reset
recordBtn.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    if (confirm("Forcer la réinitialisation du bouton ?")) {
        resetButton();
    }
});

// Envoi de commande textuelle au serveur
function sendCommandToServer(transcription) {
    fetch("/transcribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: transcription })
    })
        .then(response => response.json())
        .then(data => {
            if (data.awaiting_email_choice) {
                isWaitingForEmailChoice = true;
                recordBtn.innerHTML = "🎙️ Dites le numéro de l'email...";
                recordBtn.disabled = false;
            } else {
                isWaitingForEmailChoice = false;
                speakMessage(data.status); // 🔊 Lecture du message retourné par le serveur
                resetButton();
            }
        })
        .catch(error => {
            console.error("Erreur d'envoi de la commande:", error);
            resetButton();
        });
}

// Traitement des réponses type "email 1"
function handleEmailSelection(choice) {
    const spokenNumbers = {
        "un": 1, "premier": 1, "1": 1,
        "deux": 2, "second": 2, "2": 2,
        "trois": 3, "troisième": 3, "3": 3
    };

    const selectedNumber = spokenNumbers[choice];

    if (selectedNumber) {
        isWaitingForEmailChoice = false;

        fetch("/transcribe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: `email ${selectedNumber}` })
        })
            .then(response => response.json())
            .then(data => {
                resultText.innerHTML = `<strong>Contenu :</strong> "${data.status}"`;
                speakMessage(data.status);
                resetButton();
            })
            .catch(error => {
                console.error("Erreur de sélection d'email:", error);
                resetButton();
            });
    }
}

// Réinitialisation du bouton
function resetButton() {
    recordBtn.disabled = false;
    recordBtn.textContent = "🎤 Commencer l'enregistrement";
    recordBtn.style.backgroundColor = "#ff4d4d";
}

// Pour éviter un bug d’état bloqué
setTimeout(resetButton, 2000);
