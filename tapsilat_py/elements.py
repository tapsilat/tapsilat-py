from .models import ElementsSession, ElementsSessionCreateRequest, ElementsSessionWithSecret


class ElementsMixin:
    """Tapsilat Elements sessions for the native Android and iOS card sheet.

    Your backend creates a session with its secret API key and passes only the session's
    ``client_secret`` to the app, which opens the sheet with it. Card data goes from the sheet to
    Tapsilat encrypted and never reaches your backend. Call these methods from your backend only.
    """

    def create_elements_session(
        self, request: ElementsSessionCreateRequest
    ) -> ElementsSessionWithSecret:
        """Create an Elements session.

        Hand the returned ``client_secret`` to the app that opens the card sheet; only this
        response carries it. Do not log or store it.
        """
        response = self._make_request(
            "POST", "/elements/sessions", json_payload=request.to_dict()
        )
        return ElementsSessionWithSecret.from_dict(response)

    def get_elements_session(self, session_id: str) -> ElementsSession:
        """Return the session's authoritative state and outcome.

        Read it on your backend before fulfilling, rather than trusting what the app reports.
        """
        endpoint = f"/elements/sessions/{self._path_id(session_id, 'session_id')}"
        return ElementsSession.from_dict(self._make_request("GET", endpoint))

    def cancel_elements_session(self, session_id: str) -> ElementsSession:
        """Cancel a session that is still waiting for a card.

        A session that is confirming or has completed comes back unchanged.
        """
        endpoint = f"/elements/sessions/{self._path_id(session_id, 'session_id')}/cancel"
        return ElementsSession.from_dict(self._make_request("POST", endpoint))
