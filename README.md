# 📈 Monte Carlo Cycle Time Simulator

A desktop application that predicts delivery timelines for backlog items using **Monte Carlo simulation** based on your historical cycle time data.

Built with **Python + Tkinter** 🐍🪟

---

## 🔧 Features

- 📁 Upload historical cycle time data from **Excel or CSV**
- 🔢 Set number of backlog items (N)
- 🧪 Run 10,000 to 30,000 Monte Carlo simulations
- 🎯 Choose percentiles: **P50, P80, P85, P90**
- 🔍 Limit cycle time history used (e.g., last 500 records)
- 📋 Results shown in a **sortable table**
- 📊 Forecasts visualized in a **line chart**
- ℹ️ **Help popup** explains how it works

---

## 🛠 Installation

Install required libraries:

```bash
pip install pandas numpy matplotlib openpyxl
