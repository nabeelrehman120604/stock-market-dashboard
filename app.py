import streamlit as st
import plotly.graph_objects as go

from database import StockDatabase
from data_fetcher import fetch_stock_data
from indicators import add_indicators


st.set_page_config(page_title="Stock Market Dashboard", layout="wide")

st.title("📈 Real-Time Stock Market Dashboard")
st.markdown(
    "<h4 style='text-align: center;'>Interactive Stock Analysis</h4>",
    unsafe_allow_html=True
)

st.sidebar.header("Settings")

symbol = st.sidebar.text_input("Stock Symbol", value="AAPL").upper()
period = st.sidebar.selectbox(
    "Select Period",
    ["3mo", "6mo", "1y", "5y"]
)

window = st.sidebar.number_input(
    "Indicator Window (Days)",
    min_value=5,
    max_value=100,
    value=20
)

db = StockDatabase()

if symbol:
    try:
        with st.spinner("Fetching stock data..."):
            api_data = fetch_stock_data(symbol, period)
            db.insert_stock_data(api_data, symbol)
            df = db.get_stock_data(symbol)

        if df.empty:
            st.warning("No data available.")
        else:
            # Period Filtering
            if period == "3mo":
                df = df.last("90D")
            elif period == "6mo":
                df = df.last("180D")
            elif period == "1y":
                df = df.last("365D")
            elif period == "5y":
                df = df.last("1825D")

            # Add indicators
            df = add_indicators(df, window)

            #Chart
            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["close"],
                    mode="lines",
                    line=dict(width=2),
                    name="Close Price"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[f"SMA_{window}"],
                    mode="lines",
                    line=dict(width=1.5, dash="dash"),
                    name=f"SMA {window}"
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df[f"EMA_{window}"],
                    mode="lines",
                    line=dict(width=1.8),
                    name=f"EMA {window}"
                )
            )

            fig.update_layout(
                template="plotly_dark",
                title=f"{symbol} Stock Price Trend",
                xaxis_title="Date",
                yaxis_title="Price",
                height=650,
                legend=dict(
                    orientation="h",
                    y=1.02,
                    x=1,
                    xanchor="right"
                )
            )

            st.plotly_chart(fig, use_container_width=True)


            # Key Metrics
            st.markdown("## Key Metrics")

            latest_close = df["close"].iloc[-1]
            previous_close = df["close"].iloc[-2]
            price_change = latest_close - previous_close
            percent_change = (price_change / previous_close) * 100

            col1, col2, col3 = st.columns(3)

            col1.metric("Latest Close", f"${latest_close:.2f}", f"{percent_change:.2f}%")
            col2.metric("Volume", f"{df['volume'].iloc[-1]:,}")
            col3.metric("Selected Period", period)

            st.markdown("---")


            # Performance Overview
            st.markdown("## 📊 Performance Overview")

            avg_price = df["close"].mean()
            highest_price = df["close"].max()
            lowest_price = df["close"].min()
            volatility = df["close"].std()
            total_return = ((df["close"].iloc[-1] - df["close"].iloc[0]) / df["close"].iloc[0]) * 100

            row1_col1, row1_col2, row1_col3 = st.columns(3)

            row1_col1.metric("Average Price", f"${avg_price:.2f}")
            row1_col2.metric("Highest Price", f"${highest_price:.2f}")
            row1_col3.metric("Lowest Price", f"${lowest_price:.2f}")

            row2_col1, row2_col2, row2_col3 = st.columns(3)

            row2_col1.metric("Volatility (Std Dev)", f"{volatility:.2f}")
            row2_col2.metric("Total Return", f"{total_return:.2f}%")
            row2_col3.metric("Data Points", len(df))

            st.markdown("---")

            # Download and View Raw Data

            csv = df.to_csv().encode("utf-8")

            st.download_button(
                label="Download Data as CSV",
                data=csv,
                file_name=f"{symbol}_data.csv",
                mime="text/csv"
            )

            with st.expander("View Raw Data"):
                st.dataframe(df.tail(50))


    except Exception:
        st.error("Invalid symbol or unable to fetch data.")