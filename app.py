from flask import Flask, render_template_string, request, redirect, session
import json, os, requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = "segredo_fake_123"

ADMIN_PASSWORD = "admin123"
LOGINS_FILE = "logins.json"

# ================= IP REAL =================
def get_ip_real():
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    elif request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP")
    return request.remote_addr

# ================= LOCALIZAÇÃO =================
def get_localizacao(ip):
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = r.json()
        if data.get("status") == "success":
            return {
                "pais": data.get("country", "Desconhecido"),
                "regiao": data.get("regionName", "Desconhecida"),
                "cidade": data.get("city", "Desconhecida"),
                "isp": data.get("isp", "Desconhecido"),
                "vpn": data.get("proxy", False) or data.get("hosting", False)
            }
    except:
        pass
    return {
        "pais": "Desconhecido",
        "regiao": "Desconhecida",
        "cidade": "Desconhecida",
        "isp": "Desconhecido",
        "vpn": False
    }

# ================= SALVAR LOGIN =================
def salvar_login(usuario):
    ip = get_ip_real()
    loc = get_localizacao(ip)

    if os.path.exists(LOGINS_FILE):
        with open(LOGINS_FILE, "r", encoding="utf-8") as f:
            try:
                dados = json.load(f)
            except:
                dados = []
    else:
        dados = []

    dados.append({
        "usuario": usuario,
        "ip": ip,
        "pais": loc["pais"],
        "regiao": loc["regiao"],
        "cidade": loc["cidade"],
        "isp": loc["isp"],
        "vpn_proxy": loc["vpn"],
        "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    })

    with open(LOGINS_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

# ================= LOGIN PAGE =================
login_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Login</title>
<style>
body{background:#000;font-family:Arial}
.box{background:#fff;width:300px;margin:120px auto;padding:30px;border-radius:10px;text-align:center}
input,button{width:100%;padding:10px;margin:10px 0}
button{background:#0800FA;color:#fff;border:none;border-radius:5px}
.erro{color:red}
</style>
</head>
<body>
<div class="box">
<h2>CLT SUPREMO 🐍</h2>
{% if erro %}<p class="erro">{{ erro }}</p>{% endif %}
<form method="post">
<input name="usuario" placeholder="Usuário" required>
<input name="senha" type="password" placeholder="Senha" required>
<button>Entrar</button>
</form>
<p style="font-size:12px">Dica: clt6969</p>
</div>
</body>
</html>
"""

# ================= SITE =================
site_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>CLT SUPREMO V2</title>
<style>
body{margin:0;font-family:Arial;background:#111;color:#fff}
header{background:#000000;padding:20px;text-align:center}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:20px;padding:30px}
.card{background:#fff;color:#000000;padding:20px;border-radius:10px;transition:.3s}
.card:hover{transform:translateY(-6px)}
button{padding:8px 15px;background:#E00900;color:#fff;border:none;border-radius:5px}
</style>
</head>
<body>
<header>
<h1>CLT SUPREMO</h1>
<p>Bem-vindo {{ usuario }}</p>
<a href="/logout"><button>SAIR</button></a>
</header>

<div class="grid">
<div class="card"><h3>👤 Perfil</h3><p>Status: Ativo</p></div>
<div class="card"><h3>📄 CLT</h3><p>Contrato válido</p></div>
<div class="card"><h3>🔒 Segurança</h3><p>Segurança de alta qualidade validada</p></div>
<div class="card"><h3>🌐 Previsão </h3><p>CLT validado até 2033</p></div>
<div class="card"><h3>📊 Sistema</h3><p>Online</p></div>
<div class="card"><h3>🔔 Avisos</h3><p>15 pendência a Olhar 👀</p></div>
<div class="card"><h3>⚙️ Conta</h3><p>Verificada e Aprovada✔️</p></div>
<div class="card"><h3>💰 Salario</h3><p>Salario minimo Aprovado✔️</p></div>
<div class="card"><h3>🎁 bonus</h3><p>Desimo terceiro liberado para Retirada</p></div>
</div>
</body>
</html>
"""

# ================= ADMIN =================
admin_html = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Admin</title>
<style>
body{font-family:Arial;background:#111;color:#fff}
table{width:95%;margin:40px auto;border-collapse:collapse}
th,td{border:1px solid #555;padding:10px;text-align:center}
th{background:#0800FA}
.vpn{color:#ff4d4d;font-weight:bold}
.ok{color:#4dff88}
</style>
</head>
<body>

<h1 style="text-align:center">logs para ADMIN 🔐</h1>

<table>
<tr>
<th>Usuário</th>
<th>IP</th>
<th>Localização</th>
<th>ISP</th>
<th>VPN</th>
<th>Data</th>
</tr>

{% for l in logins %}
<tr>
<td>{{ l.usuario }}</td>
<td>{{ l.ip }}</td>
<td>{{ l.cidade }} - {{ l.regiao }} ({{ l.pais }})</td>
<td>{{ l.isp }}</td>
<td class="{{ 'vpn' if l.vpn_proxy else 'ok' }}">
{{ 'SIM ⚠️' if l.vpn_proxy else 'NÃO ❌' }}
</td>
<td>{{ l.data }}</td>
</tr>
{% endfor %}
</table>
</body>
</html>
"""

# ================= ROTAS =================
@app.route("/", methods=["GET","POST"])
def login():
    erro = None
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]

        if senha == "zoreia":
            session["usuario"] = usuario
            salvar_login(usuario)
            return redirect("/site")
        elif senha == "clt6969":
            erro = "Achou mesmo que era a senha?kkkkkkk 😏"
        else:
            erro = "Senha incorreta ❌"

    return render_template_string(login_html, erro=erro)

@app.route("/site")
def site():
    if "usuario" not in session:
        return redirect("/")
    return render_template_string(site_html, usuario=session["usuario"])

@app.route("/admin")
def admin():
    if request.args.get("senha") != ADMIN_PASSWORD:
        return "ACESSO NEGADO ❌"

    if os.path.exists(LOGINS_FILE):
        with open(LOGINS_FILE, "r", encoding="utf-8") as f:
            logins = json.load(f)
    else:
        logins = []

    return render_template_string(admin_html, logins=logins)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
