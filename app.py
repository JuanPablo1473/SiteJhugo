from flask import Flask, render_template, request
import json

app = Flask(__name__)

# Dados básicos de campeões e escalamentos (com níveis das habilidades)
champions = {
    "Akali": {
        "skills": {
            "Q": {"name": "Golpe dos Cinco Pontos", "damage": [50, 80, 110, 140, 170], "ratio": {"AP": 0.6}},
            "E": {"name": "Investida Shuriken", "damage": [60, 90, 120, 150, 180], "ratio": {"AP": 0.5}},
            "R": {"name": "Execução Perfeita", "damage": [120, 180, 240], "ratio": {"AD": 1.0}}
        }
    },
    # Adicionar mais campeões conforme necessário
}

def calcular_dano_real(dano, resistencia):
    return dano * (100 / (100 + resistencia))

@app.route("/")
def home():
    return render_template("index.html", champions=champions)

@app.route("/calculate", methods=["POST"])
def calculate():
    champion = request.form.get("champion")
    skill = request.form.get("skill")
    level = request.form.get("level")
    resistencia = request.form.get("resistencia")
    ap = float(request.form.get("ap", 0))
    ad = float(request.form.get("ad", 0))

    if not champion or not skill or not level or not resistencia:
        return render_template("index.html", champions=champions, result="Erro: Todos os campos devem ser preenchidos.")

    max_level = 3 if skill == "R" else 5
    level = max(1, min(int(level), max_level)) - 1
    
    resistencia = float(resistencia)
    
    if champion in champions and skill in champions[champion]["skills"]:
        skill_data = champions[champion]["skills"][skill]
        base_damage = skill_data["damage"][level]
        
        total_damage = base_damage
        for stat, ratio in skill_data["ratio"].items():
            if stat == "AP":
                total_damage += ap * ratio
            elif stat == "AD":
                total_damage += ad * ratio
        
        dano_real = calcular_dano_real(total_damage, resistencia)

        # Enviar dados do gráfico (dano por habilidade)
        chart_data = {
            "labels": [skill_data['name']],
            "datasets": [{
                "label": "Dano Estimado",
                "data": [total_damage],
                "backgroundColor": "rgba(75, 192, 192, 0.2)",
                "borderColor": "rgba(75, 192, 192, 1)",
                "borderWidth": 1
            }]
        }

        return render_template(
            "index.html",
            champions=champions,
            result=f"Habilidade: {skill_data['name']} | Dano estimado: {total_damage:.2f}, Dano real após resistência: {dano_real:.2f}",
            selected_champion=champion,
            chart_data=json.dumps(chart_data)  # Passar os dados do gráfico para o template
        )
    else:
        return render_template("index.html", champions=champions, result="Erro ao calcular dano. Verifique os dados.")

if __name__ == "__main__":
    app.run(debug=True)
