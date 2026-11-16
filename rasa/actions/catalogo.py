# -*- coding: utf-8 -*-
"""
CATALOGO - regras deterministicas que complementam o modelo de linguagem.

Por que este arquivo existe?
----------------------------
O NLU do Rasa (DIETClassifier) e bom em generalizar frases, mas devolve o
texto como o usuario escreveu: "meditei", "1" (de "1 hora"), "intenso".
Antes de gravar no banco, precisamos de valores canonicos: "meditacao",
60 minutos, "intensa". Isso se faz com regra simples, testavel e previsivel.

Licao da aula: aprendizado de maquina para ENTENDER, regra para NORMALIZAR.

Este modulo nao depende do Rasa: roda em qualquer Python 3.8+ e tem testes
proprios em tests/test_catalogo.py.
"""
import re
import unicodedata
from datetime import date, datetime, timedelta

# ---------------------------------------------------------------------------
# 1. Tipos de atividade
# ---------------------------------------------------------------------------
# chave = forma canonica gravada no banco; valores = variacoes aceitas.
TIPOS = {
    "água": ["agua", "água", "hidratacao", "hidratar", "hidratei"],
    "corrida": ["corrida", "corri", "correr", "running", "run"],
    "caminhada": ["caminhada", "caminhei", "caminhar", "andei", "andar", "walking"],
    "meditação": ["meditacao", "meditei", "meditar", "mindfulness"],
    "natação": ["natacao", "nadei", "nadar", "swimming", "piscina"],
    "musculação": ["musculacao", "malhei", "malhar", "academia", "treino", "gym"],
    "exercício": ["exercicio", "exercitei", "exercitar"],
    "yoga": ["yoga", "ioga"],
    "ciclismo": ["ciclismo", "pedalei", "pedalar", "bicicleta", "bike"],
    "alongamento": ["alongamento", "alonguei", "alongar"],
    "leitura": ["leitura", "li", "ler", "livro"],
    "tarefa": ["tarefa"],
}

# Resgate por palavra-chave no texto (mesma lista da versao 1 do projeto).
# "h2o" fica DE FORA de proposito: e a falha usada na correcao ao vivo.
PALAVRAS_RESGATE = ["corrida", "caminhada", "natação", "meditação", "exercício",
                    "musculação", "ciclismo"]


def sem_acento(texto):
    """'Meditação' -> 'meditacao'. Facilita comparar o que o usuario digitou."""
    nfkd = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


_INDICE_TIPOS = {}
for _canonico, _variacoes in TIPOS.items():
    for _v in _variacoes + [_canonico]:
        _INDICE_TIPOS[sem_acento(_v)] = _canonico


def normalizar_tipo(valor):
    """
    Converte o valor extraido pelo NLU na forma canonica.
    Se nao conhecer a palavra, devolve o proprio texto em minusculas
    (nao descartamos atividades novas, como 'pilates').
    """
    if valor is None:
        return None
    chave = sem_acento(valor)
    if not chave:
        return None
    return _INDICE_TIPOS.get(chave, str(valor).strip().lower())


def resgatar_tipo_do_texto(texto):
    """
    Plano B quando o NLU reconheceu a intencao mas nao marcou a entidade.
    Procura palavra por palavra apenas nos tipos de PALAVRAS_RESGATE.
    """
    palavras = re.findall(r"[a-z0-9]+", sem_acento(texto))
    for palavra in palavras:
        canonico = _INDICE_TIPOS.get(palavra)
        if canonico in PALAVRAS_RESGATE:
            return canonico
    return None


# ---------------------------------------------------------------------------
# 2. Duracao em minutos
# ---------------------------------------------------------------------------
_NUM = r"(\d+(?:[.,]\d+)?)"
_EXTENSO = {"uma": 1, "um": 1, "duas": 2, "dois": 2, "tres": 3, "quatro": 4}


def extrair_duracao_min(texto, valor_entidade=None):
    """
    Devolve a duracao em minutos (float) ou None.

    Exemplos:
        "malhei 1 hora"        -> 60.0   (a versao 1 gravava 1 minuto)
        "nadei meia hora"      -> 30.0
        "corri 1h30"           -> 90.0
        "pedalei 2 horas e meia" -> 150.0
        "corri 30 minutos"     -> 30.0
        "45" (resposta do formulario) -> 45.0
    """
    t = sem_acento(texto or "")

    m = re.search(r"(\d+)\s*h\s*(\d{1,2})\b", t)                 # 1h30
    if m:
        return float(int(m.group(1)) * 60 + int(m.group(2)))

    m = re.search(_NUM + r"\s*(?:h|hora|horas)\b(\s*e\s*meia)?", t)  # 2 horas (e meia)
    if m:
        minutos = float(m.group(1).replace(",", ".")) * 60
        return minutos + (30 if m.group(2) else 0)

    m = re.search(r"\b(uma|um|duas|dois|tres|quatro)\s+horas?\b(\s*e\s*meia)?", t)
    if m:
        return float(_EXTENSO[m.group(1)] * 60 + (30 if m.group(2) else 0))

    if re.search(r"\bmeia\s+hora\b", t):
        return 30.0

    m = re.search(_NUM + r"\s*(?:min|mins|minuto|minutos)\b", t)   # 30 min
    if m:
        return float(m.group(1).replace(",", "."))

    # Sem unidade no texto: usa o numero que o NLU marcou (assume minutos).
    for candidato in (valor_entidade, t):
        if candidato is None:
            continue
        m = re.fullmatch(r"\s*" + _NUM + r"\s*", str(candidato))
        if m:
            return float(m.group(1).replace(",", "."))
    return None


