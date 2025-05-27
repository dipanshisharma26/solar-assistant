import streamlit as st
import requests
import json

def analyze_text_with_openrouter(prompt, api_key):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    json_payload = {
        "model": "openai/gpt-4o-mini",  # or whichever text model you want to use
        "messages": [
            {"role": "system", "content": "You are an expert in solar rooftop design and installation."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 500
    }
    
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=json_payload
    )
    
    try:
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error from OpenRouter: {e} | Raw: {response.text}"

def calculate_solar_installation(area_sqm):
    try:
        area = float(area_sqm)
    except:
        return {"error": "Invalid area input."}

    panel_area = 1.6  # m² per panel
    panel_watt = 400  # W
    cost_per_watt = 45  # ₹
    savings_per_kwh = 8  # ₹
    sunlight_hours = 1600  # hrs/year (average)

    num_panels = int(area // panel_area)
    total_capacity_kw = (num_panels * panel_watt) / 1000  # in kW
    estimated_cost = total_capacity_kw * 1000 * cost_per_watt
    annual_generation_kwh = total_capacity_kw * sunlight_hours
    annual_savings = annual_generation_kwh * savings_per_kwh
    payback_years = round(estimated_cost / annual_savings, 1)

    return {
        "panels": num_panels,
        "capacity_kw": round(total_capacity_kw, 2),
        "estimated_cost_inr": round(estimated_cost),
        "annual_generation_kwh": round(annual_generation_kwh),
        "annual_savings_inr": round(annual_savings),
        "payback_period_years": payback_years
    }

# Streamlit UI
st.set_page_config(page_title="Solar Rooftop Analysis Tool")
st.title("🌍 AI Solar Rooftop Analysis (Manual Input)")

api_key = st.text_input("Enter your OpenRouter API Key", type="password")

uploaded_file = st.file_uploader("Upload rooftop image (optional, for reference)", type=["jpg", "jpeg", "png"])
if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Rooftop Image", use_column_width=True)

st.write("### Enter rooftop details manually:")
area_sqm = st.number_input("Usable rooftop area (in square meters)", min_value=0.0, step=0.1)
orientation = st.text_input("Orientation (e.g., South-facing)")
obstructions = st.text_input("Notable obstructions (e.g., water tanks, AC units, trees)")
shading = st.text_input("Estimated shading percentage (e.g., 10%)")

if st.button("Analyze and Generate Report") and api_key:
    if area_sqm <= 0:
        st.error("Please enter a valid rooftop area greater than 0.")
    else:
        prompt = f"""
        Analyze the following rooftop details for solar installation feasibility and provide recommendations:

        Usable Area: {area_sqm} sqm
        Orientation: {orientation}
        Obstructions: {obstructions}
        Shading: {shading}

        Provide a summary report including expected solar panel capacity, estimated cost, potential annual energy generation, savings, and payback period.
        """
        with st.spinner("Generating solar rooftop analysis..."):
            analysis_text = analyze_text_with_openrouter(prompt, api_key)
        
        st.subheader("📝 AI-generated Solar Rooftop Analysis Report")
        st.write(analysis_text)

        roi_data = calculate_solar_installation(area_sqm)
        if "error" not in roi_data:
            st.markdown("### 📊 Installation Summary (Calculation)")
            st.write(f"🔋 **Estimated Panels:** {roi_data['panels']}")
            st.write(f"⚡ **Total Capacity:** {roi_data['capacity_kw']} kW")
            st.write(f"💸 **Estimated Cost:** ₹{roi_data['estimated_cost_inr']}")
            st.write(f"☀️ **Annual Generation:** {roi_data['annual_generation_kwh']} kWh")
            st.write(f"🪙 **Annual Savings:** ₹{roi_data['annual_savings_inr']}")
            st.write(f"📈 **Payback Period:** {roi_data['payback_period_years']} years")
        else:
            st.error(roi_data["error"])
