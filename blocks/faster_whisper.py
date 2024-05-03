from rx import create


def faster_whisper(language, **kwargs):
    print("Loading faster_whisper... ", end="", flush=True)
    from faster_whisper import WhisperModel
    model = WhisperModel("whisper-large-v2-ct2/", device="cuda", compute_type="float16")
    print("ok.")
    def _faster_whisper(source):
        def subscribe(observer, scheduler = None):
            def on_next(audio):
                segments, info = model.transcribe(audio, language=language.value, task="translate")
                translated_text = "".join((s.text) for s in segments)
                observer.on_next(translated_text)
            
            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler
            )
        return create(subscribe)
    return _faster_whisper
