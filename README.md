# CAMHEALTH - AI Calorie Estimator

This repository contains the source code and documentation for our EECE 490 course project, supervised by Prof. Ammar Mohanna.



## Project Contributors

*   [Paolo Hadaie]
*   [Hossam Mostafa]

## Project Overview

This project implements an interactive web application for estimating meal calories using AI. It leverages APIs for computer vision (Roboflow) for food identification from user-uploaded images and natural language processing (OpenAI Assistants API) to provide a conversational user experience via a dedicated AI assistant. The application is built using Python and the Streamlit framework, integrating custom data processing and unit conversion logic to calculate calorie estimates based on user input and internal nutritional data. The primary goal is to offer a user-friendly alternative to manual calorie tracking.

## Key Features

*   **AI-Powered Food Identification:** Upload a meal photo for automated food suggestion.
*   **Interactive Calorie Estimation:** Guided workflow to confirm food, specify portion size using various units, and add meal components.
*   **Conversational AI Assistant:** Provides feedback during the process and answers food/nutrition-related questions.
*   **Detailed Meal Summary:** Displays estimated grams and calories for each item and the total meal.
*   **Flexible Unit Handling:** Supports input in grams, oz, tsp, tbsp, pieces, slices, small/medium/large, etc.

## Installation and Setup

Follow these steps to set up the project environment locally.

### Prerequisites

*   Python 3.9 or later installed.
*   `pip` (Python package installer).
*   Git (for cloning the repository).
*   Accounts and API Keys for:
    *   Roboflow (API Key and Classification Model ID is required - the model used in the code is `food-101-ih2pp/4`)
    *   OpenAI (API Key and Assistant ID is required - the assistant used in the code is `asst_Qwxm9bSS2gu771Cqx3jG46B6`)

### Setup Steps

1.  **Clone the Repository:**
    ```bash
    git clone <repository-url> # Replace <repository-url> with the actual URL
    cd <repository-directory> # Navigate into the cloned project folder
    ```

2.  **Create and Activate a Virtual Environment (Recommended):**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    Install the required Python packages using the provided `requirements.txt` file:
    ```bash
    pip install -r requirements.txt
    ```
    *(See contents below if `requirements.txt` is not provided)*

4.  **Prepare Calorie Data (One-Time Step):**
    The application relies on a processed data file (`calorie_table_processed.csv`). You need to run the `csv.py` script **once** to generate this file from its internal data source.
    ```bash
    python csv.py
    ```
    This command will create the `calorie_table_processed.csv` file in the same directory. If you update the data within `csv.py`, you will need to run this script again.

5.  **Configure API Keys and IDs (Streamlit Secrets):**
    Create a file named `.streamlit/secrets.toml` in your project directory (create the `.streamlit` folder if it doesn't exist). Add your API keys and Assistant ID to this file like follows:

    ```toml
    # .streamlit/secrets.toml

    # --- OpenAI Configuration ---
    # Ensure this key is used in ut.py where openai.api_key is set, or modify ut.py accordingly
    OPENAI_API_KEY = "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" 

    # Ensure this key is used in ut.py for the ASSISTANT_ID constant
    ASSISTANT_ID = "asst_Qwxm9bSS2gu771Cqx3jG46B6"        

    # --- Roboflow Configuration ---
    # Ensure these keys match how they are accessed in stream.py (e.g., st.secrets["ROBOFLOW_API_KEY"])
    # Note: The provided stream.py currently hardcodes these. Modify stream.py to use secrets for production.
    ROBOFLOW_API_KEY = "xxxxxxxxxxxxxxxxxxxx"           # Replace with your actual Roboflow API Key
    ROBOFLOW_MODEL_ID = "food-101-ih2pp/4"    

    # Optional: If using a different Roboflow API URL (e.g., for serverless)
    ROBOFLOW_API_URL = "https://detect.roboflow.com" # Adjust if necessary based on Roboflow model type/deployment
    ```
    **Important:** Modify the application code (`stream.py` and `ut.py`) to consistently retrieve these values using `st.secrets["KEY_NAME"]` instead of hardcoding them, especially for production use.

## Running the Application

Once the setup is complete:

1.  Ensure your virtual environment is activated.
2.  Navigate to the project directory in your terminal.
3.  Run the Streamlit application using the following command:

    ```bash
    streamlit run stream.py
    ```
    This will start the Streamlit server, and the application should open automatically in your default web browser (typically at `http://localhost:8501`).

## Usage

1.  Open the application in your web browser.
2.  Follow the on-screen prompts: Upload an image -> Confirm/Select food -> Specify quantity -> Add extras (optional) -> Calculate.
3.  Interact with the CAMHEALTH assistant for feedback and Q&A in the final step.

## `requirements.txt` Contents

If a `requirements.txt` file is not included, create one with the following content:

```txt
streamlit
openai>=1.0.0 # Ensure version supports the required beta Assistants API features
inference-sdk # Roboflow SDK
Pillow
