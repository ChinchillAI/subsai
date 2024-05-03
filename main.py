import typer
from rx import just
from enum import Enum
from os.path import exists
import streamlink
from whisper.tokenizer import LANGUAGES
from blocks import ffmpeg, silero, whisper, translate, faster_whisper
import rx.operators as ops
from rx.subject import Subject
import rx

Language = Enum('Language', {v:k for k,v in LANGUAGES.items()})

def main(
        url_or_path: str, 
        language: Language = Language.english.value
    ):
    if exists(url_or_path):
        print("Using local file... ", end="", flush=True)
        stream_url = url_or_path
    else:
        print("Fetching streams... ", end="", flush=True)
        streams = streamlink.streams(url_or_path)
        stream_url = streams["best"].to_url()

    # print(vars())

    # stage1 = just(stream_url).pipe(
    #     ffmpeg(),
    #     silero(16000),
    #     whisper(language),
    # ).subscribe(on_next=lambda x: print(x))

    root = Subject()
    
    stage1 = root.pipe(
        ffmpeg(),
        silero(16000),
        faster_whisper(language),
        ops.share()
    )

    stage2_l = stage1.pipe(
        ops.map(lambda x: x),
        ops.share()
    )

    stage2_r = stage1.pipe(
        translate("english", "french"),
        ops.share()
    )

    rx.zip(stage2_l, stage2_r).subscribe(on_next=print)

    root.on_next(stream_url)

if __name__ == '__main__':
    typer.run(main)