import asyncio
import aiohttp

async def delete_all_features(session):
    print("Deletando todas as features...")
    async with session.delete('http://localhost:8000/api/v1/features/') as response:
        if response.status == 200:
            print("Features deletadas com sucesso")
        else:
            print("Erro ao deletar features:", await response.text())

async def delete_all_feature_groups(session):
    print("Deletando todos os grupos de features...")
    async with session.delete('http://localhost:8000/api/v1/feature-groups/') as response:
        if response.status == 200:
            print("Grupos deletados com sucesso")
        else:
            print("Erro ao deletar grupos:", await response.text())

async def main():
    async with aiohttp.ClientSession() as session:
        await delete_all_features(session)
        await delete_all_feature_groups(session)

if __name__ == "__main__":
    asyncio.run(main())
