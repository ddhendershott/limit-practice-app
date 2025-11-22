# -----------------------------------------------------------------------------
# Limit Practice Application
#
# A Streamlit app designed to generate random limit problems involving square roots
# and rational expressions. It features symbolic math validation, interactive
# visualizations of removable discontinuities, and state management for tracking
# user progress.
#
# Built for the Technical Generalist evaluation.
# -----------------------------------------------------------------------------

import streamlit as st
import random
import pandas as pd
import numpy as np
import altair as alt
import base64
import sympy as sp

# --- 1. Page Configuration ---
st.set_page_config(
    page_title="Limit Practice",
    page_icon="∫",
    layout="centered"
)

# --- 2. Custom CSS Styling ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .st-emotion-cache-1plm3a3 { display: none; } 

    /* Math Formula Display */
    .hero-math .katex {
        font-size: 2.6em !important; 
        font-weight: 600;
        color: var(--text-color) !important;
    }
    
    /* Input Field Styling */
    .stTextInput input { text-align: center; font-weight: 500; }
    div[data-testid="InputInstructions"] { display: none; }

    /* Metrics & Dashboard Styling */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] { opacity: 0.7; justify-content: center; }
    div[data-testid="stMetricValue"] { font-size: 1.5rem; }

    /* Primary Button (Submit) */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #00FFAA !important;
        color: #000000 !important;
        font-weight: 800;
        border: none;
        width: 100%;
        padding: 0.6rem 1rem;
        font-size: 1.1rem;
    }
    div[data-testid="stFormSubmitButton"] > button:hover {
        background-color: #00CC88 !important;
        box-shadow: 0 0 10px rgba(0, 255, 170, 0.4);
    }

    /* Secondary Button (New Problem) */
    div.stButton > button[kind="secondary"] {
        background-color: var(--secondary-background-color) !important;
        color: var(--text-color) !important; 
        border: 2px solid rgba(128, 128, 128, 0.5) !important;
        border-radius: 8px;
        font-weight: 600;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #00FFAA !important;
        color: #00FFAA !important;
    }
    
    .limit-label {
        text-align: center;
        color: var(--text-color);
        font-size: 1.3rem;
        font-weight: 500;
        margin-bottom: 10px;
        opacity: 0.8;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. Core Application Logic ---

def encode_problem(a):
    """Encodes problem integer 'a' to base64."""
    return base64.b64encode(str(a).encode()).decode()

def decode_problem(code):
    """Decodes base64 string to integer 'a'."""
    try:
        return int(base64.b64decode(code.encode()).decode())
    except:
        return None

def generate_problem():
    """Generates coefficients b and c."""
    a = random.randint(2, 12)
    c = a**2 + 2
    b = c - 1
    return {"a": a, "b": b, "c": c}

def load_problem_from_url():
    """Checks URL query parameters for problem ID."""
    params = st.query_params
    if "problem_id" in params:
        a = decode_problem(params["problem_id"])
        if a:
            c = a**2 + 2
            b = c - 1
            return {"a": a, "b": b, "c": c}
    return None

def check_answer(user_input, correct_a):
    """Validates user input using SymPy."""
    try:
        if not user_input.strip():
            return False
        user_expr = sp.sympify(user_input)
        correct_sym = sp.Rational(1, correct_a)
        
        # Check symbolic equality
        if sp.simplify(user_expr - correct_sym) == 0:
            return True
        
        # Fallback to numerical check for floats
        return abs(float(user_expr) - float(correct_sym)) < 1e-4
    except (sp.SympifyError, ValueError, TypeError, AttributeError):
        return False

@st.cache_data
def get_plot_data(c):
    """
    Generates data for the function curve dynamically based on 'c'.
    Includes a 'None' value at x=-1 to force a break in the line chart.
    """
    asymptote = 1 - c
    x_start = asymptote + 0.05
    x_end = 5 
    x_vals = np.linspace(x_start, x_end, 2000)

    # Create the visual gap
    x_vals = x_vals[np.abs(x_vals + 1) > 0.08] 
    y_vals = np.sqrt(1 / (x_vals + c - 1))
    
    df = pd.DataFrame({'x': x_vals, 'f(x)': y_vals})
    gap_point = pd.DataFrame({'x': [-1], 'f(x)': [None]})
    
    df = pd.concat([df, gap_point], ignore_index=True).sort_values('x')
    return df

def create_solution_chart(df, prob):
    """
    Constructs the layered Altair chart. 
    Extracted from main flow for better code organization.
    """
    actual_limit = 1 / prob['a']
    asymptote_loc = 1 - prob['c']
    
    # 1. Dynamic Axis Scaling
    x_min, x_max = df['x'].min(), df['x'].max()
    x_padding = (x_max - x_min) * 0.05
    x_domain = [x_min - x_padding, x_max]
    
    y_max = df['f(x)'].max() * 1.1
    y_domain = [0, y_max]

    shared_x = alt.Scale(domain=x_domain)
    shared_y = alt.Scale(domain=y_domain)

    # Layer 1: The Function Curve
    line = alt.Chart(df).mark_line(color='#00FFAA', strokeWidth=3).encode(
        x=alt.X('x', title='x', scale=shared_x),
        y=alt.Y('f(x)', title='f(x)', scale=shared_y)
    )

    # Layer 2: The Asymptote Line
    asymp_line = alt.Chart(pd.DataFrame({'x': [asymptote_loc]})).mark_rule(
        strokeDash=[5, 5], color='#FF4B4B', opacity=0.8
    ).encode(
        x=alt.X('x', scale=shared_x),
        tooltip=[alt.Tooltip('x', title="Vertical Asymptote")]
    )

    # Layer 3: Reference Axes
    axis_x = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='gray', opacity=0.5).encode(
        y=alt.Y('y', scale=shared_y)
    )
    axis_y = alt.Chart(pd.DataFrame({'x': [0]})).mark_rule(color='gray', opacity=0.5).encode(
        x=alt.X('x', scale=shared_x)
    )

    # Layer 4: The Hole
    hole_data = pd.DataFrame({'x': [-1], 'f(x)': [actual_limit]})
    hole = alt.Chart(hole_data).mark_point(
        shape='circle', size=150, filled=False, 
        stroke='red', strokeWidth=2, opacity=1
    ).encode(
        x=alt.X('x', scale=shared_x),
        y=alt.Y('f(x)', scale=shared_y),
        tooltip=[alt.Tooltip('f(x)', format='.4f', title="Limit at x=-1")]
    )

    # Layer 5: Text Label
    text_data = pd.DataFrame({'x': [-1], 'f(x)': [actual_limit], 'label': [f"Limit ≈ {actual_limit:.3f}"]})
    text = alt.Chart(text_data).mark_text(
        align='left', dx=15, dy=-15, color='white'
    ).encode(
        x=alt.X('x', scale=shared_x),
        y=alt.Y('f(x)', scale=shared_y),
        text='label'
    )

    return (asymp_line + axis_x + axis_y + line + hole + text).properties(
        height=350,
        title="Graph of f(x)"
    )

