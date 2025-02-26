class FeatureStoreException(Exception):
    """Exceção base para todas as exceções da Feature Store."""
    pass

class ValidationError(FeatureStoreException):
    """Exceção para erros de validação."""
    pass

class RegistryError(FeatureStoreException):
    """Exceção para erros no registro de features."""
    pass

class TransformationError(FeatureStoreException):
    """Exceção para erros durante transformações."""
    pass

class StorageError(FeatureStoreException):
    """Exceção para erros de armazenamento."""
    pass

class ProcessingError(FeatureStoreException):
    """Exceção para erros durante o processamento de features."""
    pass

class ConfigurationError(FeatureStoreException):
    """Exceção para erros de configuração."""
    pass

class DependencyError(FeatureStoreException):
    """Exceção para erros relacionados a dependências."""
    pass

class SecurityError(FeatureStoreException):
    """Exceção para erros de segurança."""
    pass

class MonitoringError(FeatureStoreException):
    """Exceção para erros de monitoramento."""
    pass
