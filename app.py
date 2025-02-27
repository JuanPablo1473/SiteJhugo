from flask import Flask, render_template
import requests

app = Flask(__name__)

# URL base para obter os dados da API do LoL
API_VERSION = "14.3.1"
API_BASE_URL = f"https://ddragon.leagueoflegends.com/cdn/{API_VERSION}/"

# Cache para evitar requisições repetitivas desnecessárias
champions, runes, items = {}, [], {}

# Função para organizar campeões por função automaticamente
def get_champions_by_role(champions_data):
    roles = {
        "top": [],
        "jungle": [],
        "mid": [],
        "adc": [],
        "support": []
    }
    
    for champ_id, champ_info in champions_data.items():
        champ_id_clean = champ_id.replace("'", "").replace(" ", "").replace(".", "").replace("&", "").replace("’", "")
        champ_id_clean = champ_id_clean[0].upper() + champ_id_clean[1:] if champ_id_clean else champ_id_clean
        tags = champ_info.get("tags", [])
        
        icon_url = f"{API_BASE_URL}img/champion/{champ_id_clean}.png"
        
        if "Fighter" in tags or "Tank" in tags:
            roles["top"].append({"id": champ_id_clean, "name": champ_info["name"], "icon": icon_url})
        if "Assassin" in tags or "Mage" in tags:
            roles["mid"].append({"id": champ_id_clean, "name": champ_info["name"], "icon": icon_url})
        if "Marksman" in tags:
            roles["adc"].append({"id": champ_id_clean, "name": champ_info["name"], "icon": icon_url})
        if "Support" in tags:
            roles["support"].append({"id": champ_id_clean, "name": champ_info["name"], "icon": icon_url})
        if "Jungle" in tags:
            roles["jungle"].append({"id": champ_id_clean, "name": champ_info["name"], "icon": icon_url})
    
    return roles

# Função para carregar campeões
def get_champions():
    try:
        response = requests.get(f"{API_BASE_URL}data/pt_BR/champion.json")
        champions_data = response.json().get("data", {})
        champions = get_champions_by_role(champions_data)
        print(f"✅ {len(champions_data)} campeões carregados e organizados por função!")
        return champions
    except Exception as e:
        print("❌ Erro ao carregar campeões:", e)
        return {}

# Função para obter detalhes do campeão
def get_champion_details(champion_id):
    try:
        formatted_id = champion_id.replace("'", "").replace(" ", "").replace(".", "").replace("&", "").replace("’", "")
        formatted_id = formatted_id[0].upper() + formatted_id[1:]

        url = f"{API_BASE_URL}data/pt_BR/champion/{formatted_id}.json"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"❌ Erro {response.status_code}: Não foi possível obter os dados do campeão {formatted_id}. URL: {url}")
            return {}

        champion_data = response.json().get("data", {}).get(formatted_id, {})
        if not champion_data:
            print(f"❌ Campeão {formatted_id} não encontrado na API! Verifique o nome correto.")
            return {}

        # Corrigir caminho da imagem do campeão
        champion_data["icon"] = f"https://ddragon.leagueoflegends.com/cdn/{API_VERSION}/img/champion/{champion_data['image']['full']}"

        # Adicionar estatísticas de nível 1 a 18 e remover o traço extra
        for stat in ["hp", "mp", "armor", "spellblock", "attackdamage", "attackspeed"]:
            stat_growth = champion_data["stats"].get(f"{stat}perlevel", 0)
            stat_base = champion_data["stats"].get(stat, 0)
            stat_final = round(stat_base + stat_growth * 17, 2)  # Calcula o valor final no nível 18
            champion_data["stats"][stat] = f"{stat_base} - {stat_final}".strip(" -")

        # Corrigir caminhos das habilidades
        for spell in champion_data.get("spells", []):
            spell["icon"] = f"https://ddragon.leagueoflegends.com/cdn/{API_VERSION}/img/spell/{spell['image']['full']}"

        # Corrigir caminho da passiva
        if "passive" in champion_data:
            champion_data["passive"]["icon"] = f"https://ddragon.leagueoflegends.com/cdn/{API_VERSION}/img/passive/{champion_data['passive']['image']['full']}"

        return champion_data
    except Exception as e:
        print(f"❌ Erro ao carregar dados do campeão {champion_id}: {e}")
        return {}

# Função para carregar runas
def get_runes():
    try:
        response = requests.get(f"{API_BASE_URL}data/pt_BR/runesReforged.json")
        runes = response.json()
        print(f"✅ {len(runes)} categorias de runas carregadas!")
        return runes
    except Exception as e:
        print("❌ Erro ao carregar runas:", e)
        return []

# Função para carregar itens
def get_items():
    try:
        response = requests.get(f"{API_BASE_URL}data/pt_BR/item.json")
        items_data = response.json().get("data", {})
        categorized_items = {"Iniciais": [], "Épicos": [], "Lendários": []}
        
        for item_id, item_info in items_data.items():
            item = {
                "name": item_info["name"],
                "description": item_info["description"],
                "icon": f"{API_BASE_URL}img/item/{item_id}.png",
                "cost": item_info.get("gold", {}).get("total", 0),
            }
            categorized_items["Lendários"].append(item)
        
        print(f"✅ Itens carregados: {sum(len(v) for v in categorized_items.values())}")
        return categorized_items
    except Exception as e:
        print("❌ Erro ao carregar itens:", e)
        return {}

# Inicializa os dados
print("🔄 Carregando dados do League of Legends...")
champions = get_champions()
runes = get_runes()
items = get_items()
print("✅ Dados carregados com sucesso!")

# Rotas do Flask
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/champions")
def champions_page():
    return render_template("champions.html", champions_by_role=champions)

@app.route("/champion/<champion_id>")
def champion_page(champion_id):
    champion_data = get_champion_details(champion_id)
    if not champion_data:
        return "Campeão não encontrado", 404
    return render_template("champion.html", champion=champion_data)

@app.route("/runes")
def runes_page():
    return render_template("runes.html", runes=runes)

@app.route("/items")
def items_page():
    return render_template("items.html", items=items)

if __name__ == "__main__":
    app.run(debug=True)
 
