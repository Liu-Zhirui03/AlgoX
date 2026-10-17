"""Serve AlgoX and dispatch requests to registered algorithm modules."""

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from backend.ollama import ConnectionStatus, check_connection
from backend.registry import ALGORITHMS, AlgorithmDefinition
from backend.schemas import AlgorithmInfo, AlgorithmResult

FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
app = FastAPI(title="AlgoX", docs_url=None, redoc_url=None)


def get_algorithm(algorithm_id: str) -> AlgorithmDefinition:
    algorithm = ALGORITHMS.get(algorithm_id)
    if algorithm is None:
        raise HTTPException(status_code=404, detail="Algorithm is not supported.")
    return algorithm


def execute(algorithm: AlgorithmDefinition, payload: dict[str, Any]) -> AlgorithmResult:
    try:
        validated = algorithm.input_model.model_validate(payload)
    except ValidationError as error:
        errors = [{**item, "loc": ("body", *item["loc"])} for item in error.errors()]
        raise RequestValidationError(errors, body=payload) from error
    return algorithm.run(validated)


@app.get("/api/status", response_model=ConnectionStatus)
def status(response: Response) -> ConnectionStatus:
    response.headers["Cache-Control"] = "no-store"
    return check_connection()


@app.get("/api/algorithms", response_model=list[AlgorithmInfo])
def list_algorithms(response: Response) -> list[AlgorithmInfo]:
    response.headers["Cache-Control"] = "no-store"
    return [algorithm.info() for algorithm in ALGORITHMS.values()]


@app.get("/api/algorithms/{algorithm_id}", response_model=AlgorithmResult)
@app.get("/api/examples/{algorithm_id}", response_model=AlgorithmResult, include_in_schema=False)
def algorithm_example(algorithm_id: str, response: Response) -> AlgorithmResult:
    response.headers["Cache-Control"] = "no-store"
    algorithm = get_algorithm(algorithm_id)
    return execute(algorithm, algorithm.default_input)


@app.post("/api/algorithms/{algorithm_id}", response_model=AlgorithmResult)
@app.post("/api/examples/{algorithm_id}", response_model=AlgorithmResult, include_in_schema=False)
def run_algorithm(algorithm_id: str, payload: dict[str, Any], response: Response) -> AlgorithmResult:
    response.headers["Cache-Control"] = "no-store"
    return execute(get_algorithm(algorithm_id), payload)


@app.get("/algorithms/{algorithm_id}", include_in_schema=False)
def algorithm_page(algorithm_id: str) -> FileResponse:
    return FileResponse(FRONTEND / get_algorithm(algorithm_id).playground_file)


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(FRONTEND / "index.html")


app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")