def reset_problem():
    """Resets session state."""
    st.session_state.problem = generate_problem()
    st.session_state["user_input"] = ""
    st.session_state.problem_solved = False
    st.session_state.failed = False
    st.session_state.attempts = 0
    st.session_state.show_solution = False
    st.query_params.clear()

# --- 4. Session State Initialization ---
if 'problem' not in st.session_state:
    url_prob = load_problem_from_url()
    if url_prob:
        st.session_state.problem = url_prob
        st.toast("🔗 Challenge Problem Loaded!", icon="🔥")
    else:
        st.session_state.problem = generate_problem()

for key, default in [('streak', 0), ('total_correct', 0), ('attempts', 0), 
                     ('problem_solved', False), ('failed', False), ('show_solution', False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- 5. UI Layout ---

st.markdown("<h1 style='text-align: center;'>Limit Practice</h1>", unsafe_allow_html=True)
st.write("") 

# Metrics and Sharing Row
sp_l, c1, c2, c3, sp_r = st.columns([2, 2, 2, 4, 2])
with c1:
    streak_placeholder = st.empty()
with c2:
    solved_placeholder = st.empty()
with c3:
    st.write("") 
    if st.button("🔗 Challenge a Friend", help="Generates a shareable URL"):
        prob = st.session_state.problem
        encoded_id = encode_problem(prob['a'])
        st.query_params["problem_id"] = encoded_id
        st.toast("URL updated! Copy it from your address bar.", icon="📋")

st.divider()

# Problem Display
prob = st.session_state.problem
numerator = "x + 1"
denominator = f"x^2 + {prob['c']}x + {prob['b']}"

st.markdown("<div class='limit-label'>Evaluate the limit:</div>", unsafe_allow_html=True)
st.markdown('<div class="hero-math" style="text-align: center;">', unsafe_allow_html=True)
st.latex(rf"\lim_{{x\to -1}} \sqrt{{\frac{{{numerator}}}{{{denominator}}}}}")
st.markdown('</div>', unsafe_allow_html=True)

st.write("")

# Input Form
spacer_l, main_col, spacer_r = st.columns([1, 2, 1])
with main_col:
    with st.form(key='limit_form'):
        user_answer = st.text_input("Your Answer", key="user_input", placeholder="Enter answer...")
        submit = st.form_submit_button("Submit")

# --- 6. Feedback & Evaluation Logic ---
if submit:
    if not user_answer.strip():
        st.warning("⚠️ Please enter an answer before submitting.")
        st.stop()

    correct_a = prob['a']
    is_correct = check_answer(user_answer, correct_a)

    with main_col:
        if is_correct:
            if st.session_state.failed:
                 st.warning(f"That matches the answer, but you have already used all attempts.")
            else:
                if not st.session_state.problem_solved:
                    st.session_state.streak += 1
                    st.session_state.total_correct += 1
                    st.session_state.problem_solved = True
                    st.session_state.failed = False
                    st.balloons()
                
                st.success(f"Correct! The limit is $\\frac{{1}}{{{correct_a}}}$.")
                st.session_state.show_solution = True

        else:
            if st.session_state.failed:
                 st.error(f"Answer: $\\frac{{1}}{{{correct_a}}}$.")
            elif st.session_state.problem_solved:
                 st.success(f"Correct! The limit is $\\frac{{1}}{{{correct_a}}}$. (You solved this earlier)")
            else:
                st.session_state.streak = 0
                st.session_state.attempts += 1
                attempts_left = 3 - st.session_state.attempts
                
                if attempts_left > 0:
                    st.warning(f"Not quite. {attempts_left} attempts left.")
                    if attempts_left == 2:
                        st.info("💡 **Hint 1 (Strategy):** Direct substitution gives $0/0$. This indicates a removable discontinuity. Try factoring.")
                    elif attempts_left == 1:
                        st.info(f"💡 **Hint 2 (Algebra):** Since the numerator is $(x+1)$, look for an $(x+1)$ factor in $x^2 + {prob['c']}x + {prob['b']}$.")
                else:
                    st.error(f"Answer: $\\frac{{1}}{{{correct_a}}}$.")
                    st.session_state.problem_solved = True
                    st.session_state.failed = True 
                    st.session_state.show_solution = True

# --- 7. Metrics Update ---
streak_placeholder.metric("Streak 🔥", st.session_state.streak)
solved_placeholder.metric("Solved ✅", st.session_state.total_correct)

# --- 8. Solution Breakdown & Visualization ---
if st.session_state.show_solution:
    st.write("")
    should_auto_expand = st.session_state.failed
    
    with st.expander("📘 View Solution Breakdown", expanded=should_auto_expand):
        st.write("1. **Factor the denominator:**")
        st.latex(rf"x^2 + {prob['c']}x + {prob['b']} = (x+1)(x + {prob['c']-1})")
        st.write("2. **Simplify the fraction:**")
        st.latex(rf"\frac{{x+1}}{{(x+1)(x + {prob['c']-1})}} = \frac{{1}}{{x + {prob['c']-1}}}")
        st.write("3. **Evaluate the limit as $x \\to -1$:**")
        st.latex(rf"\lim_{{x\to -1}} \left( \frac{{1}}{{x + {prob['c']-1}}} \right) = \frac{{1}}{{-1 + {prob['c']-1}}} = \frac{{1}}{{{prob['c']-2}}}")
        st.write(f"4. **Apply the Square Root:** (Note: ${prob['c']-2} = {prob['a']}^2$)")
        st.latex(rf"\sqrt{{\frac{{1}}{{{prob['a']}^2}}}} = \frac{{1}}{{{prob['a']}}}")
        
        st.divider()
        st.caption("Visual Proof (Removable Discontinuity at x = -1):")
        
        # --- Altair Visualization (Cleaned via helper function) ---
        df = get_plot_data(prob['c'])
        final_chart = create_solution_chart(df, prob)
        st.altair_chart(final_chart, use_container_width=True)

# --- 9. Footer / Reset ---
st.write("")
st.write("")
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.button("New Problem", on_click=reset_problem, type="secondary", use_container_width=True)