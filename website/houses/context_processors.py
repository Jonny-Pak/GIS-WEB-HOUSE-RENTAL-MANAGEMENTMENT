from .models import House

def house_categories(request):
    """
    Returns the available house categories from the House model's HOUSE_TYPE_CHOICES
    to be available globally in all templates.
    """
    return {
        'house_categories': House.HOUSE_TYPE_CHOICES
    }
