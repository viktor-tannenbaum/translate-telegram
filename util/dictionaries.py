import typing


class Snippet(typing.NamedTuple):
    en: str
    ru: str
    target: str


class Dictionary(typing.NamedTuple):
    snippets: tuple[Snippet]


ba = Dictionary(
    snippets=(
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
        Snippet("notification", "уведомление", "белдереү"),
        Snippet("poll", "опрос", "һорашыу"),
        Snippet("video message", "видеосообщение", "видеохәбәр"),
        Snippet("audio message", "аудиосообщение", "аудиохәбәр"),
        Snippet("member", "участник", "ҡатнашыусы"),
        Snippet("subscriber", "подписчик", "яҙылыусы"),
        Snippet("comment", "комментарий", "фекер"),
        Snippet("network", "сеть", "селтәр"),
        Snippet("online", "в сети", "селтәрҙә"),
        Snippet("pinned", "закрепленный", "беркетелгән"),
        Snippet(
            "live location", "трансляция геопозиции", "торған урын күрһәтеү"
        ),
        Snippet("exception", "исключение", "айырма"),
        Snippet("tag", "тег", "тамға"),
        Snippet("anonymous", "анонимный", "имзаһыҙ"),
        Snippet("block", "блокировать", "бикләргә"),
        Snippet("ban", "заблокировать", "тыйырға"),
        Snippet("preview", "предпросмотр", "алҡарау"),
    ),
)

tt = Dictionary(
    snippets=(
        Snippet("chat", "чат", "чат"),
        Snippet("secret", "секретный", "яшерен"),
        Snippet("story", "история", "хикәя"),
        Snippet("voice message", "голосовое сообщение", "тавышхат"),
        Snippet("folder", "папка", "бөклем"),
        Snippet("wallpaper", "обои", "артлык"),
        Snippet("group", "группа", "төркем"),
        Snippet("link", "ссылка", "сылтама"),
        Snippet("history", "история", "тарих"),
        Snippet("last seen", "был(а)", "булган"),
        Snippet("recently", "недавно", "күптән түгел"),
        Snippet("gallery", "галерея", "галерея"),
        Snippet("app", "приложение", "кушымта"),
        Snippet("number", "номер", "номер"),
        Snippet("phone number", "номер телефона", "телефон номеры"),
        Snippet("contact", "контакт", "контакт"),
        Snippet("unpin", "открепить", "беркетмәскә"),
        Snippet("save", "сохранить", "сакларга"),
        Snippet("saved", "сохраненный", "сакланган"),
        Snippet("channel", "канал", "канал"),
        Snippet("forward", "переслать", "таратырга"),
        Snippet("forwarded", "переслано", "таратылган"),
        Snippet("settings", "настройки", "көйләүләр"),
        Snippet("profile", "профиль", "профиль"),
        Snippet("saved messages", "избранное", "сакланган хәбәрләр"),
        Snippet("password", "пароль", "серсүз"),
        Snippet("notification", "оповещение", "белдермә"),
        Snippet("poll", "опрос", "сорашу"),
        Snippet("video message", "видеосообщение", "видеохат"),
        Snippet("audio message", "аудиосообщение", "аудиохат"),
        Snippet("member", "участник", "катнашучы"),
        Snippet("subscriber", "подписчик", "язылучы"),
        Snippet("comment", "комментарий", "шәрех"),
        Snippet("network", "сеть", "челтәр"),
        Snippet("online", "в сети", "онлайнда"),
        Snippet("pinned", "закрепленный", "беркетелгән"),
        Snippet(
            "live location", "трансляция геопозиции", "геопозиция трансляциясе"
        ),
        Snippet("exception", "исключение", "чыгарма"),
        Snippet("tag", "тег", "тәг"),
        Snippet("administrator", "администратор", "идарәче"),
    )
)


def load_dictionary(iso_language_code: str) -> Dictionary:
    if iso_language_code == "ba":
        return ba

    if iso_language_code == "tt":
        return tt

    raise ValueError(f"Unsupported language code: {iso_language_code}")


def get_language_name(iso_language_code: str) -> str:
    if iso_language_code == "ba":
        return "Bashkir"

    if iso_language_code == "tt":
        return "Tatar"

    raise ValueError(f"Unsupported language code: {iso_language_code}")
