# Contributing to Investment Workflow Evaluations

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Ways to Contribute

### Code Contributions

Developers can contribute improvements, bug fixes, and new features:

- **Tooling improvements** - Eval runner, grading engine enhancements
- **New evaluation modules** - Additional scenario types and rubrics
- **Documentation** - Guides, tutorials, examples
- **Bug fixes** - Issue resolution and patches

### Content Contributions

Domain experts can contribute evaluation content:

- **Scenario Creation** - Design evaluation scenarios based on real market situations
- **Golden Answer Writing** - Create expert-level reference responses
- **Rubric Development** - Define scoring criteria and calibration examples
- **Adversarial Tests** - Create edge cases that target AI failure modes

## Development Setup

### Prerequisites

- Python 3.10+
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/bdschi1/investment-workflow-evals.git
cd investment-workflow-evals

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the pipeline to verify setup
./run_all.sh
```

## Code Standards

### Python Style

- Use clear, descriptive variable names
- Add docstrings to functions and classes
- Keep functions focused and concise

### Git Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Test your changes: `./run_all.sh`
5. Commit with clear message: `git commit -m "Add feature X"`
6. Push to your fork: `git push origin feature/your-feature`
7. Open a Pull Request

### Commit Messages

Use clear, descriptive commit messages:

```
Add biotech catalyst scenario for equity thesis module

- Create scenario YAML with Phase 3 readout context
- Add golden answer with probability analysis
- Include adversarial tests for hallucination detection
```

## Content Guidelines

### Scenarios

When creating evaluation scenarios:

1. **Use real market situations** - Base scenarios on actual events
2. **Provide complete context** - Include all information needed for analysis
3. **Cite verifiable sources** - All data should be publicly available
4. **Define clear evaluation criteria** - What makes a good/bad response?
5. **Include pitfalls** - What mistakes should the AI avoid?

See `templates/scenario_template.yaml` for the format.

### Golden Answers

Expert reference responses should:

1. **Follow institutional standards** - What a senior analyst would produce
2. **Show complete reasoning** - Thesis → Evidence → Conclusion
3. **Include all required sections** - Valuation, risks, catalysts, sizing
4. **Cite sources properly** - Specific filings, page numbers

See `templates/investment_memo_template.md` for the format.

## Questions?

- Open a GitHub issue for questions or bug reports
- See the README for usage documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
