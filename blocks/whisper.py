from rx import create


def whisper(language, **kwargs):
    print("Loading whisper model... ", end="", flush=True)
    import whisper
    model = whisper.load_model("large")
    print("ok.")
    def _whisper(source):
        def subscribe(observer, scheduler = None):
            def on_next(audio):
                result = model.transcribe(audio, language=language.value, task="translate")
                translated_text = "".join((s["text"]) for s in result["segments"])
                observer.on_next(translated_text)
            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler = scheduler
            )
        return create(subscribe)
    return _whisper