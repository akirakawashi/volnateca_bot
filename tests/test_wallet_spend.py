import unittest

from domain.services.wallet import WalletService


class WalletSpendTests(unittest.TestCase):
    def test_spend_reduces_balance_and_increases_spent_total(self) -> None:
        result = WalletService.spend(
            balance_before=500,
            spent_points_total_before=100,
            amount=120,
        )
        self.assertEqual(result.balance_after, 380)
        self.assertEqual(result.spent_points_total_after, 220)

    def test_spend_rejects_insufficient_balance(self) -> None:
        with self.assertRaises(ValueError):
            WalletService.spend(
                balance_before=50,
                spent_points_total_before=0,
                amount=120,
            )

    def test_refund_spend_restores_balance(self) -> None:
        result = WalletService.refund_spend(
            balance_before=380,
            spent_points_total_before=220,
            amount=120,
        )
        self.assertEqual(result.balance_after, 500)
        self.assertEqual(result.spent_points_total_after, 100)


if __name__ == "__main__":
    unittest.main()
