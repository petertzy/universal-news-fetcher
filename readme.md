**## Getting Started**

### 1. Install the required modules

First, run the command below to install the necessary modules in your project:

```bash
pip install -r requirements.txt
```

This will install all the dependencies listed in the `requirements.txt` file.

### 2. Start the ASGI server with Uvicorn

Next, run the command below to start the **ASGI server** using **Uvicorn** to serve your **FastAPI application**:

```bash
uvicorn app:app --reload
```

This will start the server with automatic reloading enabled, which is helpful during development. Your FastAPI app will now be running, and you can interact with the API at `http://localhost:8000`.
