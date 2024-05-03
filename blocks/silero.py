from rx import create


def silero(sample_rate, **kwargs):
    """ReactiveX Silero VAD Operator

    Dyanmically load the Silero VAD model and create a ReactiveX operator for use in pipelines.

    Arguments:
    sample_rate: int -- the sample rate of the audio to be processed (e.g. 16000 for 16kHz)

    Returns:
    rx.Operator -- An operator that takes audio samples, and only propogates forward ones with detected speech.
    """

    print("Loading silero model... ", end="", flush=True)
    import torch
    vad_model, vad_utils = torch.hub.load(repo_or_dir="snakers4/silero-vad", model="silero_vad", verbose=False, trust_repo=True)
    (get_speech_timestamps, save_audio, read_audio, VADIterator, collect_chunks) = vad_utils
    print("ok.")

    def _silero(source):
        """ReactiveX Silero VAD Oberservable Factory

        Takes an existing ReactiveX Observable and bind the VAD model to it.  This allows it to be chained with other observables.

        Arguments:
        source: rx.Observable

        Returns: 
        rx.Observable
        """

        def subscribe(observer, scheduler = None):
            def on_next(audio):
                """ Silero VAD Processing

                Forward audio samples through the Silero VAD.  Samples that have detected speech are forwarded to the next subscribe.

                Arguments:
                audio: np.Array -- a numpy array of audio samples taken at the rate supplied to the operator.

                Returns:
                None
                """

                speech_timestamps = get_speech_timestamps(audio, vad_model, sampling_rate=sample_rate, return_seconds=True)
                if not len(speech_timestamps) == 0:
                    observer.on_next(audio)
            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler = scheduler
            )
        return create(subscribe)
    return _silero