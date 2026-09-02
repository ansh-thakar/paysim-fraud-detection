import streamlit as st
import requests

# 1. Target the /predict POST endpoint
API_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(
    page_title="PaySim Fraud Detector",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Real-Time Transaction Fraud Detection")
st.caption("Input raw transaction details to evaluate fraud probability via the FastAPI engine.")

st.divider()

# Input layout 
col1, col2 = st.columns(2)

with col1:
    st.subheader("Transaction Metadata")
    step = st.number_input("Elapsed Hour (Step)", min_value=1, value=1, help="Simulation hour (1-744)")
    type_val = st.selectbox("Transaction Type", ["TRANSFER", "CASH_OUT"])
    amount = st.number_input("Amount ($)", min_value=0.01, value=181.0, step=100.0)

with col2:
    st.subheader("Account Balance")
    oldbalanceOrg = st.number_input("Sender Old Balance (oldbalanceOrg)", min_value=0.0, value=181.00, step=100.00)
    newbalanceOrig = st.number_input("Sender New Balance (newbalanceOrig)", min_value=0.0, value=0.0, step=100.00)
    oldbalanceDest = st.number_input("Recipient Old Balance (oldbalanceDest)", min_value=0.0, value=0.0, step=100.00)
    newbalanceDest = st.number_input("Recipient New Balance (newbalanceDest)", min_value=0.0, value=0.0, step=100.00)

st.divider()

if st.button("Evaluate Transaction Risk!!", type='primary', use_container_width=True):
    # Feature Engineering matching training logic
    errorBalanceOrig = float(newbalanceOrig + amount - oldbalanceOrg)
    errorBalanceDest = float(oldbalanceDest + amount - newbalanceDest)
    is_orig_zero = int(1 if newbalanceOrig == 0 else 0)
    ratio_orig_amount = float(amount / (oldbalanceOrg + 0.001))
    ratio_Dest_amount = float(amount / (newbalanceDest + 0.001))
    hour_of_day = int(step % 24)

    # Data payload sent to API
    payload = {
        "type": type_val,
        "amount": float(amount),
        "oldbalanceOrg": float(oldbalanceOrg),
        "newbalanceOrig": float(newbalanceOrig),
        "oldbalanceDest": float(oldbalanceDest),
        "newbalanceDest": float(newbalanceDest),
        "errorBalanceOrig": errorBalanceOrig,
        "errorBalanceDest": errorBalanceDest,
        "is_orig_zero": is_orig_zero,
        "ratio_orig_amount": ratio_orig_amount,
        "ratio_Dest_amount": ratio_Dest_amount,
        "hour_of_day": hour_of_day
    }

    # 2. Placed inside button block so execution only triggers on click
    with st.spinner("Calculating Risk Profile...."):
        try:
            response = requests.post(API_URL, json=payload, timeout=5)

            # 3. Compare status_code as an integer
            if response.status_code == 200:
                result = response.json()

                st.subheader("Inference Result!")
                res_col1, res_col2, res_col3 = st.columns(3)

                with res_col1:
                    if result["is_fraud"]:
                        st.error("🚨 **FRAUD DETECTED**")
                    else:
                        st.success("✅ **TRANSACTION CLEAN**")

                with res_col2:
                    st.metric(label="Risk Score", value=f"{result['risk_score']:.4f}")

                with res_col3:
                    st.metric(label="Decision Threshold", value=f"{result['decision_threshold']:.4f}")

                with st.expander("Inspect Transmitted Payload & Response"):
                    st.json({
                        "Client_Engineered_Payload": payload,
                        "FastAPI_Response": result
                    })
            else:
                st.error(f"API Error ({response.status_code}): {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Failed to connect to FastAPI. Ensure `uvicorn api.main:app` is running on port 8000.")