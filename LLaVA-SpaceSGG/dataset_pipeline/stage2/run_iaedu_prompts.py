import argparse
import json
import sys
import time
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from stage2.iaedu_client import call_iaedu, load_dotenv
    from stage2.llm_based_query import create_dynamic_prompt, load_json, save_json
else:
    from .iaedu_client import call_iaedu, load_dotenv
    from .llm_based_query import create_dynamic_prompt, load_json, save_json


def build_message(system_msg, query):
    return (
        f"{system_msg.strip()}\n\n"
        "Use the following context/task and return only the final answer.\n\n"
        f"{query.strip()}"
    )


def main():
    parser = argparse.ArgumentParser(description="Run LLaVA-SpaceSGG generated prompts through the IAedu agent API.")
    parser.add_argument("--anno-file", required=True, help="Path to the annotation JSON file.")
    parser.add_argument(
        "--prompt-function",
        required=True,
        choices=["create_layer_prompt", "create_comparative_prompt", "create_between_prompt", "create_rotation_prompt"],
        help="Prompt generation function to use.",
    )
    parser.add_argument("--output-file", default="iaedu_outputs.json", help="Path to save API outputs.")
    parser.add_argument("--channel-id", default=None, help="IAedu channel_id for the agent. Defaults to IAEDU_CHANNEL_ID from .env.")
    parser.add_argument("--thread-id", default=None, help="Thread id to use for the conversation. Defaults to IAEDU_THREAD_ID from .env.")
    parser.add_argument("--limit", type=int, default=None, help="Optional maximum number of prompts to run.")
    parser.add_argument("--sleep", type=float, default=0.0, help="Seconds to wait between API calls.")
    args = parser.parse_args()
    load_dotenv()
    channel_id = args.channel_id or __import__("os").environ.get("IAEDU_CHANNEL_ID")
    thread_id = args.thread_id or __import__("os").environ.get("IAEDU_THREAD_ID") or "llava-spacesgg-local"
    if not channel_id:
        raise RuntimeError("Set --channel-id or IAEDU_CHANNEL_ID in .env.")

    annotations = load_json(args.anno_file)
    prompts = create_dynamic_prompt(annotations, args.prompt_function)
    if args.limit is not None:
        prompts = prompts[: args.limit]

    outputs = []
    for index, prompt in enumerate(prompts, start=1):
        key, system_msg, query, *_ = prompt
        print(f"[{index}/{len(prompts)}] {key}")
        answer = call_iaedu(
            message=build_message(system_msg, query),
            channel_id=channel_id,
            thread_id=f"{thread_id}-{key}",
        )
        outputs.append(
            {
                "key": key,
                "prompt_function": args.prompt_function,
                "query": query,
                "answer": answer,
            }
        )
        save_json(outputs, args.output_file)
        if args.sleep:
            time.sleep(args.sleep)

    print(f"Saved {len(outputs)} outputs to {args.output_file}")


if __name__ == "__main__":
    main()
