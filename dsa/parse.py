import xml.etree.ElementTree as ET
import re
import json
from typing import Any


def get_messages(data):
    """This function gets all messages"""
    all_data = data.findall("sms")
    if not all_data:
        return []
    return [node.attrib["body"] for node in all_data]


class TransactionMessages:
    def __init__(self, messages: Any):
        self.__all_messages = messages

    def check_messages(self, messages) -> list[str]:
        """This function checks if message is available"""
        if not messages:
            return None
        self.__all_messages = messages
        return self.__all_messages

    def get_received(self, messages) -> list[str]:
        """This function gets all income messages from Momo to Momo"""
        if not self.check_messages(messages):
            return []
        return [
            message
            for message in self.__all_messages
            if message.startswith("You have received")
        ]

    def get_momo_payment(self, messages) -> list[str]:
        """This function gets all momo payment messages"""
        import re

        if not self.check_messages(messages):
            return []
        return [
            message
            for message in self.__all_messages
            if re.search(r"your payment of", message, re.I)
        ]

    def get_bank_deposit(self, messages) -> list[str]:
        """This function gets all bank deposit messages"""
        if not self.check_messages(messages):
            return []
        return [
            message
            for message in self.__all_messages
            if message.startswith("*113*R*A bank deposit of")
        ]

    def get_withdraw(self, messages) -> list[str]:
        """This function gets all withdraw messages"""
        import re

        if not self.check_messages(messages):
            return []
        return [
            message
            for message in self.__all_messages
            if re.search("withdrawn", message, re.I)
        ]

    def get_transfer(self, messages) -> list[str]:
        """This function gets all transfer messages"""
        import re

        if not self.check_messages(messages):
            return []
        return [
            message
            for message in self.__all_messages
            if re.search(r"transferred to", message, re.I)
        ]


def parse_sms(xml_file, json_file):
    # Load XML
    tree = ET.parse(xml_file)
    root = tree.getroot()
    transactions = []

    # Regex to capture values from body
    pattern = re.compile(
        r"You have received (?P<amount>\d+)\s*RWF from (?P<sender>[^(]+).*"
        r"on your mobile money account at (?P<datetime>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}).*"
        r"Your new balance:(?P<balance>\d+)\s*RWF.*"
        r"Financial Transaction Id:\s*(?P<txid>\d+)"
    )

    for sms in root.findall("sms"):
        body = sms.get("body", "")
        match = pattern.search(body)

        record = {
            "id": sms.get("id"),
            "address": sms.get("address"),
            "date": sms.get("date"),
            "readable_date": sms.get("readable_date"),
            "body": body,
            "txid": None,
            "amount": None,
            "fee": None,  # could be added later if fee is in message
            "balance": None,
            "transaction_type": None,
            "sender": None,
            "receiver": None,
        }

        if match:
            record.update({
                "txid": match.group("txid"),
                "amount": match.group("amount"),
                "balance": match.group("balance"),
                "transaction_type": "credit",  # since message says "received"
                "sender": match.group("sender").strip(),
                "receiver": sms.get("address")  # or your mobile money account
            })

        transactions.append(record)

# Sort transactions by date
    transactions.sort(key=lambda x: x["date"])
    # Assign sequential IDs
    for idx, record in enumerate(transactions, start=1):
        record["id"] = str(idx)
        
    # Save to JSON
    with open(json_file, "w") as f:
        json.dump(transactions, f, indent=2)

    print(f"Saved {len(transactions)} transactions to {json_file}")


if __name__ == "__main__":
    momo_data = ET.parse("data/modified_sms_v2.xml")
    all_messages = get_messages(data=momo_data.getroot())
    user_transaction = TransactionMessages(messages=all_messages)

    json_path = "data/processed/dashboard.json"
    parse_sms("data/modified_sms_v2.xml", json_path)

    for pay in user_transaction.get_transfer(messages=all_messages):
        print(f"{pay}\n")
