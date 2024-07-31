import argparse
import pathlib

import util.helpers as helpers


Path = pathlib.Path


def make_xml(translation: list[tuple[str, str]]) -> str:
    res = []
    res.append('<?xml version="1.0" encoding="utf-8"?>')
    res.append("<resources>")
    for name, text in translation:
        res.append(f'  <string name="{name}">{text}</string>')
    res.append("</resources>\n")

    return "\n".join(res).encode("utf-8")


def make_strings(translation: list[tuple[str, str]]) -> str:
    res = []
    for name, text in translation:
        res.append(f'"{name}" = "{text}";')

    return "\n".join(res).encode("utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--defaults_dir", type=Path, required=True)
    parser.add_argument("--default_languague_code", type=str, required=True)
    parser.add_argument("--canonical_data_dir", type=Path, required=True)
    parser.add_argument("--canonical_languague_code", type=str, required=True)
    parser.add_argument("--platform", type=str, required=True)
    parser.add_argument("--snapshots_dir", type=Path, required=True)
    parser.add_argument("--output_dir", type=Path, required=True)
    parser.add_argument("--telegram_language_code", type=str, required=True)
    args = parser.parse_args()

    snapshot = helpers.Snapshot(
        args.snapshots_dir, args.telegram_language_code, args.platform
    )

    canonical_phrases: list[helpers.Phrase] = helpers.load_phrases(
        args.canonical_data_dir, args.canonical_languague_code, args.platform
    )
    default_phrases: list[helpers.Phrase] = helpers.load_phrases(
        args.defaults_dir, args.default_languague_code, args.platform
    )

    default_phrases = {phrase.name: phrase for phrase in default_phrases}

    translation = {}

    for phrase in canonical_phrases:
        default_phrase = default_phrases[phrase.name]
        if phrase.text == default_phrase.text:
            continue
        translation[phrase.name] = phrase.text

    print(f"Canonical phrases: {len(translation)}")

    for name, text in snapshot.phrases.items():
        if name in translation:
            continue
        translation[name] = text

    translation = sorted(translation.items())
    half = len(translation) // 2

    output_filename_scheme: Path = args.output_dir / "platform.ext"
    if args.platform in ("android", "android_x", "unigram"):
        output_filename_scheme = output_filename_scheme.with_suffix(".xml")
        output = open(
            output_filename_scheme.with_stem(f"{args.platform}_1"), "wb"
        )
        output.write(make_xml(translation[:half]))
        output = open(
            output_filename_scheme.with_stem(f"{args.platform}_2"), "wb"
        )
        output.write(make_xml(translation[half:]))
    else:
        output_filename_scheme = output_filename_scheme.with_suffix(".strings")
        output = open(
            output_filename_scheme.with_stem(f"{args.platform}_1"), "wb"
        )
        output.write(make_strings(translation[:half]))
        output = open(
            output_filename_scheme.with_stem(f"{args.platform}_2"), "wb"
        )
        output.write(make_strings(translation[half:]))


if __name__ == "__main__":
    main()
