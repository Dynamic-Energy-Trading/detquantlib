import importlib.metadata

from src.main import main

if __name__ == "__main__":
    # Print package name and version, as defined in pyproject.toml
    distribution_metadata = importlib.metadata.metadata("poetrytemplate")
    print(f">> {distribution_metadata['Name']} v.{distribution_metadata['Version']} <<")

    main()
