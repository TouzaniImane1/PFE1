const recordBtn = document.getElementById("recordBtn");
const resultText = document.getElementById("result");

let mediaRecorder;
let audioChunks = [];
let isWaitingForEmailChoice = false; // Ajout d'un état pour savoir si on attend un numéro d'email

// Fonction pour faire parler l'assistant avec la première voix disponible en français
function speakMessage(message) {
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.rate = 0.95; // Légèrement ralenti pour un son plus naturel
    utterance.lang = "fr-FR"; // Définir la langue en français
    utterance.rate = 1; // Vitesse normale
    utterance.pitch = 1; // Tonalité normale

// Fonction pour sélectionner la première voix française
function setVoice() {
        const voices = window.speechSynthesis.getVoices();
        const frenchVoice = voices.find(voice => voice.lang === "fr-FR") || voices[0]; // Prendre la première voix FR
        if (frenchVoice) {
            utterance.voice = frenchVoice;
            window.speechSynthesis.cancel(); // Annuler toute autre voix en cours
            window.speechSynthesis.speak(utterance);
        }
    }

    // Vérifier si les voix sont déjà chargées
    if (window.speechSynthesis.getVoices().length > 0) {
        setVoice();
    } else {
        window.speechSynthesis.onvoiceschanged = () => {
            setVoice();
            window.speechSynthesis.onvoiceschanged = null; // Désactiver après la première utilisation
        };
    }
}

// Exécuter le message de bienvenue au chargement de la page
window.addEventListener("load", () => {
    setTimeout(() => {
        speakMessage("Bonjour ! Je suis votre assistant vocal. Si vous voulez ouvrir un site ou une application local, dites 'Ouvre' suivi du nom du site ou de l'application, ou dites juste le nom lu site ou de l'application .");
    }, 1500); // Ajout d'un délai pour éviter les conflits de chargement
});


recordBtn.addEventListener("click", async () => {
    if (recordBtn.classList.contains("processing")) {
        // Si bloqué, clic = reset
        resetButton();
    }

    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        recordBtn.textContent = "🎤 Commencer l'enregistrement";

    } else {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream, { mimeType: "audio/webm" });

            audioChunks = [];

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };

            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
                const formData = new FormData();
                formData.append("audio", audioBlob, "audio.webm");
                console.log("🔍 Envoi du fichier :", formData.get("audio"));

                // Désactiver le bouton et indiquer le chargement
                recordBtn.disabled = true;
                recordBtn.textContent = "🔄 Traitement...";

                try {
                    const response = await fetch("/transcribe", {
                        method: "POST",
                        body: formData,
                    });
                    
                    if (!response.ok) {
                        const errorData = await response.json();
                        throw new Error(errorData.error || "Le serveur a renvoyé une erreur.");
                    }

                    const responseData = await response.json(); // Convertir la réponse en JSON
                    const transcription = responseData.text || "Aucune transcription disponible.";
                    
                    // Affichage de la transcription (même si ce n'est pas une commande)
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
                    // Réactiver le bouton sauf si on attend un numéro
                    if (!isWaitingForEmailChoice) {
                        recordBtn.disabled = false;
                        recordBtn.innerHTML = "🎤 Commencer l'enregistrement";
                    }
                }
            };

            mediaRecorder.start();
            recordBtn.textContent = "🛑 Arrêter l'enregistrement";
        } catch (error) {

            console.error("Erreur d'accès au microphone:", error);
            resultText.textContent = "🎤 Impossible d'accéder au microphone. Vérifiez votre configuration.";

        }
    }
});

recordBtn.addEventListener("dblclick", () => {
    // Si double-clic, on force le reset même si bloqué
    resetButton();
});

recordBtn.addEventListener("contextmenu", (e) => {
    e.preventDefault();
    if (confirm("Forcer la réinitialisation du bouton ?")) {
        resetButton();
    }
});

// Fonction pour envoyer une commande vocale au serveur
function sendCommandToServer(transcription) {
    fetch("/transcribe", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: transcription })
    })
    .then(response => response.json())
    .then(data => {
        // ✅ S'il attend un choix d'email, ne pas reset le bouton
        if (data.awaiting_email_choice) {
            isWaitingForEmailChoice = true;
            recordBtn.innerHTML = "🎙️ Dites le numéro de l'email...";
            recordBtn.disabled = false;
        } else {
            isWaitingForEmailChoice = false;
           // ✅ Ne pas lire côté navigateur si les emails sont déjà lus côté serveur
        if (!data.status.includes("Lecture des e-mails en cours...")) {
            speakMessage(data.status);
        }
        resetButton();

        }
    })
    .catch(error => {
        console.error("Erreur d'envoi de la commande:", error);
        resetButton();
    });
}

// Fonction pour gérer la sélection d'un e-mail
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
            speakMessage(data.status);  // 🔊 Lecture du contenu
            resetButton();
        })
        .catch(error => {
            console.error("Erreur de sélection d'email:", error);
            resetButton();
        });
        
    }
}    
function resetButton() {
    const recordBtn = document.getElementById("recordBtn"); // Vérifie l'ID de ton bouton
    recordBtn.disabled = false;
    recordBtn.textContent = "🎤 Commencer l'enregistrement";
    recordBtn.style.backgroundColor = "#ff4d4d"; // Remettre la couleur normale
}
setTimeout(resetButton, 2000);

// Modifier la fonction qui envoie la commande à Flask
async function sendCommand(command) {
    const recordBtn = document.getElementById("recordBtn");
    recordBtn.disabled = true;
    recordBtn.textContent = "🔄 Traitement...";
    recordBtn.style.backgroundColor = "#ffcc00"; // Changer la couleur

    try {
        const response = await fetch("/transcribe", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ command: command }),
        });

        const data = await response.json();
        console.log("📩 Réponse du serveur :", data);

        // Vérifier si la commande était "raconte une blague"
        if (command.includes("blague")) {
            setTimeout(() => {
                resetButton(); // Réinitialiser le bouton après la blague
            }, 5000); // Laisse le temps à la blague d'être racontée avant de reset
        } else {
            resetButton();
        }

    } catch (error) {
        console.error("❌ Erreur :", error);
        resetButton();
    }
}
