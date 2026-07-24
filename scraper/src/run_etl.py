import asyncio
import logging

# Backward-compat shim: lógica real em estagio_shared.services.etl
from estagio_shared.services.etl import (  # noqa: F401
    run_pipeline,
    get_or_create_gupy_source,
    get_or_create_eureca_source,
)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    asyncio.run(run_pipeline())
