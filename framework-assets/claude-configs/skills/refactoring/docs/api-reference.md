# Refactoring Tools and IDE Reference

Complete guide to IDE refactoring tools, static analyzers, linters, and automation utilities for safe and efficient refactoring.

## Table of Contents

- [IDE Refactoring Tools](#ide-refactoring-tools)
- [Static Analysis Tools](#static-analysis-tools)
- [Code Quality Metrics](#code-quality-metrics)
- [Automated Refactoring Tools](#automated-refactoring-tools)
- [Testing Tools](#testing-tools)
- [Version Control Integration](#version-control-integration)
- [CI/CD Integration](#cicd-integration)

## IDE Refactoring Tools

### Visual Studio Code

#### Built-in Refactoring

**Rename Symbol** (`F2`)
```typescript
// Place cursor on variable/function/class name
// Press F2
// Type new name
// All references updated automatically
```

**Extract Function** (`Ctrl+Shift+R` → Extract Method)
```javascript
// Select code to extract
function calculateTotal() {
    const tax = price * 0.08;
    const shipping = 10;
    const total = price + tax + shipping;  // Select these lines
    return total;
}

// After extraction
function calculateTotal() {
    const total = calculateFinalTotal(price);
    return total;
}

function calculateFinalTotal(price) {
    const tax = price * 0.08;
    const shipping = 10;
    const total = price + tax + shipping;
    return total;
}
```

**Extract Variable** (`Ctrl+Shift+R` → Extract Constant)
```python
# Select complex expression
return user.subscription.plan.price * (1 - user.discount_rate)

# After extraction
discount_multiplier = 1 - user.discount_rate
return user.subscription.plan.price * discount_multiplier
```

**Move to New File**
```typescript
// Right-click on class/function
// Select "Move to new file"
// Automatically creates file and updates imports
```

#### VS Code Extensions

**Better Comments**
```python
# ! Critical refactoring needed
# TODO: Extract this to separate class
# ? Should this be async?
# * Important note
```

**SonarLint**
- Real-time code quality feedback
- Detects code smells
- Suggests refactorings

**ESLint / Pylint**
- Enforce coding standards
- Auto-fix available for many issues

### JetBrains IDEs (IntelliJ, PyCharm, WebStorm)

#### Advanced Refactorings

**Extract Method**
```java
// Select code
// Right-click → Refactor → Extract Method
// Or: Ctrl+Alt+M (Windows/Linux), Cmd+Alt+M (Mac)
```

**Inline**
```java
// Place cursor on method call
// Ctrl+Alt+N
// Replaces call with method body
```

**Change Signature**
```python
# Right-click on method → Refactor → Change Signature
# Add/remove/reorder parameters
# All call sites updated automatically
```

**Move**
```java
// Drag and drop class to different package
// Or: F6 → Select destination
// Automatically updates imports
```

**Safe Delete**
```javascript
// Right-click → Refactor → Safe Delete
// Warns if element is used elsewhere
// Shows usages before deleting
```

**Extract Interface**
```typescript
class UserService {
    getUser() { }
    saveUser() { }
    deleteUser() { }
}

// Refactor → Extract Interface
interface IUserService {
    getUser();
    saveUser();
    deleteUser();
}
```

#### Structural Search and Replace

**Find Complex Patterns**
```java
// Template: Find all if statements without braces
if ($condition$)
    $statement$;

// Replace with:
if ($condition$) {
    $statement$;
}
```

### Eclipse

**Refactoring Menu**
```
Alt+Shift+T → Opens refactoring menu
- Rename
- Move
- Extract Method/Variable/Constant
- Inline
- Change Method Signature
- Extract Interface/Superclass
```

### Vim/Neovim

**LSP-based Refactoring**
```vim
" With coc.nvim or nvim-lsp
:CocCommand document.renameCurrentWord
:CocCommand refactor.extract
:CocCommand refactor.inline
```

## Static Analysis Tools

### Python

#### Pylint

**Installation**:
```bash
pip install pylint
```

**Usage**:
```bash
# Analyze file
pylint myfile.py

# Analyze directory
pylint src/

# Generate config
pylint --generate-rcfile > .pylintrc
```

**Common Checks**:
- `C0103`: Invalid name
- `C0111`: Missing docstring
- `R0913`: Too many arguments
- `R0914`: Too many local variables
- `R0915`: Too many statements

**Example Output**:
```
************* Module mymodule
mymodule.py:15:0: R0913: Too many arguments (6/5) (too-many-arguments)
mymodule.py:23:4: C0103: Variable name "x" doesn't conform to snake_case naming style
```

#### Flake8

```bash
pip install flake8
flake8 src/
```

**Configuration** (`.flake8`):
```ini
[flake8]
max-line-length = 120
exclude = .git,__pycache__,build,dist
ignore = E203,W503
```

#### mypy (Type Checking)

```bash
pip install mypy
mypy src/
```

**Example**:
```python
def add(a: int, b: int) -> int:
    return a + b

result: str = add(1, 2)  # mypy error: Incompatible types
```

#### Bandit (Security)

```bash
pip install bandit
bandit -r src/
```

Detects:
- SQL injection
- Hard-coded passwords
- Use of `exec()`
- Weak crypto

### JavaScript/TypeScript

#### ESLint

**Installation**:
```bash
npm install eslint --save-dev
npx eslint --init
```

**Configuration** (`.eslintrc.js`):
```javascript
module.exports = {
    extends: ['eslint:recommended'],
    rules: {
        'no-unused-vars': 'error',
        'no-console': 'warn',
        'complexity': ['error', 10],
        'max-lines': ['error', 300],
        'max-params': ['error', 4]
    }
};
```

**Auto-fix**:
```bash
eslint --fix src/
```

#### TSLint (deprecated, use ESLint)

#### Prettier (Formatting)

```bash
npm install prettier --save-dev
npx prettier --write "src/**/*.{js,ts,jsx,tsx}"
```

**Configuration** (`.prettierrc`):
```json
{
    "semi": true,
    "singleQuote": true,
    "tabWidth": 2,
    "trailingComma": "es5"
}
```

### Java

#### Checkstyle

**Configuration** (`checkstyle.xml`):
```xml
<module name="Checker">
    <module name="LineLength">
        <property name="max" value="120"/>
    </module>
    <module name="TreeWalker">
        <module name="CyclomaticComplexity">
            <property name="max" value="10"/>
        </module>
    </module>
</module>
```

#### PMD

```bash
pmd check -d src/ -R rulesets/java/quickstart.xml
```

Detects:
- Unused variables
- Empty catch blocks
- Overly complex code
- God classes

#### SpotBugs

```bash
spotbugs -textui target/classes
```

Finds:
- Null pointer dereferences
- Resource leaks
- Concurrency issues

### Multi-Language

#### SonarQube

**Installation** (Docker):
```bash
docker run -d --name sonarqube -p 9000:9000 sonarqube:latest
```

**Analysis**:
```bash
# Python
sonar-scanner \
    -Dsonar.projectKey=myproject \
    -Dsonar.sources=src \
    -Dsonar.host.url=http://localhost:9000

# JavaScript
sonar-scanner \
    -Dsonar.projectKey=myproject \
    -Dsonar.sources=src \
    -Dsonar.javascript.lcov.reportPaths=coverage/lcov.info
```

**Provides**:
- Code smells
- Bugs
- Security vulnerabilities
- Technical debt estimation
- Duplication detection

## Code Quality Metrics

### Cyclomatic Complexity

**Definition**: Number of linearly independent paths through code

**Tool** (Python):
```bash
pip install radon
radon cc src/ -a
```

**Output**:
```
src/service.py
    M 15:0 UserService.process_order - B (6)
    M 45:0 UserService.calculate_discount - A (2)
```

**Grades**:
- A: 1-5 (simple)
- B: 6-10 (moderate)
- C: 11-20 (complex)
- D: 21-50 (very complex)
- F: 51+ (extremely complex)

**Target**: Keep functions at grade A or B

### Lines of Code

**Tool** (cloc):
```bash
cloc src/
```

**Output**:
```
-------------------------------------------------------------------------------
Language                     files          blank        comment           code
-------------------------------------------------------------------------------
Python                          45           1230            850           3420
JavaScript                      32            890            450           2890
-------------------------------------------------------------------------------
```

**Guidelines**:
- Function: < 50 lines
- Class: < 300 lines
- File: < 500 lines

### Code Duplication

**Tool** (Python):
```bash
pip install pylint
pylint --disable=all --enable=duplicate-code src/
```

**Tool** (JavaScript):
```bash
npm install -g jsinspect
jsinspect src/
```

**Target**: < 3% duplication

### Maintainability Index

**Formula**:
```
MI = 171 - 5.2 * ln(HV) - 0.23 * CC - 16.2 * ln(LOC)
```

Where:
- HV = Halstead Volume
- CC = Cyclomatic Complexity
- LOC = Lines of Code

**Tool**:
```bash
radon mi src/
```

**Scale**:
- 85-100: Highly maintainable
- 65-85: Moderately maintainable
- < 65: Difficult to maintain

## Automated Refactoring Tools

### Python

#### Rope

```python
from rope.base.project import Project
from rope.refactor.rename import Rename

project = Project('.')
resource = project.root.get_child('mymodule.py')

# Rename refactoring
renamer = Rename(project, resource, 12)  # Line 12
changes = renamer.get_changes('new_name')
project.do(changes)
```

#### autoflake (Remove Unused Imports)

```bash
pip install autoflake
autoflake --remove-all-unused-imports --in-place src/*.py
```

#### isort (Sort Imports)

```bash
pip install isort
isort src/
```

#### Black (Formatter)

```bash
pip install black
black src/
```

### JavaScript/TypeScript

#### jscodeshift

**Example Codemod**:
```javascript
// Transform var to const/let
module.exports = function(fileInfo, api) {
    const j = api.jscodeshift;
    const root = j(fileInfo.source);

    root.find(j.VariableDeclaration, {kind: 'var'})
        .forEach(path => {
            path.value.kind = 'const';
        });

    return root.toSource();
};
```

**Run**:
```bash
jscodeshift -t transform.js src/
```

#### ts-morph (TypeScript AST)

```typescript
import { Project } from "ts-morph";

const project = new Project();
project.addSourceFilesAtPaths("src/**/*.ts");

// Rename class
const sourceFile = project.getSourceFile("myfile.ts");
const myClass = sourceFile.getClass("OldClassName");
myClass.rename("NewClassName");

project.save();
```

### Java

#### Eclipse JDT

Programmatic refactoring via Eclipse API

#### OpenRewrite

**Recipe** (YAML):
```yaml
type: specs.openrewrite.org/v1beta/recipe
name: com.example.RefactorExample
recipeList:
  - org.openrewrite.java.ChangeType:
      oldFullyQualifiedTypeName: com.old.OldClass
      newFullyQualifiedTypeName: com.new.NewClass
```

**Run**:
```bash
mvn rewrite:run
```

## Testing Tools

### Unit Testing

**Python (pytest)**:
```bash
pytest --cov=src --cov-report=html
```

**JavaScript (Jest)**:
```bash
jest --coverage
```

**Java (JUnit)**:
```bash
mvn test
```

### Mutation Testing

**Python (mutmut)**:
```bash
pip install mutmut
mutmut run
mutmut results
```

**JavaScript (Stryker)**:
```bash
npm install -g stryker-cli
stryker run
```

**What it does**:
- Mutates code (e.g., `>` to `>=`)
- Runs tests
- Reports if mutation survived (weak tests)

### Property-Based Testing

**Python (Hypothesis)**:
```python
from hypothesis import given
import hypothesis.strategies as st

@given(st.integers(), st.integers())
def test_commutative(a, b):
    assert add(a, b) == add(b, a)
```

**JavaScript (fast-check)**:
```javascript
fc.assert(
    fc.property(fc.integer(), fc.integer(), (a, b) => {
        return add(a, b) === add(b, a);
    })
);
```

## Version Control Integration

### Git Hooks

**Pre-commit Hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/bash

# Run tests
pytest
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

# Run linter
pylint src/
if [ $? -ne 0 ]; then
    echo "Linting failed. Commit aborted."
    exit 1
fi

exit 0
```

**Or use pre-commit framework**:
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v3.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml

  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
```

**Install**:
```bash
pip install pre-commit
pre-commit install
```

### Commit Message Standards

**commitlint**:
```bash
npm install --save-dev @commitlint/cli @commitlint/config-conventional
```

**Configuration** (`commitlint.config.js`):
```javascript
module.exports = {
    extends: ['@commitlint/config-conventional'],
    rules: {
        'type-enum': [2, 'always', [
            'feat', 'fix', 'refactor', 'docs', 'test', 'chore'
        ]]
    }
};
```

## CI/CD Integration

### GitHub Actions

**Workflow** (`.github/workflows/refactoring-checks.yml`):
```yaml
name: Refactoring Quality Checks

on: [pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9

      - name: Install dependencies
        run: |
          pip install pylint pytest pytest-cov radon

      - name: Run tests
        run: pytest --cov=src

      - name: Check code quality
        run: pylint src/

      - name: Check complexity
        run: radon cc src/ -nc -a

      - name: Check maintainability
        run: radon mi src/ -s

      - name: Fail if complexity too high
        run: |
          radon cc src/ --total-average -nb | \
          awk '{if($NF > 10) exit 1}'
```

### GitLab CI

**Configuration** (`.gitlab-ci.yml`):
```yaml
stages:
  - test
  - quality

test:
  stage: test
  script:
    - pytest --cov=src

code_quality:
  stage: quality
  script:
    - pylint src/
    - radon cc src/ -nc
  allow_failure: false
```

### Jenkins

**Jenkinsfile**:
```groovy
pipeline {
    agent any

    stages {
        stage('Test') {
            steps {
                sh 'pytest --cov=src'
            }
        }

        stage('Quality') {
            steps {
                sh 'pylint src/ || true'
                sh 'radon cc src/ -a'

                // Fail if complexity average > 10
                script {
                    def complexity = sh(
                        script: "radon cc src/ --total-average -nb | awk '{print \$NF}'",
                        returnStdout: true
                    ).trim().toFloat()

                    if (complexity > 10) {
                        error("Average complexity too high: ${complexity}")
                    }
                }
            }
        }
    }
}
```

## Tool Configuration Examples

### Complete Python Setup

**pyproject.toml**:
```toml
[tool.black]
line-length = 120
target-version = ['py39']

[tool.isort]
profile = "black"
line_length = 120

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "--cov=src --cov-report=html --cov-report=term"

[tool.pylint.messages_control]
disable = ["C0111", "C0103"]

[tool.pylint.format]
max-line-length = 120

[tool.pylint.design]
max-args = 5
max-locals = 15
max-branches = 12
max-statements = 50
```

### Complete JavaScript Setup

**package.json**:
```json
{
    "scripts": {
        "lint": "eslint src/",
        "lint:fix": "eslint --fix src/",
        "format": "prettier --write 'src/**/*.{js,ts}'",
        "test": "jest --coverage",
        "test:watch": "jest --watch"
    },
    "devDependencies": {
        "eslint": "^8.0.0",
        "prettier": "^2.5.0",
        "jest": "^27.0.0"
    }
}
```

## Summary

### Essential Tools by Language

**Python**:
- Linting: `pylint`, `flake8`
- Formatting: `black`, `isort`
- Testing: `pytest`
- Complexity: `radon`
- Security: `bandit`

**JavaScript/TypeScript**:
- Linting: `eslint`
- Formatting: `prettier`
- Testing: `jest`
- Refactoring: `jscodeshift`

**Java**:
- Linting: `checkstyle`, `PMD`
- Testing: `JUnit`
- Refactoring: IDE-based (IntelliJ, Eclipse)
- Quality: `SpotBugs`, `SonarQube`

### Integration Strategy

1. **Local Development**: IDE refactoring tools
2. **Pre-commit**: Linting and formatting
3. **CI/CD**: Comprehensive quality checks
4. **Code Review**: Static analysis results
5. **Production**: Monitoring and metrics

### Next Steps

- Set up [local tools](#ide-refactoring-tools)
- Configure [static analysis](#static-analysis-tools)
- Integrate with [CI/CD](#cicd-integration)
- Practice with [Examples](../examples/)
