"""
Configuración del API Gateway
Define las URLs base de todos los microservicios
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de microservicios"""
    
    # Gateway
    gateway_host: str = "0.0.0.0"
    gateway_port: int = 8000
    
    # Microservicios URLs (ajustar según despliegue real)
    # Grupo 1 - Usuarios
    users_service_url: str = "http://users-api:8001"
    
    # Grupo 2 - Canales
    channels_service_url: str = "http://channels-api:8002"
    
    # Grupo 3 - Hilos
    threads_service_url: str = "http://threads-api:8003"
    
    # Grupo 4 - Mensajes
    messages_service_url: str = "http://messages-api:8004"
    
    # Grupo 5 - Presencia
    presence_service_url: str = "http://presence-api:8005"
    
    # Grupo 6 - Moderación
    moderation_service_url: str = "http://moderation-api:8006"
    
    # Grupo 7 - Archivos (nuestro servicio)
    files_service_url: str = "http://134.199.176.197"
    
    # Grupo 8 - Búsqueda
    search_service_url: str = "http://search-api:8008"
    
    # Grupo 9 - Chatbot Académico
    chatbot_academic_service_url: str = "http://chatbot-academic-api:8009"
    
    # Grupo 10 - Chatbot de Utilidad
    chatbot_utility_service_url: str = "http://chatbot-utility-api:8010"
    
    # Grupo 11 - Chatbot de Cálculo
    chatbot_calc_service_url: str = "http://chatbot-calc-api:8011"
    
    # Grupo 12 - Chatbot de Wikipedia
    chatbot_wiki_service_url: str = "http://chatbot-wiki-api:8012"
    
    # Grupo 13 - Chatbot de Programación
    chatbot_programming_service_url: str = "http://chatbot-programming-api:8013"
    
    # Configuración
    request_timeout: int = 30
    max_retries: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
