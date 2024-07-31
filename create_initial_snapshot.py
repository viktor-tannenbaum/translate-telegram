import argparse
from pathlib import Path

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
    parser.add_argument("--default_data_dir", type=Path, required=True)
    parser.add_argument("--default_languague_code", type=str, required=True)
    parser.add_argument("--canonical_data_dir", type=Path, required=True)
    parser.add_argument("--canonical_languague_code", type=str, required=True)
    parser.add_argument("--platform", type=str, required=True)
    parser.add_argument("--snapshots_dir", type=str, required=True)
    parser.add_argument("--output_language_code", type=str, required=True)
    args = parser.parse_args()

    canonical_phrases: list[helpers.Phrase] = helpers.load_phrases(
        args.canonical_data_dir, args.platform, args.canonical_languague_code
    )
    default_phrases: list[helpers.Phrase] = helpers.load_phrases(
        args.default_data_dir, args.platform, args.default_languague_code
    )

    canonical_phrases = {phrase.name: phrase for phrase in canonical_phrases}
    default_phrases = {phrase.name: phrase for phrase in default_phrases}

    snapshot_path = f"{args.snapshots_dir}/snapshot_{args.platform}_{args.output_language_code}.json"
    snapshot = helpers.Snapshot(snapshot_path)
    assert len(snapshot.phrases) == 0, "Snapshot already exists"

    for name, phrase in canonical_phrases.items():
        default_phrase = default_phrases[name]
        if phrase.text == default_phrase.text:
            continue
        snapshot.phrases[name] = phrase.text

    snapshot.save()


if __name__ == "__main__":
    main()
