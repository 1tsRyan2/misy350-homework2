import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import time

st.set_page_config(page_title="Smart Coffee Kiosk", layout="centered")
st.title("Smart Coffee Kiosk Application")

json_file = Path("inventory.json")
orders_file = Path("orders.json")

default_inventory = [
    {"id": 1, "name": "Espresso", "price": 2.50, "stock": 40},
    {"id": 2, "name": "Latte", "price": 4.25, "stock": 25},
    {"id": 3, "name": "Cold Brew", "price": 3.75, "stock": 30},
    {"id": 4, "name": "Mocha", "price": 4.50, "stock": 20},
    {"id": 5, "name": "Blueberry Muffin", "price": 2.95, "stock": 18}
]

if json_file.exists():
    with open(json_file, "r") as f:
        inventory = json.load(f)
else:
    inventory = default_inventory
    with open(json_file, "w") as f:
        json.dump(inventory, f, indent=4)

if orders_file.exists():
    with open(orders_file, "r") as f:
        saved_orders = json.load(f)
else:
    saved_orders = []
    with open(orders_file, "w") as f:
        json.dump(saved_orders, f, indent=4)

if "orders" not in st.session_state:
    st.session_state["orders"] = saved_orders

if "last_order" not in st.session_state:
    st.session_state["last_order"] = None

tab1, tab2, tab3, tab4 = st.tabs([
    "Place Order",
    "View Inventory",
    "Restock",
    "Manage Orders"
])

with tab1:
    st.subheader("Place Order")

    with st.container(border=True):
        item_names = []
        for item in inventory:
            item_names.append(item["name"])

        selected_item_name = st.selectbox("Select Item", item_names)
        quantity = st.number_input("Quantity", min_value=1, step=1, value=1)
        customer_name = st.text_input("Customer Name")

        if st.button("Place Order", type="primary", use_container_width=True):
            with st.spinner("Placing order..."):
                time.sleep(2)

                selected_item = None
                for item in inventory:
                    if item["name"] == selected_item_name:
                        selected_item = item
                        break

                if customer_name.strip() == "":
                    st.error("Please enter a customer name.")
                elif selected_item is None:
                    st.error("Item not found.")
                elif selected_item["stock"] < quantity:
                    st.error("Out of Stock")
                else:
                    selected_item["stock"] -= quantity
                    total_price = selected_item["price"] * quantity

                    order_id = len(st.session_state["orders"]) + 1

                    new_order = {
                        "order_id": order_id,
                        "customer": customer_name,
                        "item": selected_item["name"],
                        "quantity": quantity,
                        "total": round(total_price, 2),
                        "status": "Placed",
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }

                    st.session_state["orders"].append(new_order)
                    st.session_state["last_order"] = new_order

                    with open(json_file, "w") as f:
                        json.dump(inventory, f, indent=4)

                    with open(orders_file, "w") as f:
                        json.dump(st.session_state["orders"], f, indent=4)

                    st.success("Order Placed")

    if st.session_state["last_order"] != None:
        with st.expander("View Receipt"):
            last_order = st.session_state["last_order"]
            st.write(f"**Order ID:** {last_order['order_id']}")
            st.write(f"**Customer:** {last_order['customer']}")
            st.write(f"**Item:** {last_order['item']}")
            st.write(f"**Quantity:** {last_order['quantity']}")
            st.write(f"**Total:** ${last_order['total']:.2f}")
            st.write(f"**Status:** {last_order['status']}")
            st.write(f"**Time:** {last_order['time']}")

with tab2:
    st.subheader("View & Search Inventory")

    with st.container(border=True):
        search_text = st.text_input("Search Items")

        total_stock = 0
        for item in inventory:
            total_stock += item["stock"]

        st.metric("Total Items in Stock", total_stock)

        filtered_inventory = []
        for item in inventory:
            if search_text.strip() == "":
                filtered_inventory.append(item)
            elif search_text.lower() in item["name"].lower():
                filtered_inventory.append(item)

        if len(filtered_inventory) == 0:
            st.warning("No matching items found.")
        else:
            for item in filtered_inventory:
                with st.container(border=True):
                    st.write(f"**{item['name']}**")
                    st.write(f"ID: {item['id']}")
                    st.write(f"Price: ${item['price']:.2f}")

                    if item["stock"] < 10:
                        st.error(f"Low Stock: {item['stock']}")
                    else:
                        st.success(f"Stock: {item['stock']}")

with tab3:
    st.subheader("Restock")

    with st.container(border=True):
        restock_names = []
        for item in inventory:
            restock_names.append(item["name"])

        restock_item_name = st.selectbox("Select Item to Restock", restock_names)
        restock_amount = st.number_input("Amount to Add", min_value=1, step=1, value=1)

        if st.button("Update Stock", use_container_width=True):
            with st.spinner("Updating stock..."):
                time.sleep(2)

                for item in inventory:
                    if item["name"] == restock_item_name:
                        item["stock"] += restock_amount
                        break

                with open(json_file, "w") as f:
                    json.dump(inventory, f, indent=4)

                st.success(f"{restock_item_name} stock updated successfully.")

with tab4:
    st.subheader("Manage Orders")

    with st.container(border=True):
        active_orders = []
        for order in st.session_state["orders"]:
            if order["status"] == "Placed":
                active_orders.append(order)

        if len(st.session_state["orders"]) == 0:
            st.info("No orders have been placed yet.")
        else:
            st.write("### Current Orders")
            for order in st.session_state["orders"]:
                with st.container(border=True):
                    st.write(f"**Order ID:** {order['order_id']}")
                    st.write(f"Customer: {order['customer']}")
                    st.write(f"Item: {order['item']}")
                    st.write(f"Quantity: {order['quantity']}")
                    st.write(f"Total: ${order['total']:.2f}")

                    if order["status"] == "Placed":
                        st.success("Placed")
                    else:
                        st.error("Cancelled")

        if len(active_orders) > 0:
            cancel_options = []
            for order in active_orders:
                cancel_options.append(
                    f"Order #{order['order_id']} - {order['customer']} - {order['item']}"
                )

            selected_cancel = st.selectbox("Select Order to Cancel", cancel_options)

            if st.button("Cancel Order", type="primary", use_container_width=True):
                with st.spinner("Cancelling order..."):
                    time.sleep(2)

                    selected_order = None
                    for order in active_orders:
                        label = f"Order #{order['order_id']} - {order['customer']} - {order['item']}"
                        if label == selected_cancel:
                            selected_order = order
                            break

                    if selected_order != None:
                        for item in inventory:
                            if item["name"] == selected_order["item"]:
                                item["stock"] += selected_order["quantity"]
                                break

                        for order in st.session_state["orders"]:
                            if order["order_id"] == selected_order["order_id"]:
                                order["status"] = "Cancelled"
                                break

                        with open(json_file, "w") as f:
                            json.dump(inventory, f, indent=4)

                        with open(orders_file, "w") as f:
                            json.dump(st.session_state["orders"], f, indent=4)

                        st.success("Order Cancelled and Stock Refunded")
        else:
            st.info("No active orders to cancel.")
            