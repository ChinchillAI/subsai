from rx import create


def ffmpeg(**kwargs):
    """ ReactiveX FFmpeg Operator

    Takes a URI parseable by FFmpeg and coverts it to a numpy array of audio samples.
    """
    import ffmpeg
    import numpy as np
    def _ffmpeg(source):
        def subscribe(observer, scheduler = None):
            def on_next(value):
                sample_rate = 16000
                interval = 5
                n_bytes = interval * sample_rate * 2
                ffmpeg_process = (
                    ffmpeg
                    .input(value, loglevel="quiet")
                    .output("pipe:", format="s16le", acodec="pcm_s16le", ac=1, ar=sample_rate)
                    .global_args("-nostdin")
                    .run_async(pipe_stdout=True)
                )

                try: 
                    while ffmpeg_process.poll() is None:
                        in_bytes = ffmpeg_process.stdout.read(n_bytes)
                        if len(in_bytes) != n_bytes:
                            break
                        audio = np.frombuffer(in_bytes, np.int16).flatten().astype(np.float32) / 32768.0
                        observer.on_next(audio)
                except KeyboardInterrupt:
                    pass
                finally:
                    ffmpeg_process.terminate()
                    ffmpeg_process.wait()
                    observer.on_completed()
            
            return source.subscribe(
                on_next,
                observer.on_error,
                observer.on_completed,
                scheduler=scheduler
            )
        return create(subscribe)
    return _ffmpeg