try:
    from utils.http import default_response
except ImportError:
    pass # raises ImportError in case imported outside of Django
