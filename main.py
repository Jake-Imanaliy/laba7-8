import json
import os
import aiohttp
import asyncio
from dotenv import load_dotenv

load_dotenv()
X_API_KEY = os.getenv("X_API_KEY")

API_URL = "https://api.ataix.kz/api/orders/"

INPUT_FILE = "result.json"
OUTPUT_FILE = "updated_orders.json"


async def fetch_order_status(session, order_id):
    url = f"{API_URL}{order_id}"
    headers = {
        "X-API-KEY": X_API_KEY,
        "Content-Type": "application/json"
    }
    async with session.get(url, headers=headers) as response:
        if response.status == 200:
            return await response.json()
        else:
            print(f"Error fetching {order_id}: {response.status}")
            return None


async def main():
    # Шаг 1: Чтение исходного файла
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        orders = json.load(file)

    updated_orders = []

    async with aiohttp.ClientSession() as session:
        for order in orders:
            order_id = order["order_id"]
            print(f"Проверка ордера: {order_id}")

            data = await fetch_order_status(session, order_id)
            print(f"🔍 Ответ API для {order_id}:\n{json.dumps(data, indent=2)}")


            if data and data["status"] == "filled":
                order["status"] = "filled"  # подтверждение
                cum_quote = float(data.get("cumQuoteQuantity", 0))
                commission = float(data.get("cumCommission", 0))
                quantity = float(data.get("origQuantity", order["quantity"]))

                buy_price = cum_quote / quantity
                sell_price = float(order["price"])
                profit = sell_price - buy_price
                percent = (profit / buy_price) * 100 if buy_price != 0 else 0

                order["profit_usdt"] = round(profit * quantity, 6)
                order["profit_percent"] = round(percent, 2)

                print(f"✔️ Ордер выполнен. Доход: {order['profit_usdt']} USDT ({order['profit_percent']}%)")

            updated_orders.append(order)

    # Шаг 3: Сохранение в файл
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump(updated_orders, out, indent=2, ensure_ascii=False)

    print(f"✅ Обновленные ордера сохранены в {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
