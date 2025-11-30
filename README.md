# Robot Framework with Playwright & Page Object Model

This project demonstrates an end-to-end e-commerce test suite using Robot Framework, Playwright (Browser Library), and the Page Object Model (POM) design pattern. It supports parallel execution and cross-browser testing on local and cloud environments.

## Project Structure

- `tests/`: Contains the test suites (e.g., `ecommerce_tests.robot`).
- `resources/`: Contains reusable keywords and variables.
  - `pages/`: Page Object files (keywords specific to pages).
  - `common.robot`: Common setup and teardown keywords.
  - `variables.robot`: Global variables and configuration.
- `custom_libs/`: Custom Python libraries (e.g., image comparison).
- `results/`: Directory for test reports and logs (git-ignored).
- `requirements.txt`: Python dependencies.

## Setup

1.  **Install Python**: Ensure Python 3.8+ is installed.
2.  **Create Virtual Environment** (Recommended):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Mac/Linux
    source .venv/bin/activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Initialize Playwright**:
    ```bash
    rfbrowser init
    ```

## Execution

### 1. Local Sequential Execution
Run all tests sequentially using the default browser (Chromium):
```bash
robot -d results tests/
```

### 2. Local Parallel Execution
Run tests in parallel using Pabot (e.g., 2 processes):
```bash
pabot --processes 2 -d results tests/
```

### 3. Cross-Browser Testing
Run tests on a specific browser (chromium, firefox, webkit):
```bash
robot -v BROWSER:firefox -d results tests/
```

### 4. Cloud Execution (LambdaTest/BrowserStack/SauceLabs)
To run on a cloud provider, set the `EXECUTION_ENV` variable to `remote` and provide credentials.

**Using Environment Variables (Recommended):**
```bash
# Set credentials (example for LambdaTest)
set LT_USERNAME=your_username
set LT_ACCESS_KEY=your_access_key

# Run tests
robot -v EXECUTION_ENV:remote -d results tests/
```
** parallel execution using pabot**
```bash
  pabot --pabotlib --testlevelsplit --processes 3 -v EXECUTION_ENV:remote -d results tests/
```

**Note**: You can also update `resources/variables.robot` with your credentials, but avoid committing secrets to version control.

## Custom Libraries
- `compare_images.py`: Used for visual regression testing (SSIM and OCR).