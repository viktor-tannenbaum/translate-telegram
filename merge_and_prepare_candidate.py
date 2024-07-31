import argparse
import json

import util.helpers as helpers


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
    parser.add_argument("--default_data_dir", type=str, required=True)
    parser.add_argument("--default_languague_code", type=str, required=True)
    parser.add_argument("--canonical_data_dir", type=str, required=True)
    parser.add_argument("--canonical_languague_code", type=str, required=True)
    parser.add_argument("--platform", type=str, required=True)
    parser.add_argument("--snapshots_dir", type=str, required=True)
    parser.add_argument("--output_dir", type=str, required=True)
    parser.add_argument("--output_language_code", type=str, required=True)
    args = parser.parse_args()

    snapshot_path = f"{args.snapshots_dir}/snapshot_{args.platform}_{args.output_language_code}.json"
    snapshot = helpers.Snapshot(snapshot_path)

    canonical_phrases: list[helpers.Phrase] = helpers.load_phrases(
        args.canonical_data_dir, args.platform, args.canonical_languague_code
    )
    default_phrases: list[helpers.Phrase] = helpers.load_phrases(
        args.default_data_dir, args.platform, args.default_languague_code
    )

    default_phrases = {phrase.name: phrase for phrase in default_phrases}

    translation = {}

    for phrase in canonical_phrases:
        default_phrase = default_phrases[phrase.name]
        if phrase.text == default_phrase.text:
            continue
        translation[phrase.name] = phrase.text
    
    print(len(translation))

    for name, text in snapshot.phrases.items():
        if name in translation:
            continue
        translation[name] = text

    translation = sorted(translation.items())
    half = len(translation) // 2

    output_files_format = f"{args.output_dir}/{args.platform}_{args.output_language_code}_{{id}}.{{ext}}"
    if args.platform in ("android", "android_x", "unigram"):
        output = open(output_files_format.format(id=1, ext="xml"), "wb")
        output.write(make_xml(translation[:half]))
        output = open(output_files_format.format(id=2, ext="xml"), "wb")
        output.write(make_xml(translation[half:]))
    else:
        output = open(output_files_format.format(id=1, ext="strings"), "wb")
        output.write(make_strings(translation[:half]))
        output = open(output_files_format.format(id=2, ext="strings"), "wb")
        output.write(make_strings(translation[half:]))


if __name__ == "__main__":
    main()
