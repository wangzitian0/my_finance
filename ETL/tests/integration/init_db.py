from fetch_historical import fetch_historical

from common import ensure_common_tables


def main():
    ensure_common_tables()
    # Add other initialization logic here, such as fetching data for specific stocks
    result = fetch_historical("AAPL")
    print(result)


if __name__ == "__main__":
    main()
