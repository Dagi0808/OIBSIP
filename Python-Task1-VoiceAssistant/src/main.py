try:
    from src.assistant import get_response
    from src.speech import listen_microphone, speak
except ModuleNotFoundError:
    from assistant import get_response
    from speech import listen_microphone, speak


def run_assistant():
    print("Voice assistant is listening. Say 'hello' or ask for the time.")
    speak("Hello! How can I help you?")
    history = []

    while True:
        try:
            text = listen_microphone()
            if not text:
                print("No speech detected. Please try again.")
                continue

            print(f"You said: {text}")
            reply = get_response(text, speak_fn=speak, history=history)
            history.append({"role": "user", "text": text})
            history.append({"role": "assistant", "text": reply})
            history = history[-10:]  # keep last 5 exchanges
            print(f"Assistant: {reply}")
            speak(reply)

        except KeyboardInterrupt:
            print("\nExiting voice assistant.")
            break
        except Exception as exc:
            print(f"An error occurred: {exc}")
            speak("I had trouble processing that. Please try again.")


if __name__ == "__main__":
    run_assistant()
