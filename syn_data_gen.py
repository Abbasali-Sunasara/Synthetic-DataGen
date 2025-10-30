import streamlit as st
import pandas as pd
from sdv.single_table import (
    GaussianCopulaSynthesizer,
    CTGANSynthesizer,
    TVAESynthesizer
)
from sdv.metadata import SingleTableMetadata
import matplotlib.pyplot as plt
import seaborn as sns
import time

st.set_page_config(layout="wide")
st.title("🔐 Synthetic Data Generator for Privacy")

def detect_sensitive_columns(df):
    synth_cols = []
    keep_cols = []

    for col in df.columns:
        col_lower = col.lower()
        unique_ratio = df[col].nunique() / len(df)

        if "id" in col_lower or df[col].is_unique or unique_ratio > 0.9:
            keep_cols.append(col)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            keep_cols.append(col)
        elif df[col].dtype == "object":
            avg_len = df[col].astype(str).str.len().mean()
            if avg_len > 15:
                keep_cols.append(col)
            else:
                synth_cols.append(col)
        else:
            synth_cols.append(col)

    return synth_cols, keep_cols

uploaded_file = st.file_uploader("📂 Upload your CSV", type="csv")
if uploaded_file:
    progress = st.progress(0)
    with st.spinner("📥 Reading file..."):
        df = pd.read_csv(uploaded_file)
        time.sleep(1)
    progress.progress(20)

    synth_cols, keep_cols = detect_sensitive_columns(df)
    st.success("✅ Columns successfully classified")
    st.write("🔍 **Synthesis Columns:**", synth_cols)
    st.write("✅ **Kept Columns:**", keep_cols)
    progress.progress(40)

    model_choice = st.selectbox(
        "🤖 Choose synthesizer model",
        [
            "GaussianCopula (Best for mixed tabular, fast training)",
            "CTGAN (Best for imbalanced categorical data)",
            "TVAE (Best for complex/large datasets, stable but slower)"
        ]
    )

    metadata = SingleTableMetadata()
    metadata.detect_from_dataframe(df[synth_cols])

    if "GaussianCopula" in model_choice:
        synthesizer = GaussianCopulaSynthesizer(metadata)
        selected_name = "GaussianCopula"
    elif "CTGAN" in model_choice:
        synthesizer = CTGANSynthesizer(metadata)
        selected_name = "CTGAN"
    elif "TVAE" in model_choice:
        synthesizer = TVAESynthesizer(metadata)
        selected_name = "TVAE"

    with st.spinner(f"⏳ Training {selected_name} synthesizer..."):
        synthesizer.fit(df[synth_cols])
        time.sleep(1)
    progress.progress(70)

    with st.spinner("🔄 Generating synthetic data..."):
        synthetic_sensitive = synthesizer.sample(num_rows=len(df))
        time.sleep(1)
    progress.progress(90)

    synthetic_df = df[keep_cols].reset_index(drop=True)
    synthetic_df[synth_cols] = synthetic_sensitive[synth_cols]
    progress.progress(100)
    st.success(f"🎉 Synthetic dataset ready using {selected_name}!")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("📘 Original Data")
        st.dataframe(df, use_container_width=True, height=400)
    with col2:
        st.subheader("📙 Synthetic Data")
        st.dataframe(synthetic_df, use_container_width=True, height=400)

    numeric_cols = [col for col in synth_cols if pd.api.types.is_numeric_dtype(df[col])]
    for col in numeric_cols:
        st.subheader(f"📊 Distribution Comparison: {col}")
        c1, c2 = st.columns(2)

        with c1:
            fig, ax = plt.subplots()
            sns.kdeplot(df[col], label='Original', fill=True, color="blue")
            plt.title("Original")
            st.pyplot(fig)

        with c2:
            fig, ax = plt.subplots()
            sns.kdeplot(synthetic_df[col], label='Synthetic', fill=True, color="orange")
            plt.title("Synthetic")
            st.pyplot(fig)

    st.subheader("Correlation Heatmaps (Sensitive Numeric Columns Only)")
    if len(numeric_cols) > 1:
        c1, c2 = st.columns(2)

        with c1:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(df[numeric_cols].corr(), annot=True, cmap="Blues")
            plt.title("Original Correlation")
            st.pyplot(fig)

        with c2:
            fig, ax = plt.subplots(figsize=(6, 4))
            sns.heatmap(synthetic_df[numeric_cols].corr(), annot=True, cmap="Oranges")
            plt.title("Synthetic Correlation")
            st.pyplot(fig)
    else:
        st.info("Not enough sensitive numeric columns for correlation heatmap.")

    st.download_button(
        label="📥 Download Synthetic CSV",
        data=synthetic_df.to_csv(index=False),
        file_name="synthetic_data.csv",
        mime="text/csv"
    )
