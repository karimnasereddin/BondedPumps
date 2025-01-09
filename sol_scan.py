import asyncio
import json
import csv
from datetime import datetime
import aiohttp
from websockets import connect
from urllib.parse import urlparse
import os
import platform
from termcolor import cprint, colored

RAYDIUM_PROGRAM_ID="675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
PUMP_FUN_PROGRAM_ID="6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

CSV_FILE_PATH="sol_scan.csv"
SOLANA_RPC_URL="https://api.mainnet-beta.solana.com"
TOKEN_PROGRAM_ID = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"

 
async def main():
    while True:
        try:
            await run_websocket()
        except Exception as e:
            print(f'Error in Websocket connection: {e}')
            print(f'Reconnecting...')
            await asyncio.sleep(1)
        
async def print_confirmation():
    while True:
        await asyncio.sleep(30)
        print("Still listening to the WSS...")

async def run_websocket():
    url = urlparse('wss://api.mainnet-beta.solana.com')
    async with connect(url.geturl()) as websocket:
        print("Connected to Websocket")

        subscribe_msg= {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "logsSubscribe",
            "params": [
                {
                    "mentions": [PUMP_FUN_PROGRAM_ID]
                },
                {
                    "commitment": "finalized"
                }
            ]
        }

        await websocket.send(json.dumps(subscribe_msg))

        seen_signatures = set()
        ensure_csv_file_exists()
        session= aiohttp.ClientSession()

        # start the confirmation task
        confirmation_task= asyncio.create_task(print_confirmation())

        try:
            while True:
                try:
                    message= await asyncio.wait_for(websocket.recv(), timeout=30)
                    data= json.loads(message)
                    #print(f"Data received: {data}") 
                    if "params" in data and "result" in data["params"]:
                        signature= data["params"]["result"]["value"].get("signature")
                        if signature and signature not in seen_signatures:
                            seen_signatures.add(signature)
                            logs= data["params"]["result"]["value"].get("logs", [])
                            #if any("InitializeMint2" in log for log in logs): #raydium
                            if any("Program log: Instruction: MintTo" in log for log in logs):
                                new_token= await get_new_token(session,signature)
                                if new_token:
                                    cprint(f"New token launched: {new_token}", 'white', 'on_blue', attrs=['bold'])
                                    cprint(f"https://solscan.io/token/{new_token}", 'white', 'on_green', attrs=['bold'])
                                    save_to_csv(new_token, signature)

                except asyncio.TimeoutError:
                    await websocket.ping()

        finally:
            confirmation_task.cancel()
            await session.close()
    
async def get_new_token(session,signature):
    request_body={
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTransaction",
        "params":[
            signature,
            {
                "encoding": "jsonParsed",
                "commitment": "finalized",
                "maxSupportedTransactionVersion": 0
            },

        ]
    }

    async with session.post(SOLANA_RPC_URL, json=request_body) as response:
        data = await response.json()
        #print(f"Data received: {data}")
        instructions = data.get("result",{}).get("transaction",{}).get("message",{}).get("instructions",[])
        for instruction in instructions:           
            program_id = instruction.get("programId")
            if program_id == PUMP_FUN_PROGRAM_ID:
                accs= instruction.get("accounts",[])
                if len(accs)==12:
                    return accs[2]

    return None

def ensure_csv_file_exists():
    if not os.path.exists(CSV_FILE_PATH) or os.path.getsize(CSV_FILE_PATH)==0:
        with open(CSV_FILE_PATH,'w',newline='') as file:
            writer=csv.writer(file)
            writer.writerow(["Token Address","Time Found","Epoch Time","Solscan Link","DexScreener Link","Birdeye Link"])

def save_to_csv(new_token,signature):
    with open(CSV_FILE_PATH,'a',newline='') as file:
        writer=csv.writer(file)
        now=datetime.utcnow()
        time_found= now.strftime("%Y-%m-%d %H:%M:%S")
        epoch_time= int(now.timestamp())
        solscan_link= f'https://solscan.io/tx/{signature}'
        dexscreener_link=f'https://dexscreener.com/token/{new_token}'
        birdeye_link=f'https://birdeye.so/{new_token}'

        writer.writerow([new_token ,time_found ,epoch_time ,solscan_link ,dexscreener_link ,birdeye_link ])


if __name__=="__main__":
    if platform.system()=="Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

