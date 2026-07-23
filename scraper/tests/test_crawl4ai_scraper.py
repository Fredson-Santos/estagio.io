"""
test_crawl4ai_scraper.py — Testes unitarios para o scraper Crawl4AI
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from estagio_shared.services.scrapers.crawl4ai_scraper import (
    parse_crawl4ai_markdown,
    run_crawl4ai_scraper,
    _guess_area,
    _guess_modality
)
from estagio_shared.taxonomy import JobArea, JobModality


def test_parse_crawl4ai_markdown():
    url = "https://empresa.com/vagas/123"
    markdown = """# Estágio em Engenharia de Software
Empresa: Tech Solutions
Modalidade: Remoto
Buscamos estudante para atuar no desenvolvimento de APIs com Python e FastAPI.
"""
    parsed = parse_crawl4ai_markdown(url, markdown)

    assert parsed["title"] == "Estágio em Engenharia de Software"
    assert parsed["company"] == "Empresa"
    assert parsed["modality"] == JobModality.REMOTE
    assert parsed["area"] == JobArea.TI_SOFTWARE
    assert parsed["source_url"] == url


def test_guess_modality_and_area():
    assert _guess_modality("Trabalho 100% home office") == JobModality.REMOTE
    assert _guess_modality("Modelo Híbrido 2x por semana") == JobModality.HYBRID
    assert _guess_modality("Atuação no escritório de SP") == JobModality.ONSITE

    assert _guess_area("Estágio em Ciência de Dados", "Python e Pandas") == JobArea.DADOS
    assert _guess_area("Estágio de Design", "Figma e UI/UX") == JobArea.DESIGN


@pytest.mark.asyncio
async def test_run_crawl4ai_scraper_mocked():
    mock_res = MagicMock()
    mock_res.success = True
    mock_res.markdown = "# Estágio em Marketing Digital\nAtuação com redes sociais e SEO."

    mock_crawler = AsyncMock()
    mock_crawler.arun.return_value = mock_res
    
    mock_crawler_context = AsyncMock()
    mock_crawler_context.__aenter__.return_value = mock_crawler
    mock_crawler_context.__aexit__.return_value = None

    with patch("estagio_shared.services.scrapers.crawl4ai_scraper.CRAWL4AI_AVAILABLE", True), \
         patch("estagio_shared.services.scrapers.crawl4ai_scraper.AsyncWebCrawler", return_value=mock_crawler_context):

        results = await run_crawl4ai_scraper(["https://empresa.com/vaga"])

        assert len(results) == 1
        assert results[0]["title"] == "Estágio em Marketing Digital"
        assert results[0]["area"] == JobArea.MARKETING
