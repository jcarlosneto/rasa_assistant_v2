# 🎓 MÓDULO DE API DE CLIMA - SUPER DIDÁTICO
# ============================================
# Este módulo integra com OpenWeatherMap API para buscar clima.
#
# 📚 CONCEITOS:
# - API: Interface de Programação de Aplicações (permite apps conversarem)
# - HTTP Request: Pedido para um servidor web
# - JSON: Formato de dados (JavaScript Object Notation)
# - Environment Variables: Variáveis de ambiente (.env)
#
# 🌤️ API USADA: OpenWeatherMap
# - Gratuita (até 60 chamadas/minuto)
# - Dados em tempo real
# - Suporta português

import requests
import os
from typing import Dict, Any, Optional
from .database import carregar_env

# 🔐 Carrega variáveis do arquivo .env (sem depender de biblioteca externa)
carregar_env()


class WeatherAPI:
    """
    🌤️ Classe que integra com OpenWeatherMap API.
    
    💡 POR QUE USAR API DE CLIMA?
    - Torna saudações mais personalizadas
    - Contexto útil para atividades (ex: "tempo bom para correr!")
    - Demonstra integração com APIs externas
    
    🔑 COMO OBTER API KEY (GRÁTIS):
    1. Acesse: https://openweathermap.org/api
    2. Crie conta gratuita
    3. Ative API Key no painel
    4. Adicione no arquivo .env
    
    ⚠️ IMPORTANTE:
    - Bot funciona SEM api key (só não mostra clima)
    - Nunca compartilhe sua API key publicamente!
    """
    
    def __init__(self):
        """
        🔧 Construtor da classe.
        
        💡 O QUE ACONTECE:
        1. Lê API key do ambiente
        2. Define URL base da API
        3. Configura unidades (Celsius) e idioma (PT-BR)
        """
        # 🔑 Lê API key do .env (ou string vazia se não existir)
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "")
        
        # 🌐 URL base da API
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"  # https: a chave nao trafega em claro
        
        # ⚙️ Configurações
        self.units = "metric"  # Celsius (imperial = Fahrenheit)
        self.lang = "pt_br"    # Português do Brasil
        
        if self.api_key:
            print("✅ [WEATHER API] API key configurada!")
    
    def obter_clima(self, cidade: str) -> Optional[Dict[str, Any]]:
        """
        🌤️ Busca informações de clima de uma cidade.
        
        Args:
            cidade: Nome da cidade (ex: "São Paulo")
        
        Returns:
            Dicionário com informações do clima, ou None se erro
        
        💡 ESTRUTURA DO RETORNO:
            {
                "temperatura": 22,  # Celsius
                "descricao": "céu limpo",
                "cidade": "São Paulo",
                "umidade": 65,  # %
                "sensacao": 21  # Sensação térmica
            }
        
        🔍 EXEMPLO DE USO:
            api = WeatherAPI()
            clima = api.obter_clima("São Paulo")
            if clima:
                print(f"Temperatura: {clima['temperatura']}°C")
        """
        # ❌ Se não tem API key, retorna None
        if not self.api_key:
            return None
        
        try:
            # 📦 Prepara parâmetros da requisição
            params = {
                "q": cidade,              # Nome da cidade
                "appid": self.api_key,    # Sua API key
                "units": self.units,      # Celsius
                "lang": self.lang         # Português
            }
            
            # 🌐 Faz requisição HTTP GET
            print(f"🌐 [WEATHER API] Buscando clima de {cidade}...")
            response = requests.get(
                self.base_url, 
                params=params, 
                timeout=5  # 5 segundos máximo
            )
            
            # ✅ Verifica se deu certo (status 200 = OK)
            response.raise_for_status()
            
            # 📊 Converte resposta JSON para dicionário Python
            data = response.json()
            
            # 🎯 Extrai informações relevantes
            clima_info = {
                "temperatura": round(data["main"]["temp"]),  # Arredonda
                "descricao": data["weather"][0]["description"],
                "cidade": data["name"],
                "umidade": data["main"]["humidity"],
                "sensacao": round(data["main"]["feels_like"])
            }
            
            print(f"✅ [WEATHER API] Clima obtido: {clima_info['temperatura']}°C")
            return clima_info
            
        except requests.exceptions.Timeout:
            # ⏱️ Timeout: API demorou muito
            print("⏱️  [WEATHER API] Timeout - API demorou muito")
            return None
            
        except requests.exceptions.HTTPError as e:
            # ❌ Erro HTTP (ex: 404 cidade não encontrada, 401 key inválida)
            print(f"❌ [WEATHER API] Erro HTTP: {e}")
            return None
            
        except requests.exceptions.RequestException as e:
            # 🌐 Erro de conexão (ex: sem internet)
            print(f"🌐 [WEATHER API] Erro de conexão: {e}")
            return None
            
        except KeyError as e:
            # 📊 Erro ao parsear JSON (estrutura diferente)
            print(f"📊 [WEATHER API] Erro ao processar dados: {e}")
            return None
            
        except Exception as e:
            # 🐛 Qualquer outro erro
            print(f"🐛 [WEATHER API] Erro inesperado: {e}")
            return None
    
    def obter_clima_multiple_cidades(self, cidades: list) -> Dict[str, Optional[Dict[str, Any]]]:
        """
        🌍 Busca clima de múltiplas cidades de uma vez.
        
        Args:
            cidades: Lista de nomes de cidades
        
        Returns:
            Dicionário {cidade: clima_info}
        
        💡 EXEMPLO:
            api = WeatherAPI()
            climas = api.obter_clima_multiple_cidades(["São Paulo", "Rio de Janeiro"])
            for cidade, clima in climas.items():
                if clima:
                    print(f"{cidade}: {clima['temperatura']}°C")
        """
        resultados = {}
        for cidade in cidades:
            resultados[cidade] = self.obter_clima(cidade)
        return resultados
    
    def formatar_clima_mensagem(self, clima_info: Optional[Dict[str, Any]]) -> str:
        """
        📝 Formata informações de clima em texto bonito.
        
        Args:
            clima_info: Dicionário retornado por obter_clima()
        
        Returns:
            String formatada para exibir ao usuário
        
        💡 EXEMPLO:
            "☀️ Hoje está 22°C e céu limpo em São Paulo"
        """
        if not clima_info:
            return ""
        
        temp = clima_info["temperatura"]
        desc = clima_info["descricao"]
        cidade = clima_info["cidade"]
        
        # 🌡️ Emoji baseado na temperatura
        if temp >= 30:
            emoji = "🔥"  # Muito quente
        elif temp >= 25:
            emoji = "☀️"  # Quente
        elif temp >= 20:
            emoji = "🌤️"  # Agradável
        elif temp >= 15:
            emoji = "⛅"  # Fresco
        else:
            emoji = "🥶"  # Frio
        
        mensagem = f"{emoji} Hoje está {temp}°C e {desc} em {cidade}"
        
        # 💧 Adiciona info de umidade se alta
        if clima_info.get("umidade", 0) > 80:
            mensagem += " (ar úmido)"
        
        return mensagem


