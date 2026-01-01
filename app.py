import streamlit as st
import yaml
import random
import time
import plotly.graph_objects as go
import json
import os
from datetime import datetime, timedelta
from streamlit_autorefresh import st_autorefresh
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.colored_header import colored_header
from streamlit_lottie import st_lottie
import requests

# Configuración de la página
st.set_page_config(
    page_title="🎃 Juegos de Halloween",
    page_icon="🎃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Auto-refresh para el timer (cada 1 segundo, sin recargar toda la página)
#count = st_autorefresh(interval=1000, key="timer_refresh")

# Función para cargar animaciones de Lottie
def load_lottieurl(url):
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

# CSS personalizado para tema Halloween
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #1a0033 0%, #330066 50%, #660033 100%);
        color: #ff6600;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a0033 0%, #330066 50%, #660033 100%);
    }
    
    .halloween-title {
        font-size: 3rem;
        color: #ff6600;
        text-align: center;
        text-shadow: 3px 3px 6px #000000;
        margin-bottom: 2rem;
        font-family: 'Creepster', cursive;
    }
    
    .game-mode {
        background: rgba(255, 102, 0, 0.1);
        border: 2px solid #ff6600;
        border-radius: 15px;
        padding: 20px;
        margin: 10px;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
    }
    
    .word-display {
        background: rgba(0, 0, 0, 0.7);
        border: 3px solid #ff6600;
        border-radius: 20px;
        padding: 30px;
        text-align: center;
        font-size: 2.5rem;
        color: #ff6600;
        text-shadow: 2px 2px 4px #000000;
        margin: 20px 0;
        box-shadow: 0 0 20px rgba(255, 102, 0, 0.5);
    }
    
    .timer-display {
        background: rgba(255, 0, 0, 0.2);
        border: 2px solid #ff0000;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        font-size: 2rem;
        color: #ff0000;
        font-weight: bold;
    }
    
    .scoreboard {
        background: rgba(102, 0, 204, 0.2);
        border: 2px solid #6600cc;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #ff6600, #ff9900);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 15px 30px;
        font-size: 1.2rem;
        font-weight: bold;
        text-shadow: 1px 1px 2px #000000;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(45deg, #ff9900, #ffcc00);
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
    }
    
    .sidebar .stSelectbox > div > div {
        background-color: rgba(255, 102, 0, 0.1);
        border: 1px solid #ff6600;
    }
