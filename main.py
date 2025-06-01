if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "fastapi_tx_classifier.main:app", host="0.0.0.0", port=8000, reload=True
    )
