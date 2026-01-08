from src.core.data_handler import analyze_data

import asyncio

async def run():
    await analyze_data()


if __name__ == "__main__":
    asyncio.run(run())