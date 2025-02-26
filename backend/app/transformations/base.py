from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import pandas as pd

class BaseTransformation(ABC):
    """Classe base para todas as transformações de features."""
    
    def __init__(self):
        """Inicializa a transformação."""
        pass

    @abstractmethod
    def handle_missing(self, data: pd.Series, strategy: str) -> pd.Series:
        """
        Trata valores faltantes nos dados.
        
        Args:
            data: Série de dados a ser processada
            strategy: Estratégia para tratar valores faltantes
            
        Returns:
            Série com valores faltantes tratados
        """
        pass

    def validate_input(self, data: pd.Series) -> bool:
        """
        Valida os dados de entrada.
        
        Args:
            data: Série de dados a ser validada
            
        Returns:
            True se os dados são válidos, False caso contrário
        """
        return isinstance(data, pd.Series) and not data.empty

    def preprocess(self, data: pd.Series) -> pd.Series:
        """
        Pré-processa os dados antes da transformação.
        
        Args:
            data: Série de dados a ser pré-processada
            
        Returns:
            Série pré-processada
        """
        if not self.validate_input(data):
            raise ValueError("Dados de entrada inválidos")
        return data.copy()

    def postprocess(self, data: pd.Series) -> pd.Series:
        """
        Pós-processa os dados após a transformação.
        
        Args:
            data: Série de dados a ser pós-processada
            
        Returns:
            Série pós-processada
        """
        return data
