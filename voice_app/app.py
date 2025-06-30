from flask import Flask, request, jsonify, render_template
import base64
import uuid
import speech_recognition as sr
import os
import subprocess

app = Flask(__name__)

TARGET_WORD = "ابدا"
import tempfile
TEMP_DIR = tempfile.gettempdir()


def convert_to_wav(input_path, output_path):
    try:
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1", output_path
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
        )
        return True
    except Exception as e:
        print("❌ خطأ في التحويل باستخدام ffmpeg:", str(e))
        return False

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/check_pronunciation", methods=["POST"])
def check_pronunciation():
    print("📥 Headers:", dict(request.headers))

    # ✅ طباعة نوع محتوى البوست
    print("📥 Content-Type:", request.content_type)

    # ✅ طباعة أسماء كل الملفات المرسلة
    print("📥 Uploaded files:", request.files)

    # ✅ طباعة أسماء الفورم
    print("📥 Form fields:", request.form)
    audio_file = request.files.get("audio")

    if not audio_file:
        return jsonify({
            "success": False,
            "message": "❌ لا يوجد ملف صوتي",
            "debug": {
                "content_type": request.content_type,
                "form_keys": list(request.form.keys()),
                "file_keys": list(request.files.keys())
            }
        })
    original_filename = os.path.join(TEMP_DIR, f"{uuid.uuid4()}.webm")
    converted_filename = original_filename.replace(".webm", ".wav")

    audio_file.save(original_filename)
    print("📁 حجم ملف webm:", os.path.getsize(original_filename))

    if not convert_to_wav(original_filename, converted_filename):
        return jsonify({"success": False, "message": "فشل تحويل الصوت"})

    recognizer = sr.Recognizer()
    recognized_word = ""

    try:
        with sr.AudioFile(converted_filename) as source:
            audio = recognizer.record(source)

        recognized_word = recognizer.recognize_google(audio, language="ar-SA")
        print("✅ النص المستخرج من الصوت:", recognized_word)

        success = (TARGET_WORD in recognized_word)
    except Exception as e:
        print("❌ حدث خطأ أثناء التعرف على الصوت:", str(e))
        return jsonify({"success": False, "message": "خطأ في التعرف على الصوت", "recognized_word": ""})

    try:
        os.remove(original_filename)
        os.remove(converted_filename)
    except:
        pass

    return jsonify({"success": success, "recognized_word": recognized_word})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
