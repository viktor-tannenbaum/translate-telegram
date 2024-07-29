import collections
import re

import bs4

Phrase = collections.namedtuple("Phrase", ["name", "text"])
Task = collections.namedtuple("Task", ["name", "text_en", "text_ru"])
Snippet = collections.namedtuple("Snippet", ["en", "ru", "ba"])
TranslationPack = collections.namedtuple(
    "TranslationPack", ["platform", "language_code", "phrases"]
)


def parse_xml(filename: str) -> list[Phrase]:
    data = open(filename, "rb").read().decode("utf-8")
    soup = bs4.BeautifulSoup(data, features="xml")
    res = []
    keys = set()
    for entry in soup.select("resources > string"):
        name = entry.attrs["name"]
        text = entry.text
        assert text.find('"""') == -1
        assert name not in keys
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
    if platform in ("android", "android_x"):
        return parse_xml(f"{filepath_prefix}_{language}.xml")
    else:
        return parse_strings(f"{filepath_prefix}_{language}.strings")


def load_tasks(base_path: str, platform: str) -> list[Task]:
    filepath_prefix = f"{base_path}/{platform}"
    if platform in ("android", "android_x"):
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


DICTIONARY: tuple[Snippet] = (
    Snippet("chat", "чат", "әңгәмә"),
    Snippet("secret", "секретный", "серле"),
    Snippet("story", "история", "хикәйә"),
    Snippet("voice message", "голосовое сообщение", "тауышлы хәбәр"),
    Snippet("folder", "папка", "тупланма"),
    Snippet("wallpaper", "обои", "ерлек"),
    Snippet("group", "группа", "төркөм"),
    Snippet("link", "ссылка", "һылтанма"),
    Snippet("history", "история", "тарих"),
    Snippet("last seen", "был(а)", "булған"),
    Snippet("recently", "недавно", "яңыраҡ"),
    Snippet("gallery", "галерея", "һүрәтхана"),
    Snippet("app", "приложение", "ҡушымта"),
    Snippet("number", "номер", "һандар"),
    Snippet("phone number", "номер телефона", "телефон һандары"),
    Snippet("contact", "контакт", "бәйләнеш"),
    Snippet("unpin", "открепить", "төшөрөргә"),
    Snippet("save", "сохранить", "һаҡларға"),
    Snippet("saved", "сохраненный", "һаҡланған"),
    Snippet("channel", "канал", "канал"),
    Snippet("forward", "переслать", "тапшырырға"),
    Snippet("forwarded", "переслано", "тапшырылған"),
    Snippet("settings", "настройки", "көйләүҙәр"),
    Snippet("profile", "профиль", "сәхифә"),
    Snippet("saved messages", "избранное", "һаҡланмалар"),
    Snippet("password", "пароль", "серһүҙ"),
    Snippet("notification", "оповещение", "белдереү"),
    Snippet("poll", "опрос", "һорашыу"),
    Snippet("video message", "видеосообщение", "видеохәбәр"),
    Snippet("audio message", "аудиосообщение", "аудиохәбәр"),
    Snippet("member", "участник", "ҡатнашыусы"),
    Snippet("subscriber", "подписчик", "яҙылыусы"),
    Snippet("comment", "комментарий", "фекер"),
    Snippet("network", "сеть", "селтәр"),
    Snippet("online", "в сети", "селтәрҙә"),
    Snippet("pinned", "закрепленный", "беркетелгән"),
    Snippet("live location", "трансляция геопозиции", "торған урын күрһәтеү"),
    Snippet("exception", "исключение", "айырма"),
    Snippet("tag", "тег", "тамға"),
)


def format_dictionary(dictionary: list[Snippet]) -> str:
    return "\n".join(
        f"{snippet.en} - {snippet.ru} - {snippet.ba}" for snippet in dictionary
    )
