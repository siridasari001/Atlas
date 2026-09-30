from app.core.config import settings


print("Atlas is starting...")
print(f"Environment: {settings.atlas_env}")
print(f"LLM Provider: {settings.llm_provider}")