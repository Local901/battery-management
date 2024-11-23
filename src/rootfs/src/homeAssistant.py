import requests

class HomeAssistant:
    def getState(entityId: str) -> str:
        """
        Get the state of a home assistant entity

        **raises**: Exception when state was failed to be retrieved.

        **returns**: The state of the entity.
        """
        request = requests.get(f"http://supervisor/core/api/states/{entityId}")
        
        # raise exception for http error statuses
        request.raise_for_status()

        data = request.json()
        state = data.state
        print(f"GET '{entityId}' = '{state}'")

        return state
