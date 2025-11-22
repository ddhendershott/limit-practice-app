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

    /* Global Typography */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .st-emotion-cache-1plm3a3 { display: none; } /* Hide default anchor links */

    /* Math Formula Display */
    .hero-math .katex {
        font-size: 2.6em !important; 
        font-weight: 600;
        color: var(--text-color) !important;
    }
    
    /* Input Field Styling */
    .stTextInput input {
        text-align: center;
        font-weight: 500;
    }
    div[data-testid="InputInstructions"] { display: none; }

    /* Metrics & Dashboard Styling */
    div[data-testid="stMetric"] {
        background-color: var(--secondary-background-color);
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        padding: 10px;
        text-align: center;
    }
    div[data-testid="stMetricLabel"] { 
        color: var(--text-color); 
        font-size: 0.8rem; 
        opacity: 0.7;
        justify-content: center; 
    }
    div[data-testid="stMetricValue"] { 
        color: var(--text-color); 
        font-size: 1.5rem; 
    }

    /* Primary Button (Submit) */
    div[data-testid="stFormSubmitButton"] > button {
        background-color: #00FFAA !important;
        color: #000000 !important;
        font-weight: 800;
        border: none;
        width: 100%;
        padding: 0.6rem 1rem;
        font-size: 1.1rem;
        transition: all 0.2s ease;
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
        font-size: 1rem;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: all 0.2s ease;
    }
    div.stButton > button[kind="secondary"]:hover {
        border-color: #00FFAA !important;
        color: #00FFAA !important;
    }
    
    /* Utility Classes */
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
    """Encodes the problem integer 'a' into a base64 string for URL sharing."""
    return base64.b64encode(str(a).encode()).decode()

def decode_problem(code):
    """Decodes the base64 string back into the problem integer 'a'."""
    try:
        return int(base64.b64decode(code.encode()).decode())
    except:
        return None

def generate_problem():
    """
    Generates coefficients b and c such that the limit evaluates to 1/a.
    Constraint: The expression must yield 0/0 at x = -1.
    """
    # Random integer 'a' leads to solution 1/a
    a = random.randint(2, 12)
    
    # Mathematical constraints for 0/0 form and integer simplification
    c = a**2 + 2
    b = c - 1
    
    return {"a": a, "b": b, "c": c}

def load_problem_from_url():
    """Checks URL query parameters for a shared problem ID."""
    params = st.query_params
    if "problem_id" in params:
        a = decode_problem(params["problem_id"])
        if a:
            c = a**2 + 2
            b = c - 1
            return {"a": a, "b": b, "c": c}
    return None

def check_answer(user_input, correct_a):
    """
    Validates user input using SymPy for symbolic equivalence.
    Accepts fractions, decimals, and unsimplified expressions.
    """
    try:
        if not user_input.strip():
            return False
        user_expr = sp.sympify(user_input)
        correct_sym = sp.Rational(1, correct_a)
        
        # Check for symbolic equality first
        if sp.simplify(user_expr - correct_sym) == 0:
            return True
        
        # Fallback to float comparison for edge cases
        return abs(float(user_expr) - float(correct_sym)) < 1e-4
    except (sp.SympifyError, ValueError, TypeError, AttributeError):
        return False

@st.cache_data
def get_plot_data(c):
    """
    Generates data for the function curve centered on the limit.
    Uses a fixed window [-2, 0] to keep the focus on x = -1.
    """
    x_vals = np.linspace(-2, 0, 200)
    
    # Filter out x values extremely close to -1 to prevent vertical asymptote artifacts
    # and to visually prepare the gap for the hollow ring marker.
    x_vals = x_vals[np.abs(x_vals + 1) > 0.05] 
    
    y_vals = np.sqrt(1 / (x_vals + c - 1))
    return pd.DataFrame({'x': x_vals, 'f(x)': y_vals})

def reset_problem():
    """Resets session state variables for a new problem."""
    st.session_state.problem = generate_problem()
    st.session_state["user_input"] = ""
    st.session_state.problem_solved = False
    st.session_state.failed = False
    st.session_state.attempts = 0
    st.session_state.show_solution = False
    # Clear URL params so refresh doesn't reload the old shared problem
    st.query_params.clear()

