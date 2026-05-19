import argparse
import json
import os
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from stage2.iaedu_client import call_iaedu, load_dotenv
else:
    from .iaedu_client import call_iaedu, load_dotenv


DEFAULT_PROMPT = """Analyze the image and generate an open-vocabulary scene graph.
Return:
1. A short scene description.
2. Objects with normalized bounding boxes in this format: <ref>object</ref><box>[[x1, y1, x2, y2]]</box>.
3. Spatial relations in this format: <pred>predicate</pred><box>[[subject_box]]</box><box>[[object_box]]</box>.
4. Depth layers from closest to farthest.
5. Four comparative question-answer pairs about object position, depth, or size.
Use coordinates from 0 to 999. Be concise."""


def main():
    parser = argparse.ArgumentParser(description="Run a real image through the IAedu agent API for scene graph generation.")
    parser.add_argument("--image", required=True, help="Path to an image file.")
    parser.add_argument("--output-file", default="image_sgg_output.json", help="Path to save the API output.")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT, help="Prompt to send with the image.")
    parser.add_argument("--channel-id", default=None, help="Defaults to IAEDU_CHANNEL_ID from .env.")
    parser.add_argument("--thread-id", default=None, help="Defaults to IAEDU_THREAD_ID from .env.")
    args = parser.parse_args()

    load_dotenv()
    channel_id = args.channel_id or os.environ.get("IAEDU_CHANNEL_ID")
    thread_id = args.thread_id or os.environ.get("IAEDU_THREAD_ID") or "llava-spacesgg-image"
    if not channel_id:
        raise RuntimeError("Set --channel-id or IAEDU_CHANNEL_ID in .env.")

    image_path = Path(args.image)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    answer = call_iaedu(
        message=args.prompt,
        channel_id=channel_id,
        thread_id=f"{thread_id}-{image_path.stem}",
        user_info={},
        image_path=image_path,
    )
    output = {
        "image": str(image_path),
        "prompt": args.prompt,
        "answer": answer,
    }
    with open(args.output_file, "w") as file:
        json.dump(output, file, indent=4)
    print(f"Saved output to {args.output_file}")


if __name__ == "__main__":
    main()
