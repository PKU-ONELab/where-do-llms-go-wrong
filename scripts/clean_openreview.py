"""Extract review and author-response conversations from OpenReview note exports."""

import argparse
import json
from pathlib import Path


def is_official_review(note):
    """Check whether this note is an Official Review."""
    invitations = note.get('invitations', note.get('invitation', ''))
    if isinstance(invitations, str):
        invitations = [invitations]
    return any("/-/Official_Review" in inv for inv in invitations)


def is_author_response(note):
    """Heuristic to check if the note is an author response or from authors."""
    invitations = note.get('invitations', note.get('invitation', ''))
    if isinstance(invitations, str):
        invitations = [invitations]
    sigs = note.get("signatures", [])
    is_comment = any("/-/Official_Comment" in inv for inv in invitations)
    is_authors = any("Authors" in sig for sig in sigs)
    return is_comment or is_authors


def extract_note_text(note):
    """
    Convert a note's content into a single text block.
    Combine typical fields (summary, strengths, weaknesses, comment, etc.)
    into one string. Adjust to your needs.
    """
    content = note.get('content', {})
    text_parts = []

    # Common fields from official reviews:
    for key in [
        "summary", "soundness", "presentation", "contribution",
        "strengths", "weaknesses", "rating", "confidence"
    ]:
        val = content.get(key, {})
        if isinstance(val, dict) and "value" in val:
            text_parts.append(f"{key.title()}: {val['value']}")
        elif isinstance(val, str):
            text_parts.append(f"{key.title()}: {val}")

    # Some notes store main text in "comment"
    comment_obj = content.get("comment")
    if isinstance(comment_obj, dict) and "value" in comment_obj:
        text_parts.append(comment_obj["value"].strip())
    elif isinstance(comment_obj, str):
        text_parts.append(comment_obj.strip())

    return "\n".join(x for x in text_parts if x).strip()


def build_note_and_replies(forum_data):
    """
    Build two lookups:
      - note_map: note_id -> note object
      - replies_map: note_id -> [child_note_ids...]
    """
    note_map = {}
    replies_map = {}
    
    # Store each note by its ID
    for note in forum_data:
        note_id = note.get('id')
        note_map[note_id] = note

        parent_id = note.get('replyto')
        if parent_id and parent_id != note_id:
            if parent_id not in replies_map:
                replies_map[parent_id] = []
            replies_map[parent_id].append(note_id)

    # Sort children by time or other criteria if needed
    for parent_id, child_ids in replies_map.items():
        child_ids.sort(key=lambda cid: note_map[cid].get('tmdate', 0))

    return note_map, replies_map


def gather_conversation(note_id, note_map, replies_map, depth=0, seen=None):
    """
    Return a list of lines showing a conversation from 'note_id' down
    through its replies, recursively.
    """
    if seen is None:
        seen = set()
    if note_id in seen:
        return []
    seen.add(note_id)

    lines = []
    note = note_map[note_id]

    # Decide the label
    if is_official_review(note):
        label = "Reviewer Comment:"
    elif is_author_response(note):
        label = "Author Comment:"
    else:
        label = "Other Comment:"

    # Indentation for nested replies
    indent = "  " * depth
    text = extract_note_text(note)

    if text:
        lines.append(f"{indent}{label}")
        for line in text.split("\n"):
            lines.append(f"{indent}  {line}")
        lines.append("")  # extra newline

    # Recurse into children
    children = replies_map.get(note_id, [])
    for child_id in children:
        lines.extend(gather_conversation(child_id, note_map, replies_map, depth+1, seen.copy()))

    return lines


def extract_conversations(forum_data):
    """
    Gathers:
      1) Each official review and its replies
      2) Any top-level author response (i.e. an author note whose replyto == forum)
    """
    note_map, replies_map = build_note_and_replies(forum_data)
    conversation_data = []
    index_counter = 1

    # 1) Collect threads from each official review
    for note_id, note in note_map.items():
        if is_official_review(note):
            conversation_lines = gather_conversation(note_id, note_map, replies_map, 0)
            conversation_text = "\n".join(conversation_lines)
            conversation_data.append({
                "type": "official_review",
                "index": index_counter,
                "conversation_text": conversation_text
            })
            index_counter += 1

    # 2) Collect any top-level author response that replies directly to the forum
    #    i.e., is_author_response(note) and note['replyto'] == note['forum']
    for note_id, note in note_map.items():
        # forum id is typically in 'forum' field:
        forum_id = note.get('forum')
        # If this note is from authors, top-level, and not an official review
        if (is_author_response(note) and
            not is_official_review(note) and
            note.get('replyto') == forum_id):
            conversation_lines = gather_conversation(note_id, note_map, replies_map, 0)
            conversation_text = "\n".join(conversation_lines)
            conversation_data.append({
                "type": "general_author_response",
                "index": index_counter,
                "conversation_text": conversation_text
            })
            index_counter += 1

    return conversation_data


def print_conversations(conversation_data):
    for conv in conversation_data:
        ctype = conv["type"]
        idx = conv["index"]
        if ctype == "official_review":
            print(f"=== Rebuttal for Official Review #{idx} ===")
        else:
            print(f"=== General Author Response #{idx} ===")
        print(conv["conversation_text"])
        print("=== End ===\n")


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def select_forum_data(raw_data, forum_id=None):
    """Return notes for one forum from either a flat note list or a list of note lists."""
    if not isinstance(raw_data, list):
        raise ValueError("Input JSON must be a list of notes or a list of note lists.")

    if raw_data and all(isinstance(item, dict) for item in raw_data):
        if forum_id is None:
            return raw_data
        return [note for note in raw_data if note.get("forum") == forum_id or note.get("id") == forum_id]

    if raw_data and all(isinstance(item, list) for item in raw_data):
        if forum_id is None:
            raise ValueError("--forum-id is required when input is a list of forum note lists.")
        for note_list in raw_data:
            if note_list and any(note.get("forum") == forum_id or note.get("id") == forum_id for note in note_list):
                return note_list
        return []

    if not raw_data:
        return []

    raise ValueError("Input JSON must contain notes as dictionaries or forum groups as lists.")


def write_json(path, data):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract official-review and author-response conversations from OpenReview notes."
    )
    parser.add_argument("--input", required=True, help="OpenReview comments JSON file.")
    parser.add_argument("--output", required=True, help="Output JSON path for extracted conversations.")
    parser.add_argument(
        "--forum-id",
        default=None,
        help="Forum id to extract. Required for a JSON file containing multiple forum note lists.",
    )
    parser.add_argument(
        "--print-text",
        action="store_true",
        help="Also print extracted conversation text to stdout.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    raw_data = load_json(args.input)
    forum_data = select_forum_data(raw_data, args.forum_id)
    conversations = extract_conversations(forum_data)
    write_json(args.output, conversations)
    if args.print_text:
        print_conversations(conversations)
    print(f"Wrote {len(conversations)} conversations to {args.output}")


if __name__ == "__main__":
    main()