def duracao_valida(minutos):
    """Regra de negocio herdada da versao 1: entre 1 e 300 minutos."""
    return minutos is not None and 1 <= minutos <= 300


# ---------------------------------------------------------------------------
# 3. Intensidade
# ---------------------------------------------------------------------------
INTENSIDADES = {
    "leve": ["leve", "tranquilo", "tranquila", "suave", "relaxante", "fraco", "fraca"],
    "moderada": ["moderada", "moderado", "medio", "media", "normal"],
    "intensa": ["intensa", "intenso", "forte", "pesado", "pesada", "puxado", "puxada"],
}
_INDICE_INTENSIDADE = {}
for _canonico, _variacoes in INTENSIDADES.items():
    for _v in _variacoes:
        _INDICE_INTENSIDADE[sem_acento(_v)] = _canonico


def normalizar_intensidade(valor):
    """'intenso', 'forte', 'pesado' -> 'intensa'. Desconhecido -> None."""
    if valor is None:
        return None
    for palavra in re.findall(r"[a-z]+", sem_acento(valor)):
        if palavra in _INDICE_INTENSIDADE:
            return _INDICE_INTENSIDADE[palavra]
    return None


# ---------------------------------------------------------------------------
# 4. Quando (para a agenda)
# ---------------------------------------------------------------------------
_DIAS_SEMANA = {"segunda": 0, "terca": 1, "quarta": 2, "quinta": 3,
                "sexta": 4, "sabado": 5, "domingo": 6}


def extrair_quando(texto, agora=None):
    """
    Interpreta data e hora de frases como "amanha as 7h" ou "sexta 18:30".

    Devolve um dicionario:
        {"data": "2026-11-20", "hora": "07:00" ou None, "entendeu_data": bool}
    Se nenhuma data aparecer no texto, assume HOJE e marca entendeu_data=False,
    para a action poder avisar o usuario do que foi assumido.
    """
    agora = agora or datetime.now()
    t = sem_acento(texto or "")
    hoje = agora.date()
    data = None

    if re.search(r"\bdepois de amanha\b", t):
        data = hoje + timedelta(days=2)
    elif re.search(r"\bamanha\b", t):
        data = hoje + timedelta(days=1)
    elif re.search(r"\bhoje\b", t):
        data = hoje
    else:
        for nome, numero in _DIAS_SEMANA.items():
            if re.search(r"\b" + nome + r"(-feira)?\b", t):
                dias = (numero - hoje.weekday()) % 7
                data = hoje + timedelta(days=dias or 7)   # "sexta" dita numa sexta = a proxima
                break
    if data is None:
        m = re.search(r"\bdia\s+(\d{1,2})\b", t)
        if m:
            dia = int(m.group(1))
            try:
                data = date(hoje.year, hoje.month, dia)
                if data < hoje:                              # "dia 5" ja passou: mes seguinte
                    mes = hoje.month % 12 + 1
                    ano = hoje.year + (1 if mes == 1 else 0)
                    data = date(ano, mes, dia)
            except ValueError:
                data = None

    hora = None
    m = (re.search(r"\b(\d{1,2})[:h](\d{2})\b", t)               # 7:30, 7h30
         or re.search(r"\b(\d{1,2})\s*(?:h|hs|hora|horas)\b", t)  # 7h, 19 horas
         or re.search(r"\bas\s+(\d{1,2})\b", t))                  # as 7
    if m:
        h = int(m.group(1))
        minuto = int(m.group(2)) if m.lastindex and m.lastindex >= 2 else 0
        if re.search(r"\b(da|de)\s+(tarde|noite)\b", t) and h < 12:
            h += 12
        if 0 <= h <= 23 and 0 <= minuto <= 59:
            hora = "%02d:%02d" % (h, minuto)

    return {
        "data": (data or hoje).isoformat(),
        "hora": hora,
        "entendeu_data": data is not None,
    }


def descrever_data(data_iso, agora=None):
    """'2026-11-20' -> 'hoje', 'amanha' ou 'sex 20/11'."""
    agora = agora or datetime.now()
    d = date.fromisoformat(data_iso)
    delta = (d - agora.date()).days
    if delta == 0:
        return "hoje"
    if delta == 1:
        return "amanhã"
    nomes = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
    return "%s %02d/%02d" % (nomes[d.weekday()], d.day, d.month)


# ---------------------------------------------------------------------------
# 5. Periodo do dia (saudacao contextual)
# ---------------------------------------------------------------------------
def saudacao_do_periodo(hora):
    """0-11 -> 'Bom dia', 12-17 -> 'Boa tarde', 18-23 -> 'Boa noite'."""
    if hora < 12:
        return "Bom dia"
    if hora < 18:
        return "Boa tarde"
    return "Boa noite"
