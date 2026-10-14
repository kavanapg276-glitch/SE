"""Order queue manager for a food delivery kitchen.

Creates orders from a menu, moves them through delivery statuses,
totals the day's revenue and backs the queue up to disk as JSON.
"""
import json
import logging
from datetime import datetime

VALID_STATUSES = ["placed", "cooking", "out_for_delivery", "delivered"]
DEFAULT_MENU = {"pizza": 250, "burger": 150, "fries": 90, "coke": 40}


class OrderQueue:
    """Holds the menu and every order taken by the kitchen."""

    def __init__(self):
        self.orders = {}
        self.menu = {}
        self.next_id = 1

    def read_menu_config(self, file="menu.json"):
        """Load the menu from a JSON file, or fall back to the default."""
        try:
            with open(file, encoding="utf-8") as menu_file:
                self.menu = json.load(menu_file)
        except (OSError, json.JSONDecodeError):
            logging.info("Could not read %s, using the default menu", file)
            self.menu = dict(DEFAULT_MENU)

    def create_order(self, customer, items, order_history=None):
        """Create an order and return its id, or None if it is rejected."""
        if order_history is None:
            order_history = []
        if not customer or not items:
            logging.warning("Rejected order: customer and items required")
            return None
        unknown = [item for item in items if item not in self.menu]
        if unknown:
            logging.warning("Rejected order: unknown dishes %s", unknown)
            return None
        total = sum(self.menu[item] for item in items)
        self.orders[self.next_id] = {
            "customer": customer,
            "items": items,
            "total": total,
            "status": "placed",
        }
        order_history.append(self.next_id)
        self.next_id += 1
        return order_history[-1]

    def update_order_status(self, order_id, status):
        """Change an order's status. Return True if it was updated."""
        if status not in VALID_STATUSES:
            logging.warning("Invalid status %r for order %s", status, order_id)
            return False
        if order_id not in self.orders:
            logging.warning("Order %s not found", order_id)
            return False
        self.orders[order_id]["status"] = status
        return True

    def daily_revenue(self):
        """Return the total value of all delivered orders."""
        return sum(
            order["total"]
            for order in self.orders.values()
            if order["status"] == "delivered"
        )

    def backup_orders(self, file="orders.json"):
        """Save all orders to a JSON file."""
        with open(file, "w", encoding="utf-8") as backup_file:
            json.dump(self.orders, backup_file)

    def restore_orders(self, file="orders.json"):
        """Load orders back from a JSON file."""
        with open(file, encoding="utf-8") as backup_file:
            data = json.load(backup_file)
        # JSON turns integer keys into strings, so convert them back
        self.orders = {int(key): value for key, value in data.items()}
        self.next_id = max(self.orders, default=0) + 1

    def print_queue(self):
        """Print every order in the queue."""
        print(f"Order queue at {datetime.now()}")
        for order_id, order in self.orders.items():
            print(order_id, order["customer"], order["status"],
                  order["total"])


def main():
    """Run a small demo of the order queue."""
    queue = OrderQueue()
    queue.read_menu_config()
    asha_order = queue.create_order("Asha", ["pizza", "coke"])
    ravi_order = queue.create_order("Ravi", ["burger", "sushi"])
    empty_order = queue.create_order("", [])
    queue.update_order_status(asha_order, "delivered")
    queue.update_order_status(ravi_order, "teleported")
    queue.update_order_status(42, "delivered")
    queue.update_order_status(empty_order, "delivered")
    print("Revenue today:", queue.daily_revenue())
    queue.backup_orders()
    queue.restore_orders()
    queue.print_queue()


if __name__ == "__main__":
    main()
