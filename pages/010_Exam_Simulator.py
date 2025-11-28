import streamlit as st

st.set_page_config(page_title="Exam Simulator", layout="wide")
st.title("🔥 Exam Simulator")

st.markdown("""
<style>
    .coming-soon-card {
        padding: 40px;
        margin-top: 50px;
        background-color: #f0f8ff; /* Light blue background */
        border: 2px solid #3b82f6; /* Blue border */
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .coming-soon-card h1 {
        color: #1e40af; /* Darker blue text */
        font-size: 2.5rem;
        margin-bottom: 10px;
    }
    .coming-soon-card p {
        color: #333;
        font-size: 1.1rem;
    }
</style>
<div class="coming-soon-card">
    <h1>Coming Soon in LogeekMind v1.4.0!</h1>
    <p>We are actively developing the Exam Simulator, the ultimate tool for serious exam preparation.</p>
    <br>
    <p>This feature will allow you to:</p>
    <ul>
        <li>Set a Strict Timer to simulate real exam pressure.</li>
        <li>Generate University-Standard Questions based on your course code.</li>
        <li>Receive an immediate A, B, C, D, E, or F Grade upon submission.</li>
        <li>Auto-submit and grade your work when the time runs out.</li>
    </ul>
    <p class="text-gray-600 mt-5">Check back soon! We appreciate your patience.</p>
</div>
""", unsafe_allow_html=True)

#st.image("https://placehold.co/800x200/5C7CFA/FFFFFF?text=Final+Exam+Simulator", caption="Your high-stakes exam prep "
                                                                                         #"is loading...",
         #use_container_width=True)

st.divider()

st.info("In the meantime, perfect your knowledge with the **Smart Quiz Generator**!")