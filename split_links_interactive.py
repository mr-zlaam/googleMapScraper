import json
from pathlib import Path
from typing import List


def read_json(filepath: Path) -> List[str]:
    with filepath.open("r", encoding="utf-8") as f:
        data = json.load(f)
        if not isinstance(data, list):
            raise ValueError("JSON file must contain an array of URLs")
        return data


def write_chunk(chunk: List[str], filename: Path) -> None:
    with filename.open("w", encoding="utf-8") as f:
        json.dump(chunk, f, indent=2)


def split_urls(urls: List[str], start_idx: int, end_idx: int, chunk_size: int, output_dir: Path) -> None:
    selected_urls = urls[start_idx - 1: end_idx]  # zero-based indexing
    output_dir.mkdir(parents=True, exist_ok=True)

    total_urls = len(selected_urls)
    num_chunks = (total_urls + chunk_size - 1) // chunk_size

    print(f"Total URLs selected: {total_urls}")
    print(f"Splitting into {num_chunks} files of up to {
          chunk_size} URLs each...")

    for i in range(num_chunks):
        chunk_urls = selected_urls[i*chunk_size: (i+1)*chunk_size]
        chunk_file = output_dir / f"links_part_{i+1}.json"
        write_chunk(chunk_urls, chunk_file)
        print(f"Created {chunk_file} with {len(chunk_urls)} URLs")


def main():
    input_json_path = Path("links.json")
    if not input_json_path.exists():
        print(f"Error: {input_json_path} does not exist.")
        return

    urls = read_json(input_json_path)
    total_urls = len(urls)
    print(f"Total URLs in {input_json_path}: {total_urls}")

    while True:
        try:
            start = int(input(f"Enter start index (1 to {total_urls}): "))
            end = int(input(f"Enter end index ({start} to {total_urls}): "))
            if not (1 <= start <= end <= total_urls):
                raise ValueError
            break
        except ValueError:
            print("Invalid range, please try again.")

    while True:
        try:
            chunk_size = int(
                input("Enter number of URLs per container (chunk size): "))
            if chunk_size <= 0:
                raise ValueError
            break
        except ValueError:
            print("Please enter a positive integer.")

    output_dir = Path("chunks")
    split_urls(urls, start, end, chunk_size, output_dir)
    print(f"All chunks saved in {output_dir.resolve()}")


if __name__ == "__main__":
    main()
