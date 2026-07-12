"""Clients for the external services the ingest pipeline depends on:

    ocr   -> prescription image to drug names
    hira  -> drug name to raw 사용상의주의사항 (with local cache)
    llm   -> raw precaution text to structured JSON
"""
