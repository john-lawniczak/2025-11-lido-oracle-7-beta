import logging
import requests


def main():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    api_key = "TEST_API_KEY"
    api_url = "http://127.0.0.1:8081"  # plaintext endpoint for PoC
    headers = {
        "Authorization": f"GenieKey {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "message": "test",
        "description": "plaintext demo",
        "priority": "P4",
        "tags": ["oracle_checks", "oracle"],
    }
    response = requests.post(
        f"{api_url}/v2/alerts",
        json=payload,
        headers=headers,
        timeout=10,
    )
    response.raise_for_status()


if __name__ == "__main__":
    main()


