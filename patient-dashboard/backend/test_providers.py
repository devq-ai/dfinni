import asyncio
from app.services.provider_service import ProviderService
from app.models.provider import ProviderSearchFilters

async def test():
    service = ProviderService()
    filters = ProviderSearchFilters()
    try:
        result = await service.list_providers(filters, page=1, limit=10)
        print("Success:", result)
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test())