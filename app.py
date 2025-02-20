import requests
from flask import Flask, render_template, request

app = Flask(__name__)

# Chave da API (substitua com sua chave real)
api_key = "RGAPI-594261dd-e7e7-46b2-a42e-030b48e4fa7d"
api_url = "https://br1.api.riotgames.com/lol"

# Função para obter dados do campeão
def get_champion_data():
    url = f"{api_url}/platform/v3/champions"
    response = requests.get(url, headers={"X-Riot-Token": api_key})
    return response.json() if response.status_code == 200 else []

# Função para calcular o dano baseado nas entradas
def calculate_damage(champion, skill, level, ap, ad, resistencia):
    # Exemplo simplificado de cálculo de dano, ajuste conforme necessário
    base_damage = {
        "Q": 100, "W": 80, "E": 60, "R": 150  # Exemplos de dano base por habilidade
    }
    skill_damage = base_damage.get(skill, 0)
    
    # Ajuste de dano com base em AP e AD
    damage = skill_damage + (ap * 0.6) + (ad * 0.7)
    
    # Considerando a resistência do alvo (armadura ou MR)
    damage_reduced = damage / (1 + resistencia / 100)
    
    return round(damage_reduced, 2)

@app.route("/", methods=["GET", "POST"])
def index():
    champions = get_champion_data()  # Carregar dados dos campeões da API
    result = None

    if request.method == "POST":
        champion = request.form["champion"]
        skill = request.form["skill"]
        level = int(request.form["level"])
        ap = float(request.form["ap"])
        ad = float(request.form["ad"])
        resistencia = float(request.form["resistencia"])

        # Calcular o dano
        result = calculate_damage(champion, skill, level, ap, ad, resistencia)

    return render_template("index.html", champions=champions, result=result)

if __name__ == "__main__":
    app.run(debug=True)
