import asyncio
from app.services.provider_service import ProviderService
from app.models.provider import ProviderCreate

async def create_sample_providers():
    service = ProviderService()
    
    providers = [
        ProviderCreate(
            first_name="Dr. Sarah",
            last_name="Johnson",
            email="sarah.johnson@pfinni.com",
            phone="(555) 123-4567",
            role="doctor",
            specialization="Cardiology",
            license_number="MD123456",
            department="Cardiology",
            status="active",
            hire_date="2015-03-15"
        ),
        ProviderCreate(
            first_name="Mary",
            last_name="Smith", 
            email="mary.smith@pfinni.com",
            phone="(555) 234-5678",
            role="nurse",
            license_number="RN789012",
            department="Emergency",
            status="active",
            hire_date="2018-06-20"
        ),
        ProviderCreate(
            first_name="James",
            last_name="Wilson",
            email="james.wilson@pfinni.com",
            phone="(555) 345-6789",
            role="admin",
            license_number="ADM345678",
            department="Administration",
            status="active",
            hire_date="2020-01-10"
        ),
        ProviderCreate(
            first_name="Dr. Michael",
            middle_name="James",
            last_name="Brown",
            email="michael.brown@pfinni.com",
            phone="(555) 456-7890",
            role="specialist",
            specialization="Neurology",
            license_number="MD987654",
            department="Neurology",
            status="active",
            hire_date="2012-09-01"
        ),
    ]
    
    for provider_data in providers:
        try:
            provider = await service.create_provider(provider_data, "admin-user-id")
            print(f"Created provider: {provider.first_name} {provider.last_name}")
        except Exception as e:
            print(f"Error creating provider {provider_data.first_name} {provider_data.last_name}: {e}")

if __name__ == "__main__":
    asyncio.run(create_sample_providers())