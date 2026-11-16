
import argparse
import time

import httpx

REQUEST_COUNT = 10
CHUNK_SIZE = 64 * 1024


def measure_download(url: str) -> None:
    total_bytes = 0
    total_seconds = 0.0

    with httpx.Client(
        timeout=httpx.Timeout(60.0),
        follow_redirects=True,
        headers={"Cache-Control": "no-cache"},
    ) as client:
        for number in range(1, REQUEST_COUNT + 1):
            downloaded_bytes = 0
            started_at = time.perf_counter()

            with client.stream("GET", url) as response:
                response.raise_for_status()

                for chunk in response.iter_raw(CHUNK_SIZE):
                    downloaded_bytes += len(chunk)

            elapsed = time.perf_counter() - started_at

            total_bytes += downloaded_bytes
            total_seconds += elapsed

            print(
                f"Запрос {number}/{REQUEST_COUNT}: "
                f"{elapsed:.3f}s, "
                f"{downloaded_bytes / 1024**2:.2f} МБ"
            )

    average_seconds = total_seconds / REQUEST_COUNT
    speed_mbps = (total_bytes * 8) / (total_seconds * 1_000_000)

    print("\nРезультат:")
    print(f"Среднее время скачивания: {average_seconds:.3f} с")
    print(f"Всего скачано: {total_bytes / 1024**2:.2f} МБ")
    print(f"Скорость скачивания: {speed_mbps:.2f} МБ\с")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Тест скорости скачивания"
    )
    parser.add_argument(
        "url",
        help="URL для скачивания файла"
    )

    args = parser.parse_args()

    try:
        measure_download(args.url)
    except httpx.HTTPError as exc:
        parser.exit(1, f"HTTP error: {exc}\n")
