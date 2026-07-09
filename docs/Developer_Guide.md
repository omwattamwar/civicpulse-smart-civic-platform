# Developer Guide

## Project Structure

- `src/`: React frontend source code.
  - `components/`: Reusable UI components.
  - `context/`: React Context providers for global state.
  - `lib/`: Configuration for Firebase, Gemini, and i18n.
  - `pages/`: Page-level components.
- `ai-microservice/`: Python FastAPI backend for YOLOv8 computer vision.
- `docs/`: Project documentation.
- `dist/`: Compiled production assets.

## Core Concepts

1. **State Management**: We use React Context API rather than Redux. See `src/context/` for implementation details.
2. **Localization**: Powered by `i18next`. Translation files are located in `src/locales/`.
3. **Styling**: Tailwind CSS is used extensively. Ensure you follow utility-first principles.

## Contributing

Please review `CONTRIBUTING.md` in the root directory for instructions on submitting Pull Requests.
