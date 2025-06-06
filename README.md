# 🖥️ Cool Terminal

A smart terminal-based system monitoring tool that provides real-time insights into your system's performance.

## 🚀 Features

- 📊 CPU, memory, disk, and process monitoring
- 🌐 Network activity tracking
- ⚠️ Custom alerts configuration
- 🎨 Rich CLI interface with color-coded output

## 🛠️ Tech Stack

- Python 3.x
- [rich](https://github.com/Textualize/rich)
- [psutil](https://github.com/giampaolo/psutil)
- [scapy](https://github.com/secdev/scapy)

## 📦 Installation

```bash
# Clone the repo
git clone https://github.com/anusha-kr01/cool_terminal.git
cd cool_terminal

# (Optional) Create a virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# ▶️ Usage
```bash
python main.py
```
You'll get a CLI dashboard with system stats, alerts, and monitoring tools.

# 📁 Project Structure
```bash
cool_terminal/
│
├── core/            # Core system monitors
├── ui/              # CLI UI components
├── config/          # Alert configuration
├── main.py          # Entry point
├── cli.py           # CLI command handler
├── requirements.txt # Python dependencies
└── README.md        # Project info
```

# 📝 License
This project is licensed under the MIT License.
