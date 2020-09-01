from aiogram import types


def get_prices(name, amount):
    prices = [
        types.LabeledPrice(label=name, amount=amount)
    ]
    return prices


POST_REG_SHIPPING = types.ShippingOption(
    id="post_reg",
    title="Почтой",
    prices=[
        types.LabeledPrice(
            "Обычная коробка", 10
        ),
        types.LabeledPrice(
            "Почтой обычной", 1000_00
        )
    ]
)

POST_FAST_SHIPPING = types.ShippingOption(
    id="post_fast",
    title="Почтой FAST",
    prices=[
        types.LabeledPrice(
            "Прочная коробка", 1000_00
        ),
        types.LabeledPrice(
            "Почтой срочной", 3000_00
        )
    ]
)

PICKUP_SHIPPING = types.ShippingOption(
    id="pickup",
    title="Самовывоз",
    prices=[
        types.LabeledPrice(
            "Самовывоз", -100_00
        )
    ]
)