# --- 4. Session State Initialization ---
if 'problem' not in st.session_state:
    url_prob = load_problem_from_url()
    if url_prob:
        st.session_state.problem = url_prob
        st.toast("🔗 Challenge Problem Loaded!", icon="🔥")
    else:
        st.session_state.problem = generate_problem()

# Initialize tracking metrics
for key, default in [('streak', 0), ('total_correct', 0), ('attempts', 0), 
                     ('problem_solved', False), ('failed', False), ('show_solution', False)]:
    if key not in st.session_state:
        st.session_state[key] = default

# --- 5. UI Layout ---

# Title
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
    if st.button("🔗 Challenge a Friend", help="Generates a shareable URL for this specific problem"):
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
    correct_a = prob['a']
    is_correct = check_answer(user_answer, correct_a)

    with main_col:
        # Scenario 1: User is mathematically correct
        if is_correct:
            # If the user has already failed this problem, acknowledge accuracy but preserve failure state
            if st.session_state.failed:
                 st.warning(f"That matches the answer, but you have already used all attempts.")
            
            # Successful solve
            else:
                if not st.session_state.problem_solved:
                    st.session_state.streak += 1
                    st.session_state.total_correct += 1
                    st.session_state.problem_solved = True
                    st.session_state.failed = False
                    st.balloons()
                
                st.success(f"Correct! The limit is $\\frac{{1}}{{{correct_a}}}$.")
                st.session_state.show_solution = True

        # Scenario 2: User is incorrect
        else:
            # If already failed, simply show correct answer again
            if st.session_state.failed:
                 st.error(f"Answer: $\\frac{{1}}{{{correct_a}}}$.")
            
            # If already solved, gently remind them they finished this one
            elif st.session_state.problem_solved:
                 st.success(f"Correct! The limit is $\\frac{{1}}{{{correct_a}}}$. (You solved this earlier)")
            
            # Genuine attempt - process retry logic
            else:
                st.session_state.streak = 0
                st.session_state.attempts += 1
                attempts_left = 3 - st.session_state.attempts
                
                if attempts_left > 0:
                    st.warning(f"Not quite. {attempts_left} attempts left.")
                    # Provide adaptive hints based on remaining attempts
                    if attempts_left == 2:
                        st.info("💡 **Hint 1 (Strategy):** Direct substitution gives $0/0$. This indicates a removable discontinuity. Try factoring.")
                    elif attempts_left == 1:
                        st.info(f"💡 **Hint 2 (Algebra):** Since the numerator is $(x+1)$, look for an $(x+1)$ factor in $x^2 + {prob['c']}x + {prob['b']}$.")
                else:
                    # Attempts exhausted
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
    # Auto-expand solution if the user failed the problem
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
        
        # --- Altair Visualization ---
        df = get_plot_data(prob['c'])
        y_min, y_max = min(df['f(x)'])-0.01, max(df['f(x)'])+0.01
        actual_limit = 1 / prob['a']

        # Layer 1: The continuous function line
        line = alt.Chart(df).mark_line(color='#00FFAA').encode(
            x=alt.X('x', axis=alt.Axis(format='.2f', title='x')),
            y=alt.Y('f(x)', axis=alt.Axis(format='.4f', title='f(x)'), scale=alt.Scale(domain=[y_min, y_max])),
            tooltip=['x', 'f(x)']
        )

        # Layer 2: The removable discontinuity (Hollow Ring)
        # Represents that the function does not exist at exactly x = -1
        point_data = pd.DataFrame({'x': [-1], 'f(x)': [actual_limit]})
        
        point = alt.Chart(point_data).mark_point(
            shape='circle', 
            size=100, 
            filled=False, 
            stroke='#00FFAA',
            strokeWidth=2,
            opacity=1
        ).encode(
            x='x', 
            y='f(x)',
            tooltip=[alt.Tooltip('f(x)', format='.4f', title="Limit Value (Undefined)")]
        )

        # Combine charts (Interactive zoom disabled for pedagogical focus)
        final_chart = (line + point).properties(height=250)
        st.altair_chart(final_chart, use_container_width=True)

# --- 9. Footer / Reset ---
st.write("")
st.write("")
c1, c2, c3 = st.columns([1, 2, 1])
with c2:
    st.button("New Problem", on_click=reset_problem, type="secondary", use_container_width=True)