const recordBtn = document.getElementById("recordBtn");
const resultText = document.getElementById("result");

let mediaRecorder;
let audioChunks = [];

// Fonction pour faire parler l'assistant avec la première voix disponible en français
function speakMessage(message) {
    const utterance = new SpeechSynthesisUtterance(message);
    utterance.lang = "fr-FR"; // Définir la langue en français
    utterance.rate = 1; // Vitesse normale
    utterance.pitch = 1; // Tonalité normale

    // Fonction pour sélectionner la première voix française
    function setVoice() {
        const voices = window.speechSynthesis.getVoices();
        const frenchVoice = voices.find(voice => voice.lang === "fr-FR") || voices[0]; // Prendre la première voix FR
        if (frenchVoice) {
            utterance.voice = frenchVoice;
            window.speechSynthesis.speak(utterance);
        }
    }

    // Vérifier si les voix sont déjà chargées
    if (window.speechSynthesis.getVoices().length > 0) {
        setVoice();
    } else {
        // Attendre que les voix soient chargées
        window.speechSynthesis.onvoiceschanged = setVoice;
    }
}

// Exécuter le message de bienvenue au chargement de la page
window.addEventListener("load", () => {
    speakMessage("Bonjour ! Je suis votre assistant vocal. Si vous voulez ouvrir un site, dites 'Ouvre' suivi du nom du site. Dites 'Stop' pour quitter.");
});


recordBtn.addEventListener("click", async () => {
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

                } catch (error) {
                    console.error("Erreur:", error);
                    resultText.textContent = `Erreur: ${error.message || "Erreur inconnue"}`;
                } finally {
                    // Réactiver le bouton après traitement
                    recordBtn.disabled = false;
                    recordBtn.textContent = "🎤 Commencer l'enregistrement";

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
