import pytest
from job_extractor import _detect_platform, _scrape_page, extract_job, _extract_with_llm

def test_detect_platform():
    assert _detect_platform("https://www.linkedin.com/jobs/view/123") == "LinkedIn"
    assert _detect_platform("https://gupy.io/vagas/123") == "Gupy"
    assert _detect_platform("https://unknown-site.com/job") == "Unknown-site"

def test_scrape_page_success(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "<html><head><title>Vaga de Teste</title></head><body><h1>Desenvolvedor</h1><p>Vaga remota Python.</p></body></html>"
    mock_response.raise_for_status = mocker.Mock()
    
    mocker.patch("requests.get", return_value=mock_response)
    
    result = _scrape_page("https://example.com/vaga")
    assert "Vaga de Teste" in result
    assert "Desenvolvedor" in result
    assert "Vaga remota Python" in result

def test_scrape_page_error(mocker):
    import requests
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mocker.patch("requests.get", side_effect=requests.exceptions.HTTPError(response=mock_response))
    
    with pytest.raises(RuntimeError, match="HTTP 404 ao acessar a URL"):
        _scrape_page("https://example.com/vaga")

def test_extract_job_success(mocker):
    mocker.patch("job_extractor._scrape_page", return_value="Conteudo raspado fake")
    
    mock_llm_result = {
        "cargo": "Dev",
        "empresa": "TechCorp",
        "plataforma": "LinkedIn",
        "localizacao": "Remoto",
        "modalidade": "Remoto",
        "tipo_contrato": "CLT",
        "salario": "Não informado",
        "descricao_resumida": "Vaga legal.",
        "url": "https://linkedin.com/vaga"
    }
    mocker.patch("job_extractor._extract_with_llm", return_value=mock_llm_result)
    
    mock_client = mocker.Mock()
    
    result = extract_job("https://linkedin.com/vaga", mock_client, "mock_model")
    
    assert result["cargo"] == "Dev"
    assert result["empresa"] == "TechCorp"
    assert result["url"] == "https://linkedin.com/vaga"
    assert "data_extracao" in result

def test_extract_job_scrape_failure(mocker):
    mocker.patch("job_extractor._scrape_page", side_effect=RuntimeError("HTTP 404 ao acessar a URL"))
    
    mock_client = mocker.Mock()
    result = extract_job("https://linkedin.com/vaga", mock_client, "mock_model")
    
    assert result["erro"] == "HTTP 404 ao acessar a URL"
    assert result["cargo"] == "N/A"


def test_scrape_with_crawl4ai_success(mocker):
    mocker.patch("job_extractor._scrape_with_crawl4ai", return_value="[Conteúdo Crawl4AI - Markdown]\n# Vaga de Estágio")
    result = _scrape_page("https://example.com/vaga-dinamica")
    assert "[Conteúdo Crawl4AI - Markdown]" in result
    assert "# Vaga de Estágio" in result


def test_scrape_with_crawl4ai_fallback(mocker):
    mock_response = mocker.Mock()
    mock_response.text = "<html><head><title>Vaga Fallback</title></head><body><h1>Estágio Python</h1></body></html>"
    mock_response.raise_for_status = mocker.Mock()
    
    mocker.patch("job_extractor._scrape_with_crawl4ai", return_value=None)
    mocker.patch("requests.get", return_value=mock_response)
    
    result = _scrape_page("https://example.com/vaga-estatica")
    assert "Vaga Fallback" in result
    assert "Estágio Python" in result

