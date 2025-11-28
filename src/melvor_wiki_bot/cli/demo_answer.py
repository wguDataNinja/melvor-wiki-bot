from melvor_wiki_bot.wiki.manifest import load_manifest


def main() -> None:
    manifest = load_manifest()
    print("Loaded wiki manifest entries:")
    for entry in manifest:
        print(f"- {entry.page_id}: {entry.title} ({entry.url})")


if __name__ == "__main__":
    main()
