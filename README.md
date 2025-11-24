# Limit Practice Generator

A Streamlit application designed to help students practice evaluating limits involving square roots and rational expressions. Built for the CMU Technical Generalist exercise.

🔗 **[Live Demo](https://limit-practice-app.streamlit.app/)**

![App Screenshot](assets/screenshot.png) 

## 🎯 Project Overview & Learning Design
This application generates randomized limit problems where direct substitution results in the indeterminate form $\frac{0}{0}$. Beyond simple practice, the tool is designed using **learning engineering principles** to scaffold student mastery:

1.  **Visualizing the Removable Discontinuity:**
    * **Dual Coding:** The application pairs symbolic manipulation with a dynamic Altair visualization.
    * **Concept Reinforcement:** Unlike standard plotters that interpolate through the hole, this tool explicitly renders the gap at $x=-1$, visually reinforcing that the limit exists even where the function is undefined.

2.  **Scaffolding & Fading:**
    * Rather than providing the answer immediately upon failure, the app uses a **faded scaffolding** approach.
    * **Tier 1 (Strategy):** Prompts the student to identify the indeterminate form and consider factoring.
    * **Tier 2 (Algebra):** Specific cues to look for the $(x+1)$ common factor.
    * This reduces cognitive load for struggling students while allowing capable students to solve it without help.

3.  **Low-Floor / High-Ceiling Input:**
    * The input validation (via SymPy) reduces **extraneous cognitive load** by accepting answers in various mathematically equivalent forms (decimals, fractions, roots), allowing students to focus on the calculus concepts rather than formatting syntax.

## 🛠️ Technical Highlights
* **Symbolic Math (SymPy):** Used to parse user input flexibly (e.g., accepting `1/3`, `0.3333`, or `sqrt(1)/3`) rather than relying on brittle string matching.
* **Performance Caching:** Implementation of `@st.cache_data` for plot generation to optimize rendering performance.
* **State Management:** Custom session state logic to handle streaks, retries, and edge cases (e.g., preventing score manipulation by switching answers after failure).
* **URL State:** "Challenge a Friend" feature that encodes problem parameters into the URL, allowing specific problems to be shared.

## 🧮 The Math Logic
The generator ensures integer solutions for the limit:
$$\lim_{x\to -1} \sqrt{\frac{x+1}{x^2 + cx + b}} = \frac{1}{a}$$

To guarantee the limit exists and equals $1/a$, the backend generates a random integer $a$ and derives coefficients:
* $c = a^2 + 2$
* $b = c - 1$

This ensures the denominator factors into $(x+1)(x + a^2 + 1)$, allowing the $(x+1)$ terms to cancel.

## ⚙️ Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/ddhendershott/limit-practice-app.git](https://github.com/ddhendershott/limit-practice-app.git)
    cd limit-practice-app
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

## 📦 Requirements
* streamlit
* pandas
* numpy
* altair
* sympy