import json
import pathlib
import re
import typing

import bs4

from . import dictionaries


Path = pathlib.Path


class Phrase(typing.NamedTuple):
    name: str
    text: str


class Task(typing.NamedTuple):
    name: str
    text_en: str
    text_ru: str


class Snapshot:
    def __init__(
        self, snapshots_dir: Path, language_code: str, platform: str
    ) -> None:
        self.filename: Path = (
            snapshots_dir / language_code / platform
        ).with_suffix(".json")
        self.phrases: dict[str, str] = json.loads(
            open(self.filename, "rb").read().decode("utf-8")
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


def parse_xml(filename: Path) -> list[Phrase]:
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


def parse_strings(filename: Path) -> list[Phrase]:
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


def load_phrases(
    base_path: Path, language_code: str, platform: str
) -> list[Phrase]:
    file_basename: Path = base_path / language_code / platform
    if platform in ("android", "android_x", "unigram"):
        return parse_xml(file_basename.with_suffix(".xml"))
    else:
        return parse_strings(file_basename.with_suffix(".strings"))


def load_tasks(defaults_dir: Path, platform: str) -> list[Task]:
    phrases_en: list[Phrase] = load_phrases(defaults_dir, "en", platform)
    phrases_ru: list[Phrase] = load_phrases(defaults_dir, "ru", platform)

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
