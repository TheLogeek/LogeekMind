import streamlit as st

def premium_gate(feature_name):

    if 'user' in st.session_state:
        return True

    st.warning(f"🔒 You must be logged in to **{feature_name}**.")
    st.info("""Creating an account is free and saves your progress!
            Simply click on the >> button in the top left corner (if the sidebar is not already open) and click the login 
            section""")
    return False


def check_guest_limit(feature_name, limit=1):

    if 'user' in st.session_state:
        return True

    usage_key = f"usage_count_{feature_name}"

    if usage_key not in st.session_state:
        st.session_state[usage_key] = 0

    if st.session_state[usage_key] >= limit:
        st.warning(f"🔒 You have reached the free limit for **{feature_name}** as a guest.")
        st.info("""Sign up for a free account to use this feature without limits!
                Simply click on the >> button in the top left corner (if the sidebar is not yet open) and click the login 
                section""")

        return False  # Block access

    st.session_state[usage_key] += 1
    return True