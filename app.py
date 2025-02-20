from flask import Flask, render_template, request

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
    "Viktor": {
        "skills": {
            "Q": {"name": "Poder Sifão", "damage": [70, 100, 130, 160, 190], "ratio": {"AP": 0.4}},
            "W": {"name": "Campo Gravitacional", "damage": [0, 0, 0, 0, 0], "ratio": {}},
            "E": {"name": "Raio da Morte", "damage": [85, 120, 155, 190, 225], "ratio": {"AP": 0.6}},
            "R": {"name": "Tempestade do Caos", "damage": [150, 250, 350], "ratio": {"AP": 1.2}}
        }
    },
    "Diana": {
        "skills": {
            "Q": {"name": "Crescente Espectral", "damage": [60, 90, 120, 150, 180], "ratio": {"AP": 0.7}},
            "W": {"name": "Lâminas da Lua", "damage": [18, 30, 42, 54, 66], "ratio": {"AP": 0.15}},
            "E": {"name": "Impulso Lunar", "damage": [40, 60, 80, 100, 120], "ratio": {"AP": 0.4}},
            "R": {"name": "Luar Caótico", "damage": [200, 300, 400], "ratio": {"AP": 0.6}}
        }
    },
    "Volibear": {
        "skills": {
            "Q": {"name": "Estrondar", "damage": [20, 40, 60, 80, 100], "ratio": {"AD": 1.0}},
            "W": {"name": "Fúria Selvagem", "damage": [60, 110, 160, 210, 260], "ratio": {"AD": 1.0}},
            "E": {"name": "Rugido Devastador", "damage": [80, 110, 140, 170, 200], "ratio": {"AP": 0.6}},
            "R": {"name": "Tormenta do Trovão", "damage": [300, 500, 700], "ratio": {"AP": 1.0}}
        }
    }
}

def calcular_dano_real(dano, resistencia):
    return dano * (100 / (100 + resistencia))

@app.route("/")
def home():
    print("Renderizando index.html")  # Debug
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
    
    # Ajuste do nível máximo da ultimate (R vai até nível 3, demais habilidades até nível 5)
    max_level = 3 if skill == "R" else 5
    level = max(1, min(int(level), max_level)) - 1  # Garantir que o nível esteja dentro do intervalo válido
    
    resistencia = float(resistencia)
    
    if champion in champions and skill in champions[champion]["skills"]:
        skill_data = champions[champion]["skills"][skill]
        base_damage = skill_data["damage"][level]
        
        # Cálculo do escalonamento com AP ou AD
        total_damage = base_damage
        for stat, ratio in skill_data["ratio"].items():
            if stat == "AP":
                total_damage += ap * ratio
            elif stat == "AD":
                total_damage += ad * ratio
        
        dano_real = calcular_dano_real(total_damage, resistencia)
        
        print(f"Dano Base: {base_damage}, Dano Total: {total_damage}, Dano Real Após Resistência: {dano_real}")  # Debug
        return render_template(
            "index.html",
            champions=champions,
            result=f"Habilidade: {skill_data['name']} | Dano estimado: {total_damage:.2f}, Dano real após resistência: {dano_real:.2f}",
            selected_champion=champion
        )
    else:
        return render_template("index.html", champions=champions, result="Erro ao calcular dano. Verifique os dados.")

if __name__ == "__main__":
    print("Iniciando servidor Flask...")  # Debug
    app.run(debug=True)
