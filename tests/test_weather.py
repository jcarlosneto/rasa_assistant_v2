# -*- coding: utf-8 -*-
"""API de clima: a chave NUNCA pode aparecer no que o modulo imprime (logs/actions.log).
Usa um servidor falso (sem internet) e uma chave falsa."""
import pytest
import requests

from actions import weather_api

CHAVE = "abc123chavefalsa0000000000000000"


class RespostaFalsa:
    def __init__(self, url):
        self.url = url

    def raise_for_status(self):
        raise requests.exceptions.HTTPError("404 Client Error: Not Found for url: " + self.url)


def url_com_chave(params):
    return "https://api.openweathermap.org/data/2.5/weather?q=%s&appid=%s" % (params["q"], params["appid"])


@pytest.fixture
def api(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", CHAVE)
    return weather_api.WeatherAPI()


def test_erro_http_nao_imprime_a_chave(api, monkeypatch, capsys):
    monkeypatch.setattr(weather_api.requests, "get", lambda url, params, timeout: RespostaFalsa(url_com_chave(params)))
    assert api.obter_clima("CidadeQueNaoExiste") is None
    saida = capsys.readouterr().out
    assert "Erro HTTP" in saida and "appid=***" in saida
    assert CHAVE not in saida


def test_erro_de_conexao_nao_imprime_a_chave(api, monkeypatch, capsys):
    def falha(url, params, timeout):
        raise requests.exceptions.ConnectionError("Max retries exceeded with url: " + url_com_chave(params))
    monkeypatch.setattr(weather_api.requests, "get", falha)
    assert api.obter_clima("São Paulo") is None
    saida = capsys.readouterr().out
    assert "Erro de conexão" in saida and CHAVE not in saida


def test_sem_chave_nao_chama_a_api(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "")
    monkeypatch.setattr(weather_api.requests, "get", lambda *a, **k: pytest.fail("não devia chamar a API"))
    assert weather_api.WeatherAPI().obter_clima("São Paulo") is None