# 🎓 NOTA DIDÁTICA:
# 
# COMO APIS FUNCIONAM?
# 
# 1. REQUISIÇÃO (seu código → servidor)
#    GET http://api.exemplo.com/dados?parametro=valor
# 
# 2. PROCESSAMENTO (servidor processa)
#    - Valida parâmetros
#    - Busca dados no banco
#    - Aplica lógica de negócio
# 
# 3. RESPOSTA (servidor → seu código)
#    JSON: {"temperatura": 22, "cidade": "São Paulo"}
# 
# 4. USO (seu código usa dados)
#    temp = dados["temperatura"]
#    print(f"Temperatura: {temp}°C")
#
# ═══════════════════════════════════════════
#
# EXERCÍCIO PARA ALUNOS:
# 
# 1. Criar método obter_previsao_5_dias(cidade)
#    Dica: endpoint /forecast usa previsão
# 
# 2. Adicionar cache para não chamar API toda hora
#    Dica: salvar resultado em dict com timestamp
# 
# 3. Criar método sugerir_atividade(clima_info)
#    Exemplo: se quente → "Ótimo para correr!"
#              se chovendo → "Dia perfeito para yoga indoor!"
# 
# 4. Integrar com outra API (ex: Advice Slip para frases motivacionais)
#    URL: https://api.adviceslip.com/advice
