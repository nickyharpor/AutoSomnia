import requests
import logging
from typing import Dict, List, Optional, Union
from app.core.backend_config import settings

logger = logging.getLogger(__name__)


class CoinGeckoClient:
    """
    CoinGecko API client for fetching cryptocurrency prices and data.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize CoinGecko client.
        
        Args:
            api_key: CoinGecko Pro API key (optional, uses settings if not provided)
        """
        self.base_url = "https://api.coingecko.com/api/v3"
        self.api_key = api_key or getattr(settings, 'COINGECKO_API_KEY', None)
        
        self.headers = {}
        if self.api_key:
            self.headers["x-cg-demo-api-key"] = self.api_key
        
        logger.info("CoinGecko client initialized")
    
    def get_simple_price(
        self, 
        ids: Union[str, List[str]], 
        vs_currencies: Union[str, List[str]] = "usd",
        include_market_cap: bool = False,
        include_24hr_vol: bool = False,
        include_24hr_change: bool = False,
        include_last_updated_at: bool = False,
        precision: Optional[int] = None
    ) -> Dict:
        """
        Get simple price data for cryptocurrencies.
        
        Args:
            ids: Coin IDs (e.g., 'bitcoin', 'ethereum') - string or list of strings
            vs_currencies: Target currencies (e.g., 'usd', 'eur') - string or list of strings
            include_market_cap: Include market cap data
            include_24hr_vol: Include 24hr volume data
            include_24hr_change: Include 24hr price change data
            include_last_updated_at: Include last updated timestamp
            precision: Decimal precision for prices (0-18)
            
        Returns:
            Dictionary with price data
            
        Example:
            client = CoinGeckoClient()
            prices = client.get_simple_price(['bitcoin', 'ethereum'], ['usd', 'eur'])
        """
        try:
            url = f"{self.base_url}/simple/price"
            
            # Convert lists to comma-separated strings
            if isinstance(ids, list):
                ids = ",".join(ids)
            if isinstance(vs_currencies, list):
                vs_currencies = ",".join(vs_currencies)
            
            # Build query parameters
            params = {
                "ids": ids,
                "vs_currencies": vs_currencies
            }
            
            # Add optional parameters
            if include_market_cap:
                params["include_market_cap"] = "true"
            if include_24hr_vol:
                params["include_24hr_vol"] = "true"
            if include_24hr_change:
                params["include_24hr_change"] = "true"
            if include_last_updated_at:
                params["include_last_updated_at"] = "true"
            if precision is not None:
                params["precision"] = str(precision)
            
            # Make API request
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched prices for {ids}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching CoinGecko prices: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in CoinGecko API call: {e}")
            raise
    
    def get_token_price_by_contract(
        self,
        platform: str,
        contract_address: str,
        vs_currencies: Union[str, List[str]] = "usd"
    ) -> Dict:
        """
        Get token price by contract address.
        
        Args:
            platform: Platform ID (e.g., 'ethereum', 'binance-smart-chain')
            contract_address: Token contract address
            vs_currencies: Target currencies
            
        Returns:
            Dictionary with price data
        """
        try:
            url = f"{self.base_url}/simple/token_price/{platform}"
            
            # Convert lists to comma-separated strings
            if isinstance(vs_currencies, list):
                vs_currencies = ",".join(vs_currencies)
            
            params = {
                "contract_addresses": contract_address,
                "vs_currencies": vs_currencies
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully fetched token price for {contract_address}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching token price: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in token price API call: {e}")
            raise
    
    def search_coins(self, query: str) -> Dict:
        """
        Search for coins by name or symbol.
        
        Args:
            query: Search query (coin name or symbol)
            
        Returns:
            Dictionary with search results
        """
        try:
            url = f"{self.base_url}/search"
            params = {"query": query}
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"Successfully searched for: {query}")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching coins: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in coin search: {e}")
            raise


# Convenience functions for easy usage
def get_crypto_prices(
    coin_ids: Union[str, List[str]], 
    currencies: Union[str, List[str]] = "usd"
) -> Dict:
    """
    Convenience function to get cryptocurrency prices.
    
    Args:
        coin_ids: Coin IDs to fetch prices for
        currencies: Target currencies
        
    Returns:
        Dictionary with price data
    """
    client = CoinGeckoClient()
    return client.get_simple_price(coin_ids, currencies)


def get_token_price(
    platform: str,
    contract_address: str,
    currencies: Union[str, List[str]] = "usd"
) -> Dict:
    """
    Convenience function to get token price by contract address.
    
    Args:
        platform: Platform ID (e.g., 'ethereum')
        contract_address: Token contract address
        currencies: Target currencies
        
    Returns:
        Dictionary with price data
    """
    client = CoinGeckoClient()
    return client.get_token_price_by_contract(platform, contract_address, currencies)