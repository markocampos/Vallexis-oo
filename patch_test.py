with open("test_main.py", "r") as f:
    content = f.read()

content = content.replace('seller = models.Seller(paymongo_subscription_id="sub_test", subscription_status="active")', 'seller = models.Seller(paymongo_subscription_id="sub_test_checkout", subscription_status="active")')

with open("test_main.py", "w") as f:
    f.write(content)
