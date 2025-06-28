let mediaRecorder;
let audioChunks = [];
let recordingStream;
const startBtn = document.getElementById("start-recording");
const resultDiv = document.getElementById("result");

startBtn.addEventListener("click", async () => {
    resultDiv.textContent = "🔴 جاري الاستماع... قل: ابدا";

    if (!recordingStream) {
        recordingStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    }

    audioChunks = [];

    mediaRecorder = new MediaRecorder(recordingStream);
    mediaRecorder.start();

    mediaRecorder.ondataavailable = (event) => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunks, { type: "audio/webm" });
        const reader = new FileReader();

        reader.onloadend = async () => {
            const base64Audio = reader.result;

            const response = await fetch("/check_pronunciation", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ audio: base64Audio })
            });

            const result = await response.json();
            console.log("✅ النتيجة:", result);

            if (result.success) {
                resultDiv.textContent = "✅ نُطقك صحيح لكلمة 'ابدا'";
            } else {
                resultDiv.textContent = `❌ نُطق غير صحيح. أنت قلت: "${result.recognized_word || 'غير واضحة'}"`;
            }
        };

        reader.readAsDataURL(audioBlob);
    };

    // أوقف التسجيل تلقائيًا بعد 3 ثواني
setTimeout(() => {
    if (mediaRecorder.state === "recording") {
        mediaRecorder.stop();
    }
}, 2500);
});
