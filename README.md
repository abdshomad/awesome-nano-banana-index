# awesome-nano-banana-index

A curated collection and index of GitHub repositories related to **Nano Banana** (Gemini-2.5-Flash-Image) image generation and editing.

## Overview

This repository serves as a centralized index of awesome-nano-banana related GitHub repositories. The collection will be aggregated, collected, indexed, and made searchable through a web application, providing easy access to all Nano Banana-related projects, tools, prompts, and resources.

## Purpose

- **Aggregate**: Collect all Nano Banana related repositories in one place
- **Index**: Organize repositories for easy discovery
- **Search**: Enable quick search and filtering through a web interface
- **Discover**: Help users find relevant tools, prompts, and resources

## Repository List

See [repo-list.md](./repo-list.md) for the complete list of indexed repositories.

## Submodules

This repository uses Git submodules to include related awesome-nano-banana repositories. 

### Initial Setup

If you're cloning this repository for the first time, initialize and update the submodules:

```bash
git submodule update --init --recursive
```

Or clone with submodules in one command:

```bash
git clone --recurse-submodules <repository-url>
```

### Updating All Submodules

To update all submodules to their latest commits from their respective remote repositories:

```bash
git submodule update --remote --merge
```

This will fetch the latest changes from each submodule's remote repository and merge them into your local submodule checkouts.

### Updating to Committed Versions

To update all submodules to the specific commits referenced in this repository:

```bash
git submodule update --recursive
```

## Contributing

Contributions are welcome! If you know of a Nano Banana related repository that should be included, please add it to [repo-list.md](./repo-list.md) or open an issue.

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.