</style>
""", unsafe_allow_html=True)

# Cargar palabras desde el archivo YAML
@st.cache_data
def load_words():
    try:
        with open('halloween_words.yml', 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo halloween_words.yml")
        return {"pictionary": [], "mimic": []}

# Función para crear la ruleta
def create_wheel():
    fig = go.Figure(data=go.Pie(
        labels=['🎨 Dibujar', '🎭 Mímica'],
        values=[1, 1],
        hole=0.3,
        marker=dict(colors=['#ff6600', '#6600cc']),
        textinfo='label+percent',
        textfont=dict(size=16, color='white'),
        hoverinfo='label'
    ))
    
    fig.update_layout(
        title=dict(
            text="🎡 Ruleta de Juegos",
            x=0.5,
            font=dict(size=20, color='#ff6600')
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400
    )
    
    return fig

# Función para guardar puntuaciones
def save_scores(scores):
    with open('scores.json', 'w', encoding='utf-8') as f:
        json.dump(scores, f, ensure_ascii=False, indent=2)

# Función para cargar puntuaciones
def load_scores():
    if os.path.exists('scores.json'):
        try:
            with open('scores.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

# Inicializar estado de la sesión
if 'game_mode' not in st.session_state:
    st.session_state.game_mode = None
if 'current_word' not in st.session_state:
    st.session_state.current_word = None
if 'timer_start' not in st.session_state:
    st.session_state.timer_start = None
if 'timer_duration' not in st.session_state:
    st.session_state.timer_duration = 60
if 'scores' not in st.session_state:
    st.session_state.scores = load_scores()
if 'teams' not in st.session_state:
    st.session_state.teams = []

# Título principal
    st.markdown('<h1 class="halloween-title">🎃 JUEGOS DE HALLOWEEN 🎃</h1>', unsafe_allow_html=True)
    
    # Cargar animaciones de Halloween
    lottie_pumpkin = load_lottieurl("https://lottie.host/1f52b4d6-7ca4-4c32-8d6a-3f2bc0abf1e1/CKjxgP9RHa.json")
    lottie_ghost = load_lottieurl("https://lottie.host/2e26a101-4393-4c3e-b1a3-b8d6d3e6e6d3/n3p9aQGGQI.json")
    
    # Mostrar animaciones en columnas
    anim_col1, title_col, anim_col2 = st.columns([1, 3, 1])
    with anim_col1:
        if lottie_pumpkin:
            st_lottie(lottie_pumpkin, height=150, key="pumpkin")
        else:
            st.markdown("🎃", unsafe_allow_html=True)
    with title_col:
        colored_header(
            label="¡Diviértete con Pictionary y Mímica!",
            description="Selecciona un modo de juego y genera palabras para jugar",
            color_name="orange-70",
        )
    with anim_col2:
        if lottie_ghost:
            st_lottie(lottie_ghost, height=150, key="ghost")
        else:
            st.markdown("👻", unsafe_allow_html=True)

# Cargar palabras
words_data = load_words()

# Sidebar para configuración
with st.sidebar:
    st.markdown("## ⚙️ Configuración")
    
    # Configuración de equipos
    st.markdown("### 👥 Equipos")
    team_name = st.text_input("Nombre del equipo:")
    if st.button("➕ Agregar Equipo") and team_name:
        if team_name not in st.session_state.teams:
            st.session_state.teams.append(team_name)
            if team_name not in st.session_state.scores:
                st.session_state.scores[team_name] = 0
            save_scores(st.session_state.scores)
            st.success(f"Equipo '{team_name}' agregado!")
        else:
            st.warning("Este equipo ya existe!")
    
    # Mostrar equipos actuales
    if st.session_state.teams:
        st.markdown("**Equipos actuales:**")
        for team in st.session_state.teams:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"• {team}")
            with col2:
                if st.button("🗑️", key=f"delete_{team}"):
                    st.session_state.teams.remove(team)
                    if team in st.session_state.scores:
                        del st.session_state.scores[team]
                    save_scores(st.session_state.scores)
                    st.rerun()
    
    # Configuración del timer
    st.markdown("### ⏰ Timer")
    st.session_state.timer_duration = st.slider("Duración (segundos):", 30, 300, st.session_state.timer_duration, 15)
    
    # Botón para limpiar puntuaciones
    if st.button("🔄 Reiniciar Puntuaciones"):
        st.session_state.scores = {team: 0 for team in st.session_state.teams}
        save_scores(st.session_state.scores)
        st.success("Puntuaciones reiniciadas!")

# Contenido principal
with stylable_container(
    key="main_container",
    css_styles="""
        {
            background: linear-gradient(135deg, rgba(26, 0, 51, 0.9) 0%, rgba(51, 0, 102, 0.9) 50%, rgba(102, 0, 51, 0.9) 100%);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(255, 102, 0, 0.5);
            margin-bottom: 20px;
        }
    """
):
    col1, col2 = st.columns([2, 1])

with col1:
    # Selección de modo de juego
    st.markdown("## 🎮 Selección de Juego")
    
    game_selection_method = st.radio(
        "¿Cómo quieres elegir el juego?",
        ["🎡 Ruleta de la Fortuna", "🎯 Selección Manual"],
        horizontal=True
    )
    
    if game_selection_method == "🎡 Ruleta de la Fortuna":
        col_wheel1, col_wheel2 = st.columns([3, 1])
        
        with col_wheel1:
            st.plotly_chart(create_wheel(), use_container_width=True)
        
        with col_wheel2:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if st.button("🎲 ¡Girar Ruleta!", key="spin_wheel"):
                choice = random.choice(['pictionary', 'mimic'])
                st.session_state.game_mode = choice
                # Reiniciar el timer cuando se gira la ruleta
                st.session_state.timer_start = None
                if choice == 'pictionary':
                    st.success("🎨 ¡Toca DIBUJAR!")
                else:
                    st.success("🎭 ¡Toca MÍMICA!")
    
    else:
        game_choice = st.selectbox(
            "Selecciona el modo de juego:",
            ["🎨 Dibujar (Pictionary)", "🎭 Mímica (Charades)"]
        )
        
        if game_choice == "🎨 Dibujar (Pictionary)":
            st.session_state.game_mode = 'pictionary'
            # Reiniciar el timer cuando se selecciona manualmente el modo
            st.session_state.timer_start = None
        elif game_choice == "🎭 Mímica (Charades)":
            st.session_state.game_mode = 'mimic'
            # Reiniciar el timer cuando se selecciona manualmente el modo
            st.session_state.timer_start = None
    
    # Mostrar modo de juego actual
    if st.session_state.game_mode:
        mode_text = "🎨 DIBUJAR" if st.session_state.game_mode == 'pictionary' else "🎭 MÍMICA"
        st.markdown(f'<div class="game-mode"><h2>Modo actual: {mode_text}</h2></div>', unsafe_allow_html=True)
        
        # Botones de acción
        col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
        
        with col_btn1:
            if st.button("🎲 Generar Palabra", key="generate_word"):
                words_list = words_data.get(st.session_state.game_mode, [])
                if words_list:
                    st.session_state.current_word = random.choice(words_list)
                    # Reiniciar el timer cuando se genera una nueva palabra
                    st.session_state.timer_start = None
                else:
                    st.error("No hay palabras disponibles para este modo")
        
        with col_btn2:
            if st.button("🔁 Cambiar Modo de Juego", key="change_mode"):
                st.session_state.game_mode = None
                st.session_state.current_word = None
                # Reiniciar el timer cuando se cambia el modo de juego
                st.session_state.timer_start = None
                st.rerun()
        
        with col_btn3:
            if st.button("⏰ Iniciar Timer", key="start_timer"):
                st.session_state.timer_start = time.time()
        with col_btn4:
            if st.button("⏹ Detener Timer", key="stop_timer", disabled=not bool(st.session_state.timer_start)):
                st.session_state.timer_start = None
                st.rerun()
        
        # Mostrar palabra actual
        if st.session_state.current_word:
            st.markdown(f'<div class="word-display">🎯 {st.session_state.current_word.upper()}</div>', unsafe_allow_html=True)
        
        # Timer con autorefresh incremental (permite detenerlo con el botón)
        if st.session_state.timer_start:
            elapsed = time.time() - st.session_state.timer_start
            remaining = max(0, st.session_state.timer_duration - elapsed)
            
            while remaining > 0:
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)

                # Usar stylable_container para mejorar la apariencia del timer
                with stylable_container(
                    key="timer_container",
                    css_styles="""
                        {
                            background-color: rgba(0, 0, 0, 0.7);
                            border-radius: 10px;
                            padding: 10px;
                            border: 2px solid #ff6600;
                            box-shadow: 0 0 10px #ff6600;
                        }
                    """
                ):
                    st.markdown(f'<div class="timer-display">⏰ {minutes:02d}:{seconds:02d}</div>', unsafe_allow_html=True)
                # Sleep for 1 sec, then refresh only this container
                time.sleep(1)
                st.rerun()
            else:
                with stylable_container(
                    key="timer_end_container",
                    css_styles="""
                        {
                            background-color: rgba(255, 0, 0, 0.3);
                            border-radius: 10px;
                            padding: 10px;
                            border: 2px solid #ff0000;
                            box-shadow: 0 0 10px #ff0000;
                        }
                    """
                ):
                    st.markdown('<div class="timer-display">⏰ ¡TIEMPO AGOTADO!</div>', unsafe_allow_html=True)

                # Marcar el timer como finalizado para detener autorefresh
                st.session_state.timer_start = None

                # Mostrar animación cuando se acaba el tiempo
                lottie_timeout = load_lottieurl("https://lottie.host/58ebb8ac-8e8c-49d7-9bd1-5c6565749d5d/Xey6u0sHRb.json")
                if lottie_timeout:
                    st_lottie(lottie_timeout, height=100, key="timeout")
                else:
                    st.markdown("🎃 ¡TIEMPO AGOTADO! 🎃", unsafe_allow_html=True)
                st.balloons()

                if st.button("🔄 Reiniciar Timer"):
                    st.session_state.timer_start = None

with col2:
    # Marcador
    if st.session_state.teams:
        st.markdown("## 🏆 Marcador")
        
        # Mostrar puntuaciones
        for team in st.session_state.teams:
            score = st.session_state.scores.get(team, 0)
            st.markdown(f'<div class="scoreboard"><strong>{team}:</strong> {score} puntos</div>', unsafe_allow_html=True)
            
            # Botones para sumar/restar puntos
            col_minus, col_plus = st.columns(2)
            with col_minus:
                if st.button("➖", key=f"minus_{team}"):
                    st.session_state.scores[team] = max(0, st.session_state.scores[team] - 1)
                    save_scores(st.session_state.scores)
                    st.rerun()
            with col_plus:
                if st.button("➕", key=f"plus_{team}"):
                    st.session_state.scores[team] = st.session_state.scores[team] + 1
                    save_scores(st.session_state.scores)
                    st.rerun()
        
        # Mostrar ganador
        if st.session_state.scores:
            max_score = max(st.session_state.scores.values())
            winners = [team for team, score in st.session_state.scores.items() if score == max_score]
            
            if len(winners) == 1 and max_score > 0:
                st.markdown(f"### 👑 Líder: {winners[0]}")
            elif len(winners) > 1 and max_score > 0:
                st.markdown(f"### 🤝 Empate: {', '.join(winners)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #ff6600; font-size: 1.2rem;'>
        🎃 ¡Feliz Halloween! 🎃<br>
        <small>Creado con ❤️ para diversión espeluznante</small>
    </div>
    """, 
    unsafe_allow_html=True
)