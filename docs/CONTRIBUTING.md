# Contributing to Hand Landmarks Detection

Thank you for your interest in contributing to this project! This document provides guidelines for contributing.

## Development Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd hand-landmarks-detection
```

2. **Create a virtual environment**
```bash
python3 -m venv hand_detection_env
source hand_detection_env/bin/activate  # On Windows: hand_detection_env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Install development dependencies**
```bash
pip install -e .[dev]
```

## Code Style

- Follow PEP 8 guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and small
- Add type hints where appropriate

## Testing

Before submitting a pull request:

1. **Test camera functionality**
```bash
python test_camera.py
```

2. **Test all examples**
```bash
python example_usage.py
```

3. **Verify gesture recognition**
```bash
python camera_gesture_detection.py
```

## Submitting Changes

1. **Fork the repository**
2. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make your changes**
4. **Test thoroughly**
5. **Commit with clear messages**
```bash
git commit -m "Add: Brief description of your changes"
```

6. **Push to your fork**
```bash
git push origin feature/your-feature-name
```

7. **Create a Pull Request**

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Camera specifications
- Error messages (full traceback)
- Steps to reproduce
- Expected vs actual behavior

## Feature Requests

We welcome feature requests! Please:

- Check existing issues first
- Describe the use case
- Explain why it would be valuable
- Consider implementation complexity

## Areas for Contribution

- **New gesture recognition algorithms**
- **Performance optimizations**
- **Additional camera support**
- **Better error handling**
- **Documentation improvements**
- **Unit tests**
- **Cross-platform compatibility**

## Code Review Process

All submissions require review. We use GitHub pull requests for this purpose.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
