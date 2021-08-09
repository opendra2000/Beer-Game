"""Constants and Configurations."""
from enum import Enum

class Role(Enum):
    """Enum class for User Roles."""

    PLAYER = 'player'
    INSTRUCTOR = 'instructor'

class Game_Role(Enum):
    """Enum class for game player roles"""
    DISTRIBUTOR = 'distributor'
    WHOLESALER = 'wholesaler'
    FACTORY = 'factory'
    RETAILER = 'retailer'