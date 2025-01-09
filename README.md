# PumpFun Token Migration Tracker

**Python 3.8.20**

This script monitors PumpFun tokens after they complete their bonding curve phase and detects when they migrate to Raydium.

## Features

*   Listens to Solana blockchain events in real-time.
*   Tracks these tokens for migration to the Raydium DEX.
*   Provides alerts when a token migrates, including relevant links (SolScan, DexScreener, Birdeye).
*   Saves the detected token migrations to a CSV file (`solgrads.csv`) for future reference.

## Setup

1.  **Install required libraries:**

    ```bash
    pip install aiohttp websockets termcolor
    ```

2.  **Run the script:**

    ```bash
    python graduate.py
    ```

## Usage

1.  Make sure you have Python 3.8.20 installed.
2.  Clone this repository.
3.  Run the script (`python sol_scan.py`).

The script will connect to the Solana blockchain and start monitoring for new PumpFun tokens and their subsequent migration to Raydium.

**Note:** For more accurate, smooth results and improved performance, using a paid RPC service like QuickNode is recommended instead of the Solana mainnet public RPC.

