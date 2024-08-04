import argparse
import concurrent.futures
import datetime
import pathlib
import re
import typing

import util.chatgpt as chatgpt
import util.helpers as helpers
import util.dictionaries as dictionaries


Path = pathlib.Path


class Batch(typing.NamedTuple):
    tasks: list[helpers.Task]
    prompt_template: str
    language_name: str
    dictionary: dictionaries.Dictionary


def process_batch(
    batch: Batch, chatgpt_client: chatgpt.ChatGpt
) -> list[helpers.Phrase]:
    example_strs = []
    example_count = 0
    used_snippets = set()
    for id, task in enumerate(batch.tasks):
        for snippet in batch.dictionary.snippets:
            if (
                task.text_en.lower().find(snippet.en) != -1
                or task.text_ru.lower().find(snippet.ru) != -1
            ):
                used_snippets.add(snippet)
        example_strs.append(f"{id+1}.")
        example_strs.append(f'"""{task.text_en}"""')
        example_strs.append(f'"""{task.text_ru}"""')
        example_strs.append("")
        example_count += 1
    if not used_snippets:
        used_snippets = batch.dictionary.snippets[:5]

    footer = "\n".join(example_strs)
    prompt = batch.prompt_template.format(
        language_name=batch.language_name,
        example_count=example_count,
        snippets=helpers.format_snippets(used_snippets),
        footer=footer,
    )

    resp = chatgpt_client.get_response(prompt)
    answers = re.findall(r'\d+\.\s*"""(.*?)"""', resp, re.DOTALL)
    if len(answers) != len(batch.tasks):
        print(prompt)
        print(resp)
        raise ValueError("Invalid response")

    result = []
    for i in range(len(batch.tasks)):
        result.append(helpers.Phrase(batch.tasks[i].name, answers[i]))

    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--defaults_dir", type=Path, required=True)
    parser.add_argument("--platform", type=str, required=True)
    parser.add_argument("--telegram_language_code", type=str, required=True)
    parser.add_argument("--iso_language_code", type=str, required=True)
    parser.add_argument("--snapshots_dir", type=Path, required=True)
    parser.add_argument("--prompt_template_filename", type=Path, required=True)
    parser.add_argument("--openai_api_key", type=str, required=True)
    args = parser.parse_args()

    chatgpt_client: chatgpt.ChatGpt = chatgpt.ChatGpt(
        api_key=args.openai_api_key
    )

    PROMPT_TEMPLATE = open(args.prompt_template_filename).read()
    LANGUAGE_NAME = dictionaries.get_language_name(args.iso_language_code)

    snapshot = helpers.Snapshot(
        args.snapshots_dir, args.telegram_language_code, args.platform
    )

    tasks: list[helpers.Task] = helpers.load_tasks(
        args.defaults_dir, args.platform
    )

    tasks = [task for task in tasks if task.text_en.strip()]
    tasks = [task for task in tasks if task.name not in snapshot]
    tasks.sort(key=lambda task: task.name)

    dictionary: dictionaries.Dictionary = dictionaries.load_dictionary(
        args.iso_language_code
    )

    BATCH_SIZE = 32

    batches = []
    slice = []
    for task in tasks:
        slice.append(task)
        if len(slice) >= BATCH_SIZE:
            batches.append(
                Batch(
                    tasks=slice,
                    prompt_template=PROMPT_TEMPLATE,
                    language_name=LANGUAGE_NAME,
                    dictionary=dictionary,
                )
            )
            slice = []
    if slice:
        batches.append(
            Batch(
                tasks=slice,
                prompt_template=PROMPT_TEMPLATE,
                language_name=LANGUAGE_NAME,
                dictionary=dictionary,
            )
        )
    print("Batch count:", len(batches))

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        future_to_batch = {
            executor.submit(process_batch, batch, chatgpt_client): batch
            for batch in batches
        }
        for future in concurrent.futures.as_completed(future_to_batch):
            try:
                phrases: list[helpers.Phrase] = future.result()
            except Exception as ex:
                print(f"Exception when processing a batch: {ex}")
            else:
                print(f"Done batch at {datetime.datetime.now()}")
                for phrase in phrases:
                    snapshot.update_phrase(phrase)
                snapshot.save()


if __name__ == "__main__":
    main()
