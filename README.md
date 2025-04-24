# CAMHEALTH - AI Calorie Estimator

This repository contains the source code and documentation for our EECE 490 course project, supervised by Prof. Ammar Mohanna.



## Project Contributors

*   Paolo Hadaie
*   Hossam Mostafa

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
