from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3 as sql
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "administrator@#2024??"



# Função para obter a conexão com o banco de dados
def get_db():
    conn = sql.connect("form_db.db")
    conn.row_factory = sql.Row  # Para que os resultados das consultas sejam acessíveis como dicionários
    return conn

# Decorador para proteger rotas que exigem login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa estar logado para acessar esta página.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Função para gerar token de redefinição de senha
def generate_token(email):
    serializer = URLSafeTimedSerializer(app.secret_key)
    return serializer.dumps(email, salt=app.secret_key)

# Função para enviar email de redefinição de senha
def send_reset_email(email):
    token = generate_token(email)
    reset_url = url_for('reset_password', token=token, _external=True)
    msg = Message('Redefinir Senha', sender='seu_email@gmail.com', recipients=[email])
    msg.body = f'Clique no link para redefinir sua senha: {reset_url}'
    mail.send(msg)

# Rota principal que exibe o formulário de login
@app.route('/')
def home():
    return redirect(url_for('login'))
##############################################################################
# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        db = get_db()
        cur = db.execute('SELECT * FROM usuarios WHERE EMAIL = ?', (email,))
        usuario = cur.fetchone()
        db.close()
        
        if usuario and check_password_hash(usuario['SENHA'], senha):  # Verifica a senha hash
            session['user_id'] = usuario['ID']
            session['username'] = usuario['NOME']
            flash(f'Bem-vindo, {usuario["NOME"]}!', 'success')
            return redirect(url_for('menu'))  # Redireciona para a página do menu após login bem-sucedido
        
        flash('Email ou Senha Incorretos', 'warning')  # Mensagem de erro se as credenciais estiverem incorretas
    
    return render_template('login/login.html')  # Exibe o formulário de login

# Função para verificar se o email já está registrado
def email_exists(email, user_id=None):
    db = get_db()
    if user_id:
        cur = db.execute('SELECT * FROM usuarios WHERE EMAIL = ? AND ID != ?', (email, user_id))
    else:
        cur = db.execute('SELECT * FROM usuarios WHERE EMAIL = ?', (email,))
    usuario = cur.fetchone()
    db.close()
    return usuario is not None

# Rota para adicionar um novo usuário
@app.route("/add_user", methods=['POST', 'GET'])
@login_required
def add_user():
    if request.method == 'POST':
        nome = request.form["nome"]
        idade = request.form["idade"]
        rua = request.form["rua"]
        cidade = request.form["cidade"]
        numero = request.form["numero"]
        estado = request.form["estado"]
        email = request.form["email"]

        if email_exists(email):
            flash('Email já registrado', 'warning')
        else:
            con = get_db()
            cur = con.cursor()
            cur.execute("INSERT INTO usuarios(NOME, IDADE, RUA, CIDADE, NUMERO, ESTADO, EMAIL) VALUES(?, ?, ?, ?, ?, ?, ?)", 
                        (nome, idade, rua, cidade, numero, estado, email))
            con.commit()
            con.close()
            flash("DADOS CADASTRADOS COM SUCESSO!", "warning")
            return redirect(url_for("menu"))  # Redireciona para o menu após cadastro bem-sucedido
    return render_template("add_user.html")  # Exibe o formulário para adicionar usuário

# Rota para cadastro de usuário com login
@app.route("/cadastrar", methods=['POST', 'GET'])
def cadastro_usuario():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])  # Gera hash da senha para armazenamento seguro
        idade = request.form['idade']
        rua = request.form['rua']
        cidade = request.form['cidade']
        numero = request.form['numero']
        estado = request.form['estado']
        
        if email_exists(email):
            flash('Email já registrado', 'warning')  # Mensagem de erro se o email já estiver registrado
        else:
            db = get_db()
            try:
                db.execute("INSERT INTO usuarios(NOME, EMAIL, SENHA, IDADE, RUA, CIDADE, NUMERO, ESTADO) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", 
                        (nome, email, senha, idade, rua, cidade, numero, estado))
                db.commit()
                return redirect(url_for('login'))  # Redireciona para a página de login após cadastro
            finally:
                db.close()
    return render_template('cadastrar/cadastro_usuario.html')  # Exibe o formulário de cadastro

# Rota para editar um usuário existente
@app.route("/edit_user/<string:id>", methods=['POST', 'GET'])
@login_required
def edit_user(id):
    if request.method == "POST":
        nome = request.form["nome"]
        idade = request.form["idade"]
        rua = request.form["rua"]
        cidade = request.form["cidade"]
        numero = request.form["numero"]
        estado = request.form["estado"]
        email = request.form["email"]

        if email_exists(email, id):
            flash('Email já registrado por outro usuário', 'warning')
        else:
            con = get_db()
            cur = con.cursor()
            cur.execute("UPDATE usuarios SET NOME=?, IDADE=?, RUA=?, CIDADE=?, NUMERO=?, ESTADO=?, EMAIL=? WHERE ID=?", 
                        (nome, idade, rua, cidade, numero, estado, email, id))
            con.commit()
            con.close()
            flash("Dados Atualizados com sucesso!", "success")
            return redirect(url_for("menu"))  # Redireciona para o menu após atualização bem-sucedida
    else:
        con = get_db()
        cur = con.cursor()
        cur.execute("SELECT * FROM usuarios WHERE ID = ?", (id,))
        data = cur.fetchone()
        con.close()
        return render_template("edit_user.html", datas=data)  # Exibe o formulário de edição com dados atuais

# Rota para deletar um usuário
@app.route("/delete_user/<string:id>", methods=['GET'])
@login_required
def delete_user(id):
    con = get_db()
    cur = con.cursor()
    cur.execute("DELETE FROM usuarios WHERE ID = ?", (id,))
    con.commit()
    con.close()
    flash("Dados Deletados com sucesso!", "warning")
    return redirect(url_for("menu"))  # Redireciona para o menu após exclusão

# Rota para o menu
@app.route('/menu')
@login_required
def menu():
    return render_template('menu/menu.html')  # Renderiza a página do menu

# Rota para solicitar redefinição de senha
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        db = get_db()
        cur = db.execute('SELECT * FROM usuarios WHERE EMAIL = ?', (email,))
        usuario = cur.fetchone()
        db.close()

        if usuario:
            send_reset_email(email)
            flash('Um email foi enviado com instruções para redefinir sua senha.', 'success')
        else:
            flash('Email não encontrado.', 'warning')

    return render_template('forgot_password.html')

# Rota para redefinir a senha
@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        serializer = URLSafeTimedSerializer(app.secret_key)
        email = serializer.loads(token, salt=app.secret_key, max_age=3600)  # O token é válido por 1 hora
    except:
        flash('O link para redefinição de senha é inválido ou expirou.', 'warning')
        return redirect(url_for('forgot_password'))

    if request.method == 'POST':
        senha = generate_password_hash(request.form['senha'])
        db = get_db()
        db.execute('UPDATE usuarios SET SENHA = ? WHERE EMAIL = ?', (senha, email))
        db.commit()
        db.close()
        flash('Sua senha foi redefinida com sucesso.', 'success')
        return redirect(url_for('login'))

    return render_template('reset_password.html', token=token)

# Rota para logout
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Você foi desconectado.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)  # Inicia o servidor Flask em modo debug
