import argparse
import collections
import concurrent.futures
import datetime
import json
import re

import util.chatgpt as chatgpt
import util.helpers as helpers


Batch = collections.namedtuple(
    "Batch", ["tasks", "prompt_template", "dictionary"]
)


def process_batch(
    batch: Batch, chatgpt_client: chatgpt.ChatGpt
) -> list[helpers.Phrase]:
    example_strs = []
    example_count = 0
    used_snippets = set()
    for id, task in enumerate(batch.tasks):
        for snippet in batch.dictionary:
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
        used_snippets = batch.dictionary[:5]

    footer = "\n".join(example_strs)
    prompt = batch.prompt_template.format(
        example_count=example_count,
        dictionary=helpers.format_dictionary(used_snippets),
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
    parser.add_argument("--data_dir", type=str, required=True)
    parser.add_argument("--platform", type=str, required=True)
    parser.add_argument("--snapshots_dir", type=str, required=True)
    parser.add_argument("--prompt_template_filname", type=str, required=True)
    parser.add_argument("--openai_api_key", type=str, required=True)
    args = parser.parse_args()

    chatgpt_client: chatgpt.ChatGpt = chatgpt.ChatGpt(
        api_key=args.openai_api_key
    )

    PROMPT_TEMPLATE = open(args.prompt_template_filname).read()

    snapshot_path = f"{args.snapshots_dir}/snapshot_{args.platform}.json"
    snapshot: dict[str, str] = json.loads(
        open(snapshot_path, "rb").read().decode("utf-8")
    )

    tasks: list[helpers.Task] = helpers.load_tasks(
        args.data_dir, args.platform
    )

    tasks = [task for task in tasks if task.text_en.strip()]
    tasks = [task for task in tasks if task.name not in snapshot]
    tasks.sort(key=lambda task: task.name)

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
                    dictionary=helpers.DICTIONARY,
                )
            )
            slice = []
    if slice:
        batches.append(
            Batch(
                tasks=slice,
                prompt_template=PROMPT_TEMPLATE,
                dictionary=helpers.DICTIONARY,
            )
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
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
                    snapshot[phrase.name] = phrase.text
                open(
                    snapshot_path,
                    "wb",
                ).write(
                    json.dumps(
                        snapshot, indent=2, sort_keys=True, ensure_ascii=False
                    ).encode("utf-8")
                )


if __name__ == "__main__":
    main()
