import json
import re
import typing

import bs4

from . import dictionaries


class Phrase(typing.NamedTuple):
    name: str
    text: str


class Task(typing.NamedTuple):
    name: str
    text_en: str
    text_ru: str


class Snapshot:
    def __init__(self, filename: str):
        self.filename: str = filename
        self.phrases: dict[str, str] = json.loads(
            open(filename, "rb").read().decode("utf-8")
        )

    def save(self) -> None:
        open(self.filename, "wb").write(
            json.dumps(
                self.phrases, indent=2, ensure_ascii=False, sort_keys=True
            ).encode("utf-8")
        )

    def update_phrase(self, phrase: Phrase) -> None:
        self.phrases[phrase.name] = phrase.text

    def get_phrase(self, name: str) -> Phrase:
        return Phrase(name, self.phrases[name])

    def __contains__(self, name: str) -> bool:
        return name in self.phrases


def parse_xml(filename: str) -> list[Phrase]:
    data = open(filename, "rb").read().decode("utf-8")
    soup = bs4.BeautifulSoup(data, features="xml")
    res = []
    keys = set()
    for entry in soup.select("resources > string"):
        name = entry.attrs["name"]
        text = entry.text
        assert text.find('"""') == -1
        if name in keys:
            print("Problematic key: " + name)
            continue
        keys.add(name)
        res.append(Phrase(name, text))

    return res


def parse_strings(filename: str) -> list[Phrase]:
    lines = open(filename, "rb").read().decode("utf-8").splitlines()
    res = {}
    for line in lines:
        m = re.search(r'^\s*"([^"]+)"\s*=\s*"(.+)"', line)
        if not m:
            continue
        name = m.group(1)
        text = m.group(2)
        assert text.find('"""') == -1
        if res.get(name, text) != text:
            print("Problematic key: " + name)
            continue
        res[name] = text

    return [Phrase(name, text) for name, text in res.items()]


def load_phrases(base_path: str, platform: str, language: str) -> list[Phrase]:
    filepath_prefix = f"{base_path}/{platform}"
    if platform in ("android", "android_x", "unigram"):
        return parse_xml(f"{filepath_prefix}_{language}.xml")
    else:
        return parse_strings(f"{filepath_prefix}_{language}.strings")


def load_tasks(base_path: str, platform: str) -> list[Task]:
    filepath_prefix = f"{base_path}/{platform}"
    if platform in ("android", "android_x", "unigram"):
        phrases_en: list[Phrase] = parse_xml(f"{filepath_prefix}_en.xml")
        phrases_ru: list[Phrase] = parse_xml(f"{filepath_prefix}_ru.xml")
    else:
        phrases_en: list[Phrase] = parse_strings(
            f"{filepath_prefix}_en.strings"
        )
        phrases_ru: list[Phrase] = parse_strings(
            f"{filepath_prefix}_ru.strings"
        )

    dict_ru = {phrase.name: phrase for phrase in phrases_ru}
    tasks = []
    for phrase_en in phrases_en:
        if phrase_en.name not in dict_ru:
            continue
        phrase_ru = dict_ru[phrase_en.name]
        tasks.append(Task(phrase_en.name, phrase_en.text, phrase_ru.text))

    return tasks


def select_modified(
    phrases: list[Phrase], base_phrases: list[Phrase]
) -> list[Phrase]:
    base_phrases_dict = {phrase.name: phrase for phrase in base_phrases}
    assert all(phrase.name in base_phrases_dict for phrase in phrases)
    return [
        phrase
        for phrase in phrases
        if phrase.text != base_phrases_dict[phrase.name].text
    ]


def merge_translations(
    default_phrases: list[Phrase], manual_phrases: list[Phrase]
) -> list[Phrase]:
    result = {}
    manual_phrases_dict = {phrase.name: phrase for phrase in manual_phrases}
    for phrase in default_phrases:
        if phrase.name in manual_phrases_dict:
            result[phrase.name] = manual_phrases_dict[phrase.name]
        else:
            result[phrase.name] = phrase

    return list(result.values())


def format_snippets(snippets: dictionaries.Snippet) -> str:
    return "\n".join(
        f"{snippet.en} - {snippet.ru} - {snippet.target}"
        for snippet in snippets
    )
