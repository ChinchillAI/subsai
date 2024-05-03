from rx import create


def translate(source_language, target_language, **kwargs):
    print("Loading translation model...", end="", flush=True)
    import dl_translate as dlt
    model = dlt.TranslationModel()
    print("ok.")
    def _translate(source):
        def subscribe(observer, scheduler = None):
            def on_next(text):
                translated_text = model.translate(text, source=source_language, target=target_language)
                observer.on_next(translated_text)
            
            return source.subscribe(
                on_next=on_next,
                on_completed=observer.on_completed,
                on_error=observer.on_error,
                scheduler=scheduler
            )
        return create(subscribe)
    return _translate