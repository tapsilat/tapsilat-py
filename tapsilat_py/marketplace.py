from typing import Optional

from .models import (
    MarketplaceAccountAction,
    MarketplaceApprovalPolicyInput,
    MarketplaceApprovalSettings,
    MarketplaceContractFilter,
    MarketplacePayoutApproval,
    MarketplacePayoutFilter,
    MarketplacePayoutOperationInput,
    MarketplaceProfileUpdate,
    MarketplaceReleasePolicyInput,
)


class MarketplaceMixin:
    """Marketplace API (version 2).

    Calls use the version 2 routes derived from ``base_url`` and are scoped to
    the API token's organization. Revisions are opaque strings: send them back
    exactly as received.
    """

    def list_marketplace_submerchants(
        self, page: int = 1, per_page: int = 20, external_id: Optional[str] = None
    ) -> dict:
        """List sellers; ``external_id`` selects an exact external ID match"""
        params = {"page": page, "per_page": per_page}
        if external_id:
            params["external_id"] = external_id
        return self._make_request("GET", "/submerchants", params=params, version="v2")

    def get_marketplace_submerchant(self, seller_id: str) -> dict:
        """Return the seller profile and its current revision"""
        endpoint = f"/submerchants/{self._path_id(seller_id, 'seller_id')}"
        return self._make_request("GET", endpoint, version="v2")

    def update_marketplace_submerchant(self, seller_id: str, update: MarketplaceProfileUpdate) -> dict:
        """Replace the seller profile at its revision; inspect ``approval_required``"""
        if not update.revision:
            raise ValueError("revision is required; read it with get_marketplace_submerchant")
        endpoint = f"/submerchants/{self._path_id(seller_id, 'seller_id')}"
        return self._make_request("PATCH", endpoint, json_payload=update.to_dict(), version="v2")

    def get_marketplace_seller_contracts(self, contract_filter: MarketplaceContractFilter) -> dict:
        """Return the selected accounts' requirements for a seller operation"""
        params = {
            "currency_id": contract_filter.currency_id,
            "seller_type": contract_filter.seller_type,
            "operation": contract_filter.operation,
            "vpos_id": list(contract_filter.vpos_ids),
        }
        return self._make_request(
            "GET", "/marketplace/seller-contracts", params=params, version="v2"
        )

    def get_marketplace_seller_accounts(self, seller_id: str) -> dict:
        """Return account registration, synchronization and available actions"""
        endpoint = f"/submerchants/{self._path_id(seller_id, 'seller_id')}/providers"
        return self._make_request("GET", endpoint, version="v2")

    def run_marketplace_seller_account_action(
        self, seller_id: str, vpos_id: str, action: MarketplaceAccountAction
    ) -> dict:
        """Run an action listed on the account at its revision and environment; inspect the returned status"""
        endpoint = (
            f"/submerchants/{self._path_id(seller_id, 'seller_id')}"
            f"/providers/{self._path_id(vpos_id, 'vpos_id')}/actions"
        )
        return self._make_request("POST", endpoint, json_payload=action.to_dict(), version="v2")

    def list_marketplace_payouts(self, payout_filter: Optional[MarketplacePayoutFilter] = None) -> dict:
        payout_filter = payout_filter or MarketplacePayoutFilter()
        return self._make_request(
            "GET", "/submerchant-payouts", params=payout_filter.to_params(), version="v2"
        )

    def get_marketplace_payout(self, payout_id: str) -> dict:
        """Return a payout's eligibility, approval and settlement state"""
        endpoint = f"/submerchant-payouts/{self._path_id(payout_id, 'payout_id')}"
        return self._make_request("GET", endpoint, version="v2")

    def approve_marketplace_payouts(self, approval: MarketplacePayoutApproval) -> dict:
        """Submit up to 100 eligible payouts for approval; poll the payouts for settlement"""
        return self._make_request(
            "POST", "/submerchant-payouts/approve", json_payload=approval.to_dict(), version="v2"
        )

    def list_marketplace_approval_policies(self) -> dict:
        return self._make_request("GET", "/marketplace/approval-policies", version="v2")

    def get_marketplace_approval_policy(self, policy_id: str) -> dict:
        endpoint = f"/marketplace/approval-policies/{self._path_id(policy_id, 'policy_id')}"
        return self._make_request("GET", endpoint, version="v2")

    def create_marketplace_approval_policy(self, policy: MarketplaceApprovalPolicyInput) -> dict:
        """Create an approval rule; a currency unit such as "TRY" is resolved to its UUID"""
        return self._make_request(
            "POST",
            "/marketplace/approval-policies",
            json_payload=self._approval_policy_payload(policy),
            version="v2",
        )

    def update_marketplace_approval_policy(
        self, policy_id: str, policy: MarketplaceApprovalPolicyInput
    ) -> dict:
        """Replace an approval rule; a currency unit such as "TRY" is resolved to its UUID"""
        endpoint = f"/marketplace/approval-policies/{self._path_id(policy_id, 'policy_id')}"
        return self._make_request(
            "PATCH", endpoint, json_payload=self._approval_policy_payload(policy), version="v2"
        )

    def delete_marketplace_approval_policy(self, policy_id: str) -> dict:
        endpoint = f"/marketplace/approval-policies/{self._path_id(policy_id, 'policy_id')}"
        return self._make_request("DELETE", endpoint, version="v2")

    def list_marketplace_release_policies(self) -> dict:
        return self._make_request("GET", "/marketplace/release-policies", version="v2")

    def get_marketplace_release_policy(self, policy_id: str) -> dict:
        endpoint = f"/marketplace/release-policies/{self._path_id(policy_id, 'policy_id')}"
        return self._make_request("GET", endpoint, version="v2")

    def create_marketplace_release_policy(self, policy: MarketplaceReleasePolicyInput) -> dict:
        return self._make_request(
            "POST", "/marketplace/release-policies", json_payload=policy.to_dict(), version="v2"
        )

    def update_marketplace_release_policy(
        self, policy_id: str, policy: MarketplaceReleasePolicyInput
    ) -> dict:
        endpoint = f"/marketplace/release-policies/{self._path_id(policy_id, 'policy_id')}"
        return self._make_request("PATCH", endpoint, json_payload=policy.to_dict(), version="v2")

    def delete_marketplace_release_policy(self, policy_id: str) -> dict:
        endpoint = f"/marketplace/release-policies/{self._path_id(policy_id, 'policy_id')}"
        return self._make_request("DELETE", endpoint, version="v2")

    def get_marketplace_approval_settings(self) -> dict:
        return self._make_request("GET", "/marketplace/approval-settings", version="v2")

    def update_marketplace_approval_settings(self, settings: MarketplaceApprovalSettings) -> dict:
        return self._make_request(
            "PATCH", "/marketplace/approval-settings", json_payload=settings.to_dict(), version="v2"
        )

    def run_marketplace_payout_operation(
        self, payout_id: str, operation: MarketplacePayoutOperationInput
    ) -> dict:
        """Change a payout allocation or withdraw approval; inspect ``status`` before treating it as complete"""
        endpoint = f"/submerchant-payouts/{self._path_id(payout_id, 'payout_id')}/operations"
        return self._make_request("POST", endpoint, json_payload=operation.to_dict(), version="v2")

    def get_marketplace_payout_operation(self, operation_id: str) -> dict:
        """Return a persisted payout operation receipt"""
        endpoint = f"/marketplace/payout-operations/{self._path_id(operation_id, 'operation_id')}"
        return self._make_request("GET", endpoint, version="v2")

    def reconcile_marketplace_payout_operation(self, operation_id: str) -> dict:
        """Check the provider result without repeating the change"""
        endpoint = f"/marketplace/payout-operations/{self._path_id(operation_id, 'operation_id')}/reconcile"
        return self._make_request("POST", endpoint, version="v2")

    def retry_marketplace_payout_operation(self, operation_id: str) -> dict:
        """Repeat an unresolved change only after the previous provider state is verified"""
        endpoint = f"/marketplace/payout-operations/{self._path_id(operation_id, 'operation_id')}/retry"
        return self._make_request("POST", endpoint, version="v2")

    def _approval_policy_payload(self, policy: MarketplaceApprovalPolicyInput) -> dict:
        payload = policy.to_dict()
        if payload.get("currency_id"):
            payload["currency_id"] = self.resolve_currency_id(payload["currency_id"])
        return payload
